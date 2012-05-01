# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.forms import ModelForm

class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ('username','password','email')
			
def user_register(request):
	if request.method == "GET":
		form = UserForm()
		return render_to_response("scrapbook/user_register.html", { "form": form }, context_instance=RequestContext(request))
	elif request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		email = request.POST['email']
		user = User.objects.create_user(username, email, password)
		user.save()
		return HttpResponseRedirect('/scrapbook/')
		
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/scrapbook/')