from scrapbook.models import Entry, Checkin, Photo
from django.contrib import admin

class PhotoInline(admin.StackedInline):
	model = Photo
	extra = 3

class EntryAdmin(admin.ModelAdmin):
	inlines=[PhotoInline]

admin.site.register(Entry, EntryAdmin)