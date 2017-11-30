#coding=utf-8
'''
Created on Dec 1, 2016

@author: Felix
'''
from django import forms
from django.core.validators import EmailValidator, MinLengthValidator
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _

class AccountErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()
    
    def __unicode__(self):
        return self.as_divs()
    
    def as_divs(self):
        if not self:
            return ''
        return '<div class="alert alert-danger">%s</div>' \
            % ''.join(['<div class="error"><div class="glyphicon glyphicon-exclamation-sign"></div> <strong>%s</strong></div>' % e for e in self])

class LoginForm(forms.Form):
    '''for user login'''
    email = forms.EmailField(required=True, 
                             label=_("Work Email"),
                             validators=[EmailValidator(),], 
                             widget=forms.EmailInput(attrs={'id': 'email', 
                                                            'placeholder': _("Work Email"), 
                                                            'class': 'form-control', 
                                                            'required':'true', 
                                                            'autofocus': 'true'}))
    password = forms.CharField(required=True, 
                               label=_("Password"), 
                               max_length=64,
                               widget=forms.PasswordInput(attrs={'id': 'password', 
                                                                 'placeholder': _("Password"), 
                                                                 'class': 'form-control', 
                                                                 'required': 'true'}))
    remember = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'id': 'remember'}))
    captcha = forms.CharField(required=False, 
                              max_length=4, 
                              label=_("Captcha"), 
                              widget=forms.TextInput(attrs={'id': 'captcha', 
                                                            'placeholder': _("Captcha"), 
                                                            'class': 'form-control', 
                                                            'required': 'true'}))
class SignupForm(forms.Form):
    '''for user sign up'''
    email = forms.EmailField(required=True, 
                             label=_("Work Email"),
                             validators=[EmailValidator(),], 
                             widget=forms.EmailInput(attrs={'id': 'email', 
                                                            'placeholder': _("Work Email"), 
                                                            'class': 'form-control', 
                                                            'required':'true', 
                                                            'autofocus': 'true'}))
    password = forms.CharField(required=True, 
                               label=_("Password"), 
                               max_length=64, 
                               validators=[MinLengthValidator(7),], 
                               widget=forms.PasswordInput(attrs={'id': 'password', 
                                                                 'placeholder': _("Password"), 
                                                                 'class': 'form-control', 
                                                                 'required': 'true'}))
    password2nd = forms.CharField(required=True, 
                               label=_("Password"), 
                               max_length=64, 
                               validators=[MinLengthValidator(7),], 
                               widget=forms.PasswordInput(attrs={'id': 'password2nd', 
                                                                 'placeholder': _("Password Again"), 
                                                                 'class': 'form-control', 
                                                                 'required': 'true'}))
    captcha = forms.CharField(required=False, 
                              max_length=4, 
                              label=_("Captcha"), 
                              widget=forms.TextInput(attrs={'id': 'captcha', 
                                                            'placeholder': _("Captcha"), 
                                                            'class': 'form-control', 
                                                            'required': 'true'}))

class ResetPasswordForm1st(forms.Form):
    '''Reset password form 1'''
    email = forms.EmailField(required=True,
                             label=_("Work Email"),
                             validators=[EmailValidator(),], 
                             widget=forms.EmailInput(attrs={'id': 'email', 
                                                            'placeholder': _('Work Email'), 
                                                            'class': 'form-control', 
                                                            'required':'true', 
                                                            'autofocus': 'true'}))
    captcha = forms.CharField(required=False, 
                              label=_("Captcha"),
                              max_length=4, 
                              widget=forms.TextInput(attrs={'id': 'captcha', 
                                                            'placeholder': _('Captcha'), 
                                                            'class': 'form-control', 
                                                            'required': 'true'}))

class ResetPasswordForm2nd(forms.Form):
    '''Reset password form 2'''
    password = forms.CharField(required=True, 
                               max_length=64, 
                               validators=[MinLengthValidator(7)], 
                               widget=forms.PasswordInput(attrs={'id': 'newpassword', 
                                                                    'placeholder': _('Password'), 
                                                                    'class': 'form-control', 
                                                                    'required': 'true',
                                                                    'autofocus': 'true'}))
    password2nd = forms.CharField(required=True, 
                               max_length=64, 
                               validators=[MinLengthValidator(7)], 
                               widget=forms.PasswordInput(attrs={'id': 'newpassword', 
                                                                    'placeholder': _('Password Again'), 
                                                                    'class': 'form-control', 
                                                                    'required': 'true',
                                                                    'autofocus': 'true'}))
    captcha = forms.CharField(required=False, 
                              max_length=4, 
                              widget=forms.TextInput(attrs={'id': 'captcha', 
                                                            'placeholder': _('Captcha'), 
                                                            'class': 'form-control', 
                                                            'required': 'true'}))


class ChangePasswordForm(forms.Form):
    '''Renew password form'''
    password = forms.CharField(required=True, 
                               max_length=64, 
                               validators=[], 
                               widget=forms.PasswordInput(attrs={'id': 'currentpassword', 
                                                                 'placeholder': _('Current Password'), 
                                                                 'class': 'form-control', 
                                                                 'required': 'true'}))
    newpassword = forms.CharField(required=True, 
                                  max_length=64, 
                                  validators=[MinLengthValidator(7)], 
                                  widget=forms.PasswordInput(attrs={'id': 'newpassword', 
                                                                    'placeholder': _('New Password'), 
                                                                    'class': 'form-control', 
                                                                    'required': 'true'}))
    captcha = forms.CharField(required=False,
                              label=_("Captcha"),
                              max_length=4, 
                              widget=forms.TextInput(attrs={'id': 'captcha', 
                                                            'placeholder': _('Captcha'), 
                                                            'class': 'form-control', 
                                                            'required': 'true'}))

class ProfileForm(forms.Form):
    '''Profile form'''
    first_name = forms.CharField(required=False, 
                                 widget=forms.TextInput(attrs={'id': 'first_name', 
                                                               'placeholder': _('First Name'), 
                                                               'class': 'form-control'}))
    last_name = forms.CharField(required=False, 
                                widget=forms.TextInput(attrs={'id': 'last_name', 
                                                              'placeholder': _('Last Name'), 
                                                              'class': 'form-control'}))
    captcha = forms.CharField(required=False, 
                              max_length=4, widget=forms.TextInput(attrs={'id': 'captcha', 
                                                                          'placeholder': _('Captcha'), 
                                                                          'class': 'form-control', 
                                                                          'required': 'true'}))