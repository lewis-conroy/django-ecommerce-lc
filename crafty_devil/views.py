# django imports
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict  # used to populate view_account_details_form with existing user data
from crafty_devil.forms import *
from django.urls import reverse
from django.conf import settings

# EXTRA LIBRARIES!! :)
# for making objects JSON compatible to be saved into the session object
import jsonpickle
# for paypal payment integration
from paypal.standard.forms import PayPalPaymentsForm  # paypal api library
# for storing / using dates
from datetime import datetime
# For Sending Emails
import smtplib
import ssl

# READ ME!
''' READ ME! by Lewis Conroy May 11th 8:30am 2020

this is an example of roughly what all dynamic pages in my project will look like in the views.py file.

the name of the function here is used by the urls.py file to link the url typed into the browser to the function which
prepares the html page. Imagine, in the urls.py file, there's a "path('index', views.index, name='index') (which there
definitely is). the first argument will match up with the url which was typed into the address bar in the browser.
the second will match up with the name of the corresponding function in the views.py file. The third is a helper for
certain functions to hook onto so as to be able to reference the function in other ways. So if I wanted a url to match
up with this example, I would have 'path('url/pattern/i/want', views.example_dynamic_page, name='example')

def example_dynamic_page(request):
    if request.method == 'POST':
        form = ExampleForm(request.POST)
        if form.is_valid():
            field1 = form.cleaned_data.get('field1')
            field2 = form.cleaned_data.get('field2)
            
            object = Object(field1=field1,
                            field2=field2,)
                            
            object.save()
            
            context = {
                'user': get_session_user(request),
                'something_useful': object,
                }
            return render(request, 'crafty_devil/example_dynamic_page', context)
        else:  # i.e. form is not valid
            context = {
                'user': get_session_user(request)
                'form': ExampleForm,
                'label': 'the form was invalid. please try again.'
                }
            return render(request, 'crafty_exaple_dynamic_page.html', context)
    else:  # i.e. GET
        context = {
            'user': get_session_user(request),
            'form': ExampleForm,
            }
        return render(request, 'crafty_exaple_dynamic_page.html', context)
        
the first thing to note is the first conditional. This allows the function to both process a POST from and provide a GET
to the HTTP request. So 'if request.method == 'POST'' will be true if the user submitted a form on the page. This makes
processing POSTs very tidy as it's in the same function as it's GET counterpart. 

Next, we retrieve the contents of the returned form using form = FormType(request.POST). These forms live in the 
forms.py file and can be made and used freely for our purposes. You can iterate over a form's fields or draw them 
individually, which is extremely versatile. We can use these fields to initialise an object, as seen in the example.

These objects live in the models.py file, and are essentially representations of tables in the database. You can save
these objects to their corresponding tables by using object.save(). No SQL necessary for this.

Once the object has been saved, we can return the page with an updated context to reflect the changes made. For
instance, we can pass a value called 'update_success' into the view using the context dictionary, and then, using an if
inside the page, we can draw a success message, or a failure message depending on whether the object was saved
successfully.

context dicts are provided to all pages so that they can use the contained data to dynamically produce the html file.
I might put my current user, current form, success labels, lists of things etc. into the context so that it can
dynamically / iteratively display these things to the user. So my page uses the value inside context['user'] to show
the logged in user.

Having said all this, providing dynamic pages is quite simple in django. All you really need to know is:
    how views.py works
    how forms.py works
    how urls.py works
    how models.py works
    how to create a conditional block in a template
    how to use template inheritance
    how to use the session
    how to use static files
    
This may seem like a lot, but it comes very quickly and is quite intuitive.
'''

''' Non Page functions 
    
    These functions essentially do what they say they do but do not return views or anything
    Just little helpers to reduce repeating code.
    
    None of these functions are referenced by urls.py and so they're not directly accessible by the user.
'''


# sends an email confirming that the user's order was a success. details order contents etc.
def order_confirmation_email(request, order, user):
    # information required to send email
    port = 465  # smtp port to connect to gmail service
    sender_email = "noreply.craftydevil@gmail.com"  # crafty devil email account to send email from
    receiver_email = user.email  # target user email to send email to
    password = "tkhp29xwpd5QJXg"  # crafty devil email account password

    # preparing the orderlines for the email
    # creating a string of all the orderline details to insert into the following formatted email string
    order_contents = ""
    for orderline in get_orderlines(request, order):
        order_contents += \
            "{product_desc}, price: £{product_price}, quantity: {quantity}, Line Total: £{total}\n".format(
                product_desc=orderline.product.desc,
                product_price=orderline.product.price,
                quantity=orderline.quantity,
                total=orderline.line_total
            )

    # preparing the main body of the email text
    text = """Subject:Your Crafty Devil Order\n
    Hello {name},\n
    Thank you for placing an order with Crafty Devil.\n
    Your Order no.: {order_no}\n
    Order Contents:\n
    {order_contents}\n
    Total: £{order_total}
    """.format(name=user.firstname,
               order_no=order.id,
               order_contents=order_contents,
               order_total=order.total)

    # the smtp server expects utf-8 data, so encoding the email in unicode form
    text = text.encode('utf-8').strip()

    # establishing connection to ssl server
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        # logging into smtp server
        server.login("noreply.craftydevil@gmail.com", password)
        # sending email
        server.sendmail(sender_email, receiver_email, text)


# Decodes session data from JSON session object, using jsonpickle
def get_session_user(request):
    try:  # attempts to decode User class object from JSON code from the session object
        user = jsonpickle.decode(request.session.__getitem__('user'))
        if len(Customer.objects.filter(id=user.id)) <= 0:  # failsafe incase the user is deleted while logged in
            raise ValueError("User doesn't exist in database")
        else:
            return user
    except (KeyError, ValueError):  # if there is no user in the session, return None
        return None


# returns true if there is a logged in user, else false
def confirm_user_logged_in(request):
    return get_session_user(request) is not None


# encodes and saves user object as session user
def set_session_user(request, user):
    try:  # attempts to encode the User object and save it as JSON information in the session object
        serialised_user = jsonpickle.encode(user)
        request.session.__setitem__("user", serialised_user)
    except (ValueError, KeyError):
        return False


# encodes and sets the session's staff user
def set_session_staff_user(request, user):
    try:  # attempts to encode the User object and save it as JSON information in the session object
        serialised_user = jsonpickle.encode(user)
        request.session.__setitem__("staff", serialised_user)
    except (ValueError, KeyError):
        return False


# Decodes session data from JSON session object, using jsonpickle
def get_session_staff_user(request):
    try:
        staff = jsonpickle.decode(request.session.__getitem__('staff'))
        if len(Staff.objects.filter(id=staff.id)) <= 0:
            raise ValueError("User doesn't exist")
        else:
            return staff
    except (KeyError, ValueError):  # if there is no staff member, return None
        return None


# retrieves the orderlines of a given order by using its id
def get_orderlines(request, order):
    return OrderLine.objects.filter(order_id=order.id)


# retrieves the order and corresponding orderlines from database and returns them conveniently in a tuple object
def get_basket(request):
    user = get_session_user(request)

    # retrieves all user's orders
    orders = Order.objects.filter(customer=user)
    for order in orders:
        if order.status == 'in basket':  # finds the one whose status is 'in basket'
            return order, get_orderlines(request, order)

    # if it doesn't find one, it makes a new one and returns it, along with an empty list since there are no orderlines.
    order = Order(customer=get_session_user(request))
    order.save()
    return order, []


# validates each necessary form field for creating or editing a user one by one.
# returns a helpful string which is used to provide an error label in the html view.
def validate_user_details(form):
    # gets all the necessary fields
    firstname = form.cleaned_data.get('firstname')
    lastname = form.cleaned_data.get('lastname')
    password = form.cleaned_data.get('password')
    address_line1 = form.cleaned_data.get('address_line1')
    post_code = form.cleaned_data.get('post_code')
    email = form.cleaned_data.get('email')
    city = form.cleaned_data.get('city')
    telephone = form.cleaned_data.get('telephone')

    # ensures the first and lastnames aren't too short
    if len(firstname) < 2 or len(lastname) < 2:
        return 'name-failed'
    # ensures the password isn't too short
    if len(password) < 5:
        return 'password-failed'
    # ensures an actual address has been entered
    elif len(address_line1) < 5:
        return 'address-failed'
    # ensures the post code is the correct length
    elif len(post_code) < 6 or len(post_code) > 7:
        return 'post-code-failed'
    # ensures the telephone number is the correct length
    elif len(telephone) < 11 or len(telephone) > 12:
        return 'telephone-failed'
    # ensures that a city has been entered
    elif len(city) < 3:
        return 'city-failed'
    # ensures that the email contains the necessary parts of an email
    elif '@' not in email and ('.com' not in email or '.co.uk' not in email):
        return 'email-failed'
    # ensures email isn't in use already
    elif len(Customer.objects.filter(email=email)):
        return 'email-used'
    # if all the fields are valid, returns 'success' to show it was a success

    for x in telephone:
        if x.isalpha():
            return 'telephone-failed'

    return 'success'


# validates each necessary form field for creating or editing a supplier one by one.
# returns a helpful string which is used to provide an error label in the html view.
def validate_supplier_details(form):
    name = form.cleaned_data.get('name')
    address_1 = form.cleaned_data.get('address_1')
    post_code = form.cleaned_data.get('post_code')
    city = form.cleaned_data.get('city')
    telephone = form.cleaned_data.get('telephone')

    if len(name) < 3:
        return 'name-failed'
    elif len(address_1) < 3:
        return 'address1-failed'
    elif len(post_code) < 6 or len(post_code) > 7:
        return 'post-code-failed'
    elif len(city) < 3:
        return 'city-failed'
    elif len(telephone) < 11:
        return 'telephone-failed'

    for x in telephone:
        if x.isalpha():
            return 'telephone-failed'

    return 'success'


# determines whether the given card number is valid using an algorithm based on the Luhn algorithm
def validate_card_number(number):
    validatelist = []

    for i in number:
        validatelist.append(int(i))
    for i in range(0, len(number), 2):
        validatelist[i] *= 2
        if validatelist[i] >= 10:
            validatelist[i] = validatelist[i] // 10 + validatelist[i] % 10

    if sum(validatelist) % 10 == 0:
        return True
    else:
        return False


# validates card data when submitting a payment
# returns helpful string describing what isn't valid
def validate_card_details(form):
    cardholder_name = form.cleaned_data.get('cardholder_name')
    card_number = form.cleaned_data.get('card_number')
    expiry_date = form.cleaned_data.get('expiry_date')
    security_number = form.cleaned_data.get('security_number')

    if len(cardholder_name) < 3:
        return 'cardholder-name-fail'
    elif not validate_card_number(card_number):
        return 'cardnumber-fail'
    elif len(expiry_date) != 6:
        return 'expiry-date-fail'
    elif len(security_number) != 3:
        return 'ccv-fail'

    expiry_date = int(expiry_date[:2]), int(expiry_date[2:])
    if (expiry_date[1] < datetime.now().year) or (expiry_date[1] < datetime.now().month):
        return 'expiry-date-fail'

    return 'success'


''' Page Functions

    Most of these functions actually return the views to the browser.
    All of them are referenced by urls.py which means a user can access them by typing the
    url pattern into their browser.
    
    This means that they have to be secured by checking session variables, otherwise Bob will be able to
    access and cancel Joe's latest order, for instance.
'''

''' Core Functionality Functions

    These are basically the view functions which fulfil the core functionality as put in a word document I was emailed
    by James on March 26th 2020. I went a bit overboard with the functionality I had planned because I had the ball
    rolling haha so feel free to ignore all the admin functions which I will label accordingly.

'''


# returns homepage
def index(request):
    try:
        latest_products = list(Product.objects.all())[-3:]  # negative index gets last 3 items in list :)
    except ValueError:  # if there are not 3 products, returns as many as it can
        latest_products = Product.objects.all()

    # dict of info required for page to generate dynamic parts (used in almost all view methods)
    context = {
        'user': get_session_user(request),
        'staff': get_session_staff_user(request),
        'products': latest_products,
    }
    return render(request, 'crafty_devil/index.html', context)


# returns page for browsing products
def products(request, page=1):
    page_products = list(Product.objects.all())[page - 1 * 25: page * 25]  # gets 25 items from the products list

    page_products *= 5  # multiplies the array by five to demonstrate how the products page displays products

    context = {
        'user': get_session_user(request),
        'staff': get_session_staff_user(request),
        'products': page_products,
    }
    return render(request, 'crafty_devil/products.html', context)


# returns page detailing one product and allowing to add it to basket
def product(request, product_id):
    if request.method == 'POST':  # i.e. user has clicked 'Add to Basket' !
        if not get_session_user(request):  # checks user is logged in
            return redirect('login')  # if not logged in, send to login page

        order, lines = get_basket(request)  # get order and orderlines from db

        form = AddToBasketForm(request.POST)
        if form.is_valid():
            p = Product.objects.filter(id=product_id)[0]  # p cause the function is called product already >:/
            quantity = form.cleaned_data.get('quantity')

            # ensures that the customer can't buy more of a product than there is in stock
            if quantity > p.stock_level:
                context = {
                    'user': get_session_user(request),
                    'product': Product.objects.filter(id=product_id)[0],
                    'form': AddToBasketForm,
                    'error_label': 'You have selected too much of this product',  # text to assign to error label
                }
                return render(request, 'crafty_devil/product.html', context)

            # calculates line total and order total
            line_total = p.price * quantity
            order.total += line_total

            # create new orderline
            new_ol = OrderLine(product=p,
                               quantity=quantity,
                               line_total=line_total,
                               order_id=order.id)

            # check if this product already has an orderline with this order id, and if so, combine quantity and line
            # total in a new orderline, and then overwrite the existing orderline with updated info.
            if len(OrderLine.objects.filter(order_id=order.id, product=p)) > 0:
                existing_ol = OrderLine.objects.filter(order_id=order.id, product=p)[0]
                new_quantity = quantity + existing_ol.quantity
                new_total = new_quantity * p.price

                # overwrite existing orderline with new quantity
                OrderLine.objects.filter(order_id=order.id, product=p).update(quantity=new_quantity,
                                                                              line_total=new_total)
            else:
                new_ol.save()  # write orderline to database

            # deducts quantity from stock level
            Product.objects.filter(id=p.id).update(stock_level=p.stock_level - quantity)

            # recalculate basket total
            lines = get_orderlines(request, order)
            total = 0
            for orderline in lines:
                total += orderline.line_total

            # update order status to be in basket
            Order.objects.filter(id=order.id).update(total=total, status='in basket')

            return redirect('view basket')
    else:  # Anything other than a POST i.e. GET
        context = {
            'user': get_session_user(request),
            'staff': get_session_staff_user(request),
            'product': Product.objects.filter(id=product_id)[0],
            'form': AddToBasketForm,
        }
        return render(request, 'crafty_devil/product.html', context)


# returns page detailing basket contents
def view_basket(request, quantity_label='', ol_error_id=0):
    if not confirm_user_logged_in(request):  # if the user isn't logged in, send them to the login page
        return redirect('index')

    if request.method == 'POST':  # i.e. the user has clicked 'proceed to checkout'
        return redirect('checkout')
    else:  # i.e. http get
        context = {
            'user': get_session_user(request),
            'staff': get_session_staff_user(request),
            'open_order': get_basket(request)[0],
            'orderlines': get_basket(request)[1],
            'form': EditBasketForm,
            'quantity_label': quantity_label,
            'quantity_error_ol_id': ol_error_id,
        }
        return render(request, 'crafty_devil/user/basket.html', context)


# removes basket orderline
def delete_basket_line(request, orderline_id):
    if not confirm_user_logged_in(request):  # if the user isn't logged in, send to index (security measure)
        return redirect('index')

    # gets basket and basket orderlines
    basket, orderlines = get_basket(request)
    orderline = OrderLine.objects.filter(id=orderline_id)[0]

    # recalculate total
    total = basket.total - orderline.line_total

    # add quantity back to product stock level
    p = orderline.product
    Product.objects.filter(id=p.id).update(stock_level=p.stock_level + orderline.quantity)

    # updates basket and deletes orderline in database
    OrderLine.objects.filter(id=orderline_id).delete()
    Order.objects.filter(id=basket.id).update(total=total)

    return redirect('view basket')


# edits basket orderline quantity
def update_basket_orderline_quantity(request, orderline_id, quantity):
    if not confirm_user_logged_in(request):
        return redirect('index')

    # converts string arguments from URL into ints
    orderline_id = int(orderline_id)
    quantity = int(quantity)

    # updated line quantity and total
    orderline = OrderLine.objects.filter(id=orderline_id)[0]
    p = orderline.product  # p to avoid shadowing product() name
    new_total = p.price * quantity

    if quantity > p.stock_level:
        return view_basket(request, quantity_label='Quantity too high', ol_error_id=orderline_id)
    elif quantity <= 0:
        return view_basket(request, quantity_label='Quantity too low', ol_error_id=orderline_id)

    OrderLine.objects.filter(id=orderline_id).update(quantity=quantity, line_total=new_total)

    # update basket total
    basket, orderlines = get_basket(request)
    total = 0
    for orderline in orderlines:
        total += orderline.line_total

    Order.objects.filter(id=basket.id).update(total=total)

    return redirect('view basket')


# returns about page
def about(request):
    context = {
        'user': get_session_user(request),
        'staff': get_session_staff_user(request),
    }
    return render(request, 'crafty_devil/about.html', context)


# returns contact page
def contact(request):
    context = {
        'user': get_session_user(request),
        'staff': get_session_staff_user(request),
    }
    return render(request, 'crafty_devil/contact.html', context)


# handles a POST request from login form and attempts to log in the user.
# returns index page upon success, and the login page with modified context upon failure
# if GET request, returns login page with fresh form and context
def login(request, label='Login', user_type='customer'):
    context = {
        'form': LoginForm,
        'label': label,
        'user': get_session_user(request),
    }
    # if the user is a staff member, the label is changed to staff login, and the login() function searches the Staff
    # table, instead of the Customer table.
    if user_type == 'staff':
        context['label'] = 'Staff Login'
    if request.method == 'POST':  # i.e. user clicked 'login' button
        form = LoginForm(request.POST)
        if form.is_valid():
            form_email = form.cleaned_data.get('email')
            form_password = form.cleaned_data.get('password')

            try:  # try to find user with matching email
                if user_type == 'customer':
                    user = Customer.objects.filter(email=form_email)[0]

                    if user.password == form_password:  # if the matched user's password matches the entered one.
                        if get_session_staff_user(request) is not None:
                            request.session.delete('staff')
                        set_session_user(request, user)  # save user as the logged in user in the session.
                        return redirect('index')
                    else:
                        raise ValueError('Password Incorrect')
                elif user_type == 'staff':
                    user = Staff.objects.filter(email=form_email)[0]

                    if user.password == form_password:
                        request.session.delete('user')  # to prevent a user being staff and user at once
                        set_session_staff_user(request, user)
                        return staff_dashboard(request)
                    else:
                        raise ValueError('Password Incorrect')
            except (ValueError, IndexError):  # failed to log in
                context['label'] = 'Login Failed'
                return render(request, 'crafty_devil/user/login.html', context)
    else:  # Anything other than a POST i.e. GET
        return render(request, 'crafty_devil/user/login.html', context)


# deletes the current session user and returns the index page
def logout(request):
    request.session.delete('user')  # deletes user
    request.session.delete('staff')  # deletes staff user
    return redirect('index')  # returns home


# handles a POST request to create a new user in the database.
# returns login page with modified context upon success,
def signup(request, label=''):
    context = {
        'form': UserDetailsForm,
        'user': get_session_user(request),
        'staff': get_session_staff_user(request),
        'label': label,
    }
    if request.method == 'POST':
        form = UserDetailsForm(request.POST)
        if form.is_valid():
            # collecting data from form
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            password = form.cleaned_data.get('password')
            address_line1 = form.cleaned_data.get('address_line1')
            address_line2 = form.cleaned_data.get('address_line2')
            post_code = form.cleaned_data.get('post_code')
            email = form.cleaned_data.get('email')
            city = form.cleaned_data.get('city')
            telephone = form.cleaned_data.get('telephone')

            # validating fields have been entered properly
            validate_success = validate_user_details(form)
            if validate_success is not 'success':  # i.e. if the validation did not succeed
                context['label'] = validate_success
                return render(request, 'crafty_devil/user/signup.html', context)

            # creates customer object
            customer = Customer(firstname=firstname,
                                lastname=lastname,
                                password=password,
                                address_line1=address_line1,
                                address_line2=address_line2,
                                post_code=post_code,
                                email=email,
                                city=city,
                                telephone=telephone)

            # saves new customer to database
            customer.save()

            return redirect('login/signup-success')
    else:  # i.e. GET
        return render(request, 'crafty_devil/user/signup.html', context)


# page for user to view their details, orders and (?) invoices.
def view_account(request, page='info'):
    if not confirm_user_logged_in(request):
        return redirect('index')

    user = get_session_user(request)

    context = {
        'user': get_session_user(request),
        'staff': get_session_staff_user(request),
        'form': UserDetailsForm(initial=model_to_dict(user)),
        'edit': None,  # i.e. edit details has not occurred.
        'current_tab': page,
        'orders': Order.objects.filter(customer=user),
        'invoices': Order.objects.filter(customer=user, status='paid'),
    }

    if request.method == 'POST':  # i.e. user clicked 'Submit Changes' button
        form = UserDetailsForm(request.POST)
        confirmation_password = request.POST.get('confirm-password')
        if form.is_valid() and confirmation_password == user.password:  # if form data & password are correct.
            # collecting form data
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            password = form.cleaned_data.get('password')
            address_line1 = form.cleaned_data.get('address_line1')
            address_line2 = form.cleaned_data.get('address_line2')
            post_code = form.cleaned_data.get('post_code')
            email = form.cleaned_data.get('email')
            city = form.cleaned_data.get('city')

            # validating fields have been entered properly
            validate_success = validate_user_details(form)
            # i.e. if the validation did not succeed
            if validate_success != 'email-used':
                if validate_success != 'success':
                    context['label'] = validate_success
                    return render(request, 'crafty_devil/user/view_account.html', context)
            customers = Customer.objects.filter(email=email)
            for customer in customers:
                if customer.email == email and customer.id != user.id:
                    context['label'] = validate_success
                    return render(request, 'crafty_devil/user/view_account.html', context)

            # Overwrite db row
            Customer.objects.filter(id=user.id).update(firstname=firstname,
                                                       lastname=lastname,
                                                       password=password,
                                                       address_line1=address_line1,
                                                       address_line2=address_line2,
                                                       post_code=post_code,
                                                       email=email,
                                                       city=city)

            # overwrites current session user with new data
            new_user = Customer.objects.filter(id=user.id).first()
            set_session_user(request, new_user)

            # fills form initial data with new user data
            form = UserDetailsForm(initial=model_to_dict(new_user))
            context = {
                'user': get_session_user(request),
                'form': form,
                'edit': True,  # i.e. edit details was successful
                'current_tab': page,
                'label': 'succcess',
            }
            return render(request, 'crafty_devil/user/view_account.html', context)
        else:  # if the form data was invalid, or the confirmation password was invalid
            context = {
                'user': get_session_user(request),
                'staff': get_session_staff_user(request),
                'form': UserDetailsForm(initial=model_to_dict(user)),
                'edit': False,  # i.e. edit details was not successful
                'current_tab': page,
            }
            return render(request, 'crafty_devil/user/view_account.html', context)
    else:  # i.e. if GET
        return render(request, 'crafty_devil/user/view_account.html', context)


def view_order(request, order_id):
    if not confirm_user_logged_in(request):  # if user isn't logged in, return to index
        if get_session_staff_user(request) is None:
            return redirect('index')

    # gets relevant order and its orderlines
    order = Order.objects.filter(id=order_id)[0]
    orderlines = get_orderlines(request, order)

    context = {
        'user': get_session_user(request),
        'staff': get_session_staff_user(request),
        'order': order,
        'orderlines': orderlines,
    }
    return render(request, 'crafty_devil/user/view_order.html', context)


def checkout(request):
    if len(get_basket(request)[1]) <= 0:  # if the basket is empty, return to the basket page
        return redirect('view basket')

    # gets basket
    order = get_basket(request)[0]

    # dictionary of information the paypal api needs to process the payment, which is passed to the paypal form
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': order.total,
        'item_name': 'Order %d' % order.id,
        'invoice': str(order.id),
        'currency_code': 'GBP',
        'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
        'return_url': request.build_absolute_uri(reverse('confirm order')),
        'cancel_url': request.build_absolute_uri(reverse('view basket'))
    }
    # creates paypal and credit card forms
    paypal_form = PayPalPaymentsForm(initial=paypal_dict)
    cc_form = CustomerCardForm()

    if request.method == 'POST':
        form = CustomerCardForm(request.POST)
        if form.is_valid():
            cardholder_name = form.cleaned_data.get('cardholder_name')
            card_number = form.cleaned_data.get('card_number')
            expiry_date = form.cleaned_data.get('expiry_date')
            security_number = form.cleaned_data.get('security_number')

            if validate_card_details(form) == 'success':
                form_data = {
                    'cardholder_name': cardholder_name,
                    'card_number': card_number,
                    'expiry_date': expiry_date,
                    'security_number': security_number,
                }
                return confirm_order(request, form_data)
        # will execute if the server encounters a ValueError, which will occur if any of the data is invalid
            else:
                context = {
                    'user': get_session_user(request),
                    'label': 'transaction failed',
                    'paypal_form': paypal_form,
                    'card_form': cc_form,
                }
                return render(request, 'crafty_devil/checkout.html', context)
    else:
        context = {
            'user': get_session_user(request),
            'staff': get_session_staff_user(request),
            'paypal_form': paypal_form,
            'card_form': cc_form,
        }
        return render(request, 'crafty_devil/checkout.html', context)


# user must not be able to reach this without going about it properly!
def confirm_order(request, form_data=None):
    # gets basket, orderlines and logged in user
    basket, orderlines = get_basket(request)
    user = get_session_user(request)

    # checks there is a logged in user
    if user is None:
        return redirect('index')
    # checks that the order belongs to the logged in user
    if user != Order.objects.filter(id=basket.id)[0].customer:
        return redirect('index')

    if form_data is None:
        # this acts as a default argument, since it isn't advised to have mutable default parameters
        form_data = {'paypal': True}
    else:
        form_data['paypal'] = False

    # creates fresh payment order in case control flow fails
    payment = Payment()

    # if paypal was not used
    if not form_data['paypal']:
        cardholder_name = form_data['cardholder_name']
        card_number = form_data['card_number']
        expiry_date = form_data['expiry_date']
        security_number = form_data['security_number']

        # saves payment to database
        payment = Payment(cardholder_name=cardholder_name,
                          card_number=card_number,
                          expiry_date=expiry_date,
                          security_number=security_number,
                          paypal=False)
        payment.save()
    # paypal was used
    elif form_data['paypal']:
        # saves payment to database
        payment = Payment(paypal=True)
        payment.save()

    # update basket with payment, and change status to 'paid'
    Order.objects.filter(id=basket.id).update(payment=payment, status='paid')

    # return payment success page
    return redirect('payment-success/%d' % basket.id)


def payment_success(request, order_id):
    user = get_session_user(request)  # if user isn't logged in, send to login page
    if user is None:
        return redirect('index')

    # get relevant order and its orderlines
    order = Order.objects.filter(id=order_id)[0]
    orderlines = get_orderlines(request, order)

    # checks if the order has been placed already
    if order.status is 'paid':
        return redirect('index')

    # sends an email to the user confirming their order!
    order_confirmation_email(request, order, user)

    context = {
        'user': get_session_user(request),
        'staff': get_session_staff_user(request),
        'order': order,
        'orderlines': orderlines,
    }
    return render(request, 'crafty_devil/user/payment_success.html', context)


''' Extra non-core functions below

    Here are the functions which don't align with James' core functionalities.
'''


def staff_dashboard(request, page='customers'):
    # gets staff user and ensures they are signed in
    staff = get_session_staff_user(request)
    if staff is None:  # if there is no staff logged in, return to index
        return redirect('index')

    context = {
        'user': None,
        'staff': staff,
        'page': page,
    }

    # provides the correct context object depending on which page is selected
    if page == 'customers':
        context['customers'] = Customer.objects.all()
    elif page == 'orders':
        context['orders'] = Order.objects.all()
    elif page == 'suppliers':
        context['suppliers'] = Supplier.objects.all()
    elif page == 'products':
        context['products'] = Product.objects.all()
    elif page == 'low stock':
        context['low_stock'] = Product.objects.filter(stock_level__lte=100)  # stock level < 100

    return render(request, 'crafty_devil/staff/staff_dashboard.html', context)


def edit_customer(request, user_id):
    # gets staff and ensures they are signed in
    staff = get_session_staff_user(request)
    if staff is None:
        return redirect('index')

    # gets user object and converts their attributes into a dictionary to be used as initial data for the form
    user = Customer.objects.filter(id=user_id)[0]
    user_details = model_to_dict(user)

    context = {
        'user': user,
        'staff': staff,
        'form': UserDetailsForm(initial=user_details),
        'label': '',
    }

    if request.method == 'POST':
        form = UserDetailsForm(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            password = form.cleaned_data.get('password')
            address1 = form.cleaned_data.get('address_line1')
            address2 = form.cleaned_data.get('address_line2')
            postcode = form.cleaned_data.get('post_code')
            city = form.cleaned_data.get('city')
            email = form.cleaned_data.get('email')
            telephone = form.cleaned_data.get('telephone')

            user = Customer.objects.filter(id=user_id)[0]

            # validating fields have been entered properly
            validate_success = validate_user_details(form)
            if validate_success == 'success' or validate_success == 'email-used':
                if email == user.email:
                    Customer.objects.filter(id=user_id).update(firstname=firstname,
                                                               lastname=lastname,
                                                               password=password,
                                                               address_line1=address1,
                                                               address_line2=address2,
                                                               post_code=postcode,
                                                               city=city,
                                                               email=email,
                                                               telephone=telephone)

                    return staff_dashboard(request, page='customers')
                else:
                    context['label'] = validate_success
                    return render(request, 'crafty_devil/staff/edit_user.html', context)
            else:  # i.e. if the validation did not succeed
                context['label'] = validate_success
                return render(request, 'crafty_devil/staff/edit_user.html', context)
    else:
        return render(request, 'crafty_devil/staff/edit_user.html', context)


def delete_customer(request, user_id):
    if get_session_staff_user(request) is None:  # ensures staff is logged in
        return redirect('index')

    # removes row from customer table
    Customer.objects.filter(id=user_id).delete()
    return staff_dashboard(request, page='customers')


def delete_product(request, product_id):
    if get_session_staff_user(request) is None:  # ensures staff is logged in
        return redirect('index')

    # removes row from table
    Product.objects.filter(id=product_id).delete()
    return staff_dashboard(request, page='products')


def delete_supplier(request, supplier_id):
    if get_session_staff_user(request) is None:  # ensures staff is logged in
        return redirect('index')

    # removes row from database
    Supplier.objects.filter(id=supplier_id).delete()
    return staff_dashboard(request, page='suppliers')


def delete_order(request, order_id):
    if get_session_staff_user(request) is None:  # ensures staff is logged in
        return redirect('index')

    # removes row from database
    Order.objects.filter(id=order_id).delete()
    return staff_dashboard(request, page='orders')


def edit_product(request, product_id):
    # gets staff user and ensures they are logged in
    staff = get_session_staff_user(request)
    if staff is None:
        return redirect('index')

    # gets product object from product id
    p = Product.objects.filter(id=product_id)[0]

    # fills dictionary with data for the ProductDetailsForm to use
    product_details = model_to_dict(p)

    context = {
        'staff': staff,
        'label': '',
    }

    if request.method == 'POST':
        form = ProductDetailsForm(request.POST)
        if form.is_valid():
            desc = form.cleaned_data.get('desc')
            stock_level = form.cleaned_data.get('stock_level')
            price = form.cleaned_data.get('price')
            supplier_id = form.cleaned_data.get('supplier')

            # checks the given supplier id and if it doesn't exist, return an error label to the view
            try:
                supplier = Supplier.objects.filter(id=supplier_id)[0]
            except IndexError:
                context['form'] = ProductDetailsForm(initial=product_details)
                context['label'] = 'bad-id'
                return render(request, 'crafty_devil/staff/edit_product.html', context)

            # updates product with new data
            Product.objects.filter(id=product_id).update(desc=desc,
                                                         stock_level=stock_level,
                                                         price=price,
                                                         supplier=supplier)

            return staff_dashboard(request, page='products')
    else:
        context['form'] = ProductDetailsForm(initial=product_details)

        return render(request, 'crafty_devil/staff/edit_product.html', context)


def edit_supplier(request, supplier_id):
    # gets staff user and ensures they are logged in
    staff = get_session_staff_user(request)
    if staff is None:
        return redirect('index')

    # gets supplier object from id
    supplier = Supplier.objects.filter(id=supplier_id)[0]

    # fills dictionary with data for the SupplierDetailsForm to use
    supplier_details = model_to_dict(supplier)

    context = {
        'staff': staff,
        'form': SupplierDetailsForm(initial=supplier_details),
    }

    if request.method == 'POST':
        form = SupplierDetailsForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            address_1 = form.cleaned_data.get('address_1')
            address_2 = form.cleaned_data.get('address_2')
            post_code = form.cleaned_data.get('post_code')
            city = form.cleaned_data.get('city')

            # validating fields have been entered properly
            validate_success = validate_supplier_details(form)
            if validate_success is not 'success':  # i.e. if the validation did not succeed
                context['label'] = validate_success
                return render(request, 'crafty_devil/staff/edit_supplier.html', context)

            # updates supplier object with new data
            Supplier.objects.filter(id=supplier_id).update(name=name,
                                                           address_1=address_1,
                                                           address_2=address_2,
                                                           post_code=post_code,
                                                           city=city)

            return staff_dashboard(request, page='suppliers')
    else:
        return render(request, 'crafty_devil/staff/edit_supplier.html', context)


def add_product(request):
    if get_session_staff_user(request) is None:
        return redirect('index')

    context = {
        'staff': get_session_staff_user(request),
        'form': ProductDetailsForm,
    }

    if request.method == 'POST':
        form = ProductDetailsForm(request.POST)
        if form.is_valid():
            desc = form.cleaned_data.get('desc')
            stock_level = form.cleaned_data.get('stock_level')
            price = form.cleaned_data.get('price')
            supplier_id = form.cleaned_data.get('supplier')

            # checks the given supplier id and if it doesn't exist, return an error label to the view
            try:
                supplier = Supplier.objects.filter(id=supplier_id)[0]
            except IndexError:
                context['label'] = 'bad-id'
                return render(request, 'crafty_devil/staff/add_product.html', context)

            p = Product(desc=desc,
                        stock_level=stock_level,
                        price=price,
                        supplier=supplier)

            p.save()

            return staff_dashboard(request, page='products')
    else:
        return render(request, 'crafty_devil/staff/add_product.html', context)


def add_customer(request):
    if get_session_staff_user(request) is None:
        return redirect('index')

    context = {
        'staff': get_session_staff_user(request),
        'form': UserDetailsForm,
    }

    if request.method == 'POST':
        form = UserDetailsForm(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            address_1 = form.cleaned_data.get('address_line1')
            address_2 = form.cleaned_data.get('address_line2')
            post_code = form.cleaned_data.get('post_code')
            city = form.cleaned_data.get('city')
            telephone = form.cleaned_data.get('telephone')

            # validating fields have been entered properly
            validate_success = validate_user_details(form)
            if validate_success is not 'success':  # i.e. if the validation did not succeed
                context['label'] = validate_success
                return render(request, 'crafty_devil/staff/add_customer.html', context)

            customer = Customer(firstname=firstname,
                                lastname=lastname,
                                password=password,
                                email=email,
                                address_line1=address_1,
                                address_line2=address_2,
                                post_code=post_code,
                                city=city,
                                telephone=telephone)

            customer.save()

            return staff_dashboard(request, page='customers')
    else:
        return render(request, 'crafty_devil/staff/add_customer.html', context)


def add_supplier(request):
    if get_session_staff_user(request) is None:
        return redirect('index')

    context = {
        'staff': get_session_staff_user(request),
        'form': SupplierDetailsForm,
    }

    if request.method == 'POST':
        form = SupplierDetailsForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            address_1 = form.cleaned_data.get('address_1')
            address_2 = form.cleaned_data.get('address_2')
            post_code = form.cleaned_data.get('post_code')
            city = form.cleaned_data.get('city')
            telephone = form.cleaned_data.get('telephone')
            website = form.cleaned_data.get('website')

            # validating fields have been entered properly
            validate_success = validate_supplier_details(form)
            if validate_success is not 'success':  # i.e. if the validation did not succeed
                context['label'] = validate_success
                return render(request, 'crafty_devil/staff/add_supplier.html', context)

            supplier = Supplier(name=name,
                                address_1=address_1,
                                address_2=address_2,
                                post_code=post_code,
                                city=city,
                                telephone=telephone,
                                website=website)

            supplier.save()

            return staff_dashboard(request, page='suppliers')
    else:
        return render(request, 'crafty_devil/staff/add_supplier.html', context)


def cancel_order(request, order_id):
    if get_session_user(request) is None and get_session_staff_user(request) is None:
        return redirect('index')

    datethen = Order.objects.filter(id=order_id)[0].date
    dt = datetime.now().date() - datethen

    if dt.seconds < 86399:
        if get_session_user(request) == Order.objects.filter(id=order_id)[0].customer:
            Order.objects.filter(id=order_id).update(status='cancelled')
            return redirect('view account', page='orders')
    else:
        return view_account(request, page='orders')
