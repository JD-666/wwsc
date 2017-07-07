from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

from datetime import datetime


class Profile(models.Model):
    """ Custom User model to add additional data on top of the User model
    provided in auth.User. It is better practice to link this Profile to
    auth.User using a OneToOneField() rather than inheriting and overriding
    because if you had other applications in the same project they may need the
    original auth.User without the additional data or with different data. 
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # additional attributes we wish to add
    picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    def get_upload_name(instance, filename):
        """ NOT CURRENTLY IN USE, WILL HAVE THE VIEW HANDLE THIS. 
        """
        name = ("profile_pics/{}_{}"
                .format(str(time()).replace(".","_"), filename))
        return name

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Callback for a signal sent when User Model involkes it's save()
    method. This will automatically create an associated Profile() instance. 
    """
    print(created)
    print(instance)
    if created:
        Profile.objects.create(user=instance)
    return
    
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ Callback for a signal sent when a User Model involkes it's save() 
    method. This will automatically save the associated Profile() instance. 
    """
    instance.profile.save()
    return


        
class Category(models.Model):
    """ Category is a group of 'Threads'.
    """
    # 'recent_post' is a timestamp of most recent post in this category
    # 'get_upload_name()' is a helper func to add timestamp to filename
    name = models.CharField(max_length=100, unique=True)
    most_recent_post = models.DateTimeField(blank=True, null=True)
    image = models.FileField(upload_to='category_images', blank=True, null=True)
    num_threads = models.IntegerField(default=0)
    num_posts = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def new(self, *args, **kwargs):
        # validate some attributes
        if self.num_threads < 0:
            self.num_threads = 0
        if self.num_posts < 0:
            self.num_posts = 0
        # create slug
        self.slug = slugify(self.name)
        # call origional save to commit data to DB
        self.save(*args, **kwargs)
        return

    def get_upload_name(instance, filename):
        """ NOT CURRENTLY IN USE. WILL HAVE THE VIEW HANDLE THIS
        """
        name = ("category_images/{}_{}"
                .format(str(time()).replace(".","_"), filename))
        return name

    class Meta:
        """ Additional information.
        """
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Thread(models.Model):
    """ Thread is a collection of posts in a forum. Usually a Thread is about
    a single topic. 
    """
    name = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User)
    created_date = models.DateTimeField(default=timezone.now)
    most_recent_post = models.DateTimeField(blank=True, null=True)
    num_posts = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def approve(self):
        """ Function to set 'approved' flag. Only approved Threads will be
        shown. Admin users will have to approve a Thread request. 
        """
        self.approved = True
        self.save()

    def new(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.category.num_threads += 1
        self.save(*args, **kwargs)
        return

    def __str__(self):
        return self.name


class Post(models.Model):
   """ DB model to store content of a specific Category->Thread->Post. 
   """
   text = models.TextField()
   author = models.ForeignKey(User)
   thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
   created_date = models.DateTimeField(default=timezone.now)

   def new(self, *args, **kwargs):
       self.thread.most_recent_post = self.created_date
       self.thread.num_posts += 1
       self.thread.category.most_recent_post = self.created_date
       self.thread.category.num_posts += 1
       self.thread.save()
       self.thread.category.save()
       self.save(*args, **kwargs)
       return

   def __str__(self):
       return self.text

class Conversation(models.Model):
    """ Object to keep track of a group of Pm objects (Private Messages) and 
    associate them with two specific users. We will create two conversation
    objects for each conversation. One belonging to each User participating
    in the conversation.
    """
    belongs_to = models.ForeignKey(User, related_name='conversation_belongs_to')
    is_with = models.ForeignKey(User, related_name='conversation_is_with')


class Pm(models.Model):
    """ Private Message object. We will create two instances of each Pm and
    assign one to each Conversation instance. Essentially each User will have 
    his own copy of a Pm (This way one user can delete their Pm's, and it won't
    delete it for the other user too).
    """
    text = models.TextField()
    author = models.ForeignKey(User)
    created_date = models.DateTimeField(default=timezone.now)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    class Meta:
        ordering = ['created_date']
        
    def __str__(self):
        return self.text


