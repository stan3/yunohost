import pytest
import time
import requests

from moulinette.core import init_authenticator
from yunohost.app import app_install, app_change_url, app_remove, app_map
from yunohost.domain import _get_maindomain

from moulinette.core import MoulinetteError

# Instantiate LDAP Authenticator
AUTH_IDENTIFIER = ('ldap', 'as-root')
AUTH_PARAMETERS = {'uri': 'ldapi://%2Fvar%2Frun%2Fslapd%2Fldapi',
                   'base_dn': 'dc=yunohost,dc=org',
                   'user_rdn': 'gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth'}

auth = init_authenticator(AUTH_IDENTIFIER, AUTH_PARAMETERS)

# Get main domain
maindomain = _get_maindomain()


def setup_function(function):
    pass


def teardown_function(function):
    app_remove(auth, "change_url_app")


def install_changeurl_app(path):
    app_install(auth, "./tests/apps/change_url_app_ynh",
                args="domain=%s&path=%s" % (maindomain, path))


def check_changeurl_app(path):
    appmap = app_map(auth, raw=True)

    assert path + "/" in appmap[maindomain].keys()

    assert appmap[maindomain][path + "/"]["id"] == "change_url_app"

    r = requests.get("https://127.0.0.1%s/" % path, headers={"domain": maindomain}, verify=False)
    assert r.status_code == 200


def test_appchangeurl():
    install_changeurl_app("/changeurl")
    check_changeurl_app("/changeurl")

    app_change_url(auth, "change_url_app", maindomain, "/newchangeurl")

    # For some reason the nginx reload can take some time to propagate ...?
    time.sleep(2)

    check_changeurl_app("/newchangeurl")

def test_appchangeurl_sameurl():
    install_changeurl_app("/changeurl")
    check_changeurl_app("/changeurl")

    with pytest.raises(MoulinetteError):
        app_change_url(auth, "change_url_app", maindomain, "changeurl")
