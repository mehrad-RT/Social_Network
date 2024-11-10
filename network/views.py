from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django.db.models import Count
from .models import *

def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.content = data["content"]
        edit_post.save()
        return JsonResponse({"message": "Change successful", "data": data["content"]})

def index(request):
    allPosts = Post.objects.all().order_by("id").reverse()

    paginator = Paginator(allPosts, 10)
    pageNumber = request.GET.get('page')
    posts_inside_the_page = paginator.get_page(pageNumber)

    allLikes = Like.objects.all()

    liked_people = []
    try:
      for like in allLikes:
        if like.user.id == request.user.id:
            liked_people.append(like.post.id)
    except:
      liked_people = []

    return render(request, "network/index.html",{
        "allPosts": allPosts,
        "posts_inside_the_page": posts_inside_the_page,
        "liked_people": liked_people
        })

def newPost(request):
    if request.method =="POST":
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content, user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))
    
def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    allPosts = Post.objects.filter(user=user).order_by("id").reverse()

    followers = Follow.objects.filter(user_follower=user)
    following = Follow.objects.filter(user=user)

    try:
        followCheck = followers.filter(user=User.objects.get(pk=request.user.id))
        if len(followCheck) != 0 :
            isFollowing = True
        else:
            isFollowing = False
    except:
        isFollowing = False

    paginator = Paginator(allPosts, 10)
    pageNumber = request.GET.get('page')
    posts_inside_the_page = paginator.get_page(pageNumber)

    return render(request, "network/profile.html",{
        "allPosts": allPosts,
        "posts_inside_the_page": posts_inside_the_page,
        "username" : user.username,
        "followers": followers,
        "following": following,
        "isFollowing": isFollowing,
        "userProfile": user
        })

def follow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    followedUser = User.objects.get(username=userfollow)
    newFollow = Follow(user=currentUser, user_follower=followedUser)
    newFollow.save()
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': followedUser.id}))

def following(request):
    currentUser = User.objects.get(pk=request.user.id)
    followingUsers = Follow.objects.filter(user=currentUser)
    posts = Post.objects.all().order_by('id').reverse()
    followingPosts = []

    for post in posts:
        for person in followingUsers:
            if person.user_follower == post.user:
                followingPosts.append(post)

    paginator = Paginator(followingPosts, 10)
    pageNumber = request.GET.get('page')
    posts_inside_the_page = paginator.get_page(pageNumber)

    return render(request, "network/following.html",{
        "posts_inside_the_page": posts_inside_the_page
        })

def unfollow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    followedUser = User.objects.get(username=userfollow)
    newFollow = Follow.objects.get(user=currentUser, user_follower=followedUser)
    newFollow.delete()
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': followedUser.id}))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")  

def toggle_like(request, post_id):
  post = Post.objects.get(pk=post_id)
  user = User.objects.get(pk=request.user.id)
  like = Like.objects.filter(user=user, post=post).first()

  if like:
    like.delete()
    isLiked = False
  else:
    Like.objects.create(user=user, post=post)
    isLiked = True

  likeCount = Like.objects.filter(post=post).count()

  return JsonResponse({
    'success': True,
    'isLiked': isLiked,
    'likeCount': likeCount,
  })