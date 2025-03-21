from django.shortcuts import render,HttpResponse,redirect
from store.models import Product,Variation
from cart.models import Cart,CartItem
from django.core.paginator  import Paginator
from project2.forms import Registration
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


def Home(request):
    all_products= Product.objects.all()
    
    # print(len(all_products))
    context= {
        'all_products': all_products
    }
    return render(request,'home.html', context)

def Store(request):

    products= Product.objects.all()
    
    paginator = Paginator(products,6)

    try:
        page=request.GET['page']
    except:
        page=1
    
    all_product=paginator.get_page(page)

    # print(len(all_products))
    context= {
        'all_products': all_product
    }

    return render(request,'store/store.html',context)

def Category(request,x):
    
    all_products= Product.objects.filter(category__category_name=x)
    
    # print(len(all_products))
    context= {
        'all_products': all_products
    }

    return render(request,'store/store.html',context)

def ProductDetail(request,cat_name,product_id):
    product=Product.objects.get(id=product_id)
    color_variant=Variation.objects.filter(product=product,variation_category="color")
    size_variant=Variation.objects.filter(product=product,variation_category="size")
    context={
        'product':product,
        'colors':color_variant,
        'sizes':size_variant

    }
    return render(request,'store/product_detail.html',context)

def AddCart(request,product_id):
    product=Product.objects.get(id=product_id)
    cart=Cart.objects.get(cart_id='1234')


    if request.method =="POST":
        color=request.POST['color']
        size=request.POST['size']
        # print(color,size)

        size_variant=Variation.objects.get(variation_value=size,product=product)
        color_variant=Variation.objects.get(variation_value=color,product=product)
    
        current_variant= [color_variant,size_variant]

        is_product_exists= CartItem.objects.filter(product= product).exists()

        if is_product_exists:
          
          each_product_variants= []
          products=  CartItem.objects.filter(product= product)

          for product in products:
            each_product_variants.append(list(product.variations.all()))

          if  current_variant in each_product_variants:
            product_index=  each_product_variants.index(current_variant)
            product= products[product_index]
            product.quantity += 1
            product.save()


          else:
            product=Product.objects.get(id=product_id)
            cart_item=CartItem.objects.create(product=product,cart=cart,quantity=1)
            cart_item.variations.add(size_variant) 
            cart_item.variations.add(color_variant)  

            
        
        else:
          cart_item=CartItem.objects.create(product=product,cart=cart,quantity=1)
          cart_item.variations.add(size_variant) 
          cart_item.variations.add(color_variant) 
       



    # try:
    #     item=  CartItem.objects.get(cart=cart,product=product)
    #     item.quantity += 1
    #     item.save()
    
    # except:

    #     CartItem.objects.create(cart=cart,product=product,quantity=1,is_active=True)

    return redirect('/cart')

def RemoveCart(request,cart_id):
    print(cart_id)

    cart_item= CartItem.objects.get(id= cart_id)

    if cart_item.quantity>1:
        cart_item.quantity -= 1
        cart_item.save()

    else:
        cart_item.delete()

    return redirect('/cart')

def Carts(req):
    all_cart_item=CartItem.objects.filter(cart__cart_id='1234')
    total_price=0

    for cart_item in all_cart_item:
        total_price += cart_item.product.price * cart_item.quantity

    context={
        'all_cart_items':all_cart_item,
        'total' : total_price,
        'tax' : round(total_price*0.18,2),
        'grand_total':round(total_price+total_price*0.18)


        
    }

    return render(req,'store/cart.html',context)

def RemoveCartItem(request,product_id):

    cart_item=CartItem.objects.get(id=product_id)

    cart_item.delete()

    return redirect('/cart')


def Register(request):
   
   form=  Registration()

   if request.method == 'POST':
     form= Registration(request.POST)

     if form.is_valid():
        first_name= request.POST['first_name']
        last_name= request.POST['last_name']
        email= request.POST['email']
        password= request.POST['password']
        username= request.POST['username']
        user= User.objects.create_user(username=username,first_name= first_name,last_name= last_name,email= email,password=password,is_active= False)
        user.save()
        form= Registration() 

        domain_name= get_current_site(request)
        mail_subject= "Please activate account"
        userid_encode= urlsafe_base64_encode(force_bytes(user.pk))
        token= default_token_generator.make_token(user)
        message= f'http://{domain_name}/accounts/activate/{userid_encode}/{token}'
        to_email= email
       
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()



        messages.add_message(request,messages.SUCCESS,"Registration Success")
     else:
        messages.add_message(request,messages.ERROR,"Invalid info", extra_tags='danger')
   

    
    
   
   context= {
      "form":form
   }
   return render(request,'accounts/register.html',context)


def Activate(request,uid,token):
   
    try:
      pk= urlsafe_base64_decode(uid)
      user= User.objects.get(pk= pk)

      if default_token_generator.check_token(user,token):
         user.is_active= True
         user.save()
         messages.add_message(request,messages.SUCCESS,"Verification successful")
    except:
       messages.add_message(request,messages.ERROR,"Invalid credentials",extra_tags="danger")
   


    return redirect('/register')