from django.conf.urls import patterns, url
from django.views.generic import ListView, DetailView
from scrapbook.models import Book, Entry, Checkin

from django.contrib.auth.decorators import login_required

from scrapbook.views import BookView, EntryView

urlpatterns = patterns('',
	
	# book list view
	url(r'^$', BookView.List.as_view()),

	# book detail view
	url(r'^(?P<pk>\d+)/$', BookView.Detail.as_view(), name='book_detail'),
	
	# book new view
	url(r'^new/$', BookView.New.as_view()),

	url(r'^(?P<pk>\d+)/edit/$', BookView.Edit.as_view()),
)

# entries
urlpatterns += patterns('',

	# entry detail (view/update)
	url(r'entries/(?P<pk>\d+)/$', EntryView.Detail.as_view(), name='entry_detail'),
	
	# entry edit
	url(r'entries/(?P<pk>\d+)/edit/$', EntryView.Edit.as_view()),
	
	# entry new
	url(r'(?P<book>\d+)/entries/new/$', EntryView.New.as_view()),
	
	# entry create/index
	url(r'(?P<book>\d+)/entries/$', EntryView.List.as_view()),
	
	# entry delete
	url(r'entries/(?P<pk>\d+)/delete/$', EntryView.Delete.as_view()),
)

# foursquare stuff
urlpatterns += patterns('scrapbook.checkins.views',
	url(r'^checkins/$','checkins_list', name='checkins_list'),
	
	# import foursquare stuff
	url(r'checkins/import/$','checkins_import'),
	
	# import checkins response
	url(r'checkins/import_response/$','checkins_response'),
	
	# import selected checkins
	url(r'checkins/import_selected/$','checkins_save'),
)