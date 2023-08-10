from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Profile, Post, Like, Follower
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import uuid
from datetime import datetime
from .utils import is_valid_uuid
from itertools import chain
import random

# Create your views here.

@login_required(login_url= '/signin')   
def index(request):
    profile = Profile.objects.get(user=request.user)
    followings = Follower.objects.filter(follower=request.user.username)
    posts = []
    for following in followings:
        user_obj = User.objects.get(username=following.user)
        posts.append(list(Post.objects.filter(user=user_obj)))
    posts = list(chain(*posts))
    # Users that can be followed
    all_users = User.objects.all().exclude(username = request.user.username)
    suggestions = []

    for user in all_users:
        username = user.username
        follower_filter = Follower.objects.filter(follower= request.user.username , user= username)
        # if user hasen't been followed
        if not follower_filter.exists():
            suggested_user_profile = Profile.objects.filter(user=user).first()
            suggestions.append(suggested_user_profile)
    
    random.shuffle(suggestions)

    context = {
        'profile' : profile,
        'posts' : posts,
        'suggestions' : suggestions[:5]
    }
    print(f'''\n\n\n{suggestions}\n\n\n''')
    return render(request, 'index.html', context=context)

def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        agree_terms = request.POST.get('agree-terms')
        if password == password2:
            if User.objects.filter(username= username):
                messages.info(request, f'Duplicate Username: "{username}" Alredy Exists.')
                return redirect(reverse('signup'))
            elif User.objects.filter(email= email):
                messages.info(request, f'Duplicate Email: "{email}" Alredy Exists.')
                return redirect(reverse('signup'))
            elif agree_terms is None:
                messages.info(request, 'You should Agree our Terms befor signing in!')
                return redirect(reverse('signup'))
            else:
                # create profile and user objects
                new_user = User.objects.create_user(username= username, password= password, email= email)
                Profile.objects.create(user= new_user, id_user= new_user.id)

                # logging the user in
                authenticate_user = authenticate(request, username= username, password= password)
                login(request, authenticate_user)
                return redirect('/')
        else:
            messages.info(request, 'Password Doesn\'t Match')
            return redirect(reverse('signup'))
    else:
        return render(request, 'signup.html')
    
def signin(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username= username, password= password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid username or password')
            return redirect(reverse('signin'))
    else:
        return render(request, 'signin.html')
    
@login_required(login_url= '/signin')
def logout_user(request):
    logout(request)
    return redirect(reverse('signin'))

@login_required(login_url='signin/')
def setting(request):
    user = User.objects.get(username=request.user.username)
    profile = Profile.objects.get(user=user)
    
    if request.method == 'POST':
        profile_image =  request.FILES.get('profile_image')

        profile.firstname = request.POST.get('firstname')
        profile.lastname = request.POST.get('lastname')
        profile.bio = request.POST.get('bio')
        profile.location = request.POST.get('location')

        user.email = request.POST.get('email')

        if profile_image is not None:
            profile.profileimg = request.FILES.get('profile_image')
        else:
            profile.profileimg = profile.profileimg
        profile.save()
        user.save()
        return redirect(reverse('setting'))
    else:
        context = {
            'user' : user,
            'profile' : profile
        }
        return render(request, 'setting.html', context= context)

@login_required(login_url='signin/')
def upload(request):
    if request.method == 'POST':
        file = request.FILES.get('upload')
        ext = file.name.split('.')[-1]
        newname = str(uuid.uuid4()) + datetime.now().strftime(r'-%Y-%m-%d-%H-%M-%S')

        file.name = newname + '.' + ext       
        
        if file:
            owner_profile = Profile.objects.get(user=request.user)
            caption = request.POST.get('caption')
            Post.objects.create(user=request.user, file=file, caption=caption, owner_profile=owner_profile, id=uuid.uuid4())
            return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')
    
@login_required(login_url='signin')
def profile(request, username):
    user_obj = User.objects.filter(username = username).first()
    if user_obj:
        user_profile= Profile.objects.filter(user=user_obj).first()
        posts = Post.objects.filter(user= user_obj)
        followings = Follower.objects.filter(follower = username)
        followers = Follower.objects.filter(user=username)
        context = {
            'profile' : user_profile,
            'posts' : posts,
            'no_of_followings' : followings.count(),
            'no_of_followers' : followers.count()
        }
        is_following = Follower.objects.filter(follower=request.user.username, user=user_obj.username).exists()
        if is_following:
            context['button_text'] = 'Unfollow'
        else:
            context['button_text'] = 'Follow'
            
        return render(request, 'profile.html', context=context)
    else:
        return redirect('/')
    
@login_required(login_url='signin')
def like(request):
    post_id = request.GET.get('post_id')
    if is_valid_uuid(post_id):
        post_obj = Post.objects.filter(id=post_id).first()
        if post_obj:
            # retruns Like obj or None
            person_liked = Like.objects.filter(post_id=post_id, user=request.user.username).first()
            if person_liked:
                # preform Unlike
                person_liked.delete()
                post_obj.sub_likes()
                return redirect(f'/#{post_id}')
            else:
                # preform Like
                Like.objects.create(post_id=post_id, user=request.user.username)
                post_obj.add_likes()
                return redirect(f'/#{post_id}')
        else:
            return redirect('/')
    else:
        return redirect('/')   

@login_required(login_url='signin') 
def delete_post(request):
    post_id = request.GET.get('post_id')
    if is_valid_uuid(post_id):
        post_obj = Post.objects.filter(id=post_id).first()
        if post_obj:
            post_obj.delete()
            return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/') 
    
@login_required(login_url='signin') 
def follow(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        follower = request.POST.get('follower')
        # This filter is just like excel filters
        follower_obj = Follower.objects.filter(user=user, follower=follower).first()
        if follower_obj:
            # Unfollow
            follower_obj.delete()
            return redirect(reverse('profile', kwargs={'username':user}))
        else:
            Follower.objects.create(user=user, follower=follower)
            return redirect(reverse('profile', kwargs={'username':user}))
    else:
        return redirect('/')

@login_required(login_url='signin')  
def search(request):
    username = request.GET.get('username')
    qs = User.objects.filter(username__icontains=username)
    if qs.exists():
        profiles = []
        for user in qs:
            profile = Profile.objects.get(user=user)
            profiles.append(profile)
        
        context = {
            'profiles' : profiles,
            'username' : username
        }
        return render(request, 'search.html', context)
    else:
        context = {
            'profiles' : []
        }
        messages.info(request, 'user does not exist')
        return render(request, 'search.html', context)