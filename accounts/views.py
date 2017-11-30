#coding=utf-8
'''
Created on Dec 1, 2016

@author: Felix
'''

import random
from io import BytesIO
from urllib import parse
from PIL import Image, ImageDraw

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, \
                                logout, \
                                login, \
                                get_user_model
from django.core.mail import send_mail
from django.core.signing import TimestampSigner, \
                                SignatureExpired, \
                                BadSignature
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required

from .forms import LoginForm, \
                   SignupForm,\
                   ResetPasswordForm1st,\
                   ResetPasswordForm2nd,\
                   ChangePasswordForm,\
                   ProfileForm
from .forms import AccountErrorList

def captcha(request):
    '''Captcha'''
    image = Image.new('RGB', (147, 49), color = (255, 255, 255))
    draw = ImageDraw.Draw(image)
    randstr = ''.join(random.sample(settings.HUMAN_FRIENDLY_CHARSET, 4))
    draw.text((7, 0), randstr, fill=(0, 0, 0), font=settings.CAPTURE_FONT_OBJECT)
    del draw
    request.session['captcha'] = randstr.lower()
    buf = BytesIO()
    image.save(buf, 'jpeg')
    return HttpResponse(buf.getvalue(), 'image/jpeg')

def check_captcha(request, template, form):
    '''called when form.is_valid() is true'''
    if not request.session.get('_captcha', False):
        return
    
    cleaned_data = form.cleaned_data
    session_captcha = request.session.get('captcha', None)
    client_captcha = cleaned_data.get('captcha', None)
    if session_captcha:
        if not client_captcha or client_captcha.lower() != session_captcha:
            form.add_error('captcha', _('wrong Captcha, you can change the captcha by clicking the image'))
            return render(request, template, {'form': form, 'captcha': True})

def login_(request, template):
    '''login a user, use login_ to avoid name collision'''
    nexturl = request.GET.get('next', '/')
    _captcha = request.session.get('_captcha', False)
    
    if request.method == 'GET':
        if request.user.is_authenticated():
            return redirect(nexturl)
        form = LoginForm(initial={'remember': True}, error_class=AccountErrorList)
        return render(request, template, {'form': form, 'captcha': _captcha})
    elif request.method == 'POST':
        form = LoginForm(request.POST, error_class=AccountErrorList)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            
            response = check_captcha(request, template, form)
            if response:
                return response
   
            user = authenticate(**cleaned_data)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    remember = request.POST.get('remember')
                    if remember:
                        request.session.set_expiry(0)
                    request.session['_captcha'] = False
                    return redirect(nexturl)
                else:
                    form.full_clean()
                    message = _('this account is inactive.')
                    form.add_error(None, message)
                    return render(request, template, {'form': form, 'captcha': _captcha})
            else:
                form.full_clean()
                message = _('account and password doesn\'t match')
                form.add_error(None, message)
                return render(request, template, {'form': form, 'captcha': _captcha})
        else:
            return render(request, template, {'form': form, 'captcha': _captcha})
        
def logout_(request):
    logout(request)
    return redirect('/')

def signup(request, template):
    nexturl = request.GET.get('next', '/')
    _captcha = request.session.get('_captcha', False)
    
    if request.method == 'GET':
        form = SignupForm()
        return render(request, template, {'form': form, 'captcha': _captcha})
    elif request.method == 'POST':
        form = SignupForm(request.POST, error_class=AccountErrorList)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            
            response = check_captcha(request, template, form)
            if response:
                return response
            
            UserModel = get_user_model()
            
            email = cleaned_data['email']
            user = UserModel.objects.filter(email=email)
            if user.exists():
                message = _('this email is already registered')
                form.add_error(None, message)
                return render(request, template, {'form': form, 'captcha': _captcha})
            
            email_domain = email.split('@')[1]
            if not email_domain in settings.EMAIL_DOMAIN_WHITELIST:
                message = _('only work email allowed')
                form.add_error(None, message)
                return render(request, template, {'form': form, 'captcha': _captcha})
            
            password, password2nd = cleaned_data['password'], cleaned_data['password2nd']
            if password != password2nd:
                message = _('password mismatched from the second input')
                form.add_error('password', message)
                return render(request, template, {'form': form, 'captcha': _captcha})
            
            try:
                user = UserModel.objects.create(email=email, is_active=True)
                user.set_password(password)
                user.save()
            except:
                message = _('server error, please try again later')
                form.add_error(None, message)
                return render(request, template, {'form': form, 'captcha': _captcha})
            else:
                login(request, user)
                return redirect(nexturl)
        else:
            return render(request, template, {'form': form, 'captcha': _captcha})
                
@login_required
def profile(request, template):
    user = request.user
    if request.method == 'GET':
        form = ProfileForm(initial={'first_name': user.first_name, 'last_name': user.last_name})
        return render(request, template, {'form': form})
    elif request.method == 'POST':
        form = ProfileForm(request.POST, error_class=AccountErrorList) # Change first_name, last_name, username
        if form.is_valid():
            cleaned_data = form.cleaned_data
            if cleaned_data['captcha'].lower() != request.session['captcha']:
                form.add_error('captcha', _('Wrong Captcha, you can change the captcha by clicking the image'))
                return render(request, template, {'form': form})
  
            user.first_name = cleaned_data['first_name']
            user.last_name = cleaned_data['last_name']
            user.save()
            message = _('All change applied!')
            messages.success(request, message)
        return render(request, template, {'form': form})

@login_required
def lock(request, template):
    if request.method == 'GET':
        request.session['LOCKED'] = True
        form = None
        return render(request, template, {'form': form})
    elif request.method == 'POST':
        request.session['LOCKED'] = False
        
 
@login_required
def changepassword(request, template):
    '''Renew the password'''
    _captcha = request.session.get('_captcha', False)
    user = request.user
     
    if request.method == 'GET':
        form = ChangePasswordForm()
        return render(request, template, {'form': form})
    elif request.method == 'POST':
        form = ChangePasswordForm(request.POST, error_class=AccountErrorList)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            
            response = check_captcha(request, template, form)
            if response:
                return response
            
            password, newpassword = cleaned_data['password'], cleaned_data['newpassword']
            if not user.check_password(password):
                form.add_error('password', 'current password is wrong.')
            else:
                user.set_password(newpassword)
                user.save()
                message = _('new password is saved !')
                messages.success(request, message)
        return render(request, template, {'form': form})    
 
def resetpassword(request, resetpassword1st_template, resetpassword2nd_template):
    '''reset password'''
    _captcha = request.session.get('_captcha', False)
    
    if request.method == 'GET':
        sig = request.GET.get('sig', None)
        if sig is None:
            form = ResetPasswordForm1st()
            return render(request, 
                          resetpassword1st_template, 
                          {'form': form, 'captcha': _captcha})
        else:
            form = ResetPasswordForm2nd()
            return render(request, 
                          resetpassword2nd_template, 
                          {'form': form, 'captcha': _captcha})
         
    elif request.method == 'POST':
        sig = request.GET.get('sig', None)
        UserModel = get_user_model()
        signer = TimestampSigner(salt='X')
        SIG_EXPIRE = 86400 # seconds, 1day
        
        if sig is None:
            form = ResetPasswordForm1st(request.POST, error_class=AccountErrorList)
            if form.is_valid():
                cleaned_data = form.cleaned_data
                email = cleaned_data['email']
                response = check_captcha(request, 
                                         resetpassword1st_template, 
                                         form)
                if response:
                    return response

                user = UserModel.objects.filter(email=email)
                if not user.exists():
                    message = _('email not exists')
                    form.add_error('email', message)
                    return render(request, 
                                  resetpassword1st_template, 
                                  {'form': form, 'captcha': _captcha})
                else:
                    # Here we will send the password reset url to the email address
                    sig = signer.sign(email)
                    qs = parse.urlencode({'sig': sig})
                    parsed_data = parse.ParseResult(scheme='http', 
                                                    netloc='127.0.0.1:8000', 
                                                    path='/accounts/resetpassword/', 
                                                    params = '', 
                                                    query=qs, 
                                                    fragment='')
                    url = parse.urlunparse(parsed_data)
                    send_mail('Reset Password', 
                              'Reset URL is: %s' % url, 
                              '127.0.0.1', 
                              [email], 
                              fail_silently=False)
                    message = _('the password reset url has been sent to your email address, check your email to continue')
                    messages.success(request, message)
            return render(request, 
                          resetpassword1st_template, 
                          {'form': form, 'captcha': _captcha})
        elif sig is not None:
            form = ResetPasswordForm2nd(request.POST, error_class=AccountErrorList)
            if form.is_valid():
                cleaned_data = form.cleaned_data
                
                response = check_captcha(request, 
                                         resetpassword2nd_template, 
                                         form)
                if response:
                    return response
              
                try:
                    unsig = signer.unsign(sig, max_age=SIG_EXPIRE)
                    if sig.startswith(unsig):
                        user = UserModel.objects.filter(email=unsig)
                        if not user.exists():
                            form.full_clean()
                            message = _('user not exists')
                            form.add_error(None, message)
                        else:
                            user = UserModel.objects.get(email=unsig)
                            password, password2nd = cleaned_data['password'], cleaned_data['password2nd']
                            if password == password2nd:
                                user.set_password(password)
                                user.save()
                                message = _('reset password successfully')
                                messages.success(request, message)
                            else:
                                message = _('password mismatched from the second input')
                                form.add_error('password', message)
                    else:
                        form.full_clean()
                        message = _('wrong signature')
                        form.add_error(None, message)
                except SignatureExpired:
                    form.full_clean()
                    message = _('signature expired.')
                    form.add_error(None, message)
                except BadSignature:
                    message = _('bad signature')
                    form.add_error(None, message)
                         
            return render(request, 
                          resetpassword2nd_template, 
                          {'form': form, 'captcha': _captcha})
