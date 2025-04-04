from django.contrib import admin
from .models import Category, Product, Profile,User

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Profile)
admin.site.register(User)

# Mix profile info and user info
class ProfileInline(admin.StackedInline):
	model = Profile

# Extend User Model
class UserAdmin(admin.ModelAdmin):
	model = User
	field = ["username", "first_name", "last_name", "email"]


