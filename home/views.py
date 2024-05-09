from django.shortcuts import render,redirect,get_object_or_404
from .forms import RegistrationForm,ChangePasswordForm,UserProfileForm,AdminProfileForm,CustomerForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from django.views import View
from . models import Customer,Shoe,Order,Cart
from django.db.models import F

#===============For Paypal =========================
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse


# Create your views here.

def home(request):  # This check wheter user is login, if not it will redirect to login page
    return render(request,'index.html',{'name':request.user})    

def AboutUs(request):
    return render(request,'about.html')



def profile(request):
    if request.user.is_authenticated:  # This check wheter user is login, if not it will redirect to login page
        if request.method == 'POST':
            if request.user.is_superuser == True:
                mf = AdminProfileForm(request.POST,instance=request.user)
            else:
                mf = UserProfileForm(request.POST,instance=request.user)
            if mf.is_valid():
                mf.save()
        else:
            if request.user.is_superuser == True:
                mf = AdminProfileForm(instance=request.user)
            else:
                mf = UserProfileForm(instance=request.user)
        return render(request,'profile.html',{'name':request.user,'mf':mf})
    else:                                                # request.user returns the username
        return redirect('login')



def log_out(request):
    logout(request)
    return redirect('/login/')




def log_in(request):
    if not request.user.is_authenticated:  # check whether user is not login ,if so it will show login option
        if request.method == 'POST':       # otherwise it will redirect to the profile page 
            mf = AuthenticationForm(request,request.POST)
            if mf.is_valid():
                name = mf.cleaned_data['username']
                pas = mf.cleaned_data['password']
                user = authenticate(username=name, password=pas)
                if user is not None:
                    login(request,user)
                    return redirect('/profile/')
        else:
            mf = AuthenticationForm()
        return render(request,'login.html',{'mf':mf})
    else:
        return redirect('profile')




def sign_up(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            mf = RegistrationForm(request.POST)
            if mf.is_valid():
                mf.save()
                return redirect('signup')    
        else:
            mf  = RegistrationForm()
        return render(request,'Signup.html',{'mf':mf})
    else:
        return redirect('profile')



def changepassword(request):                                       # Password Change Form               
    if request.user.is_authenticated:                              # Include old password 
        if request.method == 'POST':                               
            mf =ChangePasswordForm(request.user,request.POST)
            if mf.is_valid():
                mf.save()
                update_session_auth_hash(request,mf.user)
                return redirect('profile')
        else:
            mf = ChangePasswordForm(request.user)
        return render(request,'changepassword.html',{'mf':mf})
    else:
        return redirect('login')


    

    


# ---------------------------------------------------------------------------------------
    

class MenCategoriesView(View):
    def get(self,request):
        if request.user.is_authenticated: 
            men_category = Shoe.objects.filter(category='MENS')  # we are using filter function of queryset, that will filter those data whose category belongs to dog
            return render(request,'mens.html',{'men_category':men_category,'name':request.user})
        else:
            return redirect('/login/')

class WomenCategoriesView(View):
    def get(self,request):
        if request.user.is_authenticated: 
            women_category = Shoe.objects.filter(category='WOMENS')  # we are using filter function of queryset, that will filter those data whose category belongs to dog
            return render(request,'womens.html',{'women_category':women_category})
        else:
            return redirect('/login/')
    

class ShoeDetailView(View):
    def get(self,request,id):     # id = It will fetch id of particular Shoe 
        shoe_detail = Shoe.objects.get(pk=id)

        #------ code for caculate percentage -----
        if shoe_detail.discounted_price !=0:    # fetch discount price of particular Shoe
            percentage = int(((shoe_detail.selling_price-shoe_detail.discounted_price)/shoe_detail.selling_price)*100)
        else:
            percentage = 0
        # ------ code end for caculate percentage ---------
            
        return render(request,'shoe_details.html',{'pd':shoe_detail,'percentage':percentage})
    


# ------------------------------------------------------------------------------------------------------------------



def add_to_cart(request, id):    # This 'id' is coming from 'Shoe.id' which hold the id of current Shoe , which is passing through {% url 'addtocart' Shoe.id %} from Shoe_detail.html 
    if request.user.is_authenticated:
        product = Shoe.objects.get(pk=id) # product variable is holding data of current object which is passed through 'id' from parameter
        user=request.user                # user variable store the current user i.e steveroger
        Cart(user=user,product=product).save()  # In cart model current user i.e steveroger will save in user variable and current Shoe object will be save in product variable
        return redirect('shoedetails', id)       # finally it will redirect to Shoe_details.html with current object 'id' to display Shoe after adding to the cart
    else:
        return redirect('login')                # If user is not login it will redirect to login page



def view_cart(request):
        cart_items = Cart.objects.filter(user=request.user)      # cart_items will fetch product of current user, and show product available in the cart of the current user.
        total =0
        delivery_charge =100
        for item in cart_items:
            item.product.price_and_quantity_total = item.product.discounted_price * item.quantity
            total += item.product.price_and_quantity_total
        final_price= delivery_charge + total
        return render(request, 'view_cart.html', {'cart_items': cart_items,'total':total,'final_price':final_price})
        

def add_quantity(request, id):
    product = get_object_or_404(Cart, pk=id)    # If the object is found, it returns the object. If not, it raises an HTTP 404 exception (Http404).
    product.quantity += 1                       # If object found it will be add 1 quantity to the current object   
    product.save()
    return redirect('viewcart')

def delete_quantity(request, id):
    product = get_object_or_404(Cart, pk=id)
    if product.quantity > 1:
        product.quantity -= 1
        product.save()
    return redirect('viewcart')

def delete_cart(request,id):
    if request.method == 'POST':
        de = Cart.objects.get(pk=id)
        de.delete()
    return redirect('viewcart')




#===================================== Address ============================================

def address(request):
    if request.method == 'POST':
            print(request.user)
            mf =CustomerForm(request.POST)
            print('mf',mf)
            if mf.is_valid():
                user=request.user                # user variable store the current user i.e steveroger
                name= mf.cleaned_data['name']
                address= mf.cleaned_data['address']
                city= mf.cleaned_data['city']
                state= mf.cleaned_data['state']
                pincode= mf.cleaned_data['pincode']
                print(state)
                print(city)
                print(name)
                Customer(user=user,name=name,address=address,city=city,state=state,pincode=pincode).save()
                return redirect('address')           
    else:
        mf =CustomerForm()
        address = Customer.objects.filter(user=request.user)
    return render(request,'address.html',{'mf':mf,'address':address})


def delete_address(request,id):
    if request.method == 'POST':
        de = Customer.objects.get(pk=id)
        de.delete()
    return redirect('address')

#===================================== Checkout ============================================

def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)      # cart_items will fetch product of current user, and show product available in the cart of the current user.
    total =0
    delivery_charge =100
    for item in cart_items:
        item.product.price_and_quantity_total = item.product.discounted_price * item.quantity
        total += item.product.price_and_quantity_total
    final_price= delivery_charge + total
    
    address = Customer.objects.filter(user=request.user)
    return render(request,'checkout.html', {'cart_items': cart_items,'total':total,'final_price':final_price,'address':address})

#===================================== Payment ============================================

def payment(request):

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')

    host = request.get_host()   # Will fecth the domain site is currently hosted on.

    cart_items = Cart.objects.filter(user=request.user)      # cart_items will fetch product of current user, and show product available in the cart of the current user.
    total =0
    delivery_charge =100
    for item in cart_items:
        item.product.price_and_quantity_total = item.product.discounted_price * item.quantity
        total += item.product.price_and_quantity_total
    final_price= delivery_charge + total
    
    address = Customer.objects.filter(user=request.user)
    # PAYPAL  CODE
    host = request.get_host()

    paypal_checkout = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,   #This is typically the email address associated with the PayPal account that will receive the payment.
        'amount': final_price,    #: The amount of money to be charged for the transaction. 
        'item_name': 'Shoe',       # Describes the item being purchased.
        'invoice': uuid.uuid4(),  #A unique identifier for the invoice. It uses uuid.uuid4() to generate a random UUID.
        'currency_code': 'USD',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",         #The URL where PayPal will send Instant Payment Notifications (IPN) to notify the merchant about payment-related events
        'return_url': f"http://{host}{reverse('paymentsuccess', args=[selected_address_id])}",     #The URL where the customer will be redirected after a successful payment. 
        'cancel_url': f"http://{host}{reverse('paymentfailed')}",      #The URL where the customer will be redirected if they choose to cancel the payment. 
        }
    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
    return render(request, 'payment.html', {'cart_items': cart_items,'total':total,'final_price':final_price,'address':address,'paypal':paypal_payment})
#===================================== Payment Success ============================================

def payment_success(request,selected_address_id):
    print('payment sucess',selected_address_id)   # we have fetch this id from return_url': f"http://{host}{reverse('paymentsuccess', args=[selected_address_id])}
                                                  # This id contain address detail of particular customer
    user =request.user
    customer_data = Customer.objects.get(pk=selected_address_id,)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        Order(user=user,customer=customer_data,Shoe=c.product,quantity=c.quantity).save()
        c.delete()
    return render(request,'payment_success.html')


#===================================== Payment Failed ============================================


def payment_failed(request):
    return render(request,'payment_failed.html')

#===================================== Order ====================================================

def order(request):
    ord=Order.objects.filter(user=request.user)
    return render(request,'order.html',{'ord':ord})

#========================================== Buy Now ========================================================
def buynow(request,id):
    Shoes = Shoe.objects.get(pk=id)     # cart_items will fetch product of current user, and show product available in the cart of the current user.
    delivery_charge =100
    final_price= delivery_charge + Shoes.discounted_price
    
    address = Customer.objects.filter(user=request.user)

    return render(request, 'buynow.html', {'final_price':final_price,'address':address,'Shoe':Shoes})


def buynow_payment(request,id):

    if request.method == 'POST':
        selected_address_id = request.POST.get('buynow_selected_address')

    Shoes= Shoe.objects.get(pk=id)     # cart_items will fetch product of current user, and show product available in the cart of the current user.
    delivery_charge =100
    final_price= delivery_charge + Shoes.discounted_price
    
    address = Customer.objects.filter(user=request.user)
    #================= Paypal Code ======================================

    host = request.get_host()   # Will fecth the domain site is currently hosted on.

    paypal_checkout = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': final_price,
        'item_name': 'Shoe',
        'invoice': uuid.uuid4(),
        'currency_code': 'USD',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",
        'return_url': f"http://{host}{reverse('buynowpaymentsuccess', args=[selected_address_id,id])}",
        'cancel_url': f"http://{host}{reverse('paymentfailed')}",
    }

    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
    return render(request, 'payment.html', {'final_price':final_price,'address':address,'Shoe':Shoes,'paypal':paypal_payment})





def buynow_payment_success(request,selected_address_id,id):
    print('payment sucess',selected_address_id)   # we have fetch this id from return_url': f"http://{host}{reverse('paymentsuccess', args=[selected_address_id])}
                                                  # This id contain address detail of particular customer
    user =request.user
    customer_data = Customer.objects.get(pk=selected_address_id,)
    
    Shoes = Shoe.objects.get(pk=id)
    Order(user=user,customer=customer_data,Shoe=Shoes,quantity=1).save()
   
    return render(request,'buynow_payment_success.html')