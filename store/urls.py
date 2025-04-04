from django.urls import path
from . import views

urlpatterns = [
    path('workshop/', views.workshop_view, name='workshop'),
    path('get_order_details/<int:order_id>/', views.get_order_details, name='get_order_details'),
    path('confirm_order/<int:order_id>/', views.confirm_order, name='confirm_order'),
    path('', views.home, name='home'),
    path('new/', views.workshop_view , name="workshop"),
    path('about/', views.about, name='about'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('update_password/', views.update_password, name='update_password'),
    path('update_user/', views.update_user, name='update_user'),
    path('update_info/', views.update_info, name='update_info'),
    path('product/<int:pk>', views.product, name='product'),
    path('category/<str:foo>', views.category, name='category'),
    path('category_summary/', views.category_summary, name='category_summary'),
    path('search/', views.search, name='search'),
]
