"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from scrapbook.models import Entry, Photo, Book, Checkin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

class EntryModelTest(TestCase):
	def setUp(self):
		self.owner = User.objects.create()
		self.book = Book.objects.create(title="Test Book", owner=self.owner)

	def test_first_entry_should_have_order_0(self):
		entry = Entry(book=self.book)
		entry.save()
		self.assertEqual(entry._order, 0)

	def test_second_entry_should_have_order_1(self):
		entry1 = Entry(book=self.book)
		entry2 = Entry(book=self.book)
		entry1.save()
		entry2.save()
		self.assertEqual(entry2._order, 1)

	def test_10_entrys_should_have_order_0_9(self):
		entries = [Entry(book=self.book) for i in range(10)]
		for i in range(len(entries)):
			entry = entries[i]
			entry.save()
			self.assertEqual(entry._order, i)

	def test_promote_only_photo_to_cover(self):
		entry = Entry(book=self.book)
		entry.save()

		self.assertEqual(entry.cover_photo, None)

		photo = Photo(entry=entry)
		photo.save()

		self.assertEqual(entry.cover_photo, photo)

	def test_promote_first_photo_to_cover(self):
		entry = Entry(book=self.book)
		entry.save()

		photo1 = Photo(entry=entry)
		photo2 = Photo(entry=entry)

		photo1.save()
		photo2.save()

		self.assertEqual(entry.cover_photo, photo1)

	def test_promote_first_photo_in_save_order(self):
		entry = Entry(book=self.book)
		entry.save()

		photo1 = Photo(entry=entry)
		photo2 = Photo(entry=entry)

		photo2.save()
		photo1.save()

		self.assertEqual(entry.cover_photo, photo2)


class PhotoModelTest(TestCase):
	def setUp(self):
		self.owner = User.objects.create()
		self.book = Book.objects.create(title="Test Book", owner=self.owner)
		self.entry = Entry.objects.create(title="Test Entry", description="Test Entry Desc", book=self.book)

	def test_first_Photo_should_have_order_0(self):
		photo = Photo(entry=self.entry)
		photo.save()
		self.assertEqual(photo._order, 0)

	def test_second_Photo_should_have_order_1(self):
		photo1 = Photo(entry=self.entry)
		photo2 = Photo(entry=self.entry)
		photo1.save()
		photo2.save()
		self.assertEqual(photo2._order, 1)

	def test_10_photos_should_have_order_0_9(self):
		photos = [Photo(entry=self.entry) for i in range(10)]
		for i in range(len(photos)):
			photo = photos[i]
			photo.save()
			self.assertEqual(photo._order, i)
