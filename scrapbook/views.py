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

# "Ready Only Field" adapted from http://lazypython.blogspot.com/2008/12/building-read-only-field-in-django.html
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.forms.util import flatatt

class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs):
        final_attrs = self.build_attrs(attrs, name=name)
        if hasattr(self, 'initial'):
            value = self.initial
            return mark_safe("<span %s>%s</span>" % (flatatt(final_attrs), escape(value) or ''))

    def _has_changed(self, initial, data):
        return False

class ReadOnlyField(forms.Field):
    widget = ReadOnlyWidget
    def __init__(self, widget=None, label=None, initial=None, help_text=None):
        super(type(self), self).__init__(label=label, initial=initial, 
            help_text=help_text, widget=widget)
        self.widget.initial = initial

    def clean(self, value):
        return self.widget.initial
# end readonly field

def validate_owner(request, book):
	if request.user != book.owner:
		return "Access Denied: this book belongs to %s" % book.owner
	return None

class BookView:
	class BookForm(ModelForm):
		class Meta:
			model = Book
			fields = ('title',)

	class EntryForm(ModelForm):
		class Meta:
			model = Entry
			fields = ('title',)#, 'orderNum')
	
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
			
			entries = [{ "object": entry } for entry in book.entry_set.all()]#order_by("orderNum")]
			snippet_length = 1200
			for entry in entries:
				# Cover
				if entry["object"].cover_photo:
					entry["thumbnail"] = {
						'image': entry["object"].cover_photo.image,
						'size': Photo.THUMB_SIZES['DETAIL']
					}
				
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

				# Date
				if entry["object"].date:
					date = entry["object"].date
					entry["date"] = json.dumps({
						'year': date.year,
						'month': date.month,
						'day': date.day
					})

				# show actions?
				actions = request.user == book.owner
			
			return render_to_response("scrapbook/detail.html", { "book": book, "entries": entries, "actions": actions }, context_instance=RequestContext(request))

		@method_decorator(login_required)
		def post(self, request, pk):
			"""POST /scrapbook/:id/ = update"""
			book = get_object_or_404(Book, pk=pk)

			form = BookView.BookForm(request.POST, instance=book)
			if form.is_valid():
				form.save()

				EntryInlineFormset = inlineformset_factory(Book, Entry, form=BookView.EntryForm, can_order=True)
				entries = EntryInlineFormset(request.POST, instance=book)
				
				order = []
				for entryform in entries.ordered_forms:
					if entryform.is_valid():
						entry = entryform.save(commit=False)
						order.append(entry.pk)
						entry.save()
				
				book.set_entry_order(order)

				return HttpResponseRedirect(reverse("book_detail", kwargs={ "pk": pk }))
			else:
				return render_to_response("scrapbook/edit.html", { "form": form, "error": form.errors }, context_instance=RequestContext(request))


	class Edit(View):
		@method_decorator(login_required)
		def get(self, request, pk):
			"""GET /scrapbook/:id/edit/ = edit"""
			book = get_object_or_404(Book, pk=pk)
			
			form = BookView.BookForm(instance=book)
			
			EntryInlineFormset = inlineformset_factory(Book, Entry, form=BookView.EntryForm, extra=0, can_order=True)
			entries = EntryInlineFormset(instance=book)

			return render_to_response("scrapbook/edit.html", { "form": form, "entries": entries }, context_instance=RequestContext(request))

class EntryView:
	class EntryForm(ModelForm):		
		class Meta:
			model = Entry
			fields = ('title','date','description','checkin')
		
		def __init__(self, *args, **kwargs):	
			request = kwargs.pop('request', None)
			super(EntryView.EntryForm, self).__init__(*args, **kwargs)
			if request:
				self.fields['checkin'].queryset = Checkin.objects.filter(owner=request.user).order_by("-created_at")
			
	class PhotoForm(ModelForm):
		class Meta:
			model = Photo
			fields = ('image','caption')#, 'orderNum')
											
	class List(View):
		
		def get(self, request, book):
			"""GET /scrapbook/:id/entries => index"""
			return HttpResponseRedirect(reverse('book_detail', kwargs={ 'pk': book }))
		
		@method_decorator(login_required)	
		def post(self, request, book):
			book = get_object_or_404(Book,pk=book)

			access_error = validate_owner(request, book)
			if access_error:
				# TODO: propagate error
				return self.get(request, book.id)
			
			form = EntryView.EntryForm(request.POST, request=request)
			
			PhotoInlineFormset = inlineformset_factory(Entry, Photo)#, can_order=True)
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
				for photo_form in photos:
					if photo_form.is_valid():
						photo = photo_form.save(commit=False)
						if photo.image:
							photo.save()
						else:
							print "Photo with no image! horror!"
					else:
						pass

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
			PhotoInlineFormset = inlineformset_factory(Entry, Photo, form=EntryView.PhotoForm, extra=extra, can_order=True)
			photos = PhotoInlineFormset()#initial=[{'orderNum':i+1} for i in range(extra)])
			return render_to_response("scrapbook/entry/new.html", { 'form': form, "photos": photos }, context_instance=RequestContext(request))
	
	class Detail(View):
		
		def gen_photos(self, entry):
			cover = None
			if entry.cover_photo:
				cover = {	
					"image": entry.cover_photo,
					"size": Photo.THUMB_SIZES['DETAIL'],
					"lightbox_size": Photo.THUMB_SIZES['LIGHTBOX']
				}
			
			photos = [{ 
				"image": photo, 
				"size": Photo.THUMB_SIZES['DETAIL'], 
				"lightbox_size": Photo.THUMB_SIZES['LIGHTBOX'] 
			} for photo in entry.alt_photos()]
			return cover, photos

		def get_helper(self, request, entry, error=None):
			cover, photos = self.gen_photos(entry)

			actions = request.user == entry.book.owner
								
			return render_to_response("scrapbook/entry/detail.html", { "entry": entry, "cover": cover, "photos": photos, "actions": actions, "error": error }, context_instance=RequestContext(request))

		def get(self, request, pk):
			entry = get_object_or_404(Entry, pk=pk)
			return self.get_helper(request, entry)
						
		@method_decorator(login_required)
		def post(self, request, pk):
			entry = get_object_or_404(Entry, pk=pk)

			access_error = validate_owner(request, entry.book)
			if access_error:
				return self.get_helper(request, entry, error=access_error)

			form = EntryView.EntryForm(request.POST, instance=entry, request=request)

			PhotoInlineFormset = inlineformset_factory(Entry, Photo, form=EntryView.PhotoForm, can_order=True)
			photo_forms = PhotoInlineFormset(request.POST, request.FILES, instance=entry)
			
			context = { "entry": entry, "form": form, "photos": photo_forms }

			
			if form.is_valid():
				updated_entry = form.save(commit=False)
				checkin=None
				if request.POST['checkin']:
					updated_entry.checkin = Checkin.objects.get(pk=request.POST['checkin'])
					
				photo_order = [0 for photo_form in photo_forms]
				for photo_form in photo_forms:
					if photo_form.is_valid():
						photo = photo_form.save(commit=False)
						if photo.image:
							#print "Saving: %s" % photo.image
							if 'ORDER' in photo_form.cleaned_data:
								formOrder = photo_form.cleaned_data['ORDER']
								if formOrder is not None:
									# TODO: probably should handle this better
									order = formOrder - 1
									#print "Order: %s" % order

									photo_order[order] = photo.pk
							photo.save()
						else:
							print "Photo with no image! horror!"
					else:
						pass

				entry.set_photo_order(photo_order)

				if 'cover_image' in request.POST:
					entry.cover_photo = Photo.objects.get(pk=request.POST['cover_image'])
				updated_entry.save()

				if 'error' not in context:	
					cover, photos = self.gen_photos(entry)
					context['cover'] = cover
					context['photos'] = photos
			else:
				context['error'] = form.errors
			
			if 'error' not in context:	
				return HttpResponseRedirect(reverse('entry_detail', kwargs={ 'pk': entry.id }))
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

			access_error = validate_owner(request, book)
			if access_error:
				return render_to_response('scrapbook/entry/delete.html', { 'entry': entry, 'error': access_error }, context_instance=RequestContext(request))
			else:
				entry.delete()
				return HttpResponseRedirect(reverse('book_detail', kwargs={ 'pk': book.id }))
	
	class Edit(View):
		@method_decorator(login_required)
		def get(self, request, pk):
			entry = get_object_or_404(Entry, pk=pk)

			form = EntryView.EntryForm(instance=entry, request=request)
			
			extra = 3
			maxOrderNum = len(entry.photo_set.all())
			PhotoInlineFormset = inlineformset_factory(Entry, Photo, form=EntryView.PhotoForm, extra=extra, can_order=True)
			photos = PhotoInlineFormset(instance=entry)
			
			preview_size = Photo.THUMB_SIZES['PREVIEW']
			
			return render_to_response("scrapbook/entry/edit.html", { "form": form, "photos": photos, "preview_size": preview_size }, context_instance=RequestContext(request))
		
		
