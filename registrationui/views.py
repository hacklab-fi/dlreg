# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils.encoding import smart_text
from .forms import NewUserForm, PasswordChangeForm

import ldap
from ldap import modlist as modlist
from passlib.hash import ldap_md5_crypt
from .models import LdapGroup, LdapUser
from django.core.mail import send_mail

import random
import string

def index(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)

        if form.is_valid():
            username = smart_text(form.cleaned_data['username'])
            first_name = smart_text(form.cleaned_data['first_name'])
            last_name = smart_text(form.cleaned_data['last_name'])
            email = smart_text(form.cleaned_data['email'])
            password = smart_text(form.cleaned_data['password'])
            password2 = smart_text(form.cleaned_data['password2'])

# Python LDAP library doesn't like Unicode, so we convert everything to ascii here.
# If you figure out a way to use Unicode, please let me know!

            try:
                username.encode('ascii', 'strict')
                first_name.encode('ascii', 'strict')
                last_name.encode('ascii', 'strict')
                email.encode('ascii', 'strict')
                password.encode('ascii', 'strict')
                password2.encode('ascii', 'strict')

                con = ldap.initialize(settings.LDAP_URL) 
                con.bind(settings.LDAP_ADMIN_CN, settings.LDAP_PASSWORD, ldap.AUTH_SIMPLE)

# Figure out largest UID (is there a better way to do this?)
                users = LdapUser.objects.all()
                largestUid = 0
                for user in users:
                    if user.uid > largestUid:
                        largestUid = user.uid
                print('Largest UID', largestUid)

# Create the new user record:
                add_record = [
                  ('objectclass', [b'inetOrgPerson', b'posixAccount', b'top']),
                  ('givenName', [ first_name.encode('ascii') ]),
                  ('uidNumber', [ str(largestUid + 1).encode('ascii') ]),
                  ('gidNumber', [ b'501' ]),
                  ('cn', [ username.encode('ascii') ] ),
                  ('uid', [ username.encode('ascii') ] ),
                  ('sn', [ last_name.encode('ascii') ] ),
                  ('mail', [ email.encode('ascii') ] ),
                  ('userpassword', [ ldap_md5_crypt.encrypt(password).encode('ascii') ]),
                  ('homeDirectory', [ ('/home/' + username).encode('ascii') ]),
                  ('ou', [ b'users' ])
                ]
                usercn = 'cn=' + username + ',' + settings.LDAP_USERS_CN
                con.add_s(usercn, add_record)
                con.unbind()
            except ldap.ALREADY_EXISTS:
                form.add_error('username', "User already exists")
            except UnicodeEncodeError:
                form.add_error(None, 'Non-ascii characters inputted - use only a-z as ldap sucks with Unicode. Use Ä->A and Ö->O')
            except ldap.SERVER_DOWN:
                form.add_error(None, 'Unable to connect to LDAP server - please try again or report the problem to admins.')
            if form.is_valid():
                return HttpResponseRedirect('thanks')
    else:
        form = NewUserForm()
    return render(request, 'registrationui/index.html', { 'form': form, 'settings': settings } )

def thanks(request):
    return render(request, 'registrationui/thanks.html', { 'settings': settings } )

def admin(request):
    ldusers = LdapUser.objects.all()
    admins = LdapGroup.objects.get(name='admins').members

    return render(request, 'registrationui/admin.html', { 'settings': settings, 'users': ldusers, 'admins': admins } )

def delete(request, uid):
    user = LdapUser.objects.get(uid=uid)
    print(user)
    user.delete()

    return admin(request)

def randomStringDigits(stringLength=8):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

def pwreset(request, uid):
    user = LdapUser.objects.get(uid=uid)
    plainpassword = randomStringDigits()

    con = ldap.initialize(settings.LDAP_URL) 
    con.bind(settings.LDAP_ADMIN_CN, settings.LDAP_PASSWORD, ldap.AUTH_SIMPLE)

    con.passwd_s(user.user_dn(), None, plainpassword)

    send_mail(
        f'{settings.ORGANIZATION_NAME} password changed',
        f'Your password for user {user.username} at {settings.ORGANIZATION_NAME} is {plainpassword} - go change it now at {settings.DLREG_URL}/pwchange !!',
        settings.MAIL_FROM,
        [user.email],
        fail_silently=False,
    )
    return admin(request)

def pwchange(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)

        if form.is_valid():
            username = smart_text(form.cleaned_data['username'])
            oldpassword = smart_text(form.cleaned_data['oldpassword'])
            password = smart_text(form.cleaned_data['password'])
            password2 = smart_text(form.cleaned_data['password2'])

            if password == password2:
                user = LdapUser.objects.get(username=username)
                con = ldap.initialize(settings.LDAP_URL) 
                con.set_option(ldap.OPT_REFERRALS,0)
                try:
                    con.simple_bind_s(user.user_dn(), oldpassword)
                    con.passwd_s(user.user_dn(), oldpassword, password)
                    return render(request, 'registrationui/pwchanged.html', { 'settings': settings } )
                except ldap.INVALID_CREDENTIALS:
                    form.add_error(None, 'Wrong username or password')
            else:
                form.add_error('password', 'Passwords do not match!')

    else:
        form = PasswordChangeForm()

    return render(request, 'registrationui/pwchange.html', { 'form': form, 'settings': settings } )

def setadmin(request, uid, isadmin):
    user = LdapUser.objects.get(uid=uid)
    con = ldap.initialize(settings.LDAP_URL) 
    con.bind(settings.LDAP_ADMIN_CN, settings.LDAP_PASSWORD, ldap.AUTH_SIMPLE)
    con.set_option(ldap.OPT_REFERRALS,0)
    if isadmin == 1:
        if user.is_admin():
            print('User is already admin!')
        else:
            con.modify_s(
                settings.LDAP_ADMINS_CN,
                [
                    (ldap.MOD_ADD, 'memberUid', [user.user_dn().encode('ascii')]),
                ],
            )
    else:
        if not user.is_admin():
            print('User is already not admin!')
        else:
            con.modify_s(
                settings.LDAP_ADMINS_CN,
                [
                    (ldap.MOD_DELETE, 'memberUid', [user.user_dn().encode('ascii')]),
                ],
            )
    return admin(request)
