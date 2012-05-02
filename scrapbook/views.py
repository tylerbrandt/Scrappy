# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User

from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory, BaseModelFormSet
# from django.forms.formsets import BaseFormSet
from scrapbook.models import Book, Entry, Checkin, Photo

from PIL import Image
import os.path
from FoursquareScrapbook import settings

import json

def root(request):
	return HttpResponseRedirect('/scrapbook/')
	
from django.views.generic import View

class BookView:
	class BookForm(ModelForm):
		class Meta:
			model = Book
			fields = ('title',)

	class EntryForm(ModelForm):
		class Meta:
			model = Entry
			fields = ('title', 'orderNum')
	
	class List(View):
		def get(self, request):
			"""GET /scrapbook/ = index"""
			books = []
			if request.user.is_authenticated():
				books = Book.objects.filter(owner=request.user)
			return render_to_response("scrapbook/index.html", { "object_list": books }, context_instance=RequestContext(request))
			
		@method_decorator(login_required)
		def post(self, request):
			"""POST /scrapbook/ = create"""
			form = BookView.BookForm(request.POST)
			if form.is_valid():
				new_book = form.save(commit=False)
				new_book.owner = request.user
				new_book.save()
				return HttpResponseRedirect(reverse('book_detail', kwargs={ 'pk': new_book.id }))
			else:
				return render_to_response("scrapbook/new.html", { "form": form, "error": form.errors }, context_instance=RequestContext(request))
	
	class New(View):
		@method_decorator(login_required)
		def get(self, request):
			"""GET /scrapbook/new/ = new"""
			form = BookView.BookForm()
			return render_to_response("scrapbook/new.html", { "form": form }, context_instance=RequestContext(request))
		
	class Detail(View):
		def get(self, request, pk):
			"""GET /scrapbook/:id/ = view"""
			book = get_object_or_404(Book, pk=pk)
			
			entries = [{ "object": entry } for entry in book.entry_set.order_by("orderNum")]
			snippet_length = 1200
			for entry in entries:
				# Cover
				if entry["object"].cover_photo:
					entry["thumbnail"] = entry["object"].cover_photo.get_thumbnail((200,200))
				
				# Description
				if len(entry["object"].description) > snippet_length:
					entry["description"] = entry["object"].description[0:snippet_length] + "..."
				else:
					entry["description"] = entry["object"].description

				# Location
				if entry["object"].checkin:
					book.geo = True
					checkin = entry["object"].checkin
					(lat,lng) = checkin.get_location()
					entry["location"] = json.dumps({
						"lat": lat,
						"lng": lng,
						})
			
			return render_to_response("scrapbook/detail.html", { "book": book, "entries": entries }, context_instance=RequestContext(request))

		@method_decorator(login_required)
		def post(self, request, pk):
			"""POST /scrapbook/:id/ = update"""
			book = get_object_or_404(Book, pk=pk)

			form = BookView.BookForm(request.POST, instance=book)
			if form.is_valid():
				form.save()

				EntryInlineFormset = inlineformset_factory(Book, Entry, form=BookView.EntryForm)
				entries = EntryInlineFormset(instance=book)
				if entries.is_valid():
					entries.save()

				return HttpResponseRedirect(reverse("book_detail", kwargs={ "pk": pk }))
			else:
				return render_to_response("scrapbook/edit.html", { "form": form, "error": form.errors }, context_instance=RequestContext(request))


	class Edit(View):
		@method_decorator(login_required)
		def get(self, request, pk):
			"""GET /scrapbook/:id/edit/ = edit"""
			book = get_object_or_404(Book, pk=pk)
			
			form = BookView.BookForm(instance=book)
			
			EntryInlineFormset = inlineformset_factory(Book, Entry, form=BookView.EntryForm, extra=0)
			entries = EntryInlineFormset(instance=book)

			return render_to_response("scrapbook/edit.html", { "form": form, "entries": entries }, context_instance=RequestContext(request))




class EntryView:
	class EntryForm(ModelForm):		
		class Meta:
			model = Entry
			fields = ('title','description','checkin')
		
		def __init__(self, *args, **kwargs):	
			request = kwargs.pop('request', None)
			super(EntryView.EntryForm, self).__init__(*args, **kwargs)
			if request:
				self.fields['checkin'].queryset = Checkin.objects.filter(owner=request.user).order_by("-created_at")
			
	class PhotoForm(ModelForm):
		class Meta:
			model = Photo
			fields = ('image','caption', 'orderNum')
											
	class List(View):
		def get(self, request, book):
			"""GET /scrapbook/:id/entries => index"""
			return HttpResponseRedirect(reverse('book_detail', kwargs={ 'pk': book }))
		
		@method_decorator(login_required)	
		def post(self, request, book):
			book = get_object_or_404(Book,pk=book)
			
			form = EntryView.EntryForm(request.POST, request=request)
			PhotoInlineFormset = inlineformset_factory(Entry, Photo)
			photos = PhotoInlineFormset(request.POST, request.FILES)
			
			if form.is_valid():
				print "Form is valid"
				entry = form.save(commit=False)
				entry.book = book
				checkin=None
				if request.POST['checkin']:
					entry.checkin = Checkin.objects.get(pk=request.POST['checkin'])
				entry.save()
				
				photos = PhotoInlineFormset(request.POST, request.FILES, instance=entry)
				realErrors = False
				for photo_form in photos:
					if photo_form.is_valid():
						photo_form.save()
					else:
						# TODO: try to determine if it was left blank on purpose
						pass

				if realErrors:
					return render_to_response("scrapbook/entry/edit.html", { "form": form, "photos": photos, "error": photos.errors }, context_instance=RequestContext(request))
				else:
					return HttpResponseRedirect(reverse('entry_detail', kwargs={ 'pk': entry.id }))
			else:
				print "Error: %s" % form.errors
				return render_to_response("scrapbook/entry/new.html", { "form": form, "photos": photos, "error": form.errors }, context_instance=RequestContext(request))
			
	class New(View):
		@method_decorator(login_required)
		def get(self, request, book):
			"""GET /scrapbook/:id/entries/new => new"""
			form = EntryView.EntryForm(request=request)
			extra = 3
			PhotoInlineFormset = inlineformset_factory(Entry, Photo, form=EntryView.PhotoForm, extra=extra)
			photos = PhotoInlineFormset(initial=[{'orderNum':i+1} for i in range(extra)])
			return render_to_response("scrapbook/entry/new.html", { 'form': form, "photos": photos }, context_instance=RequestContext(request))
	
	class Detail(View):
		
		def get(self, request, pk):
			entry = get_object_or_404(Entry, pk=pk)
			
			cover = None
			if entry.cover_photo:
				cover = {	
					"image": entry.cover_photo,
					"thumbnail": entry.cover_photo.get_thumbnail((400,400)),
					"lightbox": entry.cover_photo.get_thumbnail((800,600)),
				}
			
			photos = [{ "image": photo } for photo in entry.alt_photos()]
			for photo in photos:
				photo["thumbnail"] = photo['image'].get_thumbnail((400,400))
				photo["lightbox"] = photo['image'].get_thumbnail((800,600))
								
			return render_to_response("scrapbook/entry/detail.html", { "entry": entry, "cover": cover, "photos": photos }, context_instance=RequestContext(request))
			
		@method_decorator(login_required)
		def post(self, request, pk):
			entry = get_object_or_404(Entry, pk=pk)
			form = EntryView.EntryForm(request.POST, instance=entry, request=request)

			PhotoInlineFormset = inlineformset_factory(Entry, Photo)
			photo_forms = PhotoInlineFormset(request.POST, request.FILES, instance=entry)
			
			context = { "entry": entry, "form": form, "photos": photo_forms }

			
			if form.is_valid():
				updated_entry = form.save(commit=False)
				checkin=None
				if request.POST['checkin']:
					updated_entry.checkin = Checkin.objects.get(pk=request.POST['checkin'])
					
				if 'cover_image' in request.POST:
					entry.cover_photo = Photo.objects.get(pk=request.POST['cover_image'])
				updated_entry.save()
				
				for photo_form in photo_forms:
					if photo_form.is_valid():
						photo_form.save()
					else:
						pass

				if 'error' not in context:	
					cover = None
					if entry.cover_photo:
						cover = {	
							"image": entry.cover_photo,
							"thumbnail": entry.cover_photo.get_thumbnail((400,400)),
							"lightbox": entry.cover_photo.get_thumbnail((800,600)),
						}
					context['cover'] = cover
					
					photos = [{ "image": photo } for photo in entry.alt_photos()]
					for photo in photos:
						photo["thumbnail"] = photo['image'].get_thumbnail((400,400))
						photo["lightbox"] = photo['image'].get_thumbnail((800,600))
					context['photos'] = photos
			else:
				context['error'] = form.errors
			
			if 'error' not in context:	
				return render_to_response("scrapbook/entry/detail.html", context, context_instance=RequestContext(request))
			else:
				return render_to_response("scrapbook/entry/edit.html", context, context_instance=RequestContext(request)) 
			
	class Delete(View):
		"""Since django doesn't support DELETE we are going to fake it with a URL"""
		@method_decorator(login_required)
		def get(self, request, pk):
			entry = get_object_or_404(Entry, pk=pk)
			return render_to_response("scrapbook/entry/delete.html", { "entry": entry }, context_instance=RequestContext(request))
			
		@method_decorator(login_required)
		def post(self, request, pk):
			entry = get_object_or_404(Entry, pk=pk)
			book = entry.book
			entry.delete()
			return HttpResponseRedirect(reverse('book_detail', kwargs={ 'pk': book.id }))
	
	class Edit(View):
		@method_decorator(login_required)
		def get(self, request, pk):
			entry = get_object_or_404(Entry, pk=pk)
			form = EntryView.EntryForm(instance=entry, request=request)
			
			extra = 3
			maxOrderNum = len(entry.photo_set.all())
			PhotoInlineFormset = inlineformset_factory(Entry, Photo, form=EntryView.PhotoForm, extra=extra)
			photos = PhotoInlineFormset(instance=entry, initial=[{'orderNum':maxOrderNum+i+1} for i in range(extra)])
			
			thumbs = {}
			for photo in entry.photo_set.all():
				thumbs[photo.id] = photo.get_thumbnail((50,50))
			
			return render_to_response("scrapbook/entry/edit.html", { "form": form, "photos": photos, "thumbs": thumbs }, context_instance=RequestContext(request))
		
		
