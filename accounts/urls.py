from django.conf.urls import patterns, include, url

urlpatterns = patterns('django.contrib.auth.views',
    
    # login
	url(r'^login/$','login', name="user_login"),
)

urlpatterns += patterns('accounts.views',
	# register
	url(r'^register/$', 'user_register', name='user_register'),
	
	# logout
	url(r'^logout/$', 'user_logout'),
)