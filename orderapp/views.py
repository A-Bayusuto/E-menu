from django.shortcuts import render, redirect
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Menu, OrderTable
from datetime import datetime
import os

import json

def appetizer(request):
    # Fetch appetizers from the Menu model
    appetizers = Menu.objects.filter(category='Appetizer')

    # Create a list of dictionaries containing appetizer details
    appetizer_list = []
    for appetizer in appetizers:
        appetizer_details = {
            'code': appetizer.code,
            'item': appetizer.item,
            'price': appetizer.price,
            'summary': appetizer.summary,
            'picture_address': appetizer.picture_address.url 
        }
        appetizer_list.append(appetizer_details)

    # Pass the list of appetizers to the template context
    context = {
        'appetizers': appetizer_list,
    }

    if appetizers.exists():
        return render(request, 'appetizer.html', context)
    else:
        raise Http404('Appetizers not found')



def MenuPage(request):
    # Retrieve menu items from the database
    appetizers = Menu.objects.filter(category='Appetizer')
    main_courses = Menu.objects.filter(category='Main Course')
    desserts = Menu.objects.filter(category='Dessert')
    drinks = Menu.objects.filter(category='Drink')

    context = {
        'appetizers': appetizers,
        'main_courses': main_courses,
        'desserts': desserts,
        'drinks': drinks,
    }

    return render(request, 'menu.html', context)

def add_to_cart(request):

    if request.method == 'POST':
        menu_id = request.POST.get('menu_id')
        quantity = int(request.POST.get('quantity', 1))  # Ensure quantity is an integer
        menu_item = Menu.objects.get(pk=menu_id)

        # Retrieve the existing cart items from the cookie or initialize an empty dictionary
        cart_items = json.loads(request.COOKIES.get('cart_items', '{}'))

        # Add the new item to the cart items dictionary
        cart_items[menu_id] = quantity
        print('1', cart_items)
        # Serialize the cart items dictionary to JSON
        cart_items_json = json.dumps(cart_items)
        print('2', cart_items_json)

        # Set the updated cart items as a cookie in the response
        response = HttpResponseRedirect(reverse('cart'))
        response.set_cookie('cart_items', cart_items_json)

        return response
    else:
        # Return a simple response if the request method is not POST
        return HttpResponse("Method not allowed", status=405)
    
  # TODO need to check largest order ID when finishing cart 




def CartPage(request):
    # Retrieve the cart_items from the cookie or initialize an empty dictionary
    cart_items_json = request.COOKIES.get('cart_items', '{}')
    cart_items = json.loads(cart_items_json)

    # Pass the cart_items to the template context
    context = {
        'cart_items': cart_items
    }

    return render(request, 'cart.html', context)


def clear_cart(request):
    response = redirect('cart')
    response.delete_cookie('cart_items')
    return response