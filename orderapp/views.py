from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

def MenuPage(request):
  template = loader.get_template('menu.html')
  return HttpResponse(template.render())

def CartPage(request):
  template = loader.get_template('cart.html')
  return HttpResponse(template.render())