from app import db
from app.main import bp
from app.main.forms import PostForm, EditPostForm, SearchForm
from app.models import User, Post
from flask import (
    request, render_template, flash, redirect,
    url_for, current_app, g
)
from flask_login import current_user, login_required

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        g.search_form = SearchForm()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    followed_ids = [u.id for u in current_user.followed] + [current_user.id]
    query = Post.query.filter(Post.user_id.in_(followed_ids)) \
                      .order_by(Post.timestamp.desc())
    pagination = db.paginate(
        query,
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    next_url = url_for('main.index', page=page + 1) if pagination.has_next else None
    prev_url = url_for('main.index', page=page - 1) if pagination.has_prev else None
    return render_template(
        'index.html', title='Home',
        posts=posts, next_url=next_url, prev_url=prev_url
    )

@bp.route('/addpost', methods=['GET', 'POST'])
@login_required
def addpost():
    form = PostForm()
    if form.cancel.data:
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        if form.submit.data:
            post = Post(
                clientname=form.clientname.data,
                clientss=form.clientss.data,
                clientemail=form.clientemail.data,
                clientphone=form.clientphone.data,
                clientaddress=form.clientaddress.data,
                clientzip=form.clientzip.data,
                clientcity=form.clientcity.data,
                clientinfo=form.clientinfo.data,
                author=current_user
            )
            db.session.add(post)
            db.session.commit()
            flash('Client data successfully added!')
            return redirect(url_for('main.addpost'))
        else:
            return redirect(url_for('main.index'))
    return render_template('addpost.html', title='Add client', form=form)

@bp.route('/editpost/<int:id>', methods=['GET', 'POST'])
@login_required
def editpost(id):
    qry = Post.query.filter_by(id=id).first()
    form = EditPostForm(request.form, obj=qry)
    if form.validate_on_submit():
        if form.submit.data:
            form.populate_obj(qry)
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('main.index', id=id))
        else:
            return redirect(url_for('main.index'))
    return render_template(
        'editpost.html', title='Edit client', form=form, id=id
    )

@bp.route('/deletepost/<int:id>', methods=['GET', 'POST'])
@login_required
def deletepost(id):
    qry = Post.query.filter_by(id=id).first()
    db.session.delete(qry)
    db.session.commit()
    flash('Client successfully deleted!')
    return redirect(url_for('main.index'))

@bp.route('/user/<username>')
@login_required
def user(username):
    try:
        current_app.logger.info(f"Loading profile for user: {username}")
        user = User.query.filter_by(username=username).first_or_404()
        page = request.args.get('page', 1, type=int)
        pagination = db.paginate(
            user.posts.order_by(Post.timestamp.desc()),
            page=page,
            per_page=current_app.config['POSTS_PER_PAGE'],
            error_out=False
        )
        posts = pagination.items
        next_url = (
            url_for('main.user', username=user.username, page=page + 1)
            if pagination.has_next else None
        )
        prev_url = (
            url_for('main.user', username=user.username, page=page - 1)
            if pagination.has_prev else None
        )
        return render_template(
            'user.html', title='User profile', user=user,
            posts=posts, next_url=next_url, prev_url=prev_url
        )
    except Exception:
        current_app.logger.error(
            f"Error in profile view for {username}", exc_info=True
        )
        raise

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {username}!')
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}.')
    return redirect(url_for('main.user', username=username))

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.index'))
    query_str = g.search_form.q.data
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POSTS_PER_PAGE']
    posts, total = Post.search(query_str, page, per_page)
    next_url = (
        url_for('main.search', q=query_str, page=page + 1)
        if page * per_page < total else None
    )
    prev_url = (
        url_for('main.search', q=query_str, page=page - 1)
        if page > 1 else None
    )
    return render_template(
        'search.html', title='Search Results',
        posts=posts, next_url=next_url, prev_url=prev_url
    )

@bp.route('/explore')
@login_required
def explore():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Explore', posts=posts)
