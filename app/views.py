from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from . models import *
import os
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
import razorpay
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



# Create your views here.

def login(req):
    if 'admin' in req.session:
        return redirect(admin_home)
    if 'username'in req.session:
        return redirect(index)
    else:
        if req.method=='POST':
            username=req.POST['username']
            password=req.POST['password']
            data=authenticate(username=username,password=password)
            if data:
                auth_login(req,data)
                if data.is_superuser:
                    req.session['admin']=username
                    return redirect(admin_home)
                else:
                    req.session['username']=username
                    return redirect(index)
            else:
                messages.warning(req, "username or password invalid.") 
            return redirect(login)
        else:
            return render(req,'login.html')
        
def logout(req):
    auth_logout(req)
    req.session.flush()
    return redirect(login)

def register(req):
    if req.method == 'POST':
        username = req.POST.get('username', '').strip()
        email = req.POST.get('Email', '').strip()  
        password = req.POST.get('password', '').strip()

        if not username or not email or not password:
            messages.error(req, "All fields (username, email, password) are required.")
            return redirect(register)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(req, "Please enter a valid email address.")
            return redirect(register)
        
        if len(password) < 6:
            messages.error(req, "Password must be at least 6 characters long.")
            return redirect(register)
        
        if User.objects.filter(email=email).exists():
            messages.warning(req, "A user with this email already exists.")
            return redirect(register)
        
        try:
            user = User.objects.create_user(
                first_name=username,
                username=email,
                email=email,
                password=password
            )
            user.save()

            send_mail(
                'Flipkart Account Created',
                'Your Flipkart account has been created successfully.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return redirect(login)
        except Exception as e:
            messages.error(req, "An error occurred during registration. Please try again.")
            return redirect(register)
    else:
        return render(req, 'register.html')

    


def fake_index(request):

    if 'username' in request.session:
        return redirect(index) 
    elif 'admin' in request.session:
        return redirect(admin_home)

    phones = Products.objects.filter(phone=True).prefetch_related('categorys_set')
    dress = Products.objects.filter(dress=True).prefetch_related('categorys_set')
    laptop = Products.objects.filter(laptop=True).prefetch_related('categorys_set')
    others = Products.objects.filter(others=True).prefetch_related('categorys_set')


    return render(request, 'fake_index.html', {'phones': phones,'dress': dress,'laptop': laptop,'others': others
    })


def fake_search(request):
    if request.method == 'POST':
        searched = request.POST.get('searched', '').strip()  
        category = request.POST.get('category', '') 
        
        results = Products.objects.all()
        
        if searched:
            results = results.filter(name__icontains=searched)
        
        if category:
            category_filter = {f"{category}": True}
            results = results.filter(**category_filter)

        return render(request, 'fake_search.html', {'searched': searched, 'category': category, 'results': results})
    
    return render(request, 'fakesearch.html', {'searched': '', 'category': '', 'results': []})

def fake_sec(request, id):
    product = Products.objects.get(id=id)
    category = Categorys.objects.filter(product=product)

    categories = Categorys.objects.filter(product=product)

    cart1 = None

    phones = Products.objects.filter(phone=True)
    dress = Products.objects.filter(dress=True)
    laptop = Products.objects.filter(laptop=True)
    others = Products.objects.filter(others=True)
    # category_id = request.session.get('cat')
    # category_data = Categorys.objects.filter(pk=category_id).first() if category_id else None

    category_id=request.session.get('cat')
    category_data = None

    f=0
    for i in category:
        if category_id:
            if i.pk==int(category_id):
                category_data = Categorys.objects.get(pk=category_id)
                f=1
    if f==0:
        category_data=None


    context = {
        'product': product,
        'categories': category,
        'is_phone': product.phone,
        'is_dress': product.dress,
        'is_laptop': product.laptop,
        'is_others': product.others,
        'cart1': cart1,
        'phones': phones,
        'dress': dress,
        'laptop': laptop,
        'others': others,
        'category_id':category_data,
    }

    return render(request, 'fake_sec.html', context)

def fake_demo(req,id):
    req.session['cat']=id
    category=Categorys.objects.get(pk=id)
    return redirect(fake_sec,id=category.product_id)

def fake_see_more(req, a=None):
    file_type = req.GET.get('type', a or 'default')

    if file_type == 'phone':
        files = Products.objects.filter(phone=True)
    elif file_type == 'dress':
        files = Products.objects.filter(dress=True)
    elif file_type == 'laptop':
        files = Products.objects.filter(laptop=True)
    elif file_type == 'others':
        files = Products.objects.filter(others=True)
    else:
        files = Products.objects.all()

    context = {'files': files, 'file_type': file_type}
    return render(req, 'fake_see_more.html', context)


# ----------------------------------admin------------------------------------------------------

def admin_home(req):
    categories = Categorys.objects.all()

    if 'admin' in req.session:
        phones = Products.objects.filter(phone=True)
        dress = Products.objects.filter(dress=True)
        laptop = Products.objects.filter(laptop=True)
        others = Products.objects.filter(others=True)

        # phone_categories = Categorys.objects.filter (phone_categories=True)
        # dress_categories = Categorys.objects.filter(dress_categories=True)
        # laptop_categories = Categorys.objects.filter(laptop_categories=True)
        # other_categories = Categorys.objects.filter (other_categories=True)

        context = {
            'categories': categories,
            'phones': phones,
            'dress': dress,
            'laptop': laptop,
            'others': others,
            # 'phone_categories': phone_categories,
            # 'dress_categories': dress_categories,
            # 'laptop_categories': laptop_categories,
            # 'other_categories': other_categories,
        }
        return render(req, 'admin/admin_home.html', context)
    else:
        return redirect(admin_home)
    

def search_admin(request):
    if request.method == 'POST':
        searched = request.POST.get('searched', '')  
        results = Products.objects.filter(name__icontains=searched) if searched else []
        return render(request, 'admin/search_admin.html', {'searched': searched, 'results': results})
    else:
        return render(request, 'admin/search_admin.html', {'searched': '', 'results': []})

def pro_details(req,id):

    product = Products.objects.get(id=id)
    category = Categorys.objects.filter(product=product)
    category_id=req.session.get('cat')



    product=Products.objects.get(pk=id)
    categories = Categorys.objects.filter(product=product)
    f=0
    for i in category:
        if category_id:
            if i.pk==int(category_id):
                category_data = Categorys.objects.get(pk=category_id)
                f=1
    if f==0:
        category_data=None

    context = {
        'product': product,
        'categories': categories,
        'is_phone': product.phone,
        'is_dress': product.dress,
        'is_laptop': product.laptop,
        'is_others': product.others,
   
        'category_id':category_data

    }
    
    return render(req,'admin/product_details.html',context)

def demo2(req,id):
    req.session['cat']=id
    category=Categorys.objects.get(pk=id)
    return redirect(pro_details,id=category.product_id)


def add_product(req):
    if req.method == 'POST':
        pro_id = req.POST['pro_id']
        name = req.POST['name']
      
        if 'img' in req.FILES:
            image = req.FILES['img']        
        description = req.POST.get('description', '')
        highlights = req.POST.get('highlights', '')
        
        phone = 'phone' in req.POST
        dress = 'dress' in req.POST
        laptop = 'laptop' in req.POST
        others = 'others' in req.POST

        data = Products.objects.create(P_id=pro_id,name=name,image=image,description=description
        ,highlights=highlights,phone=phone,dress=dress,laptop=laptop,others=others)
        print(req.FILES)
        print(req.POST)

        data.save()
        return redirect('category',id=data.id)
    return render(req, 'admin/add_product.html')

def category(req, id):
    product = Products.objects.get(pk=id)

    if req.method == 'POST':
        storage = req.POST['storage']
        color = req.POST['color']
        price = req.POST['price']
        offer_price = req.POST['o_price']
        size = req.POST['size']

        category = Categorys.objects.create(product=product,storage=storage,color=color,price=price,offer_price=offer_price,size=size)
        return redirect('category' , id=id)

    return render(req, 'admin/category.html', {'product': product})

def edit_product(req, id):
    data = Products.objects.get(pk=id)
    if req.method == 'POST':
        pro_id = req.POST['pro_id']
        name = req.POST['name']
        image = req.FILES.get('img')
        description = req.POST.get('description', '')
        highlights = req.POST.get('highlights', '')
        
        phone = 'phone' in req.POST
        dress = 'dress' in req.POST
        laptop = 'laptop' in req.POST
        others = 'others' in req.POST
        
        data.P_id = pro_id
        data.name = name
        data.description = description
        data.highlights = highlights
        data.phone = phone
        data.dress = dress
        data.laptop = laptop
        data.others = others
        
        if image:
            data.image = image
        data.save()
        
        return redirect('edit_category', id=id)
    
    return render(req, 'admin/edit_product.html', {'data': data})


def edit_category(req, id):
    product = Products.objects.get(pk=id)
    categories = Categorys.objects.filter(product=product)

    if req.method == 'POST':
        storage = req.POST['storage']
        color = req.POST['color']
        price = req.POST['price']
        offer_price = req.POST['o_price']
        size = req.POST['size']
        category=req.POST['category']

        Categorys.objects.filter(pk=category).update(storage=storage,color=color,
            price=price,offer_price=offer_price,size=size
        )
        return redirect(admin_home)
    return render(req, 'admin/edit_category.html', {'product': product, 'categories': categories})

def del_category(req,category_id):
    # product = Products.objects.get(pk=id)
    categories = Categorys.objects.get(pk=req.session['cat'])
    categories.delete()
    return redirect(admin_home)

def delete_product(req,id):
    data=Products.objects.get(pk=id)
    url=data.image.url
    url=url.split('/')[-1]
    os.remove('media/'+url)
    data.delete()
    return redirect(admin_home)

def admin_bookings(req):
    user = User.objects.all()
    data = Buy.objects.select_related('address', 'category', 'user').all()[::-1] 
    category = Categorys.objects.select_related('product')
    total_profit = sum(item.price * item.quantity for item in data)
    
    return render(req, 'admin/admin_bookings.html', {
        'user': user,
        'data': data,
        'category': category,
        'total_profit':total_profit
    })

def cancel_order(req,id):
    data=Buy.objects.get(pk=id)
    data.delete()
    return redirect(admin_bookings)

def confirm_order(request, order_id):
    order = get_object_or_404(Buy, pk=order_id)
    
    if not order.is_confirmed:  # Avoid unnecessary updates
        order.is_confirmed = True
        order.save()

        # Email details
        subject = "Order Confirmation"
        message = f"Dear {order.user.first_name},\n\nYour order ({order.category.product.name}) has been confirmed. Thank you for shopping with us!\n\nBest regards,\nFlipkart Team"
        recipient_email = order.user.email  

        send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient_email],
                fail_silently=False,
            )

          

    return redirect("admin_booking")

def view_pro(req):
    categories = Categorys.objects.select_related('product').all()

    context = {
        'categories': categories,
    }

    return render(req, 'admin/view_all_pro.html', context)


def toggle_confirmation(request, order_id):
    order = Buy.objects.get(id=order_id)
    order.is_confirmed =True
    order.save()
    

    return redirect('admin_bookings')


# -----------------------------user-----------------------------------------------------

def index(request):
    phones = Products.objects.filter(phone=True).prefetch_related('categorys_set')
    dress = Products.objects.filter(dress=True).prefetch_related('categorys_set')
    laptop = Products.objects.filter(laptop=True).prefetch_related('categorys_set')
    others = Products.objects.filter(others=True).prefetch_related('categorys_set')


    return render(request, 'user/index.html', {'phones': phones,'dress': dress,'laptop': laptop,'others': others
    })


def search(request):
    if request.method == 'POST':
        searched = request.POST.get('searched', '').strip()  # Get the search term
        category = request.POST.get('category', '')  # Get the selected category (if any)
        
        # Filter products based on the search term and category
        results = Products.objects.all()
        
        if searched:
            results = results.filter(name__icontains=searched)
        
        if category:
            # Dynamically filter based on the category field
            category_filter = {f"{category}": True}
            results = results.filter(**category_filter)

        return render(request, 'user/search.html', {'searched': searched, 'category': category, 'results': results})
    
    # Render the empty search page for GET requests
    return render(request, 'user/search.html', {'searched': '', 'category': '', 'results': []})

def secpage(request, id):
    log_user = User.objects.get(username=request.session['username'])
    product = Products.objects.get(id=id)
    category = Categorys.objects.filter(product=product)

    categories = Categorys.objects.filter(product=product)

    cart1 = None

    phones = Products.objects.filter(phone=True)
    dress = Products.objects.filter(dress=True)
    laptop = Products.objects.filter(laptop=True)
    others = Products.objects.filter(others=True)
    # category_id = request.session.get('cat')
    # category_data = Categorys.objects.filter(pk=category_id).first() if category_id else None

    category_id=request.session.get('cat')
    category_data = None

    f=0
    for i in category:
        if category_id:
            if i.pk==int(category_id):
                category_data = Categorys.objects.get(pk=category_id)
                f=1
    if f==0:
        category_data=None


    context = {
        'product': product,
        'categories': category,
        'is_phone': product.phone,
        'is_dress': product.dress,
        'is_laptop': product.laptop,
        'is_others': product.others,
        'cart1': cart1,
        'phones': phones,
        'dress': dress,
        'laptop': laptop,
        'others': others,
        'category_id':category_data,
    }

    return render(request, 'user/secpage.html', context)


def buy_pro(req,id):
    user = User.objects.get(username=req.session['username'])
    category = Categorys.objects.get(pk=req.session['cat'])  


    return redirect(address_page)

def address_page(req,id):
    user = User.objects.get(username=req.session['username'])
    category = Categorys.objects.get(pk=req.session['cat']) 
     
    quantity = req.GET.get('quantity', 1)  

    addresses = Address.objects.filter(user=user)


    if req.method == 'POST':
        name = req.POST.get('name')
        address = req.POST.get('address')
        phone_number = req.POST.get('phone_number')

        user_address = Address(user=user, name=name, address=address, phone_number=phone_number)
        user_address.save()

        # data = Buy.objects.create(user=user, category=category, price=category.price,address=user_address,   quantity=quantity,)
        # data.save()

        return redirect(order_payment) 

    return render(req, 'user/address.html', {
        'category': category,
        'quantity':quantity,
        'addresses': addresses,
       
    })

def select_address(req, id):
    address = get_object_or_404(Address, id=id)
    
    category = Categorys.objects.get(pk=req.session['cat']) 
    
    quantity = req.GET.get('quantity', 1)
    
    user = User.objects.get(username=req.session['username'])
    
 
    
    return redirect('order_payment') 

def delete_address(req, id):
    address = get_object_or_404(Address, id=id)  
    address.delete()
    return redirect(address_page, id=id)

def pay(req):
    user = User.objects.get(username=req.session['username'])
    category = Categorys.objects.get(pk=req.session['cat']) 
    quantity = req.GET.get('quantity', 1)  
    order=Order.objects.get(pk=req.session['order_id'])
    print(user)
   
    if req.method == 'GET':
        user_address = Address.objects.filter(user=user)[::-1][:1]


        data=Buy.objects.create(user=user, 
        category=category,
         price=category.price,
         address=user_address[0],
         quantity=quantity,
         order=order
    )
        data.save()
        print(data)

        return redirect(view_bookings)  

 

    return render(req, 'user/user_bookings.html')


def order_payment(req):
    if 'username' in req.session:
        user = User.objects.get(username=req.session['username'])
        category = Categorys.objects.get(pk=req.session['cat'])
        amount = category.offer_price

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": int(amount) * 100, 
            "currency": "INR",
            "payment_capture": "1"
        })
        order_id=razorpay_order['id']
        order = Order.objects.create(
            user=user,
            price=amount,
            provider_order_id=order_id
        )
        order.save()
        req.session['order_id']=order.pk

        return render(req, "user/address.html", {
            "callback_url": "http://127.0.0.1:8000/callback/",
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "order": order,
        })
    else:
        return redirect('login') 


@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)
    print(request.POST)
    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")

        # Update Buy model with payment details
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        print('hello')
     
        if not verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
            order.save()
            return redirect("pay") 
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            return redirect("pay")

    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id =json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(provider_order_id=provider_order_id)
        # order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()

        return redirect('pay')





def cart_buy(req, id):
    cart = Cart.objects.get(pk=id)
    category = Categorys.objects.select_related('product').filter(id=cart.category_id).first()
    if not category:
        return redirect('error_page') 
    total_price = category.offer_price * cart.quantity

   
    return redirect(view_bookings)





def cart_display(req):
    user = User.objects.get(username=req.session['username'])
    data = Cart.objects.filter(user=user)[::-1]
    category = Categorys.objects.select_related('product')

    cart_items = []
    grand_total_price = 0  
    grand_dis_price = 0    

    for item in data:
        product_price = item.category.offer_price
        total_price = product_price * item.quantity
        grand_total_price += total_price

        dis_price = item.category.price
        total_dis_price = dis_price * item.quantity
        grand_dis_price += total_dis_price

        cart_items.append({
            'cart_obj': item,
            'total_price': total_price,
            'total_dis_price': total_dis_price
        })

    total_discount = grand_dis_price - grand_total_price

    context = {
        'data': data,
        'categories': category,
        'cart_items': cart_items,
        'total_price': grand_total_price,
        'total_discount': total_discount,
        'price_without_discount': grand_dis_price,  
    }
    return render(req, 'user/cart.html', context)

def cart_address(req, id=None):
    user = User.objects.get(username=req.session['username'])
    addresses = Address.objects.filter(user=user)


    if id:
        cart_items = [get_object_or_404(Cart, pk=id)]
    else:
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return redirect('cart_display')  

    if req.method == 'POST':
        user_address, created = Address.objects.get_or_create(
            user=user,
            name=req.POST.get('name'),
            address=req.POST.get('address'),
            phone_number=req.POST.get('phone_number')
        )

        total_price = 0
        for cart in cart_items:
            category = cart.category
            quantity = cart.quantity
            price = category.offer_price * quantity
            total_price += price

            # Buy.objects.create(
            #     user=user,
            #     category=category,
            #     price=price,
            #     quantity=quantity,
            #     address=user_address
            # )

            # cart.delete()  



        return redirect(order_payment2)  

    return render(req, 'user/cart_address.html', {'cart_items': cart_items,'addresses':addresses})


def select_cart_address(req, id):
    address = get_object_or_404(Address, id=id)
    
    category = Categorys.objects.get(pk=req.session['cat']) 
    
    # quantity = req.GET.get('quantity', 1)
    
    user = User.objects.get(username=req.session['username'])
    
    return redirect('order_payment2') 

def delete_cart_address(req, id):
    address = get_object_or_404(Address, id=id)  
    address.delete()
    return redirect(cart_address)


def checkout_all(req):
    user = User.objects.get(username=req.session['username'])
    order=Order.objects.get(pk=req.session['order_id'])
    cart_items = Cart.objects.filter(user=user)
    print(cart_items)
    print(user)
    if not cart_items.exists():
        return render(req, 'user/cart.html', {"error": "Your cart is empty."})
    
    if req.method == 'GET':
        user_address = Address.objects.filter(user=user)[::-1][:1]
        
        total_price = 0
        for cart in cart_items:
            category = cart.category
            quantity = cart.quantity
            price = category.offer_price * quantity
            total_price += price

            # Save the purchase
            Buy.objects.create(
                user=user,
                category=category,
                price=price,
                quantity=quantity,
                address=user_address[0],
                order=order
            )

            cart.delete() 

        return redirect(view_bookings)  

    total_price = sum(item.category.offer_price * item.quantity for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }

    return render(req, 'user/user_bookings.html', context)

 

def order_payment2(req):
    if 'username' in req.session:
        user = User.objects.get(username=req.session['username'])
        cart_items=Cart.objects.filter(user=user)


        amount = 0
        for cart in cart_items:
            category = cart.category
            quantity = cart.quantity
            price = category.offer_price * quantity
            amount += price

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": int(amount) * 100, 
            "currency": "INR",
            "payment_capture": "1"
        })
        order_id=razorpay_order['id']
        order = Order.objects.create(
            user=user,
            price=amount,
            provider_order_id=order_id
        )
        order.save()
        print(order.pk)
        req.session['order_id']=order.pk
        return render(req, "user/cart_address.html", {
            "callback_url": "http://127.0.0.1:8000/callback2/",
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "order": order,
        })
    else:
        return redirect('login') 

@csrf_exempt
def callback2(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")

        # Update Buy model with payment details
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()

        if not verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
            order.save()
            return redirect("checkout_all") 
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            return redirect("checkout_all")

    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id =json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(provider_order_id=provider_order_id)
        # order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()

        return redirect("checkout_all")

def demo(req,id):
    req.session['cat']=id
    category=Categorys.objects.get(pk=id)
    return redirect('sec',id=category.product_id)

# def demo1(req,id):
#     req.session['cat']=id
#     category=Categorys.objects.get(pk=id)
#     return redirect('cart_disp',id=category.product_id)


def cart_single_address(req, id):
    user = User.objects.get(username=req.session['username'])

    cart_items = [get_object_or_404(Cart, pk=id)]
    addresses = Address.objects.filter(user=user)

    if req.method == 'POST':
        user_address, created = Address.objects.get_or_create(
            user=user,
            name=req.POST.get('name'),
            address=req.POST.get('address'),
            phone_number=req.POST.get('phone_number')
            
        )
        req.session['cart_id']=id

        return redirect('order_payment3',id=id)  

    return render(req, 'user/cart_single_address.html', {'cart_items': cart_items,'addresses':addresses})

def single_buy(req, id):
    user = User.objects.get(username=req.session['username'])
    order = Order.objects.get(pk=req.session['order_id'])
    cart_item = Cart.objects.get(pk=req.session['cart_id'])  

    if req.method == 'GET': 
        user_address = Address.objects.filter(user=user).last() 
        
        if not user_address:
            return redirect('address_page')

        amount = cart_item.category.offer_price * cart_item.quantity    

        Buy.objects.create(
            user=user,
            category=cart_item.category,  
            price=cart_item.category.offer_price,
            quantity=cart_item.quantity,
            address=user_address,
            order=order
        )
        
        print(f"Deleting cart item: {cart_item.id}")
        cart_item.delete()



        return redirect(view_bookings)  

    total_price = cart_item.category.offer_price * cart_item.quantity
    
    context = {
        'cart_item': cart_item, 
        'total_price': total_price,
    }

    return render(req, 'user/user_bookings.html', context)


def cart_single_address(req, id):
    user = get_object_or_404(User, username=req.session.get('username'))
    cart = get_object_or_404(Cart, id=id, user=user)  # Get the specific cart
    addresses = Address.objects.filter(user=user)

    if req.method == 'POST':
        user_address, created = Address.objects.get_or_create(
            user=user,
            name=req.POST.get('name'),
            address=req.POST.get('address'),
            phone_number=req.POST.get('phone_number')
        )
        req.session['cart_id'] = id

        return redirect('order_payment3', id=id)

    return render(req, 'user/cart_single_address.html', {'cart': cart, 'addresses': addresses})




def delete_single_address(req, id):
    address = get_object_or_404(Address, id=id)
    address.delete()
    
    cart_id = req.session.get('cart_id')
    if cart_id:
        return redirect('cart_single_address', id=cart_id)  
    
    return redirect('cart_address')  

def select_single_address(req, cart_id, address_id):
    user = get_object_or_404(User, username=req.session.get('username'))
    cart = get_object_or_404(Cart, id=cart_id, user=user)
    address = get_object_or_404(Address, id=address_id, user=user)

    if req.method == 'POST':
        address_id = req.POST.get('address')  # Safely get the value

        if not address_id:  # If address_id is missing, show an error
            messages.error(req, "Please select an address.")
            return redirect('cart_single_address', id=cart_id)

        selected_address = Address.objects.get(user=user, pk=address_id)
        req.session['cart_id'] = cart.id
        req.session['address_id'] = selected_address.id

        return redirect('order_payment3', id=cart_id)

    return redirect('cart_single_address', id=cart_id)



def order_payment3(req, id):
    if 'username' in req.session:
        user = User.objects.get(username=req.session['username'])
        cart_item = Cart.objects.get(pk=req.session.get('cart_id'))

        print(f"Cart Item ID: {cart_item.id}")  
        print(f"Cart Item Product ID: {cart_item.category.product.id}") 
        print(f"Cart Item Quantity: {cart_item.quantity}")  

        amount = cart_item.category.offer_price * cart_item.quantity
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": int(amount) * 100, 
            "currency": "INR",
            "payment_capture": "1"
        })
        order_id = razorpay_order['id']
        order = Order.objects.create(
            user=user,
            price=amount,
            provider_order_id=order_id,
        )
        order.save()

        print(f"Order ID: {order.pk}")  
        req.session['order_id'] = order.pk

        return render(req, "user/cart_single_address.html", {
            "callback_url": "http://127.0.0.1:8000/callback3/",
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "order": order,
        })
    else:
        return redirect('login')


@csrf_exempt
def callback3(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")

        # Update Buy model with payment details
        order = Order.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()

        if not verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
            order.save()
            print(order.pk)

            return redirect("single_buy",id=order.pk) 
        else:
            order.status = PaymentStatus.FAILURE
            order.save()        
            print(order.pk)

            return redirect("single_buy", id=order.pk)

    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id =json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(provider_order_id=provider_order_id)
        # order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()

        return redirect("single_buy", id=order.pk)


def add_to_cart(request, pid):
    log_user = User.objects.get(username=request.session['username'])
    # category_id =request.session['cat']=pid

    category = Categorys.objects.get(pk=request.session['cat'])  
    

    cart_item, created = Cart.objects.get_or_create(user=log_user,  category=category)
    
    if created:
        cart_item.quantity = 1
    elif cart_item.quantity < 5:
        cart_item.quantity += 1
    else:
         messages.warning(request, "Maximum quantity limit of 5 reached.")
    cart_item.save()
    return redirect(cart_display) 

def add_quantity(request, category_id):
    category = Categorys.objects.get( id=category_id)
    
    cart_item, created = Cart.objects.get_or_create(user=request.user, category=category)
    
    if cart_item.quantity < 5:
        cart_item.quantity += 1
        cart_item.save()
    else:
        messages.warning(request, "Maximum quantity limit of 5 reached.")
    
    return redirect(cart_display)

    
def remove_quantity(request, category_id):
    category = Categorys.objects.get( id=category_id)
    
    cart_item = Cart.objects.filter(user=request.user, category=category).first()
    
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            messages.warning(request, "Minimum quantity limit of 1 reached.")


    else:
            return redirect('cart_display')

    
    return redirect(cart_display)




def cart_delete(req,id):
    data=Cart.objects.get(pk=id)
    data.delete()
    return redirect(cart_display)

def delete_all(req):
    Cart.objects.filter(user=req.user).delete()
    req.session['cart_cleared'] = True
    return redirect(cart_display)




def view_bookings(req):
    user = User.objects.get(username=req.session['username'])
    
    data1 = Buy.objects.filter(user=user).select_related('category', 'category__product')[::-1]
    
    for booking in data1:
        price = booking.category.offer_price if booking.category.offer_price else booking.category.price
        booking.total_price = price * booking.quantity  

    context = {
        'data1': data1,
    }
    return render(req, 'user/user_bookings.html', context)





def user_orders(request):
    user = User.objects.get(username=request.session['username'])
    orders = Buy.objects.filter(user=user)
    for order in orders:
        print(f"Order ID: {order.id}, Is Confirmed: {order.is_confirmed}")
    
    
    return render(request, 'user/user_bookings.html', {'data1': orders})

def delete_order(req,id):
    data=Buy.objects.get(pk=id)
    data.delete()
    return redirect(view_bookings)


def see_more(req, a=None):
    file_type = req.GET.get('type', a or 'default')

    if file_type == 'phone':
        files = Products.objects.filter(phone=True)
    elif file_type == 'dress':
        files = Products.objects.filter(dress=True)
    elif file_type == 'laptop':
        files = Products.objects.filter(laptop=True)
    elif file_type == 'others':
        files = Products.objects.filter(others=True)
    else:
        files = Products.objects.all()

    context = {'files': files, 'file_type': file_type}
    return render(req, 'user/see_more.html', context)



def profile_view(request):
    user = request.user
    addresses = Address.objects.filter(user=user)  

    context = {
        'user': user,
        'addresses': addresses,
    }
    return render(request, 'user/profile.html', context)


def update_profile(request):
    if request.method == "POST":
        user = request.user
        first_name = request.POST.get("first_name")
        username = request.POST.get("username")

        try:
            validate_email(username) 
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return render(request, "user/update_profile.html")

        user.first_name = first_name
        user.username = username
        user.save()
        
        return redirect("profile_view")

    return render(request, "user/update_profile.html")

def edit_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)

    if request.method == "POST":
        address.name = request.POST.get('name')
        address.address = request.POST.get('address')
        address.phone_number = request.POST.get('phone_number')
        address.save()
        return redirect('profile_view')

    return render(request, 'user/edit_address.html', {'address': address})


def delete_profile_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    return redirect('profile_view')

def delete_account(request):
    user = request.user  
    user.delete()  
    logout(request)  
    return redirect('login')

def add_address(request):
    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        phone_number = request.POST.get("phone_number")

        Address.objects.create(user=request.user, name=name, address=address, phone_number=phone_number)

    return redirect("profile_view")







 #CONTACT US

def contact_view(request):
    message = ""
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        msg = request.POST.get('message')
        message = f"Thank you {name}, your message has been sent!"
        # Optional: Save to DB or send email
    return render(request, "user/contact.html", {"message": message})

# ABOUT US
# views.py
def about_view(request):
    return render(request, "user/about.html")


