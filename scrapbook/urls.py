from django.conf.urls import patterns, url
from django.views.generic import ListView, DetailView
from scrapbook.models import Book, Entry, Checkin

urlpatterns = patterns('',
	# list view
	url(r'^$',
		ListView.as_view(
			queryset=Book.objects.all,
			template_name='scrapbook/index.html')
	),

	# detail view
	url(r'^(?P<pk>\d+)/$',
		DetailView.as_view(
			model=Book,
			template_name='scrapbook/detail.html')
	),

	# entry detail view
	url(r'entries/(?P<pk>\d+)/$',
		DetailView.as_view(
			model=Entry,
			template_name='scrapbook/entry_detail.html')
	),
	
	url(r'^checkins/$',
		ListView.as_view(
			queryset=Checkin.objects.all,
			template_name='scrapbook/checkins.html')
	),
	
	# import foursquare stuff
	url(r'checkins/import/$','scrapbook.views.checkins_import'),
	
	# import response
	url(r'checkins/import_response/$','scrapbook.views.checkins_response'),
	
	# import selected checkins
	url(r'checkins/import_selected/$','scrapbook.views.checkins_save'),
)