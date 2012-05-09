# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from django import forms
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from datetime import datetime

import oauth2 as oauth
import json

from scrapbook.models import Checkin


from django.contrib.auth.decorators import login_required
from FoursquareScrapbook import settings

FOURSQUARE_BASE="https://foursquare.com/oauth2/authenticate"
REDIRECT_URI="/scrapbook/checkins/import_response/"
ACCESS_TOKEN_URL="https://foursquare.com/oauth2/access_token"
CHECKINS_ENDPOINT="https://api.foursquare.com/v2/users/self/checkins"
CHECKINS_LIMIT=100

def oauth_client(host):
	auth = settings.FOURSQUARE_AUTH[host]
	CLIENT_ID = auth['CLIENT_ID']
	CLIENT_SECRET = auth['CLIENT_SECRET']
	consumer = oauth.Consumer(key=CLIENT_ID, secret=CLIENT_SECRET)
	client = oauth.Client(consumer)
	return client

def foursquare_auth_url(host):
	CLIENT_ID = settings.FOURSQUARE_AUTH[host]['CLIENT_ID']
	return "%s?client_id=%s&response_type=code&redirect_uri=http://%s%s" % (FOURSQUARE_BASE, CLIENT_ID, host, REDIRECT_URI)

# there's probably a better way to do this...
def foursquare_token_url(code, host):
	auth = settings.FOURSQUARE_AUTH[host]
	CLIENT_ID = auth['CLIENT_ID']
	CLIENT_SECRET = auth['CLIENT_SECRET']
	return "%s?client_id=%s&client_secret=%s&grant_type=authorization_code&redirect_uri=http://%s%s&code=%s" % (ACCESS_TOKEN_URL, CLIENT_ID, CLIENT_SECRET, host, REDIRECT_URI, code)

@login_required
def checkins_import(request):
	token = None
	try:
		prof = request.user.get_profile()
		token = prof.foursquare_token
	except ObjectDoesNotExist:
		pass
	if token is None:
		auth_url = foursquare_auth_url(request.get_host())
		return HttpResponseRedirect(auth_url)
	else:
		return checkins_import_request(request)

@login_required	
def checkins_response(request):
	if 'code' in request.GET:
		code = request.GET['code']
		client = oauth_client(request.get_host())
		token_url = foursquare_token_url(code, request.get_host())
		print token_url
		resp, content = client.request(token_url)
		if resp.status == 200:
			data = json.loads(content)
			token = data['access_token']
			try:
				prof = request.user.get_profile()
			except ObjectDoesNotExist:
				from accounts.models import UserProfile
				prof = UserProfile(user=request.user)
			prof.foursquare_token = token
			prof.save()
			return checkins_import_request(request, client=client)
		else:
			return HttpResponse("Something went wrong getting the token...")
	else:
		return HttpResponse("No authorization code found...")
		
class ImportCheckinForm(ModelForm):
	importSelected = forms.BooleanField(label='Select')

	class Meta:
		model = Checkin
		fields = ('importSelected','venue_name','created_at','location')

@login_required		
def checkins_import_request(request, client=None):
	if not client:
		client = oauth_client(request.get_host())
	token = request.user.get_profile().foursquare_token
	checkins_url = "%s?limit=%s&oauth_token=%s" % (CHECKINS_ENDPOINT, CHECKINS_LIMIT, token)
	checkins_resp, checkins_data = client.request(checkins_url)
	view_obj = {}
	if checkins_resp.status == 200:
		checkins_data_obj = json.loads(checkins_data)
		checkins = []
		for checkin in checkins_data_obj['response']['checkins']['items']:
			try:
				existing_checkins = Checkin.objects.filter(checkin_id=checkin['id'], owner=request.user)
				if len(existing_checkins) == 0:
					print checkin
					new_checkin={ 
						'checkin_id':checkin['id'], 
						'venue_name':checkin['venue']['name'],
						'created_at':checkin['createdAt'],
						'location': "(%s,%s)" % (checkin['venue']['location']['lat'], 
								checkin['venue']['location']['lng']),
						#'venueURL': checkin['venue']['venue']['canonicalURL'],
						'owner': request.user,
					}
					Checkin.objects.create(checkin_id=new_checkin['checkin_id'],
											venue_name=new_checkin['venue_name'],
											created_at=datetime.fromtimestamp(float(new_checkin['created_at'])),
											location=new_checkin['location'],
											owner=new_checkin['owner'])
					# checkins.append(new_checkin)
			except ObjectDoesNotExist:
				pass
		return HttpResponseRedirect(reverse('checkins_list'))
	else:
		return HttpResponse("Something went wrong getting the checkins data...")

@login_required		
def checkins_save(request):
	from datetime import datetime
	selected_str = request.POST['checkin_data']
	selected = json.loads(selected_str)
	for checkin in selected:
		id = checkin['id']
		try:
			existing = Checkin.objects.get(pk=id)
		except ObjectDoesNotExist:
			venue_name = checkin['venue']
			time = datetime.fromtimestamp(float(checkin['time']))
			
			
			Checkin.objects.create(checkin_id=id, created_at=time, venue_name=venue_name, owner=request.user) 
	return HttpResponseRedirect("/scrapbook/checkins/")

@login_required	
def checkins_list(request):
	checkins = Checkin.objects.filter(owner=request.user)
	return render_to_response("scrapbook/checkins.html", { "object_list": checkins }, context_instance=RequestContext(request))