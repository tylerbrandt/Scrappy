from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from sorl.thumbnail import ImageField, get_thumbnail

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
	# cover photo
	cover_photo = models.ForeignKey('Photo', null=True, blank=True, related_name='coverphoto')

	# order
	#orderNum = models.PositiveIntegerField(default=0)

	class Meta:
		order_with_respect_to= 'book'
		#unique_together = ('book','_order')

	def save(self, *args, **kwargs):
		#if self.orderNum is 0:
		#	self.orderNum = len(Entry.objects.filter(book=self.book)) + 1

		super(Entry, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.title
		
	def alt_photos(self):
		"""Return Photos for current Entry that are not the Cover Photo ordered by orderNum"""
		cover_photo_id = self.cover_photo and self.cover_photo.id or None
		return self.photo_set.exclude(id=cover_photo_id).all()

	

class Checkin(models.Model):
	"""Model for Foursquare Checkins"""
	# Checkin id
	checkin_id = models.CharField(max_length=200, editable=False)
	# Datetime when checkin occurred
	created_at = models.DateTimeField(default=timezone.now)
	# Venue Name
	venue_name = models.CharField(max_length=200)
	# Checkin Location
	location = models.CharField(max_length=200, null=True, blank=True)
	# Venue URL
	venueURL = models.URLField(null=True, blank=True)
	# owner
	owner = models.ForeignKey(User, null=True)

	def __unicode__(self):
		return "%s @ %s" % (self.venue_name, self.created_at)

	def get_location(self):
		"""Return location as (lat,lng)"""
		import re
		if self.location:
			return re.sub(r'[()\s]', '', self.location).split(',')
		return None

class Photo(models.Model):
	"""Model for user-uploaded Entry photos"""
	# Entry
	entry = models.ForeignKey(Entry)
	# File
	image = ImageField(upload_to='photos')
	# Thumb
	# thumb = models.CharField(max_length=200, null=True, blank=True)
	# Caption
	caption = models.CharField(max_length=200, null=True, blank=True)
	# order num
	#orderNum = models.PositiveIntegerField(default=0)

	THUMB_SIZES = {
		'LIGHTBOX': '800x600',
		'DETAIL': '400x400',
		'PREVIEW': '100x50',
	}
	
	class Meta:
		order_with_respect_to = 'entry'
		#unique_together = ("entry", "_order")

	
	def save(self, *args, **kwargs):

		super(Photo, self).save(*args, **kwargs)

		# precompute thumbnails
		for size, sizeString in self.THUMB_SIZES.iteritems():
			get_thumbnail(self.image, sizeString)

		
	def __unicode__(self):
		return str(self.id)