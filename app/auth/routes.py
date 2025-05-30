# app/auth/routes.py

from flask import (
    render_template, flash, redirect, url_for,
    request, current_app
)
from flask_login import (
    current_user, login_user, logout_user, login_required
)
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.auth.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
    EditProfileForm
)
from app.models import User
from app.email import send_password_reset_email

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    Show form to submit your email for a reset link.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            'Check your email for instructions to reset your password',
            'info'
        )
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/reset_password_request.html',
        title='Reset Password',
        form=form
    )

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    The actual form to set a new password, given a valid token.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/reset_password.html',
        title='Reset Password',
        form=form
    )

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Allow the current user to update their username (and other profile fields).
    """
    form = EditProfileForm(original_username=current_user.username)
    if form.cancel.data:
        return redirect(url_for('main.user', username=current_user.username))
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        # If your form has additional fields (e.g. about_me), update them here:
        # current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('auth.edit_profile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.username.data = current_user.username
        form.email.data = current_user.email
        # Pre-fill additional fields if any:
        # form.about_me.data = current_user.about_me
    return render_template(
        'auth/edit_profile.html',
        title='Edit Profile',
        form=form
    )
