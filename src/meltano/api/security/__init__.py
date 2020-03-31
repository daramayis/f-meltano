import urllib.parse
from datetime import timedelta
from functools import wraps
from flask import current_app, request, redirect, jsonify, make_response
from flask_login import current_user, user_logged_in
from flask_security import Security, login_required
from flask_security.utils import login_user
from flask_principal import identity_loaded, Identity

from .identity import users, FreeUser, ReadOnlyUser, create_dev_user
from .forms import MeltanoLoginForm, MeltanoRegisterFrom, MeltanoConfirmRegisterForm
from .auth import (
    unauthorized_callback,
    _user_logged_in_hook,
    _identity_loaded_hook,
    api_auth_required,
)


# normally one would setup the extension accordingly, but it
# seems Security.init_app() overwrites all the configuration
security = Security()


def setup_security(app, project):
    options = {
        "login_form": MeltanoLoginForm,
        "register_form": MeltanoRegisterFrom,
        "confirm_register_form": MeltanoConfirmRegisterForm,
    }

    if not app.config["MELTANO_AUTHENTICATION"]:
        if app.config["MELTANO_READONLY"]:
            # the ReadOnlyUser is free to read, but not write
            options["anonymous_user"] = ReadOnlyUser
        else:
            # the FreeUser is free to do everything and has all
            # roles and permissions automatically.
            options["anonymous_user"] = FreeUser

    security.init_app(app, users, **options)
    security.unauthorized_handler(unauthorized_callback)
    user_logged_in.connect_via(app)(_user_logged_in_hook)
    identity_loaded.connect_via(app)(_identity_loaded_hook)
