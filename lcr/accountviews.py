# -*- coding: utf-8 -*-
# Class Base Views
# https://docs.djangoproject.com/en/1.11/topics/class-based-views/
# User authentication in Django
# https://docs.djangoproject.com/en/1.11/topics/auth/
# Logging
# https://docs.djangoproject.com/en/1.11/topics/logging/
# http://gswd-a-crash-course-pycon-2014.readthedocs.io/en/latest/authviews.html
# https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
# https://docs.djangoproject.com/en/1.11/topics/auth/default/
# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication
from __future__ import unicode_literals
from __future__ import absolute_import

from django.views import generic
from django.utils.http import url_has_allowed_host_and_scheme

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from django.shortcuts import render, redirect

from .forms import RegistrationForm
from .forms import LoginForm
from .forms import PasswordChangeForm

class SignUpView(
                 generic.CreateView):

    form_class = RegistrationForm
    model = User
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')
    form_valid_message = "Sign Up finished successfully, please log in with you username and password."


class LoginView(generic.FormView):
    form_class = LoginForm
    success_url = reverse_lazy('home')
    template_name = 'accounts/login.html'
    redirect_field_name = REDIRECT_FIELD_NAME
    form_valid_message = 'Logged in successfully.'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(self.request, user)
            return super(LoginView, self).form_valid(form)
        else:
            return self.form_invalid(form)


    def get_success_url(self):
        redirect_to = self.request.GET.get(self.redirect_field_name)
        if not url_has_allowed_host_and_scheme(redirect_to, self.request.get_host()):
            redirect_to = self.success_url
        return redirect_to


class LogOutView(generic.RedirectView):
    url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogOutView, self).get(request, *args, **kwargs)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'accounts/change_password.html', {
                'form': form
                    })

class NoPermissionView(generic.TemplateView):
    template_name = 'accounts/no_permission.html'

    def get(self, request, *args, **kwargs):
        return super(NoPermissionView, self).get(request, *args, **kwargs)
