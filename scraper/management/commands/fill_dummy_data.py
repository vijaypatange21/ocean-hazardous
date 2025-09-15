import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from scraper.models import SocialMediaPost, Comment


class Command(BaseCommand):
    help = "Seed database with realistic social media posts for a single ongoing hazard event"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Seeding disaster scenario dummy data..."))

        # Clear previous dummy data
        SocialMediaPost.objects.filter(location="dummy").delete()

        # Fixed hazard and location
        hazard = "Tsunami"
        location = "dummy"

        # Templates for varied realistic reporting
        post_templates = [
            "Massive waves spotted approaching the coast. Local authorities urging people to move to higher ground immediately. Many fishing boats are still at sea!",
            "Reports coming in of strong tremors followed by a huge wave hitting coastal villages. Power lines are down and people are trying to evacuate.",
            "Several villages near the coast are completely flooded. Families are stuck on rooftops waiting for rescue teams. Water levels are still rising!",
            "Emergency sirens are blaring. Witnesses report boats being thrown onto the roads by powerful waves. This looks worse than anything we've seen in years.",
            "Chaos in coastal markets as people rush to evacuate. Supplies are running out quickly. No clear information on the number of casualties yet.",
            "Local news showing harrowing scenes: homes destroyed, families searching for loved ones. Rescuers are having difficulty reaching some areas due to submerged roads.",
            "Hospitals are overflowing with injured people. Volunteers are being asked to donate blood. Entire neighborhoods have lost communication due to the storm surge.",
            "Authorities are struggling to coordinate relief efforts. Evacuation centers are packed and there are reports of missing children.",
        ]

        comment_templates = [
            "Praying for everyone affected. Stay strong!",
            "My cousin lives near the coast, still can't reach him on phone.",
            "The government should have warned earlier, this is a disaster!",
            "Just saw live footage on TV, absolutely terrifying.",
            "Fishermen are the most vulnerable, many still haven't returned.",
            "Hearing rumors of another wave coming, is this true?",
            "Rescue teams are doing their best but the situation is chaotic.",
            "Stay safe everyone, don't take chances!",
            "Shocking to see so many people displaced overnight.",
            "Relief camps are overcrowded, urgent help needed!"
        ]

        # Create 6 posts simulating ongoing updates about the same event
        for i in range(6):
            title = f"[URGENT] {hazard} update - Situation worsening"
            body = random.choice(post_templates)

            post = SocialMediaPost.objects.create(
                location=location,
                hazard=hazard,
                title=title,
                body=body,
                url=f"https://reddit.com/r/oceanhazards/post_{i+1}",
                reddit_id=f"dummy_post_{i+1}",
                timestamp=timezone.now(),
                tested=bool(random.choice([True, False])),
                verified=bool(random.choice([True, False])),
            )

            self.stdout.write(self.style.SUCCESS(f"Created post: {title}"))

            # Add 7-8 comments per post
            for j in range(random.randint(7, 8)):
                comment_text = random.choice(comment_templates)
                Comment.objects.create(
                    post=post,
                    text=comment_text,
                    score=random.randint(1, 200),
                    parent=None,
                    reddit_id=f"dummy_comment_{post.id}_{j+1}",
                )

            self.stdout.write(self.style.SUCCESS(f"Added comments for post {post.id}"))

        self.stdout.write(self.style.SUCCESS("Scenario dummy data seeding complete!"))
