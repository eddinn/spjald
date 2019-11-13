from app import app, db
from flask import request, render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, PostForm
from app.forms import ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app.email import send_password_reset_email


# Routes
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home',
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/addpost', methods=['GET', 'POST'])
@login_required
def addpost():
    form = PostForm()
    if form.validate_on_submit():
        if form.submit.data:
            post = Post(clientname=form.clientname.data,
                        clientss=form.clientss.data,
                        clientemail=form.clientemail.data,
                        clientphone=form.clientphone.data,
                        clientaddress=form.clientaddress.data,
                        clientzip=form.clientzip.data,
                        clientcity=form.clientcity.data,
                        clientinfo=form.clientinfo.data,
                        author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Client data successfully added!')
            return redirect(url_for('addpost'))
        else:
            return redirect(url_for('index'))
    return render_template('addpost.html', title='Add Post', form=form)


@app.route('/editpost/<int:clientid>', methods=['GET', 'POST'])
@login_required
def editpost(clientid):
    qry = Post.query.filter_by(clientid=clientid).first()
    form = PostForm(request.form, obj=qry)
    if form.validate_on_submit():
        if form.submit.data:
            form.populate_obj(qry)
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('index', clientid=clientid))
        else:
            return redirect(url_for('index'))
    return render_template('editpost.html', title='Edit post',
                           form=form, clientid=clientid)


@app.route('/deletepost/<int:clientid>', methods=['GET', 'POST'])
@login_required
def deletepost(clientid):
    qry = Post.query.filter_by(clientid=clientid).first()
    db.session.delete(qry)
    db.session.commit()
    flash('Post successfully deleted!')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, username=form.username.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
