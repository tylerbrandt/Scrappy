"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from scrapbook.models import Entry, Photo, Book
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class EntryModelTest(TestCase):
	def setUp(self):
		self.owner = User.objects.create()
		self.book = Book.objects.create(title="Test Book", owner=self.owner)

	def test_first_entry_should_have_orderNum_1(self):
		entry = Entry(book=self.book)
		entry.save()
		self.assertEqual(entry.orderNum, 1)

	def test_second_entry_should_have_orderNum_2(self):
		entry1 = Entry(book=self.book)
		entry2 = Entry(book=self.book)
		entry1.save()
		entry2.save()
		self.assertEqual(entry2.orderNum, 2)

	def test_10_entrys_should_have_orderNum_1_10(self):
		entries = [Entry(book=self.book) for i in range(10)]
		for i in range(len(entries)):
			entry = entries[i]
			entry.save()
			self.assertEqual(entry.orderNum, i+1)

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

	def test_first_Photo_should_have_orderNum_1(self):
		photo = Photo(entry=self.entry)
		photo.save()
		self.assertEqual(photo.orderNum, 1)

	def test_second_Photo_should_have_orderNum_2(self):
		photo1 = Photo(entry=self.entry)
		photo2 = Photo(entry=self.entry)
		photo1.save()
		photo2.save()
		self.assertEqual(photo2.orderNum, 2)

	def test_10_photos_should_have_orderNum_1_10(self):
		photos = [Photo(entry=self.entry) for i in range(10)]
		for i in range(len(photos)):
			photo = photos[i]
			photo.save()
			self.assertEqual(photo.orderNum, i+1)
