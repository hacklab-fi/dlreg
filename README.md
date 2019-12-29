# dlreg

Django-based minimalistic LDAP user self-registration service.

A simple web form to add user. Asks for username, first & last name, etc and
adds the user to LDAP.

Supports also verification question, that must be answered correctly. This is
to avoid spambots registering junk accounts.

Contributions welcome!

## OpenLDAP

https://github.com/osixia/docker-openldap

```bash
ldapadd -x -H ldap://localhost -D "cn=admin,dc=ldap" -w admin -f init.ldif
```

## Docker

Create image:
```bash
docker build -t dlreg:latest .
```
Create local_settings.py from settings_local.py_template:
```
cp settings_local.py_template settings_local.py
$EDITOR settings_local.py
```

Run image:
```
docker run -it --name dlreg -p 8887:8000 --mount type=bind,source="$PWD/settings_local.py",target=/dlreg/dlreg/settings_local.py,readonly dlreg:latest
```
The registration UI should now be visible at http://localhost:8887/

By Ville Ranki <ville.ranki@iki.fi>

