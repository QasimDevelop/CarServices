from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from cart.cart import Cart
from payment.forms import *
from payment.models import DeletedOrder, Order, OrderItem,Slots
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product, Profile
import datetime
from django.db import transaction
from django.shortcuts import redirect
from django.contrib import messages
import datetime
# Import Some Paypal Stuff
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid # unique user id for duplictate orders

def orders(request, pk):
	if request.user.is_authenticated and request.user.is_superuser:
		# Get the order
		order = Order.objects.get(id=pk)
		# Get the order items
		items = OrderItem.objects.filter(order=pk)

		if request.POST:
			status = request.POST['shipping_status']
			# Check if true or false
			if status == "true":
				# Get the order
				order = Order.objects.filter(id=pk)
				# Update the status
				now = datetime.datetime.now()
				order.update(shipped=True, date_shipped=now)
			else:
				# Get the order
				order = Order.objects.filter(id=pk)
				# Update the status
				order.update(shipped=False)
			messages.success(request, "Shipping Status Updated")
			return redirect('home')


		return render(request, 'payment/orders.html', {"order":order, "items":items})




	else:
		messages.success(request, "Access Denied")
		return redirect('home')



def not_shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=False)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# Get the order
			order = Order.objects.filter(id=num)
			# grab Date and time
			now = datetime.datetime.now()
			# update order
			order.update(shipped=True, date_shipped=now)
			# redirect
			messages.success(request, "Shipping Status Updated")
			return redirect('home')

		return render(request, "payment/not_shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=True)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# grab the order
			order = Order.objects.filter(id=num)
			# grab Date and time
			now = datetime.datetime.now()
			# update order
			order.update(shipped=False)
			# redirect
			messages.success(request, "Shipping Status Updated")
			return redirect('home')


		return render(request, "payment/shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def process_order(request):
    if request.method != "POST":
        messages.error(request, "Access Denied")
        return redirect('login')
    
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    slots_queryset = Slots.objects.filter(status=True)
    
    # Initialize the slot form with POST data
    slot_form = SlotSelectForm(request.POST, request.FILES, slots=slots_queryset)
    
    if not slot_form.is_valid():
        print(slot_form.errors)  # Debugging purpose
        messages.error(request, "Invalid slot selection.")
        return redirect('checkout')
    
    # Extract form data
    selected_slot_index = slot_form.cleaned_data['slot_time']
    
    try:
        selected_slot_val = Slots.objects.get(id=selected_slot_index)
        
        # Check if slot is still available
        if not selected_slot_val.status:
            messages.error(request, "Sorry, this slot is no longer available.")
            return redirect('checkout')
            
        selected_image = slot_form.cleaned_data['image']
        description = slot_form.cleaned_data['description']
        selected_slot = selected_slot_val.start_time.strftime("%I:%M %p")
        amount_paid = totals
        with transaction.atomic():
            # Create order with common fields
            create_order = Order(
                amount_paid=amount_paid,
                slot_time=selected_slot,
                image=selected_image,
                description=description
            )
            
            # Add user if authenticated
            if request.user.is_authenticated:
                create_order.user = request.user
            
            create_order.save()
            
            # Add order items
            order_id = create_order.pk
            order_items = []
            
            for product in cart_products:
                product_id = product.id
                price = product.sale_price if product.is_sale else product.price
                quantity = quantities.get(str(product_id), 0)
                
                if quantity > 0:
                    order_item = OrderItem(
                        order_id=order_id,
                        product_id=product_id,
                        quantity=quantity,
                        price=price
                    )
                    
                    if request.user.is_authenticated:
                        order_item.user = request.user
                    
                    order_items.append(order_item)
            
            # Bulk create order items for better performance
            if order_items:
                OrderItem.objects.bulk_create(order_items)
            
            # Update slot status
            selected_slot_val.status = False
            selected_slot_val.save()
            
            # Update user profile if authenticated
            if request.user.is_authenticated:
                Profile.objects.filter(user__id=request.user.id).update(old_cart="")
            
            # Clear cart
            cart.clear()
            
            messages.success(request, "Order Placed!")
            return redirect('orders')
            
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing order: {str(e)}")
        messages.error(request, "An error occurred while processing your order.")
        return redirect('checkout')


def billing_info(request):
	if request.POST:
		# Get the cart
		cart = Cart(request)
		cart_products = cart.get_prods
		quantities = cart.get_quants
		totals = cart.cart_total()

		# Create a session with Shipping Info
		my_shipping = request.POST
		request.session['my_shipping'] = my_shipping

		# Get the host
		host = request.get_host()
		# Create Paypal Form Dictionary
		paypal_dict = {
			'business': settings.PAYPAL_RECEIVER_EMAIL,
			'amount': totals,
			'item_name': 'Book Order',
			'no_shipping': '2',
			'invoice': str(uuid.uuid4()),
			'currency_code': 'USD', # EUR for Euros
			'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
			'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
			'cancel_return': 'https://{}{}'.format(host, reverse("payment_failed")),
		}

		# Create acutal paypal button
		paypal_form = PayPalPaymentsForm(initial=paypal_dict)


		# Check to see if user is logged in
		if request.user.is_authenticated:
			# Get The Billing Form
			billing_form = PaymentForm()
			return render(request, "payment/billing_info.html", {"paypal_form":paypal_form, "cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})

		else:
			# Not logged in
			# Get The Billing Form
			billing_form = PaymentForm()
			return render(request, "payment/billing_info.html", {"paypal_form":paypal_form, "cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})


		
		shipping_form = request.POST
		return render(request, "payment/billing_info.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})	
	else:
		messages.success(request, "Access Denied")
		return redirect('home')


def checkout(request):
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    
    if request.user.is_authenticated:
        # Fetch available slots (assuming they are fetched from the database)
        slots_queryset = Slots.objects.filter(status=True)  # Adjust the query as per your requirements
        
        if request.method == 'POST':
            # Process the submitted form data
            slot_form = SlotSelectForm(request.POST, slots=slots_queryset)
            if slot_form.is_valid():
                selected_slot_time = slot_form.cleaned_data['slot_time']
                
                # Do something with the selected slot time, e.g., save it or use it in some logic
                # For example, you might want to save it to the order or session
                print(f"Selected Slot Time: {selected_slot_time}")
                
                # Redirect or proceed with further processing
                return render(request, "checkout.html")  # Replace with your actual success URL
            
        else:
            # Show the form for GET request
            slot_form = SlotSelectForm(slots=slots_queryset)
        
        return render(request, "payment/checkout.html", 
                      {"cart_products": cart_products, 
                       "quantities": quantities,
                       "totals": totals,
                       "slot_form": slot_form})
    else:
        # Checkout as guest
        return render(request, "payment/checkout.html", {"cart_products": cart_products, "quantities": quantities, "totals": totals})

	

def payment_success(request):
	return render(request, "payment/payment_success.html", {})


def payment_failed(request):
	return render(request, "payment/payment_failed.html", {})

def order_status(request):
	if request.user.is_authenticated:
		orders=Order.objects.filter(user=request.user)
		return render(request, "payment/order_status.html", {"orders":orders})
	else:
		messages.error(request, "Access Denied")
		return redirect('login')
def order_delete(request):
    if request.POST.get('action') == 'post':
        order_id = request.POST.get('order_id')
        try:
            order = get_object_or_404(Order, id=order_id)
            
            # Store order info in DeletedOrder
            deleted_order = DeletedOrder(
                original_id=order.id,
                customer_name=order.user.username,
                service_date=order.date_ordered,
            )
            deleted_order.save()

            # Convert the TimeField to match the stored CharField format
            slots = Slots.objects.all()
            for slot in slots:
                if slot.start_time.strftime('%I:%M %p') == order.slot_time:
                    slot.status = True  # Make the slot available again
                    slot.save()
                    break
            order.delete()
            
            messages.success(request, "Order Deleted Successfully.")
            return JsonResponse({'order': order_id})
            
        except Exception as e:
            print(f"Error: {str(e)}")  # For debugging
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_available_slots(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        selected_date_str = request.GET.get('date')
        available_slots = Slots.objects.filter(date=selected_date_str, status=True) #filter by date
        slots = []
        for s in available_slots:
            slots.append({'id': s.id, 'time': s.start_time.strftime("%I:%M %p")})
        return JsonResponse({'slots': slots})
    return JsonResponse({'error': 'Invalid request'}, status=400)