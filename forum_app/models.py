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

    def save(self, *args, **kwargs):
        """ Overrides the save method to create a slug attribute based on
        name then continue to call normal save() method again like normal. 
        Also ensures num_threads and num_posts are valid.
        """
        # validate some attributes
        if self.num_threads < 0:
            self.num_threads = 0
        if self.num_posts < 0:
            self.num_posts = 0
        # Only new Posts will update this field
        if self.most_recent_post:
            self.most_recent_post = None
        # create slug
        self.slug = slugify(self.name)
        # call origional save to commit data to DB
        super(Category, self).save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        """ Overrides the save method to create a slug attribute based on
        name then continue to call normal save() method again like normal. 
        """
        self.slug = slugify(self.name)
        super(Thread, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
   """ DB model to store content of a specific Category->Thread->Post. 
   """
   text = models.TextField()
   author = models.ForeignKey(User)
   thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
   created_date = models.DateTimeField(default=timezone.now)

   def __str__(self):
       return self.text

    

        