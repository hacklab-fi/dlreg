from django.contrib import admin
from . import models

class LDAPGroupAdmin(admin.ModelAdmin):
    exclude = ['dn', 'objectClass']
    list_display = ['gid', 'name']

admin.site.register(models.LDAPGroup, LDAPGroupAdmin)
