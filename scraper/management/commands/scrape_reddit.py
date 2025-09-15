import praw
import os
from dotenv import load_dotenv
from .query_related import generate_queries
from django.core.management.base import BaseCommand
from scraper.models import SocialMediaPost, Comment, ExtractedInfo
from django.core.paginator import Paginator
import json
import google.generativeai as genai
from django.core.paginator import Paginator
import os
from django.db.models import Prefetch


load_dotenv()
genai.configure(api_key=os.environ.get('GEMINI'))
class Command(BaseCommand):
    @staticmethod
    def load_reddit_profile():
        # Try multiple Reddit configurations
        reddit_configs = []

        # Config 1: User 1
        if os.getenv("REDDIT_ID") and os.getenv("REDDIT_SECRET"):
            reddit_configs.append({
                "client_id": os.getenv("REDDIT_ID"),
                "client_secret": os.getenv("REDDIT_SECRET"),
                "user_agent": f"{os.getenv('OS')}:oceanhazard:1.0 (by u/{os.getenv('REDDIT_USERNAME')})",
                "name": "User1"
            })

        # Initialize working Reddit instance
        reddit = None
        for config in reddit_configs:
            try:
                reddit = praw.Reddit(
                    client_id=config["client_id"],
                    client_secret=config["client_secret"],
                    user_agent=config["user_agent"]
                )
                print(f"Using {config['name']} - {config['user_agent']}")
                return reddit
            except Exception as e:
                print(f"✗ {config['name']} failed: {e}")
                continue

        if not reddit:
            print("No working Reddit configuration found!")
            exit(1)
    
    reddit = load_reddit_profile()


    @staticmethod
    def fetch_posts(query_dict, limit=5, time_filter="day"):
        """fetches and saves the post in post model."""
        query = query_dict["query"]
        location = query_dict['location']
        hazard = query_dict['hazard']

        print(f"\n Searching for: {query}")
        reddit = Command.reddit

        try:
            for post in reddit.subreddit("all").search(query, time_filter=time_filter, limit=limit):
                # Check for duplicates
                existing_post = SocialMediaPost.objects.filter(url=post.url).first()
                if existing_post:
                    print(f"- Skipping duplicate: {post.title[:50]}...")
                    continue
                    
                p = SocialMediaPost.objects.create(location = location, 
                                            hazard=hazard,
                                            title=post.title,
                                            body=post.selftext,
                                            url=post.url,    
                                            reddit_id = post.id                       
                                            )
                p.save()
                print(f"- {post.title} (Score: {post.score}, Subreddit: {post.subreddit.display_name})")
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            return f"Error: {e}"

        return
    
    @staticmethod
    def fill_prompt(data):
        return f"""
You are a classifier that analyzes social media posts to determine whether they report **real, ongoing ocean-related hazards** anywhere in the world. 

Instructions:
1. Only classify a post as a hazard if it refers to a **real, current, or very recent ocean disaster** (e.g., tsunami, storm surge, high waves, coastal flooding, or dangerous coastal currents).
2. Do NOT classify posts as hazards if they:
   - Talk about past events or historical disasters
   - Are fictional stories, books, or movies
   - Are hypothetical, speculative, or personal memories
   - Refer to simulations, reports, or educational content without immediate danger
3. Take into account the **search query** that caused the post to appear. Use it as context to help determine whether the post is relevant to a real, ongoing hazard.
4. The output must be a JSON array, where each element corresponds to a post, with:
   - `"id"`: the post id
   - `"is_hazard"`: `true` if the post is a real, ongoing ocean disaster, `false` otherwise

Input JSON:
{data}

Output example:
[
  {{"id": 1, "is_hazard": true}},
  {{"id": 2, "is_hazard": false}}
]

**Return strictly valid JSON, no extra text, no explanations.**
"""

    

    @staticmethod
    def verify_post(posts, per_page_limit = 5):
        paginator = Paginator(posts, per_page_limit)
        for i in range(1, paginator.num_pages + 1):
            data = []
            page = paginator.get_page(i)
            for post in page.object_list:
                post_info = {}
                post_info['id'] = post.pk
                post_info['title'] = post.title
                post_info['body'] = post.body
                post_info['search_query'] = f"{post.hazard} {post.location}"
                
                data.append(post_info)
            
            data_json = json.dumps(data)

            prompt = Command.fill_prompt(data_json)


            json_schema = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "is_hazard": {"type": "boolean"}
                    },
                    "required": ["id", "is_hazard"]
                }
            }
            model = genai.GenerativeModel("gemini-2.5-flash", generation_config=
                        {
                        "response_mime_type": "application/json",
                        "response_schema": json_schema 
                        })
            response = model.generate_content(prompt)

            try:
                result = json.loads(response.text)
                                   
                
            except json.JSONDecodeError:
                result = {"error": "Invalid JSON returned by Gemini", "raw_response": response.text}

            print(f"Page {i} done")
            for item in result:
                relevent_post = SocialMediaPost.objects.get(pk= item['id'])
                relevent_post.tested = True
                relevent_post.verified = item['is_hazard']
                relevent_post.save()
                print(f"For post with id {item['id']}, verification status updated: {item['is_hazard']}")            
    
    
    def fetch_comments(post_obj: SocialMediaPost):
        """
        Fetch top 10 top-level comments and up to 5 replies for each,
        and save them into the Comment model.
        """

        if not post_obj.tested:
            print(f"Post with ID:{post_obj.id} hasn't been verified yet.")
            return
        elif not post_obj.verified:
            print(f"Post with ID:{post_obj.id} isn't about ocean hazard.")
            return
        reddit = Command.reddit
        # Create a submission object from stored post URL
        submission = reddit.submission(id = post_obj.reddit_id)
        submission.comment_sort = "top"
        submission.comment_limit = 10  # Fetch only top 10 comments

        # Replace 'load more comments' placeholders
        submission.comments.replace_more(limit=0)

        # Get top 10 top-level comments
        top_comments = submission.comments[:10]

        for top_comment in top_comments:
            # Save the top-level comment
            if not len(Comment.objects.filter(reddit_id = top_comment.id)):
                parent_comment = Comment.objects.create(
                    post=post_obj,
                    text=top_comment.body,
                    score=top_comment.score,
                    parent=None,
                    reddit_id = top_comment.id
                )
                parent_comment.save()
                print('comment created')

                #NOTE TO SELF: add logic to fetch nested replies.


                # # Fetch up to 5 direct replies for each top-level comment
                # top_comment.replies.replace_more(limit=0)

                # # Now .replies.list() will contain ALL actual reply objects
                # replies = top_comment.replies.list()[:5]  # limit to 5 replies

                # for reply in replies:
                #     # Skip duplicate check if you already store reddit_id
                #     Comment.objects.create(
                #         post=post_obj,
                #         text=reply.body,
                #         score=reply.score,
                #         parent=parent_comment
                #     )
                #     print('Reply comment created:', reply.body[:50])

    @staticmethod
    def get_posts_with_comments(location):
        """
        Fetch up to 5 posts for the given location, 
        with each post having up to 10 related comments preloaded.
        """
        posts = (
            SocialMediaPost.objects
            .filter(location=location)
            .prefetch_related(
                Prefetch(
                    'comment_set',
                    queryset=Comment.objects.order_by('-score')[:10],
                    to_attr='top_comments'
                )
            )
            .order_by('-timestamp')[:5]
        )
        return posts

    @staticmethod
    def format_posts_for_gemini(posts):
        data = []
        for post in posts:
            post_data = {
                "title": post.title,
                "body": post.body,
                "hazard": post.hazard,
                "url": post.url,
                "comments": [
                    {"text": comment.text, "score": comment.score}
                    for comment in getattr(post, 'top_comments', [])
                ]
            }
            data.append(post_data)
        return json.dumps(data, indent=2)


    def extract_info_from_gemini(posts):
        formatted_data = Command.format_posts_for_gemini(posts)
        
        prompt = f"""
        You are given social media posts and comments about ocean-related hazards.
        Your task is to carefully extract structured information.
        
        Required JSON format:
        {{
        "life_loss": "number of lives lost or 'unknown'(max length <= 20)",
        "infra_lost": "description of infrastructure damaged or lost",
        "hazard_type": "tsunami | storm_surge | high_waves | swell_surge | coastal_flooding | unusual_tides | coastal_erosion | other",
        "intensity": "1-10 scale of intensity",
        "emotions": "single word describing general emotion (fear, panic, sadness, etc.)",
        "hazard_description": "summary of the hazard event",
        "keywords": "comma-separated keywords relevant to the event"
        }}

        ** The posts are all about same hazard, just return single json, which gives overall details. Don't return separate info for each post **

        Here are the posts:
        {formatted_data}
        """

        model = genai.GenerativeModel("gemini-2.5-flash", generation_config=
                    {
                    "response_mime_type": "application/json",
                    })
        response = model.generate_content(prompt)

        return json.loads(response.text) 


    @staticmethod
    def process_location(location):
        posts = Command.get_posts_with_comments(location)
        if not posts:
            print("No posts found for this location.")
            return None

        # Send posts to Gemini for extraction
        extracted_data = Command.extract_info_from_gemini(posts)
        print(extracted_data)
        # Create ExtractedInfo instance
        info = ExtractedInfo.objects.create(
            life_loss=extracted_data["life_loss"],
            infra_lost=extracted_data["infra_lost"],
            hazard_type=extracted_data["hazard_type"],
            intensity=extracted_data["intensity"],
            emotions=extracted_data["emotions"],
            hazard_description=extracted_data["hazard_description"],
            keywords=extracted_data["keywords"],
        )

        info.related_posts.add(*posts)
        print(f"ExtractedInfo created with ID: {info.id}")
        return info


    def handle(self, *args, **kwargs):
        # queries = generate_queries()
        # for q in queries[:4]:
        #     Command.fetch_posts(q, time_filter ='all')
        
        # posts = SocialMediaPost.objects.filter(location='dummy')
        # for p in posts:
        #     print(p.pk, p.title, p.url, len(p.comment_set.all()))
        # Command.verify_post(posts[:5], 5)
        # Command.fetch_comments(posts[0])
        # info_obj = Command.process_location('dummy')
        # info_obj.save()


        ei = ExtractedInfo.objects.all()[0]
        print(ei.__dict__)

