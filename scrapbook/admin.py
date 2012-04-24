from scrapbook.models import Book, Entry, Checkin, Photo
from django.contrib import admin

admin.site.register(Book)
admin.site.register(Checkin)
admin.site.register(Photo)

class PhotoInline(admin.StackedInline):
	model = Photo
	extra = 3

class EntryAdmin(admin.ModelAdmin):
	inlines=[PhotoInline]

admin.site.register(Entry, EntryAdmin)