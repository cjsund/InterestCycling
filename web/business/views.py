# Create your views here.
from django.shortcuts import render_to_response

def index(request):
	html = 'index.html'
	return render_to_response(html, {'hello': "hello word!"})