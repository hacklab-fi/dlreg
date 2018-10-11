# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils.encoding import smart_text
from .forms import NewUserForm

import ldap
from passlib.hash import ldap_md5_crypt

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
                base_dn = settings.LDAP_USERS_CN
                filter = '(objectclass=person)'
                attrs = ['uidNumber']
                uidList = con.search_s( base_dn, ldap.SCOPE_SUBTREE, filter, attrs )
                largestUid = 0
                for user in uidList:
                    uid = int(user[1]['uidNumber'][0])
                    if uid > largestUid:
                        largestUid = uid

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
