from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from .forms import NewUserForm

import ldap
from passlib.hash import ldap_md5_crypt

def index(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)

        if form.is_valid():
	    username = form.cleaned_data['username']
	    first_name = form.cleaned_data['first_name']
	    last_name = form.cleaned_data['last_name']
	    email = form.cleaned_data['email']
	    password = form.cleaned_data['password']
            password2 = form.cleaned_data['password2']

	    con = ldap.initialize(settings.LDAP_URL) 
	    con.bind(settings.LDAP_ADMIN_CN, settings.LDAP_PASSWORD, ldap.AUTH_SIMPLE)

# Figure out largest UID (is there a better way to do this?)
	    base_dn = settings.LDAP_USERS_CN
	    filter = '(objectclass=person)'
	    attrs = ['uidNumber']
	    uidList = con.search_s( base_dn, ldap.SCOPE_SUBTREE, filter, attrs )
#	    print "Uids: " + str( uidList )
	    largestUid = 0
	    for user in uidList:
		uid = int(user[1]['uidNumber'][0])
		if uid > largestUid:
		    largestUid = uid

#	    print 'Largest Uid:' + str(largestUid)

# Create the new user record:
	    add_record = [
	      ('objectclass', ['inetOrgPerson', 'posixAccount']),
	      ('givenName', [str(first_name)]),
	      ('uidNumber', [ str(largestUid + 1)]),
	      ('gidNumber', ['501']),
	      ('cn', [str(username)] ),
	      ('sn', [str(last_name)] ),
	      ('userpassword', [ldap_md5_crypt.encrypt(password)]),
	      ('homeDirectory', [str('/home/' + username)]),
	      ('ou', ['users'])
	    ]
	    try:
                con.add_s('uid=' + str(username) + ',' + settings.LDAP_USERS_CN, add_record)
	    except ldap.ALREADY_EXISTS:
		form.add_error('username', "User already exists")
	    con.unbind()
	    if form.is_valid():
	        return HttpResponseRedirect('thanks')

    else:
        form = NewUserForm()

    return render(request, 'registrationui/index.html', { 'form': form, 'settings': settings } )

def thanks(request):
    return render(request, 'registrationui/thanks.html', { 'settings': settings } )

