from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Book(models.Model):
	"""Collection of Entries"""
	title = models.CharField(max_length=200)
	cover = models.ForeignKey('Photo', null=True, blank=True)
	owner = models.ForeignKey(User)

	def __unicode__(self):
		return self.title

class Entry(models.Model):
	"""Model for entries in the journal. Usually based around a checkin/venue"""
	# Title
	title = models.CharField(max_length=200)
	# Description
	description = models.TextField()
	# Published Date
	pub_date = models.DateTimeField('date published', default=timezone.now)
	# Checkin
	checkin = models.ForeignKey('Checkin', null=True, blank=True, on_delete=models.SET_NULL)
	# Book
	book = models.ForeignKey(Book, null=True, blank=True)

	def __unicode__(self):
		return self.title

class Checkin(models.Model):
	"""Model for Foursquare Checkins"""
	# Checkin id
	checkin_id = models.CharField(max_length=200)
	# Datetime when checkin occurred
	created_at = models.DateTimeField(default=timezone.now)
	# Venue Name
	venue_name = models.CharField(max_length=200)

	def __unicode__(self):
		return self.checkin_id

class Photo(models.Model):
	"""Model for user-uploaded Entry photos"""
	# Entry
	entry = models.ForeignKey(Entry)
	# File
	image = models.FileField(upload_to='photos')

	def __unicode__(self):
		return str(self.id)