from django.db import models

# Create your models here.
class SocialMediaPost(models.Model):
    location = models.CharField(max_length=100)
    hazard = models.CharField(max_length=50)
    title = models.TextField()
    url = models.URLField()
    timestamp = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)

class Comment(models.Model):
    post = models.ForeignKey(SocialMediaPost, on_delete=models.CASCADE)
    text = models.TextField()
    sentiment = models.FloatField()
    urgent = models.BooleanField()
    score = models.IntegerField()
