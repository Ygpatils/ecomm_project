from django.shortcuts import render, HttpResponse
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import redirect
from ecomm_app.models import Cart, product,Order
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail
# Create your views here.
def about(request):
    return HttpResponse("<h1>This is about page</h1>")

def contact(request):
    return HttpResponse("<h1>This is contact page</h1>")

def edit(request,rid):
    print("id to be edited:",rid)
    return HttpResponse("id to be edited:"+rid)

def addition(request,x1,x2):
    s=int(x1)+int(x2)
    s1=str(s)
    return HttpResponse("Addition is:"+s1)

class SimpleView(View):
    def get(self,request):
        return HttpResponse("Hello from simple view")

def hello(request):
    context={}
    context['greet']="Good morning, We are learning DTL"
    context['x']=100
    context['y']=20
    context['l']=[10,20,30,40,50]
    context['products']=[
        {'id':1,'name':'samsung','cat':'mobile','prize':2000},
        {'id':2,'name':'jeans','cat':'clothes','prize':500},
        {'id':3,'name':'vivo','cat':'mobile','prize':1500}
        ]
    return render(request,'hello.html',context)

def home(request):
    #userid=request.user.id
    #print("id is loggedin user:",userid)
    #print("Result:",request.user.is_authenticated)
    context={}
    p=product.objects.filter(is_active=True)
    context['product']=p
    print(p)
    return render(request,'index.html')  

def product_details(request,pid):
    p=product.objects.filter(id=pid)
    context={}
    context['products']=p
    return render(request,'product_details.html',context)   

def register(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        if uname=="" or upass=="" or ucpass=="":
            context['errmsg']="field can not be empty"
            return render(request,'register.html',context)
        elif upass != ucpass:
            context['errmsg']="password and confirm password Didn't Match"
            return render(request,'register.html',context) 
        else:
            try:    
                u=User.objects.create(password=upass,username=uname,email=uname)
                u.set_password(upass)
                u.save()
                context['success']="User created successfully, Please Login"
                return render(request,'register.html',context)
                #return HttpResponse("User created successfully")
            except Exception:
                context['errmsg']="User already exist!!"
                return render(request,'register.html',context)
    else:    
        return render(request, 'register.html')      

def user_login(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        context={}
        if uname=="" or upass=="":
            context['errmsg']="field can not be empty"
            return render(request,'login.html',context)
        else:
            u=authenticate(username=uname,password=upass)
            #print(u)
            if u is not None:
                login(request,u)
                return redirect('/home')
            else:
                context['errmsg']="Invalid Username and Password"
                return render(request,'login.html',context)
            #print(uname,"--",upass)
            #return HttpResponse("Data is fetched")
    else:
        return render(request, 'login.html') 

def user_logout(request):
    logout(request)
    return redirect('/home')

def catfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=product.objects.filter(q1 & q2) 
    print(p) 
    context={}
    context['products']=p
    return render(request,'index.html',context)

def sort(request,sv):
    if sv=='0':
        col='price'
    else:
        col='-price'
    #p=product.objects.order_by(col)
    p=product.objects.filter(is_active=True).order_by(col) 
    context={}
    context['products']=p
    return render(request,'index.html',context)

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p
    return render(request,'index.html',context)
    #return HttpResponse("value fetched")

def addtocart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        #print(userid)
        #print(pid)
        u=User.objects.filter(id=userid)
        print(u[0])
        p=product.objects.filter(id=pid)
        print(p[0])
        q1=Q(uid=u[0])
        q2=Q(pid=p[0])
        c=Cart.objects.filter(q1 & q2)
        n=len(c)
        context={}
        context['products']=p
        if n == 1:
            context['msg']="Product already their in cart !!"
            return render(request,'product_details.html',context)
        else:
            c=Cart.objects.create(uid=u[0],pid=p[0])
            c.save()
            context['success']="Product Added Successfully to cart !!"
            return render(request,'product_details.html',context)
            #return HttpResponse("Product add to cart")
    else:
        return redirect('/login')
    
def viewcart(request):
    c=Cart.objects.filter(uid=request.user.id)
    #print(c)
    np=len(c)
    print(np)
    s=0
    for x in c:
        #print(x)
        #print(x.pid.price)
        s=s+ x.pid.price * x.qty
    print(s)    
    context={}
    context['n']=np
    context['total']=s
    context['data']=c
    return render(request, 'cart.html',context) 

def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')   

def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)
    print(c)
    print(c[0])
    print(c[0].qty)
    if qv == 1:
        t=c[0].qty + 1
        c.update(qty=t)
        pass
    else:
        if c[0].qty > 1:
            t=c[0].qty - 1
            c.update(qty=t)
    return redirect("/viewcart")

def placeorder(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid)
    #print(c)
    oid=random.randrange(1000,9999)
    print("order id:",oid)
    for x in c:
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()
    orders=Order.objects.filter(uid=request.user.id) 
    context={}
    context['data']=orders 
    np=len(orders)
    s=0
    for x in orders:
        s=s+ x.pid.price * x.qty
        context['total']=s
        context['n']=np
    #return HttpResponse("in placeorder page")
    return render(request,'placeorder.html',context)

def makepayment(request):
    uemail=request.user.username
    print(uemail)
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    np=len(orders)
    for x in orders:
        s = s + x.pid.price * x.qty
        oid=x.order_id
    client = razorpay.Client(auth=("rzp_test_bfIsr5dBlgaEpx", "HXpvFNnr0dMMVBGPf5RakMhV"))
    data = { "amount": s*100, "currency": "INR", "receipt": oid }
    payment = client.order.create(data=data)
    #print(payment)
    context={}
    context['data']=payment
    uemail=request.user.username
    print(uemail)
    context['uemail']=uemail
    #return HttpResponse("success")
    return render(request,'pay.html',context)

def sendusermail(request,uemail):
    #uemail=request.user.email
    #print(uemail)
    msg="order detail are..."
    send_mail(
        "Ecart-order placed successfully",
        msg,
        "yogeshghadage1602@gmail.com",
        [uemail],
        fail_silently=False,
    )

    return HttpResponse("send mail successfully")


