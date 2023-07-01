from django.shortcuts import render,redirect,get_object_or_404
from .models import Profile,Tweet
from django.contrib import messages
from .forms import TweetForm,SignUpForm,ProfilePicForm,UserUpdateForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
# Create your views here.
def home(request):
    if request.user.is_authenticated:
        form = TweetForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                tweet = form.save(commit=False)
                tweet.user = request.user
                tweet.save()
                messages.add_message(request,messages.SUCCESS, "Your tweet is posted!")
                return redirect('home')
        else:
            form = TweetForm()  # Initialize the form when the request method is not POST

        tweets = Tweet.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"tweets": tweets, "form": form})
    else:
        tweets = Tweet.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"tweets": tweets})
def profile_list(request):
    if request.user.is_authenticated:
        profiles=Profile.objects.exclude(user=request.user)
        return render(request,'profile_list.html',{'profiles':profiles})
    else:
        messages.add_message(request,messages.WARNING,("Red Flag!You must be logged in!"))
        return redirect('home')
    
def profile(request,pk):
    if request.user.is_authenticated:
        profile=Profile.objects.get(user_id=pk)
        tweets=Tweet.objects.filter(user_id=pk).order_by("-created_at")
        if request.method=='POST':
            current_user_profile=request.user.profile
            action=request.POST['follow']
            if action=="unfollow":
                current_user_profile.follows.remove(profile)
            elif action=="follow":
                current_user_profile.follows.add(profile)
            current_user_profile.save()
            
        return render(request,'profile.html',{"profile":profile,"tweets":tweets})
    else:
        messages.add_message(request,messages.WARNING,("Red Flag!You must be logged in!"))
        return redirect('home')
    
def followers(request,pk):
    if request.user.is_authenticated:
        if request.user.id==pk:
            profiles=Profile.objects.get(user_id=pk)
            return render(request,'followers.html',{'profiles':profiles})
        else:
            messages.add_message(request,messages.WARNING,("3-place Grid Penalty!That's not your profile!"))
            return redirect('home')
    else:
        messages.add_message(request,messages.WARNING,("Red Flag!You must be logged in!"))
        return redirect('home')
    
def follows(request,pk):
    if request.user.is_authenticated:
        if request.user.id==pk:
            profiles=Profile.objects.get(user_id=pk)
            return render(request,'follows.html',{'profiles':profiles})
        else:
            messages.add_message(request,messages.WARNING,("3-place Grid Penalty!That's not your profile!"))
            return redirect('home')
    else:
        messages.add_message(request,messages.WARNING,("Red Flag!You must be logged in!"))
        return redirect('home')
    
def login_user(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            messages.add_message(request,messages.SUCCESS,("Lights out and away we go!You have logged in!"))
            return redirect('home')
        else:
            messages.add_message(request,messages.WARNING,("Yellow flag!There was an error logging in.Please try again!"))
            return redirect('login')
    else:
        
        return render(request,'login.html',{})
    
    
def logout_user(request):
    logout(request)
    messages.add_message(request,messages.SUCCESS,("Chequered flag!Hope to see you at the next race!"))
    return redirect('home')

def register_user(request):
    form=SignUpForm()
    if request.method=="POST":
        form=SignUpForm(request.POST)
        if form.is_valid:
            form.save()
            username=form.cleaned_data['username']  
            password=form.cleaned_data['password1']
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            email=form.cleaned_data['email']
            #Log in user
            user=authenticate(username=username,password=password)
            login(request,user)
            messages.add_message(request,messages.SUCCESS,("Line up on the Grid!You have registered!"))
            return redirect('home')
    return render(request,'register.html',{"form":form})

def update_user(request):
    if request.user.is_authenticated:
        current_user = request.user
        profile_user = get_object_or_404(Profile, user=current_user)

        if request.method == 'POST':
            profile_form = ProfilePicForm(request.POST, request.FILES, instance=profile_user)
            user_form = UserUpdateForm(request.POST, instance=current_user)

            if profile_form.is_valid() and user_form.is_valid():
                profile_form.save()
                user_form.save()
                messages.success(request, "Line up on the Grid! Your profile has been updated!")
                return redirect('home')
        else:
            profile_form = ProfilePicForm(instance=profile_user)
            user_form = UserUpdateForm(instance=current_user)

        return render(request, 'update_user.html', {"user_form": user_form, "profile_form": profile_form})
    else:
        messages.warning(request, "Red Flag! You must be logged in!")
        return redirect('home')

def tweet_like(request,pk):
    if request.user.is_authenticated:
        tweet=get_object_or_404(Tweet,id=pk)
        if tweet.likes.filter(id=request.user.id):
            tweet.likes.remove(request.user)
        else:
            tweet.likes.add(request.user)
        return redirect(request.META.get('HTTP_REFERER'))
        
    else:
            messages.add_message(request,messages.WARNING,("Red Flag!You must be logged in!"))
            return redirect('home')
        
def tweet_show(request,pk):
    tweet = get_object_or_404(Tweet,id=pk)
    if tweet:
        return render(request,'tweet_show.html',{"tweet":tweet})
    else: 
        messages.add_message(request,messages.WARNING,("Yellow Flag!That tweet doesn't exist!"))
        return redirect('home')
    
    
def delete_tweet(request,pk):
    if request.user.is_authenticated:
        tweet=get_object_or_404(Tweet,id=pk)
        if request.user.username==tweet.user.username:
            tweet.delete()
            messages.add_message(request,messages.SUCCESS,("Your tweet is deleted!"))
            return redirect(request.META.get('HTTP_REFERER'))
        
        else:
            messages.add_message(request,messages.WARNING,("5-second penalty!That's not your tweet!"))
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.add_message(request,messages.WARNING,("Red flag!Log in to continue racing!"))
        return redirect(request.META.get('HTTP_REFERER'))
def edit_tweet(request,pk):
    if request.user.is_authenticated:
        tweet=get_object_or_404(Tweet,id=pk)
        if request.user.username==tweet.user.username:
            
            form = TweetForm(request.POST or None,instance=tweet)
            if request.method == "POST":
                if form.is_valid():
                    tweet = form.save(commit=False)
                    tweet.user = request.user
                    tweet.save()
                    messages.add_message(request,messages.SUCCESS, "Your tweet is updated!")
                    return redirect('home')
            else:
        
                return render(request,'edit_tweet.html',{"form":form,"tweet":tweet})
            
        
        else:
            messages.add_message(request,messages.WARNING,("5-second penalty!That's not your tweet!"))
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.add_message(request,messages.WARNING,("Red flag!Log in to continue racing!"))
        return redirect('home')
        
