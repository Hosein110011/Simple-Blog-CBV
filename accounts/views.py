from typing import Any
from django import http
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import UserRegistrationForm, UserLoginForm, EditUserForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Relation
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy


class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'account/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form':form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(cd['username'], cd['email'], cd['password1'])
            messages.success(request, 'you registered successfully', 'success')
            return redirect('home:home')
        return render(request, self.template_name, {'form':form})
    

class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'account/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form':form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'you logged in successfully', 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(request, 'username or password is wrong', 'warning')
        return render(request, self.template_name, {'form':form})
    

class UserLogoutView(LoginRequiredMixin,View):
    def get(self, request):
        logout(request)
        messages.success(request, 'you logged out successfully', 'success')
        return redirect('home:home')
    

class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        is_following = False
        user = get_object_or_404(User, pk=user_id)
        posts = user.posts.all()
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            is_following = True
        return render(request, 'account/profile.html', {'user':user, 'posts':posts, 'is_following':is_following})
    

class UserPasswordResetView(PasswordResetView):
    template_name = 'account/password_reset_form.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = 'account/password_reset_email.html'


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account:password_reset_complete')


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'


class UserFollowView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs['user_name'])
        if user.id != request.user.id:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, 'you cant follow/unfollow your account', 'danger')
            return redirect('account:user_profile',user.id)
        
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            relation.delete()
            messages.success(request, 'you unfollowed this user', 'success')
        else:
            messages.error(request, 'you are not following this user', 'danger')
        return redirect('account:user_profile', user.id)
    


class UserUnfollowView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        user = User.objects.get(id = kwargs['user_id'])
        if user.id != request.user:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, 'you cant follow or unfollow your account', 'danger')
            return redirect('account:user_profile', user.id)

    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user=request.user,to_user=user)
        if relation.exists():
            relation.delete()
            messages.success(request, 'you unfollowed this user', 'success')
        else:
            messages.error(request, 'you are not following this user', 'danger')
        return redirect('account:user_profile', user_id)
    

class EditUserView(LoginRequiredMixin, View):
    form_class = EditUserForm
    def get(self, request):
        form = self.form_class(instance=request.user.profile, initial={'email':request.user.email})
        return render(request, 'account/edit_profile.html', {'form':form})
    
    def post(self, request):
        form = self.form_class(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'profile edited successfully', 'success')
        return redirect('account:user_profile', request.user.id)
    
    