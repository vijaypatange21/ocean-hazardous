from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class SocialMediaPost(models.Model):
    location = models.CharField(max_length=100)
    hazard = models.CharField(max_length=50)
    title = models.TextField()
    body = models.TextField()
    url = models.URLField()
    reddit_id = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    tested = models.BooleanField(default=False) #whether it went through verification process or not
    verified = models.BooleanField(default=False)

class Comment(models.Model):
    post = models.ForeignKey(SocialMediaPost, on_delete=models.CASCADE)
    text = models.TextField()
    score = models.IntegerField()
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,related_name='replies')
    reddit_id = models.CharField(max_length=50, blank=True, null=True) #note to self:remove blank and null atrribute later

class ExtractedInfo(models.Model):
    HAZARD_TYPES = [
        ('tsunami', 'Tsunami'),
        ('storm_surge', 'Storm Surge'),
        ('high_waves', 'High Waves'),
        ('swell_surge', 'Swell Surge'),
        ('coastal_flooding', 'Coastal Flooding'),
        ('unusual_tides', 'Unusual Tides'),
        ('coastal_erosion', 'Coastal Erosion'),
        ('other', 'Other'),
    ]
    
    life_loss = models.CharField(max_length=20)
    infra_lost = models.TextField()
    hazard_type = models.CharField(max_length=20, choices=HAZARD_TYPES)
    intensity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    emotions = models.CharField(max_length=20)
    hazard_description = models.TextField()
    keywords = models.TextField()

    related_posts = models.ManyToManyField('SocialMediaPost', related_name='extractions')
    created_at = models.DateTimeField(auto_now_add=True)


    def keyword_list(self):
        """Return keywords as a list, stripping spaces."""
        return [k.strip() for k in self.keywords.split(",") if k.strip()]

    def __str__(self):
        return f"{self.get_hazard_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"