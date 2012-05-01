from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	foursquare_token = models.CharField(max_length=200, null=True, blank=True)
	
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)
		
post_save.connect(create_user_profile, sender=User)