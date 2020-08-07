from django import forms

from crafty_devil.models import *


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)


class UserDetailsForm(forms.Form):
    firstname = forms.CharField(label='First Name', max_length=32)
    lastname = forms.CharField(label='Last Name', max_length=32)
    password = forms.CharField(label='Password', max_length=32, widget=forms.PasswordInput(render_value=True))
    address_line1 = forms.CharField(label='Address Line 1', max_length=32)
    address_line2 = forms.CharField(label='Address Line 2', max_length=32, required=False)
    telephone = forms.CharField(label='Telephone', max_length=12)
    post_code = forms.CharField(label='Post Code', max_length=8)
    city = forms.CharField(label='City', max_length=25)
    email = forms.CharField(label='Email', max_length=32)

    class Meta:
        model = Customer


class AddToBasketForm(forms.Form):
    quantity = forms.IntegerField(label='Quantity', initial=1, min_value=1)


class EditBasketForm(forms.Form):
    quantity = forms.IntegerField(label='Quantity', min_value=1)


class ProductDetailsForm(forms.Form):
    desc = forms.CharField(label='Product Desc')
    price = forms.FloatField(label='Price', min_value=0)
    stock_level = forms.IntegerField(label='Stock Level', min_value=0)
    supplier = forms.IntegerField(label='Supplier ID', min_value=1)


class SupplierDetailsForm(forms.Form):
    name = forms.CharField(label='Supplier Name')
    address_1 = forms.CharField(label='Address Line 1')
    address_2 = forms.CharField(label='Address Line 2', required=False)
    post_code = forms.CharField(label='Post Code')
    city = forms.CharField(label='City')
    telephone = forms.CharField(label='Telephone')
    website = forms.CharField(label='Website')


class CustomerCardForm(forms.Form):
    cardholder_name = forms.CharField(label='Cardholder Name')
    card_number = forms.CharField(label='Card Number')
    expiry_date = forms.CharField(label='Expiry Date (MM/YYYY)')
    security_number = forms.CharField(label='CCV')
