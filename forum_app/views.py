from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from datetime import datetime
import json
from markdown import markdown
import bleach

from forum_app.models import Category, Thread, Post, User, Profile, Conversation, Pm
from forum_app.forms import UserForm, ProfileForm, CategoryForm, ThreadForm
from forum_app.forms import PostForm, PmForm, ContactForm


def category_list(request):
    """ View to get all of the Category objects and pass them to a template
    to render. 
    ARGs:
        request object
    RET rendered HTML page with context:
        categories - a list of Categories objects.
    """
    categories = Category.objects.all().order_by('-most_recent_post')
    context = {'categories':categories}
    return render(request, 'forum/category_list.html', context)

def thread_list(request, category_slug):
    """ View to get all the Thread objects that belong to a specific Category.
    ARGs:
        category_slug - unique identifier for category
    RET:
        threads - a list of Thread objects
        category - a Category object
    """
    context = {}
    category = get_object_or_404(Category, slug=category_slug)
    if 'query' in request.GET:
        query = bleach.clean(request.GET.get('query'))
        context['query'] = query
        thread_list = category.thread_set.filter(category=category,name__contains=query).order_by(
                      '-most_recent_post','created_date')
    else:
        thread_list = category.thread_set.all().order_by('-most_recent_post',
              'created_date')
    paginator = Paginator(thread_list, 100) # show 10 threads per page
    if 'page' in request.GET:
        page = request.GET.get('page')
        try:
            threads = paginator.page(page)
        except:
            threads = paginator.page(1) # default to first page
    else:
        threads = paginator.page(1)
    context['paginator'] = paginator
    context['threads'] = threads
    context['category'] = category
    return render(request, 'forum/thread_list.html', context)

def thread(request, category_slug, thread_slug):
    """ View to get all the Post objects that belong to a specific Thread.
    This View will also handle the PostForm to create a new post in the Thread.
    ARGs:
        thread_slug - thread we want to show
        category_slug - parent category for this thread
    RET:
        posts - a list of Post objects we want to render
        thread - The parent Thread that the Posts belong to.
        form - the PostForm object to be rendered
    """
    context = {}
    thread = get_object_or_404(Thread, slug=thread_slug)
    category = get_object_or_404(Category, slug=category_slug)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.text = markdown(bleach.clean(post.text).replace('&gt;','>'))
            post.thread = thread
            post.author = request.user
            post.new()
            return redirect('thread', category.slug, thread.slug)
        else:
            #TODO render template again, but pass errors to be displayed
            # I think this will tell us if the object already exits :)
            print(form.errors)
            context['form'] = form
    else:
        form = PostForm()
        context['form'] = form

    post_list = thread.post_set.all().order_by('created_date')
    initial_post = post_list[0]
    paginator = Paginator(post_list, 50) # show 10 posts per page
    if 'page' in request.GET:
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            # If page not an int, deliver first page
            posts = paginator.page(1)
        except EmptyPage:
            # If page is out or range (i.e. 9999), deliver last page
            posts = paginator.page(paginator.num_pages)
    else:
        posts = paginator.page(paginator.num_pages)
    context['paginator'] = paginator
    context['posts'] = posts
    context['initial_post'] = initial_post
    context['thread'] = thread
    context['category'] = category
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
    category = get_object_or_404(Category, slug=category_slug)
    # if POST, then commit changes to existing category
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            return redirect('categories')
    else: # Allow user to see form so they can edit category
        form = CategoryForm(instance=category)
        context = {'form':form, 'category':category}
        return render(request, 'forum/category_edit.html', context)

@login_required
def category_add(request):
    """ Verify on submission that category doesn't already exist. - does django
    do this for us already? - Yes. But we must handle the errors appropriately.
    """
    banned_cat_names = ['add-category', 'add category']
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            if category.name.lower() not in banned_cat_names:
                category.new()
                return redirect('categories')
            else:
                print("this is a banned category name. not saving...")
                context = {'form':form}
                # also display some kind of feedback to the user
        else:
            print(form.errors)
            context = {'form':form}
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
    thread = get_object_or_404(Thread, slug=thread_slug)
    category = get_object_or_404(Category, slug=category_slug)
    # if POST, then commit changes to existing Thread
    if request.method == 'POST':
        form = ThreadForm(request.POST, request.FILES, instance=thread)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.save()
            return redirect('threads', category.slug)
        else:
            print(form.errors)
    form = ThreadForm(instance=thread)
    context = {'form':form, 'thread':thread,
               'category':category}
    return render(request, 'forum/thread_edit.html', context)

@login_required
def thread_add(request, category_slug):
    """ Verify on submission that thread doesn't already exist. - does django
    do this for us already?
    Also add a TextArea / PostForm to capture initial post as well.
    ENFORCE that NO thread can be named "add-thread".
    """
    context = {}
    category = get_object_or_404(Category, slug=category_slug)
    context['category'] = category
    banned_thread_names = ['add-thread', 'add thread']
    if request.method == 'POST':
        thread_form = ThreadForm(request.POST, request.FILES)
        post_form = PostForm(request.POST, request.FILES)
        if thread_form.is_valid():
            thread = thread_form.save(commit=False)
            thread.category = category
            thread.author = request.user
            if thread.name.lower() in banned_thread_names:
                print("this is a banned thread name. not saving...")
                context['thread_form'] = thread_form
                context['post_form'] = post_form
                return render(request, 'forum/thread_add.html', context)
            if post_form.is_valid():
                thread.new()
                post = post_form.save(commit=False)
                post.text = markdown(bleach.clean(post.text))
                post.thread = thread
                post.author = request.user
                post.new()
                return redirect('threads', category.slug)
            else:
                #TODO render template again, but pass errors to be displayed
                # I think this will tell us if the object already exits :)
                print(post_form.errors)
                context['thread_form'] = thread_form
                context['post_form'] = post_form
        else:
            #TODO render template again, but pass errors to be displayed
            # I think this will tell us if the object already exits :)
            print(thread_form.errors)
            context['thread_form'] = thread_form
            context['post_form'] = post_form
    else:
        thread_form = ThreadForm()
        post_form = PostForm()
        context['thread_form'] = thread_form
        context['post_form'] = post_form
    return render(request, 'forum/thread_add.html', context)

def search_bar(request):
    """ View to handle Ajax POST requests. A JS function is connected to the
    keyup signal from the search bar. Each keypress triggers the JS function
    to use Ajax to send data to this view and get data back to display in html 
    ARGs:
        None, or you can argue POST['search_type'] & POST['search_text']
        search_type is the type of object to return (category, Thread, Post).
    RET:
        results - A list of objects from the DB that contain 'search_text'
        object - the type of DB object model
        category_slug* - Category that current Thread set belong to.
    """
    context = {}
    if request.method == 'POST':
        # The JS Ajax func gets the search_object from a hidden input element
        search_type = request.POST['search_type']
        search_text = request.POST['search_text']
        ###########################################################
        # Category ajax search
        ###########################################################
        if search_type == 'category':
            categories = Category.objects.filter(name__contains=search_text).order_by(
                               '-most_recent_post')
            context = {'categories':categories, 'object':search_type}
        ###########################################################
        # Thread ajax search
        ###########################################################
        elif search_type == 'thread':
            cat_slug = request.POST['search_category']
            cat = get_object_or_404(Category, slug=cat_slug)
            query = bleach.clean(search_text)
            context['query'] = query
            thread_list = Thread.objects.filter(category=cat,name__contains=query).order_by(
                             '-most_recent_post','created_date')
            paginator = Paginator(thread_list, 100) # show 10 threads per page
            if 'page' in request.GET:
                page = request.GET.get('page')
                try:
                    threads = paginator.page(page)
                except:
                    threads = paginator.page(1) # defualt to first page
            else:
                threads = paginator.page(1)
            context['paginator'] = paginator
            context['threads'] = threads
            context['object'] = search_type
            context['category'] = cat
        ###########################################################
        # Post ajax search ( currently NOT in use )
        ###########################################################
        elif search_type == 'post':
            results = Post.objects.filter(text__contains=search_text).order_by(
                           '-most_recent_post','created_date')
            context = {'results':results, 'object':search_type}
        else:
            results = ''
            context = {'results':results, 'object':search_type}
        ###########################################################
        # No or Invalid search_type passed
        ###########################################################
    else:
        raise Http404
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
    response_data = {}
    if User.objects.filter(username=username).exists():
        user = authenticate(username=username, password=password)
        if user is None: # failed authentication
            fail_str = '<div id="login-result" class="text-danger fail"><p>Invalid password...</p></div>'
            response_data['result'] = fail_str
        else: # successfull authentication
            success_str = '<div id="login-result" class="text-success success"><p>Success!</p></div>'
            response_data['result'] = success_str
            login(request, user)
            if remember == 'false':
                settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
            elif remember == 'true':
                settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
    else:
        fail_str = '<div id="login-result" class="text-danger fail"><p>Username does not exist...</p></div>'
        response_data['result'] = fail_str
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
                profile_form.save()
            #return redirect('categories')
            context = {'username':user.username}
            return render(request, 'forum/register_success.html', context)
        else:
            print(user_form.errors)
            profile_form = ProfileForm()
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


@login_required
def conversations(request, username):
    """ View to get all the Conversation objects that belong to a specific User.
    ARGs:
        unsername - unique User object (must be logged in user)
    RET:
        threads - a list of Thread objects
        category - a Category object
    """
    print("In conversations()")
    user = get_object_or_404(User, username=username)
    context = {}
    user = get_object_or_404(User, username=username)
    if request.user != user:
        raise Http404
    conversation_list = Conversation.objects.filter(belongs_to=user).order_by('-most_recent_pm','-pk')
    paginator = Paginator(conversation_list, 100) # show 10 conversations per page
    if 'page' in request.GET:
        page = request.GET.get('page')
        try:
            conversations = paginator.page(page)
        except:
            conversations = paginator.page(1) # defualt to first page
    else:
        conversations = paginator.page(1)
    context['paginator'] = paginator
    context['conversations'] = conversations
    context['user'] = user
    return render(request, 'forum/conversations.html', context)

@login_required
def conversation(request, username, is_with):
    """ Handles PmForm. Creates two instances of the Post, One for the creator
    and one for the receiver of the message. Each User also has their own
    Conversation object.
    """
    context = {}
    user = get_object_or_404(User, username=username)
    is_with = get_object_or_404(User, username=is_with)
    if request.user != user:
        raise Http404
    if request.user == is_with:
        raise Http404
    try: # get current convo if it exists with user (but don't create one if not)
        conversation1 = Conversation.objects.get(belongs_to=user, is_with=is_with)
    except Conversation.DoesNotExist:
        conversation1 = None
        context['new_convo'] = True
    context['user'] = user
    context['is_with'] = is_with
    ######################################################
    # If this is a form submission
    ######################################################
    if request.method == 'POST': 
        form = PmForm(request.POST, request.FILES)
        if form.is_valid():
            # only create conversation objects if form submission was valid
            conversation1, created1= Conversation.objects.get_or_create(belongs_to=user, is_with=is_with)
            conversation2, created2= Conversation.objects.get_or_create(belongs_to=is_with, is_with=user)
            pm = form.save(commit=False)
            text = markdown(bleach.clean(pm.text).replace('&gt;','>'))
            pm.text = text
            pm.conversation = conversation1
            pm.author = request.user
            pm.save() # change to new() ??
            pm2 = Pm.objects.create(conversation=conversation2,author=request.user,text=text)
            pm2.save()
            return redirect('conversation', user, is_with.username)
        else:
            #TODO render template again, but pass errors to be displayed
            # I think this will tell us if the object already exits :)
            print(form.errors)
            context['form'] = form
    ######################################################
    # Else, render blank form
    ######################################################
    else:
        form = PmForm()
        context['form'] = form
    ######################################################
    # If a conversation already exists, show it rather than just a blank form
    ######################################################
    if conversation1: # only if convo object existed do we bother getting pages
        pm_list = Pm.objects.filter(conversation=conversation1)
        paginator = Paginator(pm_list, 50)
        if 'page' in request.GET:
            page = request.GET.get('page')
            try:
                pms = paginator.page(page)
            except PageNotAnInteger:
                # If page not an int, deliver first page
                pms = paginator.page(1)
            except EmptyPage:
                # If page is out or range (i.e. 9999), deliver last page
                pms = paginator.page(paginator.num_pages)
        else:
            pms = paginator.page(paginator.num_pages)
        context['paginator'] = paginator
        context['pms'] = pms
    return render(request, 'forum/conversation.html', context)

@login_required
def delete_conversation(request, username, is_with):
    """ 
    """
    print("In delete_conversation()")
    user = get_object_or_404(User, username=username)
    is_with = get_object_or_404(User, username=is_with)
    if request.user != user:
        raise Http404
    try:
        conversation = Conversation.objects.get(belongs_to=user, is_with=is_with)
        print("conversation = {}".format(conversation)) 
    except Conversation.DoesNotExist:
        pass
    else:
        conversation.delete()
    finally:
        return redirect('conversations',username=str(username))


def like_post(request):
    """ Called by an Ajax POST request. Returns a json object.
    """
    user_pk = request.POST.get('user_pk','') # defaults to '' 
    post_pk = request.POST.get('post_pk','')
    the_type = request.POST.get('type', 'like')
    response_data = {}
    user = get_object_or_404(User,pk=int(user_pk))
    post = get_object_or_404(Post,pk=int(post_pk))
    print(post.liked_by.all())
    if user in post.liked_by.all():
        print("I have already liked this post!!!")
    else:
        print("I have not yet liked this post!!!")
        if the_type == 'like':
            post.like(user)
        elif the_type == 'dislike':
            post.dislike(user)
        post.save()

    response_data['post_pk'] = post.pk
    response_data['likes'] = post.likes
    return HttpResponse(json.dumps(response_data), 
           content_type='application/json')

def about(request):
    context = {}
    return render(request, 'forum/about.html', context)

def contact(request):
    context = {}
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            #clean_msg = bleach.clean(form.message)
            cd = form.cleaned_data
            msg = cd['message']
            email = cd['email']
            # consider adding a subject fiedl
            #TODO code to send email goes here*
            # Then decide whether to redirect to home or some success page.
            # perhaps return success=True, then in the template, if success:
            # create a JS function that spawns an alert or dialog when page is
            # loaded. after "ok" is clicked, then it redirects to home.??
    else:
        form = ContactForm()
    context['form'] = form
    return render(request, 'forum/contact.html', context)






