# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils.encoding import smart_text
from .forms import NewUserForm, PasswordChangeForm, LoginForm

import ldap
from ldap import modlist as modlist
from passlib.hash import ldap_md5_crypt
from .models import LdapGroup, LdapUser
from django.core.mail import send_mail

import random
import string

def is_admin(request):
    try:
        if request.session.get('username', None):
                user = LdapUser.objects.get(username=request.session['username'])
                return user.is_admin()
    except:
        print('Error getting user for is_admin')
    return False

def randomStringDigits(stringLength=8):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

def make_admin_user_if_none():
    users = LdapUser.objects.all()
    admin_exists = False
    for user in users:
        if user.is_admin():
            admin_exists = True
    if not admin_exists:
        create_ldap_user('admin', 'Admin', 'User', 'admin@ldap.invalid', settings.LDAP_PASSWORD)
        set_ldap_user_admin('admin', 1)
        print('Admin user created')

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

            if password != password2:
                form.add_error('password', 'Passwords do not match')
            else:
                try:
                    create_ldap_user(username, first_name, last_name, email, password)
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

def create_ldap_user(username, first_name, last_name, email, password):
# Python LDAP library doesn't like Unicode, so we convert everything to ascii here.
# If you figure out a way to use Unicode, please let me know!

    username.encode('ascii', 'strict')
    first_name.encode('ascii', 'strict')
    last_name.encode('ascii', 'strict')
    email.encode('ascii', 'strict')
    password.encode('ascii', 'strict')

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

def thanks(request):
    return render(request, 'registrationui/thanks.html', { 'settings': settings } )

def admin(request):
    make_admin_user_if_none()
    if is_admin(request):
        ldusers = LdapUser.objects.all()
        admins = LdapGroup.objects.get(name='admins').members

        return render(request, 'registrationui/admin.html', { 'settings': settings, 'users': ldusers, 'admins': admins } )
    else:
        return login(request)

def delete(request, uid):
    if not is_admin(request):
        return login(request)
    user = LdapUser.objects.get(uid=uid)
    user.delete()

    return admin(request)

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

def set_ldap_user_admin(username, isadmin):
    user = LdapUser.objects.get(username=username)
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

def setadmin(request, uid, isadmin):
    if not is_admin(request):
        return login(request)
    set_ldap_user_admin(username, isadmin)
    return admin(request)

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = smart_text(form.cleaned_data['username'])
            password = smart_text(form.cleaned_data['password'])

            try:
                user = LdapUser.objects.get(username=username)
                con = ldap.initialize(settings.LDAP_URL) 
                con.set_option(ldap.OPT_REFERRALS,0)
                con.simple_bind_s(user.user_dn(), password)
                if user.is_admin():
                    request.session['username'] = username
                    return render(request, 'registrationui/admin.html', { 'settings': settings } )
                
                form.add_error(None, 'Login ok, but you are not admin')

            except ldap.INVALID_CREDENTIALS:
                form.add_error(None, 'Wrong username or password')
            except LdapUser.DoesNotExist:
                form.add_error(None, 'Wrong username or password')
    else:
        request.session['username'] = None
        form = LoginForm()

    return render(request, 'registrationui/login.html', { 'form': form, 'settings': settings } )

def logout(request):
    request.session['username'] = None
    return login(request)
