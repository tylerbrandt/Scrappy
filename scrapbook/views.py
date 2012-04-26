# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
import oauth2 as oauth
import json

CLIENT_ID="Q3XLEGRK3PECAUHJCLIKMJU2L3ASOURJUUVUPOKNHMMGULB5"
CLIENT_SECRET="CPV4YVQFSI1KQW5ADEOV5JOPOJLXTIKRPG2F1XRTZUEBKQYF"
FOURSQUARE_BASE="https://foursquare.com/oauth2/authenticate"
REDIRECT_URI="http://localhost:8000/scrapbook/checkins/import_response/"
ACCESS_TOKEN_URL="https://foursquare.com/oauth2/access_token"
CHECKINS_ENDPOINT="https://api.foursquare.com/v2/users/self/checkins"

def oauth_client():
	consumer = oauth.Consumer(key=CLIENT_ID, secret=CLIENT_SECRET)
	client = oauth.Client(consumer)
	return client

def foursquare_auth_url():
	return "%s?client_id=%s&response_type=code&redirect_uri=%s" % (FOURSQUARE_BASE, CLIENT_ID, REDIRECT_URI)

# there's probably a better way to do this...
def foursquare_token_url(code):
	return "%s?client_id=%s&client_secret=%s&grant_type=authorization_code&redirect_uri=%s&code=%s" % (ACCESS_TOKEN_URL, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, code)

def checkins_import(request):
	return HttpResponseRedirect(foursquare_auth_url())
	
def checkins_response(request):
	if 'code' in request.GET:
		code = request.GET['code']
		print "###ACCESS CODE###" + code
		client = oauth_client()
		resp, content = client.request(foursquare_token_url(code))
		if resp.status == 200:
			data = json.loads(content)
			token = data['access_token']
			view_obj = { "token": token, "token_response": data, "code": code, "request": request }
			# test the token
			# todo: save it somewhere...
			checkins_url = "%s?oauth_token=%s" % (CHECKINS_ENDPOINT, token)
			print checkins_url
			checkins_resp, checkins_data = client.request(checkins_url)
			if resp.status == 200:
				checkins_data_obj = json.loads(checkins_data)
				checkins = []
				for checkin in checkins_data_obj['response']['checkins']['items']:
					print checkin['id']
					try:
						Checkin.objects.get(pk=checkin['id'])
						print "found it!"
						checkin['imported'] = True
					except:
						pass
					checkins.append(checkin)
				view_obj["checkins"] = checkins
				view_obj["raw"] = checkins_data
				return render_to_response("scrapbook/checkins_import.html", view_obj, context_instance=RequestContext(request))
			else:
				return HttpResponse("Something went wrong getting the checkins data...")
		else:
			return HttpResponse("Something went wrong getting the token...")
	else:
		return HttpResponse("No authorization code found...")
		
def checkins_save(request):
	from scrapbook.models import Checkin
	from datetime import datetime
	selected_str = request.POST['checkin_data']
	selected = json.loads(selected_str)
	for checkin in selected:
		id = checkin['id']
		try:
			existing = Checkin.objects.get(pk=id)
		except:
			venue_name = checkin['venue']
			time = datetime.fromtimestamp(float(checkin['time']))
			Checkin.objects.create(checkin_id=id, created_at=time, venue_name=venue_name) 
	return HttpResponseRedirect("/scrapbook/checkins/")
