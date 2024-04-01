from django.shortcuts import render, redirect
from django.template import loader
from django.http import Http404, HttpResponse
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
        quantity = request.POST.get('quantity', 1)
        current_date = datetime.now().date()
        menu_item = Menu.objects.get(pk=menu_id)

        # Assuming you have the necessary information for OrderTable
        # You may need to adjust this based on your actual models and logic
        order_item = OrderTable.objects.create(
            table_id=1,  # Example table_id, replace with actual value
            supplier=menu_item.supplier,
            menu=menu_item,
            date=current_date,  # Replace with actual date object
            order_id=0,  # Replace with actual order_id
            qty=quantity,
            total=menu_item.price * int(quantity),
            order_status='Pending'  # Example order_status, replace with actual value
        )

        # Serialize the OrderTable object to JSON
        order_item_data = {
            'table_id': order_item.table_id,
            'supplier_id': order_item.supplier_id,
            'menu_id': order_item.menu_id,
            'date_id': order_item.date_id,
            'order_id': order_item.order_id,
            'qty': order_item.qty,
            'total': str(order_item.total),
            'order_status': order_item.order_status,
        }

        # Retrieve the existing cart items from the cookie
        cart_items = request.COOKIES.get('cart_items', '[]')

        # Convert the JSON string to a Python list
        cart_items = json.loads(cart_items)

        # Add the new item to the list
        cart_items.append(order_item_data)

        # Convert the list back to a JSON string
        cart_items_json = json.dumps(cart_items)

        # Set the updated cookie with the serialized OrderTable data
        response = HttpResponse("Added to Cart")
        response.set_cookie('cart_items', cart_items_json)

        return response
    
  # TODO need to check largest order ID when finishing cart 

    return redirect('cart')  # Assuming 'cart' is the name of your cart view

def CartPage(request):
  template = loader.get_template('cart.html')
  return HttpResponse(template.render())