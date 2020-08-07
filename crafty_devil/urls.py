from django.urls import path
from . import views

"""URL Patterns:

These patterns are used by the server to determine which view method to call. Each pattern is
linked up with the view method name, and it provides the method with the necessary arguments as well.

It also takes an alias which is used to reference these urls inside the html templates in order to redirect to
other views!

For example, in production, if you typed 'craftydevil.co.uk/product/5', into the URL address bar in your browser, 
the server would use this file to work out that this url should call the product(request, product_id) method, 
and pass it the argument 5 as product_id.

However this also means that a random user can access 'staff-delete-user/5', for instance, and so sensitive URLs
require security and validation on the serverside to prevent this.
"""

urlpatterns = [
    path('', views.index, name='index'),
    path('products', views.products, name='products'),
    path('products/<int:page>/', views.products, name='products'),
    path('product/<int:product_id>/', views.product, name='product'),

    path('view_basket', views.view_basket, name='view basket'),
    path('view_basket/<int:orderline_id>', views.view_basket, name='view basket'),
    path('delete_ol/<int:orderline_id>', views.delete_basket_line, name='delete basket line'),
    path('edit_basket/<str:orderline_id>/<str:quantity>', views.update_basket_orderline_quantity,
         name='update basket ol quantity'),
    path('checkout', views.checkout, name='checkout'),
    path('confirm_order', views.confirm_order, name='confirm order'),
    path('cancel-order/<int:order_id>', views.cancel_order, name='cancel order'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment success'),

    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),

    path('login', views.login, name='login'),
    path('login/<str:label>', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('signup', views.signup, name='signup'),
    path('signup/<str:label>', views.signup, name='signup failed'),

    path('staff-login/<str:user_type>', views.login, name='staff login'),
    path('staff-dashbard/<str:page>', views.staff_dashboard, name='staff dashboard'),

    path('staff-edit-user/<int:user_id>', views.edit_customer, name='edit customer'),
    path('staff-delete-user/<int:user_id>', views.delete_customer, name='delete customer'),
    path('staff-edit-product/<int:product_id>', views.edit_product, name='edit product'),
    path('staff-delete-product/<int:product_id>', views.delete_product, name='delete product'),
    path('staff-edit-supplier/<int:supplier_id>', views.edit_supplier, name='edit supplier'),
    path('staff-delete-supplier/<int:supplier_id>', views.delete_supplier, name='delete supplier'),
    path('staff-delete-order/<int:order_id>', views.delete_order, name='delete order'),
    path('staff-add-product', views.add_product, name='add product'),
    path('staff-add-product/<str:label>', views.add_product, name='add product'),
    path('staff-add-customer', views.add_customer, name='add customer'),
    path('staff-add-supplier', views.add_supplier, name='add supplier'),

    path('view_account', views.view_account, name='view account'),
    path('view_account/<str:page>', views.view_account, name='view account'),
    path('view_order/<int:order_id>', views.view_order, name='view order'),
    ]
