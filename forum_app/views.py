from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from datetime import datetime
import json

from forum_app.models import Category, Thread, Post, User, Profile
from forum_app.forms import UserForm, ProfileForm, CategoryForm, ThreadForm
from forum_app.forms import PostForm


def category_list(request):
    """ View to get all of the Category objects and pass them to a template
    to render. 
    ARGs:
        request object
    RET rendered HTML page with context:
        categories - a list of Categories objects.
    """
    categories = Category.objects.all()
    context = {'categories':categories}
    return render(request, 'forum/category_list.html', context)

def thread_list(request, category_slug):
    """ View to get all the Thread objects that belong to a specific Category.
    ARGs:
        request object
        category_slug - unique identifier for category
    RET:
        threads - a list of Thread objects
        category - a Category object
    """
    category = get_object_or_404(Category, slug=category_slug)
    threads = category.thread_set.all().order_by('most_recent_post',
              'created_date')
    context = {'threads':threads, 'category':category}
    return render(request, 'forum/thread_list.html', context)

def thread(request, category_slug, thread_slug):
    """ View to get all the Post objects that belong to a specific Thread.
    ARGs:
        request object
        thread_slug - thread we want to show
        category_slug - parent category for this thread
    RET:
        posts - a list of Post objects
        thread - a Thread object
    """
    thread = get_object_or_404(Thread, slug=thread_slug)
    posts = thread.post_set.all().order_by('created_date')
    context = {'posts':posts, 'thread':thread}
    return render(request, 'forum/thread.html', context)

@login_required
def category_edit(request, category_slug):
    """ View to display and handle CategoryForm. This will allow the user to
    create a new category or edit and existing category.
    ARGs:
        category_slug - unique identifier for a Category instance
    RET:
        form - blank or filled out CategoryForm object
    or
        HttpRedirect to a URL
    """
    # Is the user trying to edit an existing category?
    try: # YES category exists
        category = Category.objects.get(slug=category_slug)
    except Category.DoesNotExist:  # NO category doesn't exist
        #TODO raise some kind of error that says cat doesnt exist
        raise Http404
    else:
        # if POST, then commit changes to existing category
        if request.method == 'POST':
            form = CategoryForm(request.POST, request.FILES, instance=category)
            if form.is_valid():
                category = form.save(commit=False)
                category.save()
                return redirect('categories')
        else: # Allow user to see form so they can edit category
            form = CategoryForm(instance=category)
            context = {'form':form, 'category_slug':category_slug}
            return render(request, 'forum/category_edit.html', context)

@login_required
def category_add(request):
    """ Verify on submission that category doesn't already exist. - does django
    do this for us already?
    "ENFORCE that NO Category can be named "add-category"...
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            return redirect('categories')
        else:
            #TODO render template again, but pass errors to be displayed
            # I think this will tell us if the object already exits :)
            print(form.errors)
    else:
        form = CategoryForm()
        context = {'form':form}
        return render(request, 'forum/category_add.html', context)




@login_required
def thread_edit(request, category_slug, thread_slug):
    """ View to display and handle ThreadForm. This will allow the user to
    create a new Thread or edit and existing Thread.
    ARGs:
        thread_slug - thread we want to edit
        category_slug - parent category of specified thread
    RET:
        form - blank or filled out ThreadForm object
    or
        HttpRedirect to a URL
    """
    # Is the user trying to edit an existing Thread?
    try: # YES Thread exists
        thread = Thread.objects.get(slug=thread_slug)
    except Thread.DoesNotExist:  # NO thread doesn't exist
        #TODO raise some kind of error that says thread doesnt exist
        raise Http404
    else:
        # if POST, then commit changes to existing Thread
        if request.method == 'POST':
            form = ThreadForm(request.POST, request.FILES, instance=thread)
            if form.is_valid():
                thread = form.save(commit=False)
                thread.save()
                return redirect('threads')
        else: # Allow user to see form so they can edit thread
            form = ThreadForm(instance=thread)
            context = {'form':form, 'thread_slug':thread_slug,
                       'category_slug':category_slug}
            return render(request, 'forum/thread_edit.html', context)

@login_required
def thread_add(request, category_slug):
    """ Verify on submission that thread doesn't already exist. - does django
    do this for us already?
    Also add a TextArea / PostForm to capture initial post as well.
    ENFORCE that NO thread can be named "add-thread".
    """
    try: 
        category = Category.objects.get(slug=category_slug)
    except Thread.DoesNotExist: 
        #TODO raise some kind of error that says thread doesnt exist
        raise Http404
    if request.method == 'POST':
        form = ThreadForm(request.POST, request.FILES)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.category = category
            thread.author = request.user
            thread.save()
            return redirect('threads', category_slug)
        else:
            #TODO render template again, but pass errors to be displayed
            # I think this will tell us if the object already exits :)
            print(form.errors)
    else:
        form = ThreadForm()
        context = {'form':form, 'category_slug':category_slug}
        return render(request, 'forum/thread_add.html', context)

def search_bar(request):
    """ View to handle Ajax POST requests. A JS function is connected to the
    keyup signal from the search bar. Each keypress triggers the JS function
    to use Ajax to send data to this view and get data back to display in html 
    ARGs:
        None, or you can argue POST['search_object'] & POST['search_text']
        search_object is the type of object to return.
    RET:
        results - A list of objects from the DB that contain 'search_text'
        search_object - the type of DB object model
    """
    if request.method == 'POST':
        # The JS Ajax func gets the search_object from a hidden input element
        search_object = request.POST['search_object']
        search_text = request.POST['search_text']
        if search_object == 'category':
            results = Category.objects.filter(name__contains=search_text)
        elif search_object == 'thread':
            results = Thread.objects.filter(name__contains=search_text)
        elif search_object == 'post':
            results = Post.objects.filter(text__contains=search_text)
        else:
            results = ''
    else:
        raise Http404
    context = {'results':results, 'object':search_object}
    return render(request, 'forum/ajax_search.html', context)


def ajax_login(request):
    """ View to handle Ajax Post request to login a user with passed
    credentials. 
    ARGs:
        None, or you can argue POST['username','password','remember']
    RET:
        json object - with string of html element. This string gets checked
        for an exact match in the base.html Javascript function. If its a
        match then it knows login was successful.
    """
    username = request.POST.get('username','') # defaults to '' 
    password = request.POST.get('password','')
    remember = request.POST.get('remember','')
    user = authenticate(username=username, password=password)
    response_data = {}
    if user is None: # failed authentication
        fail_str = '<div class="alert alert-warning"><p>Your username and password do not match...</p></div>'
        response_data['result'] = fail_str
    else: # successfull authentication
        success_str = '<div class="alert alert-success"><p>Success!</p></div>'
        response_data['result'] = success_str
        login(request, user)
        if remember == 'false':
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
        elif remember == 'true':
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
    return HttpResponse(json.dumps(response_data), 
           content_type='application/json')


def register_user(request):
    """ Handles both the UserForm and the ProfileForm. Creates blank forms if 
    not 'POST'. If 'POST', then it validates the forms and creates User and
    Profile Objects in the DB.
    """
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            profile_form = ProfileForm(request.POST, request.FILES,
                           instance=user.profile)
            if profile_form.is_valid():
                print("profile form is valid!!")
                profile_form.save()
            #return redirect('categories')
            context = {'username':user.username}
            return render(request, 'forum/register_success.html', context)
        else:
            print(user_form.errors)
            #print(profile_form.errors)
            #error messages?
    else: # blank form
        user_form = UserForm()
        profile_form = ProfileForm()
    context = {'user_form':user_form, 'profile_form':profile_form}
    return render(request, 'registration/register.html', context)

@login_required
def profile(request, username):
    """ Will display the profile for a specified user. Handles the ProfileForm 
    if the Profile is the currently logged in user's profile. This will allow
    them to change fields in their Profile object.
    """
    context = {}
    # Try to get the user object for specified user, or redirect to Home
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect(reverse('categories'))
    # If a User exists, then get associated Profile object.
    profile = Profile.objects.get(user=user)
    # now that we have the User and Profile object in question, get the Form.
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES,
                                   instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
        else:
            print(profile_form.errors)
            #TODO handle errors
    else:
        profile_form = ProfileForm(instance=request.user.profile)
    context['profile_form'] = profile_form
    context['selecteduser'] = user
    context['profile'] = profile
    # we pass User, Profile, & ProfileForm objects to the template.
    return render(request, 'forum/profile.html', context)

@login_required
def profile_list(request):
    profile_list = Profile.objects.all()
    context = {'profile_list':profile_list}
    return render(request, 'forum/profile_list.html', context)


