from django.shortcuts import render
from django.views import View
from .models import Menu

class MenuPageView(View):
    template_name = 'orderapp/menu_page.html'