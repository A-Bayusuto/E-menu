from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Menu, OrderTable, OrderDate, Supplier
from .forms import OrderStatusForm, CustomUserChangeForm, CustomPasswordChangeForm
from datetime import date, datetime, timedelta
from django.utils.timezone import now
from django.db.models import Sum
from django.db import connection, transaction
from django.http import JsonResponse
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
    # Retrieve all suppliers
    suppliers = list(Supplier.objects.all()) 
    suppliers.append({'supplier_id': '0', 'name': 'All'})
    quantities = range(1, 21)

    # Retrieve selected supplier ID from the cookie
    s_id = request.COOKIES.get('selected_supplier')

    if s_id == None or int(s_id) == 0:
        appetizers = Menu.objects.filter(category='Appetizer')
        main_courses = Menu.objects.filter(category='Main Course')
        desserts = Menu.objects.filter(category='Dessert')
        drinks = Menu.objects.filter(category='Drink')
        current_name = "All"
        context = {
            'appetizers': appetizers,
            'main_courses': main_courses,
            'desserts': desserts,
            'drinks': drinks,
            'quantities': quantities,
            'suppliers': suppliers,
            'current_name' : current_name,
        }
        return render(request, 'menu.html', context)

    elif s_id:
        # If no supplier is selected (cookie not set), show all menu items without redirecting
        appetizers = Menu.objects.filter(category='Appetizer', supplier_id= s_id)
        main_courses = Menu.objects.filter(category='Main Course', supplier_id= s_id)
        desserts = Menu.objects.filter(category='Dessert', supplier_id= s_id)
        drinks = Menu.objects.filter(category='Drink', supplier_id= s_id)
        current_supplier = Supplier.objects.get(supplier_id=s_id)
        current_name = current_supplier.name

        context = {
            'appetizers': appetizers,
            'main_courses': main_courses,
            'desserts': desserts,
            'drinks': drinks,
            'quantities': quantities,
            'suppliers': suppliers,
            'current_name' : current_name,
        }
        return render(request, 'menu.html', context)

    else:
        # If no supplier is selected (cookie not set), show all menu items without redirecting
        appetizers = Menu.objects.filter(category='Appetizer')
        main_courses = Menu.objects.filter(category='Main Course')
        desserts = Menu.objects.filter(category='Dessert')
        drinks = Menu.objects.filter(category='Drink')
        current_name = "All"

        context = {
            'appetizers': appetizers,
            'main_courses': main_courses,
            'desserts': desserts,
            'drinks': drinks,
            'quantities': quantities,
            'suppliers': suppliers,
            'current_name' : current_name,
        }
        return render(request, 'menu.html', context)

    


def add_to_cart(request):
    if request.method == 'POST':
        menu_id = request.POST.get('menu_id')
        quantity = int(request.POST.get('quantity', 1))  # Ensure quantity is an integer
        menu_item = Menu.objects.get(pk=menu_id)

        # Retrieve the existing cart items from the cookie or initialize an empty dictionary
        cart_items_json = request.COOKIES.get('cart_items', '{}')
        cart_items = json.loads(cart_items_json)

        # Check if the menu_id already exists in the cart
        if menu_id in cart_items:
            # Menu item already exists in the cart, update the quantity
            new_quanitity = quantity + int(cart_items[menu_id])
            cart_items[menu_id] = new_quanitity
        else:
            # Add the new item to the cart items dictionary
            cart_items[menu_id] = quantity

        # Serialize the cart items dictionary to JSON
        cart_items_json = json.dumps(cart_items)

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
            'code' : menu_item.code
        })

    # Pass the items list to the template context
    context = {
        'items': items,
        'grand_total': grand_total,
    }

    return render(request, 'cart.html', context)

def increase_item(request):
    if request.method == 'POST':
        menu_id = request.POST.get('item_code')
        quantity = int(request.POST.get('quantity'))

        try:
            menu_item = Menu.objects.get(pk=menu_id)
        except Menu.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Menu item does not exist'})

        # Retrieve cart items from the cookie or initialize an empty dictionary
        cart_items_json = request.COOKIES.get('cart_items', '{}')
        cart_items = json.loads(cart_items_json)

        # Increase the quantity of the item in the cart
        cart_items[menu_id] = cart_items.get(menu_id, 0) + 1

        # Serialize the updated cart items dictionary to JSON
        cart_items_json = json.dumps(cart_items)

        # Set the updated cart items as a cookie in the response
        response = HttpResponseRedirect(reverse('cart'))
        response.set_cookie('cart_items', cart_items_json)

        return response

    else:
        return JsonResponse({'success': False, 'message': 'Method not allowed'})

def reduce_item(request):
    if request.method == 'POST':
        menu_id = request.POST.get('item_code')
        quantity = int(request.POST.get('quantity'))

        try:
            menu_item = Menu.objects.get(pk=menu_id)
        except Menu.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Menu item does not exist'})

        # Retrieve cart items from the cookie or initialize an empty dictionary
        cart_items_json = request.COOKIES.get('cart_items', '{}')
        cart_items = json.loads(cart_items_json)

        # Reduce the quantity of the item in the cart
        if menu_id in cart_items:
            cart_items[menu_id] = max(0, cart_items[menu_id] - 1)  # Ensure quantity doesn't go below 0
            if cart_items[menu_id] == 0:
                del cart_items[menu_id]  # Remove the item if quantity becomes 0

        # Serialize the updated cart items dictionary to JSON
        cart_items_json = json.dumps(cart_items)

        # Set the updated cart items as a cookie in the response
        response = HttpResponseRedirect(reverse('cart'))
        response.set_cookie('cart_items', cart_items_json)

        return response

    else:
        return JsonResponse({'success': False, 'message': 'Method not allowed'})

def remove_item(request):
    if request.method == 'POST':
        menu_id = request.POST.get('item_code')

        try:
            menu_item = Menu.objects.get(pk=menu_id)
        except Menu.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Menu item does not exist'})

        # Retrieve cart items from the cookie or initialize an empty dictionary
        cart_items_json = request.COOKIES.get('cart_items', '{}')
        cart_items = json.loads(cart_items_json)

        # Remove the item from the cart
        if menu_id in cart_items:
            del cart_items[menu_id]

        # Serialize the updated cart items dictionary to JSON
        cart_items_json = json.dumps(cart_items)

        # Set the updated cart items as a cookie in the response
        response = HttpResponseRedirect(reverse('cart'))
        response.set_cookie('cart_items', cart_items_json)

        return response

    else:
        return JsonResponse({'success': False, 'message': 'Method not allowed'})


def clear_cart(request):
    response = redirect('cart')
    response.delete_cookie('cart_items')
    return response

@transaction.atomic
def checkout(request):
    if request.method == 'POST':
        table_number = request.POST.get('table_number')

        # Fetch cart items from cookies
        cart_items_json = request.COOKIES.get('cart_items', '{}')
        cart_items = json.loads(cart_items_json)

        # Get the first supplier from the database
        # supplier = Supplier.objects.first()

        # Get current date and time
        current_datetime = datetime.now()

        # Initialize list to hold order objects
        orders = []
        grand_total = 0

        # Iterate over cart items
        for key, value in cart_items.items():
            try:
                menu_item = Menu.objects.get(code=key)
            except Menu.DoesNotExist:
                # Handle case where menu item does not exist
                continue

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
            order_id = OrderTable.objects.filter(order_date__order_date=current_datetime.date()).count() + 1
            order = OrderTable(
                table_id=table_number,
                supplier=menu_item.supplier,
                menu=menu_item,
                order_date=order_date,
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

    # Handle GET requests or other cases where method is not POST
    return redirect('cart')

def checkout_success(request):
    start_date = date.today() - timedelta(days=7)
    current_date = date.today()
    orders = OrderTable.objects.filter(order_date__order_date__range=[start_date, current_date], order_status="Pending")    
    context = {
        'orders': orders
    }
    return render(request, 'checkout_success.html', context)

def orderlist(request):
    start_date = date.today() - timedelta(days=7)
    current_date = date.today()
    orders = OrderTable.objects.filter(
        order_date__order_date__range=[start_date, current_date],
        order_status="Pending"
    )    
    form = OrderStatusForm()  # Create an instance of the form
    context = {
        'orders': orders,
        'form': form,
    }
    return render(request, 'orderlist.html', context)


def update_order_status(request):
    if request.method == 'POST' and request.is_ajax():
        table_id = request.POST.get('table_id')
        supplier_id = request.POST.get('supplier')
        menu_id = request.POST.get('menu')
        order_date = request.POST.get('order_date')
        new_status = request.POST.get('new_status')

        try:
            # Get the order object based on the unique combination of fields
            order = OrderTable.objects.get(
                table_id=table_id,
                supplier_id=supplier_id,
                menu_id=menu_id,
                order_date=order_date
            )

            # Update the order status
            order.order_status = new_status
            order.save()
            # Return success response
            return JsonResponse({'success': True})
        except OrderTable.DoesNotExist:
            return JsonResponse({'error': 'Order not found.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400)
    

def get_kpi_per_weeks():
    # Get KPIs for the last 52 weeks
    kpi_weeks = []
    current_date = now()
    for i in range(52, 0, -1):
        start_date = current_date - timedelta(days=current_date.weekday() + (i - 1) * 7)
        end_date = start_date + timedelta(days=6)
        weekly_sales = OrderTable.objects.filter(
            order_date__order_date__range=[start_date, end_date]
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
    for i in range(23, -1, -1):
        target_date = current_date - timedelta(days=i*30)
        year = target_date.year
        month = target_date.month
        _, last_day = monthrange(year, month)
        start_date = target_date.replace(day=1)
        end_date = target_date.replace(day=last_day)
        monthly_sales = OrderTable.objects.filter(
            order_date__order_date__range=[start_date, end_date]
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
            order_date__order_date__year=year
        ).aggregate(total_sales=Sum('total'))['total_sales'] or 0
        kpi_years.append({
            'year': year,
            'total_sales': yearly_sales
        })
    return kpi_years

def sales_analytics(request):
    weekly_kpi = get_kpi_per_weeks()
    monthly_kpi = get_kpi_per_months()
    yearly_kpi = get_kpi_per_years()

    # print('1 :', weekly_kpi)
    # print('2 :', monthly_kpi)
    # print('3 :', yearly_kpi)    
    
    context = {
        'monthly_kpi': monthly_kpi,
        'weekly_kpi': weekly_kpi,
        'yearly_kpi': yearly_kpi,
    }
    return render(request, 'analytics_sales.html', context)


def get_menu_performance_per_week():
    # Get performance of each menu item for the current week based on quantity ordered
    start_date = now() - timedelta(days=now().weekday())
    end_date = start_date + timedelta(days=6)
    menu_performance = OrderTable.objects.filter(
        order_date__order_date__range=[start_date, end_date]
    ).values('menu__item').annotate(total_quantity=Sum('qty')).order_by('-total_quantity')
    return menu_performance

def get_menu_performance_per_month():
    # Get performance of each menu item for the current month based on quantity ordered
    current_date = now()
    start_date = current_date.replace(day=1)
    end_date = start_date.replace(day=1) + timedelta(days=32)
    menu_performance = OrderTable.objects.filter(
        order_date__order_date__range=[start_date, end_date]
    ).values('menu__item').annotate(total_quantity=Sum('qty')).order_by('-total_quantity')
    return menu_performance

def get_menu_performance_per_year():
    # Get performance of each menu item for the current year based on quantity ordered
    current_year = now().year
    menu_performance = OrderTable.objects.filter(
        order_date__order_date__year=current_year
    ).values('menu__item').annotate(total_quantity=Sum('qty')).order_by('-total_quantity')
    return menu_performance

# def get_menu_performance_per_week():
#     # Get performance of each menu item for the current week based on quantity ordered
#     start_date = datetime.now() - timedelta(days=datetime.now().weekday())
#     end_date = start_date + timedelta(days=6)
#     query = """
#         SELECT menu_id, SUM(qty) AS total_ordered
#         FROM orderapp_ordertable
#         WHERE order_date_id >= (SELECT date_id FROM orderapp_orderdate WHERE order_date = date_trunc('week', %s))
#         AND order_date_id < (SELECT date_id FROM orderapp_orderdate WHERE order_date = date_trunc('week', %s) + interval '1 week')
#         GROUP BY menu_id;
#     """
#     with connection.cursor() as cursor:
#         cursor.execute(query, [start_date, end_date])
#         menu_performance = cursor.fetchall()
#     return menu_performance

# def get_menu_performance_per_month():
#     # Get performance of each menu item for the current month based on quantity ordered
#     current_date = datetime.now()
#     start_date = current_date.replace(day=1)
#     end_date = start_date.replace(day=1) + timedelta(days=31)
#     print([start_date, end_date])
#     query = """
#         SELECT menu_id, SUM(qty) AS total_ordered
#         FROM orderapp_ordertable
#         WHERE order_date_id >= (SELECT date_id FROM orderapp_orderdate WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM %s) AND EXTRACT(MONTH FROM order_date) = EXTRACT(MONTH FROM %s))
#         AND order_date_id < (SELECT date_id FROM orderapp_orderdate WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM %s) AND EXTRACT(MONTH FROM order_date) = EXTRACT(MONTH FROM %s) + 1)
#         GROUP BY menu_id;
#     """
#     with connection.cursor() as cursor:
#         cursor.execute(query, [start_date, end_date])
#         menu_performance = cursor.fetchall()
#     return menu_performance

# def get_menu_performance_per_year():
#     # Get performance of each menu item for the current year based on quantity ordered
#     current_year = datetime.now().year
#     query = """
#         SELECT menu_id, SUM(qty) AS total_ordered
#         FROM orderapp_ordertable
#         WHERE order_date_id >= (SELECT date_id FROM orderapp_orderdate WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM %s))
#         AND order_date_id < (SELECT date_id FROM orderapp_orderdate WHERE EXTRACT(YEAR FROM order_date) = EXTRACT(YEAR FROM %s) + 1)
    #     GROUP BY menu_id;
    # """
    # with connection.cursor() as cursor:
    #     cursor.execute(query, [current_year])
    #     menu_performance = cursor.fetchall()
    # return menu_performance


def menu_analytics(request):

    # Get menu performance data
    menu_performance_per_week = get_menu_performance_per_week()
    menu_performance_per_month = get_menu_performance_per_month()
    menu_performance_per_year = get_menu_performance_per_year()

    # print('1 :', menu_performance_per_week)
    # print('2 :', menu_performance_per_month)
    # print('3 :', menu_performance_per_year)

    # Pass data to the template context
    context = {
        'menu_performance_per_week': menu_performance_per_week,
        'menu_performance_per_month': menu_performance_per_month,
        'menu_performance_per_year': menu_performance_per_year,
    }

    # Render the template with the provided context
    return render(request, 'analytics_menu.html', context)


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserCreationForm()
    return render(request, 'create_user.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def edit_user(request, user_id):
    user = User.objects.get(id=user_id)
    
    # Set a cookie with the user ID
    response = render(request, 'edit_user.html', {'form': CustomUserChangeForm(instance=user), 'user': user})
    response.set_cookie('edit_user_id', user_id)
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = CustomUserChangeForm(instance=user)
    return response

@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

# @user_passes_test(lambda u: u.is_superuser or u.is_staff)
# def change_password(request):
#     # Get user_id from the cookie
#     user_id = request.COOKIES.get('edit_user_id')

#     if user_id is None:
#         # Handle case where cookie is missing
#         return HttpResponse("User ID not found in cookie.")
    
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         # Handle case where user does not exist
#         return HttpResponse("User not found.")

#     form = PasswordChangeForm(user)

#     if request.method == 'POST':
#         form = PasswordChangeForm(user, request.POST)
#         if form.is_valid():
#             form.save()
#             # Clear the cookie by setting its value to an empty string and expiration to a past date
#             response = redirect('user_list')
#             response.set_cookie('edit_user_id', '', expires='Thu, 01 Jan 1970 00:00:00 GMT')
#             return response
    
#     return render(request, 'change_password.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def change_password(request):
    user_id = request.COOKIES.get('edit_user_id')

    if user_id is None:
        return HttpResponse("User ID not found in cookie.")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse("User not found.")

    form = CustomPasswordChangeForm(user)

    if request.method == 'POST':
        form = CustomPasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            response = redirect('user_list')
            response.set_cookie('edit_user_id', '', expires='Thu, 01 Jan 1970 00:00:00 GMT')
            return response
    
    return render(request, 'change_password.html', {'form': form})