from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'FoursquareScrapbook.views.home', name='home'),
    # url(r'^FoursquareScrapbook/', include('FoursquareScrapbook.foo.urls')),

    # static files serve
    url(r'^media/(?P<path>.*)', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # scrapbook urls
    url(r'^$', 'scrapbook.views.root'),
    
    url(r'^scrapbook/', include('scrapbook.urls')),
    
    # user management
    
    url(r'^accounts/', include('accounts.urls')),
)
