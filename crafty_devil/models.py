from django.db import models
from datetime import datetime


# Lewis Conroy - 12/04/2020
# modified 17/05/2020
class Supplier(models.Model):
    name = models.CharField(max_length=40)
    address_1 = models.CharField('Address Line 1', max_length=30)
    address_2 = models.CharField('Address Line 2', max_length=30)
    post_code = models.CharField('Post Code', max_length=7)
    city = models.CharField(max_length=15)
    telephone = models.CharField(max_length=12)
    website = models.CharField(max_length=25)

    def __str__(self):
        return self.name


# Lewis Conroy - 12/04/2020
# modified 01/05/2020
class Product(models.Model):
    desc = models.CharField(max_length=200)
    stock_level = models.IntegerField()
    price = models.FloatField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    image_path = models.CharField(max_length=50, default="product_soon.jpg", null=True)

    def __str__(self):
        return self.desc


# Lewis Conroy - 12/04/2020
class User(models.Model):
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    email = models.CharField(max_length=30)

    class Meta:
        abstract = True

    def __str__(self):
        return self.firstname + " " + self.lastname


# Lewis Conroy - 12/04/2020
# modified 17/05/2020
class Customer(User):
    address_line1 = models.CharField(max_length=30)
    address_line2 = models.CharField(max_length=30)
    post_code = models.CharField(max_length=8)
    city = models.CharField(max_length=20)
    telephone = models.CharField(max_length=12)

    class Meta:
        db_table = 'Customers'


# Lewis Conroy - 12/04/2020
class Staff(User):
    role = models.CharField(max_length=30)

    class Meta:
        db_table = 'Staff'


# Lewis Conroy - 12/04/2020
# modified 10/05/2020
class Payment(models.Model):
    cardholder_name = models.CharField(max_length=30, default=None, blank=True, null=True)
    card_number = models.CharField(max_length=16, default=None, blank=True, null=True)
    expiry_date = models.CharField(max_length=7, default=None, blank=True, null=True)
    security_number = models.CharField(max_length=3, default=None, blank=True, null=True)
    paypal = models.BooleanField()


# Lewis Conroy - 12/04/2020
# modified 09/05/2020
class Order(models.Model):
    date = models.DateField(default=datetime.now())
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, default=None, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total = models.FloatField(default=0)
    status = models.CharField(max_length=12, default='in basket')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, default=None, blank=True, null=True)


# Lewis Conroy - 12/04/2020
# modified 09/05/2020
class OrderLine(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    line_total = models.FloatField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
