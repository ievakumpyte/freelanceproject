from itertools import chain
from django.urls import reverse
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.db.models import Q
from .helpers import send_forget_password_email
import uuid
from .forms import CommentForm, ReviewForm
from .models import Profile, Portfolio, Skelbimas, Comment, Message,Review, LikePortfolio, Likes, FollowersCount, Notification, Images


# Create your views here.



def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        name = request.POST['name']
        surname = request.POST['surname']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'El. paštas jau egzistuoja')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Vartotojo vardas jau egzistuoja')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password, first_name=name,
                                                last_name=surname)
                user.save()

                # log user in ad redirect to settings pagge
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # create a Profile object dor new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, name=name, surname=surname)
                new_profile.save()
                return redirect('/')

        else:
            messages.info(request, 'Slaptažodžiai nesutampa ')
            return redirect('signup')

    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Neteisingi prisijungimo duomenys')
            return redirect('signin')
    else:
        return render(request, 'signin.html')


def index(request):
    paginator = Paginator(Portfolio.objects.all().order_by('-date'), 8)
    page_number = request.GET.get('page')
    paged_portfolio = paginator.get_page(page_number)
    context = {
        "portfolio": paged_portfolio,
    }

    return render(request, 'index.html', context=context)

def delete_irasas(request, id):
    user = request.user.id
    portfolio = Portfolio.objects.get(id=id)
    portfolio.delete()
    return redirect('/manoprofilis/' + str(user))

def irasas(request, port_id):
    single_portfolio = get_object_or_404(Portfolio, pk=port_id)

    user = request.user
    profilis = Profile.objects.get(user=single_portfolio.user_id.user)

    favorited = False

    if request.user.is_authenticated:
        profile = Profile.objects.get(user=user)

        if profile.favorites_port.filter(id=single_portfolio.id).exists():
            favorited = True



    # Comments
    comments = Comment.objects.filter(porfolio=single_portfolio).order_by('date')

    # Comment form
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.porfolio = single_portfolio
            comment.user = user
            comment.save()
            return redirect('/' + str(single_portfolio.id))
    else:
        form = CommentForm()

    portfolio_images = Images.objects.filter(portfolio_id=single_portfolio)
    context = {
        'single_portfolio': single_portfolio,
        'portfolio_images': portfolio_images,
        'comments': comments,
        'favorited': favorited,
        'form': form,
        'profilis': profilis,
        'user': user,
    }

    return render(request, 'irasas.html', context=context)


def profilis(request, username):
    useris = request.user
    user_object = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=user_object.id)
    user_posts = Portfolio.objects.filter(user_id=user_profile.id)
    user_posts_length = len(user_posts)

    follower = request.user
    user = user_object

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"

    user_followers = len(FollowersCount.objects.filter(user=username))
    user_following = len(FollowersCount.objects.filter(follower=username))


    # Reviews
    reviews = Review.objects.filter(profile=user_profile).order_by('date')

    # Review form
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.profile = user_profile
            review.user = useris
            review.save()
            return redirect('/profilis/' + str(user_profile.user.username))
    else:
        form = ReviewForm()


    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_posts_length': user_posts_length,
        'button_text': button_text,
        'reviews': reviews,
        'form': form,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    return render(request, 'profilis.html', context)


@login_required(login_url="signin")
def manoprofilis(request, pk):
    user_object = User.objects.get(id=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Portfolio.objects.filter(user_id=user_profile.id)
    user_posts_length = len(user_posts)
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))
    useris = request.user
    # Reviews
    reviews = Review.objects.filter(profile=user_profile).order_by('date')

    # Review form
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.profile = user_profile
            review.user = useris
            review.save()
            return redirect('/manoprofilis/' + str(user_profile.user.id))
    else:
        form = ReviewForm()

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'reviews': reviews,
        'form': form,
        'user_posts_length': user_posts_length,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    return render(request, 'manoprofilis.html', context)


def top(request):
    paginator = Paginator(Portfolio.objects.all().order_by('-nr_of_likes')[:10:1], 8)
    page_number = request.GET.get('page')
    paged_portfolio = paginator.get_page(page_number)
    context = {
        "portfolio": paged_portfolio,
    }

    return render(request, 'index.html', context=context)

@login_required(login_url="signin")
def redaguotiprofili(request, pk):
    user = request.user
    user_profile = Profile.objects.get(user=user)


    if request.method == 'POST':

        if request.FILES.get('image') == None:
            about = request.POST['aprasymas']
            name = request.POST['vardas']
            surname = request.POST['pavarde']
            location = request.POST['miestas']


            user_profile.about = about
            user_profile.name = name
            user_profile.surname = surname
            user_profile.location = location
            user_profile.save()

        if request.FILES.get('image') != None:
            image = request.FILES['image']
            about = request.POST['aprasymas']
            name = request.POST['vardas']
            surname = request.POST['pavarde']
            location = request.POST['miestas']

            user_profile.profile_img = image
            user_profile.about = about
            user_profile.name = name
            user_profile.surname = surname
            user_profile.location = location
            user_profile.save()

    # return redirect('/manoprofilis/' + str(user_profile))

    # else:
    #     return redirect('/manoprofilis/' + str(user_profile)) + "/redaguotiprofili/"

    context = {
        'user_profile': user_profile,

    }
    return render(request, 'redaguotiprofili.html', context=context)


def skelbimai(request):
    paginator = Paginator(Skelbimas.objects.all(), 3)
    page_number = request.GET.get('page')
    paged_skelbimai = paginator.get_page(page_number)

    context = {
        "skelbimai": paged_skelbimai,
    }

    return render(request, 'skelbimai.html', context=context)


def skelbimas(request, skelbimas_id):
    single_skelbimas = get_object_or_404(Skelbimas, pk=skelbimas_id)
    profilis = Profile.objects.get(user=single_skelbimas.user_id.user)

    user = request.user

    favorited = False

    if request.user.is_authenticated:
        profile = Profile.objects.get(user=user)

        if profile.favorites_skelb.filter(id=skelbimas_id).exists():
            favorited = True

    context = {
        'single_skelbimas': single_skelbimas,
        'favorited': favorited,
        'profilis':profilis,
        'user':user,

    }

    return render(request, 'skelbimas.html', context=context)


@login_required(login_url="signin")
def pridetiskelbima(request):
    user_profile = Profile.objects.get(user=request.user)
    # user_object = User.objects.get(id=pk)
    # user_profile = Profile.objects.get(user=user_object)

    user = request.user
    user_profile = Profile.objects.get(user=user)

    if request.method == 'POST':

        if request.FILES.get('logo') == None:
            user = request.user.id

            name = request.POST['pavadinimas']
            area = request.POST['sritis']
            about = request.POST['aprasymas']
            type = request.POST['tipas']
            salary = request.POST['atlyginimas']
            email = request.POST['email']
            location = request.POST['location']

            naujas_skelbimas = Skelbimas.objects.create(name=name, about=about, area=area, type=type, salary=salary,location=location,
                                                        email=email, user_id=user_profile)
            naujas_skelbimas.save()
            return redirect('skelbimai')

        if request.FILES.get('logo') != None:
            logo = request.FILES['logo']
            name = request.POST['pavadinimas']
            area = request.POST['sritis']
            about = request.POST['aprasymas']
            type = request.POST['tipas']
            salary = request.POST['atlyginimas']
            email = request.POST['email']
            location = request.POST['location']

            naujas_skelbimas = Skelbimas.objects.create(logo=logo,name=name, about=about, area=area, type=type, salary=salary,location=location,
                                                        email=email, user_id=user_profile)
            naujas_skelbimas.save()
            return redirect('skelbimai')


    return render(request, 'pridetiskelbima.html')


def aplikavimas(request, skelb_id):
    skelibimas = Skelbimas.objects.get(id=skelb_id)
    from_user = request.user
    to_user_username = skelibimas.user_id.user
    body = request.POST.get('body')

    if request.method == 'POST':
        to_user = User.objects.get(username=to_user_username)
        Message.send_message(from_user, to_user, body)
        return redirect('inbox')
    else:
        HttpResponseBadRequest()
    return render(request, 'aplikavimas.html')


@login_required(login_url="signin")
def manoskelbimai(request, pk):
    user_object = User.objects.get(id=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_skelbimai = Skelbimas.objects.filter(user_id=user_profile.id)

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_skelbimai': user_skelbimai,

    }

    return render(request, 'manoskelbimai.html', context)


def delete_skelbimas(request, id):
    user = request.user.id
    skelbimas = Skelbimas.objects.get(id=id)
    skelbimas.delete()
    return redirect('/manoskelbimai/' + str(user))

def del_comment(request, id):
    comment = Comment.objects.get(id=id)
    comment.delete()
    return redirect('/' + str(comment.porfolio.id))

@login_required(login_url="signin")
def edit_skelbimas(request, id):

    user = request.user.id
    skelbimas = Skelbimas.objects.get(id=id)

    if request.method == 'POST':
        if request.FILES.get('logo') == None:
            user = request.user.id
            name = request.POST['pavadinimas']
            area = request.POST['sritis']
            about = request.POST['aprasymas']
            type = request.POST['tipas']
            salary = request.POST['atlyginimas']
            email = request.POST['email']
            location = request.POST['location']

            skelbimas.name = name
            skelbimas.area = area
            skelbimas.about = about
            skelbimas.type = type
            skelbimas.salary = salary
            skelbimas.email = email
            skelbimas.location = location
            skelbimas.save()
            return redirect('/manoskelbimai/' + str(user))

        if request.FILES.get('logo') != None:
            user = request.user.id
            logo = request.FILES['logo']
            name = request.POST['pavadinimas']
            area = request.POST['sritis']
            about = request.POST['aprasymas']
            type = request.POST['tipas']
            salary = request.POST['atlyginimas']
            email = request.POST['email']
            location = request.POST['location']

            skelbimas.logo = logo
            skelbimas.name = name
            skelbimas.area = area
            skelbimas.about = about
            skelbimas.type = type
            skelbimas.salary = salary
            skelbimas.email = email
            skelbimas.location = location
            skelbimas.save()
            return redirect('/manoskelbimai/' + str(user))

    context = {
        'skelbimas': skelbimas,
        'useris': request.user,
    }
    return render(request, 'edit_skelbimas.html', context=context)

@login_required(login_url="signin")
def inbox(request):
    user = request.user
    messages = Message.get_messages(user=user)
    active_direct = None
    directs = None

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=user, recipient=message['user'])
        directs.update(is_read=True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0

    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct
    }

    return render(request, 'direct.html', context=context)

@login_required(login_url="signin")
def new_conversation(request, username):
    from_user = request.user
    body = 'Sveiki!'

    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect('usersearch')

    if from_user != to_user:
        Message.send_message(from_user, to_user, body)
    return redirect('inbox')


def inbox_notifications(request):
    directs_count = 0
    if request.user.is_authenticated:
        directs_count = Message.objects.filter(user=request.user, is_read=False).count()

    return {'directs_count': directs_count}

@login_required(login_url="signin")
def directs(request, username):
    user = request.user
    messages = Message.get_messages(user=user)
    active_direct = username

    directs = Message.objects.filter(user=user, recipient__username=username)
    directs.update(is_read=True)

    for message in messages:
        if message['user'].username == username:
            message['unread'] = 0

    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,

    }

    return render(request, 'direct.html', context=context)


@login_required(login_url="signin")
def send_direct(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')

    if request.method == 'POST':
        to_user = User.objects.get(username=to_user_username)

        Message.send_message(from_user, to_user, body)
        return redirect('inbox')
    else:
        HttpResponseBadRequest()

@login_required(login_url="signin")
def user_search(request):
    query = request.GET.get('q')
    context = {}

    if query:
        users = User.objects.filter(Q(username__icontains=query))
        paginator = Paginator(users, 6)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

        context = {
            'users': users_paginator,
        }

    return render(request, 'search_user.html', context=context)

def search_portfolio(request):
    portfolios = Portfolio.objects.all()
    naujas = None
    paieska = request.POST["paieska"]
    filtras = request.POST["filtras"]

    if paieska != '' and paieska is not None:
        naujas = portfolios.filter(Q(name__icontains=paieska) | Q(user_id__user__first_name__icontains=paieska) | Q(user_id__user__last_name__icontains=paieska) | Q(user_id__user__username__icontains=paieska))

    elif filtras != '' and filtras is not None:
        naujas = portfolios.filter(area=filtras)

    else:
       naujas = Portfolio.objects.all()


    context = {
        'qs': naujas
    }

    return render(request, 'portfolio_paieska.html', context=context)

def search_skelbimai(request):
    skelbimai = Skelbimas.objects.all()
    naujas = None
    paieska = request.POST["paieska"]
    filtras = request.POST["filtras"]

    if paieska != '' and paieska is not None:
        naujas = skelbimai.filter(Q(name__icontains=paieska) | Q(user_id__user__first_name__icontains=paieska) | Q(user_id__user__last_name__icontains=paieska) | Q(user_id__user__username__icontains=paieska))

    elif filtras != '' and filtras is not None:
        naujas = skelbimai.filter(area=filtras)

    else:
       naujas = skelbimai.objects.all()


    context = {
        'qs': naujas
    }

    return render(request, 'paieska_skelbimai.html', context=context)


@login_required(login_url="signin")
def favorite_port(request, port_id):
    user = request.user
    portfolio = Portfolio.objects.get(id=port_id)
    profile = Profile.objects.get(user=user)

    if profile.favorites_port.filter(id=port_id).exists():
        profile.favorites_port.remove(portfolio)
    else:
        profile.favorites_port.add(portfolio)

    return HttpResponseRedirect(reverse('irasas', args=[port_id]))


@login_required(login_url="signin")
def favorite_skelb(request, skelb_id):
    user = request.user
    skelbimas = Skelbimas.objects.get(id=skelb_id)
    profile = Profile.objects.get(user=user)

    if profile.favorites_skelb.filter(id=skelb_id).exists():
        profile.favorites_skelb.remove(skelbimas)
    else:
        profile.favorites_skelb.add(skelbimas)

    return HttpResponseRedirect(reverse('skelbimas', args=[skelb_id]))

def like(request, port_id):
    user = request.user
    portfolio = Portfolio.objects.get(id=port_id)
    current_likes = portfolio.nr_of_likes

    liked = Likes.objects.filter(user=user, portfolio=portfolio).count()

    if not liked:
        likes = Likes.objects.create(user=user, portfolio=portfolio)
        current_likes = current_likes + 1
        portfolio.is_like = True
        portfolio.save()
    else:
        Likes.objects.filter(user=user, portfolio=portfolio).delete()
        current_likes = current_likes - 1
        portfolio.is_like = False
        portfolio.save()

    portfolio.nr_of_likes = current_likes
    portfolio.save()

    return HttpResponseRedirect(reverse('irasas', args=[port_id]))
    # return redirect("irasas")

@login_required(login_url="signin")
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profilis/' + user)

        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profilis/' + user)
    else:
        return redirect('/')

@login_required(login_url="signin")
def like_post(request):
    username = request.user.username
    portfolio_id = request.GET.get('portfolio_id')

    post = Portfolio.objects.get(id=portfolio_id)

    like_filter = LikePortfolio.objects.filter(portfolio_id=portfolio_id, username=username).first()

    if like_filter == None:
        new_like = LikePortfolio.objects.create(portfolio_id=portfolio_id, username=username)
        new_like.save()
        post.nr_of_likes = post.nr_of_likes + 1
        post.save()
        return redirect('/')

    else:
        like_filter.delete()
        post.nr_of_likes = post.nr_of_likes - 1
        post.save()
        return redirect('/')



def issaugoti(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    skelbimai = profile.favorites_skelb.all()
    portfolios = profile.favorites_port.all()

    context = {
        'skelbimai': skelbimai,
        'portfolios': portfolios,

    }

    return render(request, 'issaugoti.html', context=context)

def show_notifications(request):
    user = request.user
    if Notification.sender != user:
        notifications = Notification.objects.filter(user=user).order_by('-date')
    Notification.objects.filter(user=user, is_seen=False).update(is_seen=True)

    context = {
        'notifications': notifications
    }

    return render(request, 'notifications.html', context=context)


def delete_notifications(request, noti_id):
    user = request.user
    Notification.objects.filter(id=noti_id, user=user).delete()
    return redirect("show-notifications")



def count_notifications(request):
    count_notifications = 0
    if request.user.is_authenticated:
        count_notifications = Notification.objects.filter(user=request.user, is_seen=False).count()

    return {'count_notifications': count_notifications}

def ChangePass(request, token):
    context = {}
    try:
        profile_obj = Profile.objects.filter(forget_password_token=token).first()
        context = {'user_id': profile_obj.user.id}
        if request.method == 'POST':
            new_password = request.POST.get('new_pass')
            confirm_password = request.POST.get('new_pass2')
            user_id = request.POST.get('user_id')

            if user_id is None:
                messages.success(request, "Vartotojas nerastas")
                return redirect(f'change-password/{token}/')

            if new_password != confirm_password:
                messages.success(request, "Slaptažodžiai nesutampa")
                return redirect(f'change-password/{token}/')

            user_obj = User.objects.get(id=user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return redirect('/signin')



    except Exception as e:
        print(e)

    return render(request, 'change-password.html', context)


def ForgetPass(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            if not User.objects.filter(email=email).first():
                messages.info(request, 'El. pašto adresas neegzistuoja')
                return redirect('forget-password')

            user_obj = User.objects.get(email=email)
            token = str(uuid.uuid4())
            profile_obj = Profile.objects.get(user=user_obj)
            profile_obj.forget_password_token = token
            profile_obj.save()
            send_forget_password_email(user_obj, token)
            messages.info(request, 'Laiškas su nauju slaptažodžiu išsiųstas')
            return redirect('forget-password')

    except Exception as e:
        print(e)
    return render(request, 'forget-password.html')

@login_required(login_url="signin")
def addirasa(request, pk):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        useris = request.user.id
        user = request.user.username
        image = request.FILES.get('cover')
        name = request.POST['pavadinimas']
        about = request.POST['aprasymas']
        type = request.POST['tipas']
        images = request.FILES.getlist('images')



        new_post = Portfolio.objects.create(user_id=user_profile, cover=image, name=name, about=about, area=type)
        new_post.save()

        for img in images:
            new_image = Images.objects.create(image=img, portfolio_id=new_post)
            new_image.save()


        return redirect('/manoprofilis/' + str(useris))

    else:
        return render(request, 'addirasa.html')

    return render(request, 'addirasa.html')
