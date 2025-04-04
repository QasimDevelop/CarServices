from django.http import JsonResponse
from django.shortcuts import render, redirect
from sympy import mobius
from .models import Product, Category, Profile,User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
import requests
from payment.forms import ShippingForm
from payment.models import Order, ShippingAddress
from ecom.settings import API_SECRET_KEY
from django import forms
import json
from cart.cart import Cart
from django.contrib.auth.decorators import login_required




def search(request):
	# Determine if they filled out the fzorm
	if request.method == "POST":
		searched = request.POST['searched']
		# Query The Products DB Model
		searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
		# Test for null
		if not searched:
			messages.success(request, "That Product Does Not Exist...Please try Again.")
			return render(request, "search.html", {})
		else:
			return render(request, "search.html", {'searched':searched})
	else:
		return render(request, "search.html", {})	


def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        form = UserInfoForm(request.POST or None, instance=current_user)

        if form.is_valid():
            number = form.cleaned_data['phone']
            country_code_map = {
                "91": "IN",
                "03": "PK",
                "1": "US",
                "44": "UK",
                "49": "GE"
            }

            # 1. Improved Number Handling:  Clean and standardize the number
            try:
                get_initial_value = number[:2]  # More Pythonic way to slice a string
                country = country_code_map.get(get_initial_value)

                if not country:
                    messages.error(request, "Invalid country code")  # Use messages for errors
                    return render(request, "register.html", {'form': form})  # Re-render form with error

                url = f"http://apilayer.net/api/validate?access_key={API_SECRET_KEY}&number={number}&country_code={country}"

                response = requests.get(url)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("valid"):
                        form.save()
                        messages.success(request, "Your Info Has Been Updated!!")
                        return redirect('home')  # Correct redirect name
                    else:
                        error_message = data.get("error", {}).get("info", "Phone number is not valid.")
                        messages.error(request, error_message)
                        return render(request, "update_info.html", {'form': form}) # Correct template name
                else:
                    messages.error(request, "Error validating phone number.")
                    return render(request, "update_info.html", {'form': form})
            except Exception as e:
                  messages.error(request, e+"Error validating phone number")
                  return render(request, "update_info.html", {'form':form})
        else:
            messages.error(request,"Error validate in Form Submission")
            return render(request, "update_info.html", {'form':form})
    else:
        return render(request, "update_info.html", {'form':form})




def update_password(request):
	if request.user.is_authenticated:
		current_user = request.user
		# Did they fill out the form
		if request.method  == 'POST':
			form = ChangePasswordForm(current_user, request.POST)
			# Is the form valid
			if form.is_valid():
				form.save()
				messages.success(request, "Your Password Has Been Updated...")
				login(request, current_user)
				return redirect('update_user')
			else:
				for error in list(form.errors.values()):
					messages.error(request, error)
					return redirect('update_password')
		else:
			form = ChangePasswordForm(current_user)
			return render(request, "update_password.html", {'form':form})
	else:
		messages.success(request, "You Must Be Logged In To View That Page...")
		return redirect('home')
def update_user(request):
	if request.user.is_authenticated:
		current_user = User.objects.get(id=request.user.id)
		user_form = UpdateUserForm(request.POST or None, instance=current_user)

		if user_form.is_valid():
			user_form.save()

			login(request, current_user)
			messages.success(request, "User Has Been Updated!!")
			return redirect('home')
		return render(request, "update_user.html", {'user_form':user_form})
	else:
		messages.success(request, "You Must Be Logged In To Access That Page!!")
		return redirect('home')


def category_summary(request):
	categories = Category.objects.all()
	return render(request, 'category_summary.html', {"categories":categories})	

def category(request, foo):
	# Replace Hyphens with Spaces
	foo = foo.replace('-', ' ')
	# Grab the category from the url
	try:
		# Look Up The Category
		category = Category.objects.get(name=foo)
		products = Product.objects.filter(category=category)
		return render(request, 'category.html', {'products':products, 'category':category})
	except:
		messages.success(request, ("That Category Doesn't Exist..."))
		return redirect('home')


def product(request,pk):
	product = Product.objects.get(id=pk)
	return render(request, 'product.html', {'product':product})


def home(request):
	products = Product.objects.all()
	return render(request, 'home.html', {'products':products})


def about(request):
	return render(request, 'about.html', {})	

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Shopping cart stuff
            try:
                current_user = Profile.objects.get(user__id=request.user.id)
                saved_cart = current_user.old_cart
                if saved_cart:
                    converted_cart = json.loads(saved_cart)
                    cart = Cart(request)
                    for key, value in converted_cart.items():
                        cart.db_add(product=key)
            except Profile.DoesNotExist:
                pass

            messages.success(request, "You Have Been Logged In!")
            print(user.role)
            if user.role == "Workshop":
                return redirect('workshop')
            return redirect('home')
        else:
            messages.error(request, "There was an error, please try again...")
            return redirect('login')
    else:
        return render(request, 'login.html', {})



def logout_user(request):
	logout(request)
	messages.success(request, ("You have been logged out...Thanks for stopping by..."))
	return redirect('home')



def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password2'] # password2 is correct.
            user = authenticate(request, username=username, password=password) #add request.
            login(request, user)
            Profile.objects.create(user=user)
            messages.success(request, "Username Created ")
            return redirect('login') #or home
        else:
            print(form.errors)  # Add this line
            messages.error(request, "Whoops! There was a problem Registering, please try again...")
            return redirect('register')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})
    
def workshop_view(request):
    if not request.user.is_authenticated or request.user.role != "Workshop":
        return redirect('login')
    
    # Get pending orders for this workshop
    pending_orders = Order.objects.filter(
        confirmed=False
    )
    
    context = {
        'pending_orders': pending_orders
    }
    
    return render(request, 'workshop.html', context)


@login_required
def workshop_view(request):
    pending_orders = Order.objects.filter(confirmed=False)
    return render(request, 'workshop.html', {'pending_orders': pending_orders})

@login_required
def get_order_details(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        data = {
            'customer_name': order.user.username,
            'slot_time': order.slot_time,
            'description': order.description
        }
        return JsonResponse(data)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

@login_required
def confirm_order(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id)
            order.comfirmed = True
            order.save()
            return JsonResponse({'status': 'success'})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)
