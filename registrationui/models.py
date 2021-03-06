from django.db import models
from ldapdb.models.fields import CharField, IntegerField, ListField
import ldapdb.models
from ldapdb.models import fields

# Create your models here.

class LdapGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP group entry.
    """
    # LDAP meta-data
    base_dn = "ou=groups,dc=ldap"
    object_classes = ['posixGroup']

    # posixGroup attributes
    gid = IntegerField(db_column='gidNumber', unique=True)
    name = CharField(db_column='cn', max_length=200, primary_key=True)
    members = ListField(db_column='memberUid')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class LdapUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """
    # LDAP meta-data
    base_dn = "dc=ldap"
    object_classes = ['posixAccount']
#    object_classes = ['account', 'posixAccount', 'shadowAccount', 'inetOrgPerson']
#    last_modified = fields.DateTimeField(db_column='modifyTimestamp')

    # inetOrgPerson
    first_name = fields.CharField(db_column='givenName', verbose_name="Prime name")
    last_name = fields.CharField("Final name", db_column='sn')
    full_name = fields.CharField(db_column='cn')
    email = fields.CharField(db_column='mail')
    phone = fields.CharField(db_column='telephoneNumber', blank=True)

    # posixAccount
    uid = fields.IntegerField(db_column='uidNumber', unique=True)
    group = fields.IntegerField(db_column='gidNumber')
    username = fields.CharField(db_column='uid', primary_key=True)
    password = fields.CharField(db_column='userPassword')

    def user_dn(self):
        return f'cn={self.username},{self.base_dn}'

    def is_admin(self):
        admins = LdapGroup.objects.get(name='admins')
        members = admins.members
        print('admins members', members, 'my dn', self.user_dn())
        return self.user_dn() in members

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.full_name
