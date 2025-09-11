import praw
import os
from dotenv import load_dotenv
from .query_related import generate_queries
from datetime import datetime
# from models import SocialMediaPost
import django

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "incois.settings")
django.setup()
from scraper.models import SocialMediaPost

queries = generate_queries()

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
        test_reddit = praw.Reddit(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            user_agent=config["user_agent"]
        )
        # Test with a simple request
        list(test_reddit.subreddit("test").hot(limit=1))
        reddit = test_reddit
        print(f"✓ Using {config['name']} - {config['user_agent']}")
        break
    except Exception as e:
        print(f"✗ {config['name']} failed: {e}")
        continue

if not reddit:
    print("No working Reddit configuration found!")
    exit(1)

def fetch_posts(query_dict, limit=5, time_filter="day"):
    """fetches and saves the post in post model."""
    query = query_dict["query"]
    location = query_dict['location']
    hazard = query_dict['hazard']

    print(f"\n Searching for: {query}")

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
                                           url=post.url,                           
                                           )
            p.save()
            print(f"- {post.title} (Score: {post.score}, Subreddit: {post.subreddit.display_name})")
    except Exception as e:
        print(f"Error searching for '{query}': {e}")
        return f"Error: {e}"

    return "Done"

print(fetch_posts(queries[0]))