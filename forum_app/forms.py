from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from forum_app.models import Profile, Category, Thread, Post, Conversation, Pm


class CategoryForm(forms.ModelForm):
    image = forms.FileField(required=False)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = Category
        fields = ('name', 'image')


class ThreadForm(forms.ModelForm):
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = Thread
        fields = ('name',)
    def __init__(self, *args, **kwargs):
        super(ThreadForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'style':"width:100%"})


class PostForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea, required=True)
    class Meta:
        model = Post
        fields = ('text',)

class PmForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea, required=True)
    class Meta:
        model = Pm
        fields = ('text',)

class UserForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs=
            {'placeholder':'enter email'}))
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    # add attributed to the HTML input elements
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'placeholder':'enter username'})
        self.fields['email'].widget.attrs.update(
            {'placeholder':'enter email'})
        self.fields['password1'].widget.attrs.update(
            {'placeholder':'enter password'})
        self.fields['password2'].widget.attrs.update(
            {'placeholder':'confirm password'})
    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.email = self.cleaned_data['email'] # built in scrubber func
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    picture = forms.ImageField(required=False)
    class Meta:
        model = Profile
        fields = ('picture',)

    