




from django.shortcuts import render,redirect
from django.core.paginator import Paginator, EmptyPage
#===above have imported the paginator
from django.contrib.auth import login as auth_login, authenticate,logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import random, math, requests,json
from django.http import JsonResponse
from django.urls import reverse

from rave_python import Rave,  Misc, RaveExceptions


from .forms import*

#====import requests for the ip====
from requests import get


from django.contrib.auth.hashers import check_password

from accounts.models import User
# Create your views here.
from .models import*




current_email = "bbosalj@gmail.com"

#====storing the current user====
current_user = None #we are gonna change this later in the global scope

admin_email="support@tukoreug.com" #this is the admin email now








# Create your views here.
#initially to return the index page


def index(request):
    if request.user.is_authenticated:
        if not request.user.now_admin:
            return redirect(reverse("main:dash"))
    return render(request, "main/index.html", {})



def dashboard(request):
    return render(request, "main/dashboard.html", {})

def plans(request):
    return render(request, "main/plans.html", {})

def signup(request):
    form = RegisterForm()
    return render(request, "main/profile.html", {"form":form})

#====actual login view====
def logintrue(request):
    if request.user.is_authenticated:
        return redirect(reverse("main:dash"))
        #u are supposed to pass in the variables
    if request.method == "POST":
        form  = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password']
            )
            if user is not None:
                if not user.is_blocked:
                    #handling case when the user was blocked
                    auth_login(request, user)
                    messages.success(request, "Login successful.")
                    return render(request, "main/dashboard.html", {
                        "obj":user
                    })
                else:
                    messages.error(request, "Blocked by admin contact admin to unblock")
                    return render(request, "main/blocked.html",{})
                    #==must display a template here
            else:
                messages.error(request, "Check Email or password")
                for error in list(form.errors.values()):
                    messages.error(request, error)
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    form = LoginForm()
    return render(request, "main/login.html",{"form":form})


#=====add  anew signup view
def signtrue(request):
    if request.user.is_authenticated:
      
            #since i dont want the user to register every time
            user = request.user
         
      

            #just redirect from here
            #return redirect("main:dash", pk=user.id)
            #pk=user.pk
            messages.success(request, "User  already Authenticated")
            return render(request, "main/dashboard.html", {
                "obj":user,"messages":messages
            })
    else:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            #====boolean field to mark profile done=====
            authed = True;
            if form.is_valid():
                username = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                user = User.objects.create_user(
                    username=username,email=email,password=password
                )
                user.save()
                #===filter to check if user exists===
                #if User.objects.filter(username=username).exists():
                #    messages.error(request, "User with username exists")
                #    return redirect(reverse("main:sign"))
                #if User.objects.filter(email=email).exists():
                #    messages.error(request, "User with email already exists")
                #    return redirect(reverse("main:sign"))
                auth_login(request, user)
                #====go ahead and change the registered variable
                authed = False#its now ==== True

                print('user created....')
                messages.success(request, "Registration successful.")
                #==first get the wallet model=====
           
            #now that we have the user model
          
                username = user.username

                #now increment he number of the users for the admin to see
                #stats_now = Stats.objects.create(
                #    balance=int(0),
                ##     deposits = int(0),
                #    widthdraws = int(0),
                #    nousers = int(0),
                #    no_active_users=int(0),profits = int(0)
                #)
                #stats_now.save()
                #since i dont need to create data for every new user but just update the first
                #===initiating the model but i have to increment the attributes later on
                return render(request, "main/dashboard.html", {
                    "obj":user,
                    "authed":authed, #since i need to use it in the side panel
                })
            messages.error(request, "Unsuccessful registration. User with username/email exists")
        form = RegisterForm()
        authed = True
        return render(request, "main/profile.html", {"register_form": form,"authed":authed})


def handle_silver(request):
    global min_amount
    if request.user.is_authenticated:
            user = request.user
            if user:
                user.account_type = "SILVER"
                request.session['min_amount'] = int(10000)
                #min_amount = int(20000)
                #====pass in #rgument====
                #ret_arg(user.get_deposit)
                #now since i have gone with flutterwave, am gonna just redirect it to the deposit url
                return redirect(reverse("main:deposit"))
            else:
                pass
    #==go ahead and pass in the deposit amount

#===anyway just go ahead for now with individual funcs
def handle_gold(request):
    global min_amount
    if request.user.is_authenticated:
        
            user = request.user
            if user:
                user.account_type = "GOLD"
                #=====set session from here======
                request.session['min_amount'] = int(20000)
                #min_amount = int(50000)
                return redirect(reverse("main:deposit"))
            return

def return_min_amount(request):
    min_amount = request.session.get('min_amount', int(20000))
    return min_amount


def process_payment(request,name,email):
    #auth_token = env('SECRET_KEY')
    #auth_token = 'FLWSECK_TEST-74b70b363bfa87c1292a61bdc95eb38b-X'
    auth_token = 'FLWSECK_TEST-3fa8b47793beba08a1782f41a812e4e5-X'
    #auth_token = 'FLWSECK_TEST-cd4589948d43624e7215b2b48b70c788-X'
    hed = {
        'Authorization':'Bearer ' + auth_token,
        'Content-Type':'application/json',
        'Accept': 'application/json'
    }
    phone='0706626855'

    #=====get the min_amo
    min_amount = return_min_amount(request)
    #===set the min_amount in the session


    #====chnage and use json.dumps====
    url = ' https://api.flutterwave.com/v3/payments'
    data = json.dumps({
        "tx_ref":''+str(math.floor(1000000 + random.random()*9000000)),
        "amount":min_amount,
        "currency":"UGX",
        "redirect_url":"https://www.tukoreug.com/callback",
        "payment_options":"mobilemoneyuganda,card",
        "meta":{
            "consumer_id":23,
            "consumer_mac":"92a3-912ba-1192a"
        },
        "customer":{
            "email":email,
            "phonenumber":phone,
            "name":name
        },
        "customizations":{
            "title":"Topwin.games",
            "description":"Your reliable betting tips",
            "logo":"https://getbootstrap.com/docs/4.0/assets/brand/bootstrap-solid.svg"
        },
        #"subaccounts": [
        #    {
        #        "id": env('SUB_ID'),
        #    }
        #],
    })
    #response = requests.post(url, json=data, headers=hed)
    #let turn and use this code instead===
    response = requests.request("POST",url, headers=hed,data=data)
    response = response.json()
    #response = response.text
    print(response, flush=True)
    link = response['data']['link']
    return link

#=========
#====since the callback doesnt provide for me the user am going to supply to this function
#==create a global dictionary



#===handling callback=====
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def handle_callback(request):
    #===the above is the response that is sent to the callback url
    #===checking the length of the dictionary containing the request objects

    #===just declare a variable amd manipulate that===
    #==declaring received
    success = False
    received  = False
    #===get the user from the global scope===
    user = current_user
    response_dict = json.loads(str(request.GET))#first converting the JSON object to python code
    #response_dict = json.loads(str(request.GET))#first converting the JSON object to python code
    print(user,response_dict, flush=True)
    if len(response_dict) == 0:
        #return template with the loader telling user to complete transaction==
        received = False
        #just redirect since transaction is not yet compete
        return render(request, "main/after.html",{"obj":user, "received":received, "success":success})
    
    else:
        user=current_user
      
        received = True
        #now that i have received a response go ahead and use the response
        print(request.GET)
        #now that i have the request, get the status and the amount
        status = request.GET.get('status', None)
        amount = request.GET.get('amount', None)
        #====now in the callback===
        print(status,amount)
        #===set variable to indicate transaction didnt complete
        if status == "successful":
            success = True
            user.paid = True
            user.save()#saving the paid
          
            return redirect(reverse("main:dash")) #since user is still the same user
           
        else:
            success = False
            messages.success(request, "Deposit was successful")
            #return redirect(reverse("main:dash")) #since user is still the same user
            #now actually u need to display the actual message sent because it failed

            return render(request, "main/after.html",{"obj":user, "received":received, "success":success})

    messages.error(request, "Transaction didnot complete")
    return redirect(reverse("main:dash")) #since user is still the same user

            


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def payment_response(request):
    status = request.GET.get('status', None)
    tx_ref = request.GET.get('tx_ref', None)
    print(request.GET, flush=True)
    print(status)
    print(tx_ref)

    #====delete the session regardless whether it was successful or cancelled===
    min_amount = return_min_amount(request)
    found = False

    current_user = request.user
    if current_user in User.objects.all().distinct():found = True 
    else:found = False 
    if status == "successful":
        messages.success(request, "Transaction successful")
        user = current_user
        user.paid = True
        user.save()
        return redirect(reverse("main:plans"))
    elif status == "cancelled":
        messages.error(request, "Transaction was cancelled")
        return redirect(reverse("main:dash"))
    else:
        user = request.user
    

        messages.error(request, "Deposit unsuccessful")
        #return redirect(reverse("main:dash"))
        return render(request, "main/dashboard.html", {
            "obj":user, 
        })
    #return HttpResponse('Finished')
    return redirect(reverse("main:dash"))


def store_details(email,amount):
    details = {"email":email, "amount":amount}
    return details

def deposit(request):
    global current_user
    user = request.user
    email = request.user.email

    username = request.user.username
    #==to modify the email you have to first specify the global keyname

    current_user = user
    #==since min_amount will bechanging so we will have
    return redirect(process_payment(request,username,email))