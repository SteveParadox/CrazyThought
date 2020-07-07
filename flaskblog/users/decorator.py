from functools import wraps

from flask import flash, url_for, redirect
from flask_login import current_user


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('users.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function
