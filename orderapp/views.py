from django.shortcuts import render, redirect
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Menu, OrderTable, OrderDate, Supplier
from datetime import date, datetime, timedelta
from django.utils.timezone import now
from django.db.models import Sum
from django.db import connection
from calendar import monthrange
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
    quantities = range(1, 21) 

    context = {
        'appetizers': appetizers,
        'main_courses': main_courses,
        'desserts': desserts,
        'drinks': drinks,
        'quantities': quantities,
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
        # print('1', cart_items)
        # Serialize the cart items dictionary to JSON
        cart_items_json = json.dumps(cart_items)
        # print('2', cart_items_json)

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

    items = []
    grand_total = 0
    for key, value in cart_items.items():
        menu_item = Menu.objects.get(code=key)
        qty = value

        # Calculate total price for the item
        total_price = float(menu_item.price) * qty
        grand_total += total_price
        # Append item details to the items list
        items.append({
            'name': menu_item.item,
            'price': menu_item.price,
            'category': menu_item.category,
            'total_price': total_price,
            'qty' : qty,
            'grand_total': grand_total,
        })

    # Pass the items list to the template context
    context = {
        'items': items,
        'grand_total': grand_total,
    }


    return render(request, 'cart.html', context)


def clear_cart(request):
    response = redirect('cart')
    response.delete_cookie('cart_items')
    return response

def checkout(request):
    if request.method == 'POST':
        table_number = request.POST.get('table_number')

        cart_items_json = request.COOKIES.get('cart_items', '{}')
        cart_items = json.loads(cart_items_json)

        # Fetch the first supplier from the database
        supplier = Supplier.objects.first()

        # Get current date and time
        current_datetime = datetime.now()

        # Initialize variables
        orders = []
        grand_total = 0

        # Iterate over cart items
        for key, value in cart_items.items():
            menu_item = Menu.objects.get(code=key)
            qty = value

            # Calculate total price for the item
            total_price = float(menu_item.price) * qty
            grand_total += total_price

            # Create OrderDate object for the current date and time
            order_date, _ = OrderDate.objects.get_or_create(
                order_date=current_datetime.date(),
                defaults={'order_time': current_datetime.time(),
                          'order_week': current_datetime.isocalendar()[1],
                          'order_month': current_datetime.month,
                          'order_year': current_datetime.year}
            )

            # Create OrderTable object for the item
            order_id = OrderTable.objects.filter(date__order_date=current_datetime.date()).count() + 1
            order = OrderTable(
                table_id=table_number,
                supplier=supplier,
                menu=menu_item,
                date=order_date,
                order_id=order_id,
                qty=qty,
                total=total_price,
                order_status='Pending'
            )
            orders.append(order)

        # Bulk create OrderTable objects
        OrderTable.objects.bulk_create(orders)

        # Clear cart items after checkout
        response = redirect('checkout_success')  # Redirect to checkout_success view
        response.delete_cookie('cart_items')
        return response

    # Handle GET request or other cases
    return redirect('cart')  # Redirect back to cart page

def checkout_success(request):
    start_date = date.today() - timedelta(days=7)
    current_date = date.today()
    orders = OrderTable.objects.filter(date__order_date__range=[start_date, current_date])    
    context = {
        'orders': orders
    }
    return render(request, 'checkout_success.html', context)


def get_kpi_per_weeks():
    # Get KPIs for the last 52 weeks
    kpi_weeks = []
    current_date = now()
    for i in range(1, 53):
        start_date = current_date - timedelta(days=current_date.weekday() + (i - 1) * 7)
        end_date = start_date + timedelta(days=6)
        weekly_sales = OrderTable.objects.filter(
            date__order_date__range=[start_date, end_date]
        ).aggregate(total_sales=Sum('total'))['total_sales'] or 0
        kpi_weeks.append({
            'week': i,
            'start_date': start_date,
            'end_date': end_date,
            'total_sales': weekly_sales
        })
    return kpi_weeks

def get_kpi_per_months():
    # Get KPIs for the last 24 months
    kpi_months = []
    current_date = now()
    for i in range(0, 24):
        target_date = current_date - timedelta(days=i*30)
        year = target_date.year
        month = target_date.month
        _, last_day = monthrange(year, month)
        start_date = target_date.replace(day=1)
        end_date = target_date.replace(day=last_day)
        monthly_sales = OrderTable.objects.filter(
            date__order_date__range=[start_date, end_date]
        ).aggregate(total_sales=Sum('total'))['total_sales'] or 0
        kpi_months.append({
            'month': month,
            'year': year,
            'total_sales': monthly_sales
        })
    return kpi_months


def get_kpi_per_years():
    # Get KPIs for all years
    kpi_years = []
    years = OrderDate.objects.values_list('order_year', flat=True).distinct()
    for year in years:
        yearly_sales = OrderTable.objects.filter(
            date__order_date__year=year
        ).aggregate(total_sales=Sum('total'))['total_sales'] or 0
        kpi_years.append({
            'year': year,
            'total_sales': yearly_sales
        })
    return kpi_years

def sales_analytics(request):
    monthly_kpi = get_kpi_per_months()
    weekly_kpi = get_kpi_per_weeks()
    yearly_kpi = get_kpi_per_years()

    context = {
        'monthly_kpi': monthly_kpi,
        'weekly_kpi': weekly_kpi,
        'yearly_kpi': yearly_kpi,
    }
    return render(request, 'analytics_sales.html', context)


# def get_menu_performance_per_week():
#     # Get performance of each menu item for the current week based on quantity ordered
#     start_date = now() - timedelta(days=now().weekday())
#     end_date = start_date + timedelta(days=6)
#     menu_performance = OrderTable.objects.filter(
#         date__order_date__range=[start_date, end_date]
#     ).values('menu__item').annotate(total_quantity=Sum('qty')).order_by('-total_quantity')
#     return menu_performance

# def get_menu_performance_per_month():
#     # Get performance of each menu item for the current month based on quantity ordered
#     current_date = now()
#     start_date = current_date.replace(day=1)
#     end_date = start_date.replace(day=1) + timedelta(days=32)
#     menu_performance = OrderTable.objects.filter(
#         date__order_date__range=[start_date, end_date]
#     ).values('menu__item').annotate(total_quantity=Sum('qty')).order_by('-total_quantity')
#     return menu_performance

# def get_menu_performance_per_year():
#     # Get performance of each menu item for the current year based on quantity ordered
#     current_year = now().year
#     menu_performance = OrderTable.objects.filter(
#         date__order_date__year=current_year
#     ).values('menu__item').annotate(total_quantity=Sum('qty')).order_by('-total_quantity')
#     return menu_performance

def get_menu_performance_per_week():
    # Get performance of each menu item for the current week based on quantity ordered
    start_date = now() - timedelta(days=now().weekday())
    end_date = start_date + timedelta(days=7)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT menu_id, SUM(qty) as total_quantity 
            FROM orderapp_ordertable 
            WHERE date_id IN (
                SELECT id 
                FROM orderapp_orderdate 
                WHERE order_date BETWEEN %s AND %s
            )
            GROUP BY menu_id 
            ORDER BY total_quantity DESC
        """, [start_date.date(), end_date.date()])
        menu_performance = cursor.fetchall()
    return menu_performance

def get_menu_performance_per_month():
    # Get performance of each menu item for the current month based on quantity ordered
    current_date = now()
    start_date = current_date.replace(day=1)
    end_date = start_date.replace(day=1) + timedelta(days=32)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT menu_id, SUM(qty) as total_quantity 
            FROM orderapp_ordertable 
            WHERE date_id IN (
                SELECT id 
                FROM orderapp_orderdate 
                WHERE order_date BETWEEN %s AND %s
            )
            GROUP BY menu_id 
            ORDER BY total_quantity DESC
        """, [start_date.date(), end_date.date()])
        menu_performance = cursor.fetchall()
    return menu_performance

def get_menu_performance_per_year():
    # Get performance of each menu item for the current year based on quantity ordered
    current_year = now().year
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT menu_id, SUM(qty) as total_quantity 
            FROM orderapp_ordertable 
            WHERE date_id IN (
                SELECT id 
                FROM orderapp_orderdate 
                WHERE EXTRACT(YEAR FROM order_date) = %s
            )
            GROUP BY menu_id 
            ORDER BY total_quantity DESC
        """, [current_year])
        menu_performance = cursor.fetchall()
    return menu_performance

def menu_analytics(request):
    # Get menu performance data
    menu_performance_per_week = get_menu_performance_per_week()
    menu_performance_per_month = get_menu_performance_per_month()
    menu_performance_per_year = get_menu_performance_per_year()

    # Pass data to the template context
    context = {
        'menu_performance_per_week': menu_performance_per_week,
        'menu_performance_per_month': menu_performance_per_month,
        'menu_performance_per_year': menu_performance_per_year,
    }

    # Render the template with the provided context
    return render(request, 'analytics_menu.html', context)