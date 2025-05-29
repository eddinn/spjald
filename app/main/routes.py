from app import db
from app.main import bp
from app.main.forms import PostForm, EditPostForm, SearchForm
from app.models import User, Post
from flask import request, render_template, flash, redirect, url_for, current_app, g
from flask_login import current_user, login_required
from sqlalchemy import or_

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        g.search_form = SearchForm()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home',
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

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
    post = Post.query.filter_by(id=id).first()
    form = EditPostForm(obj=post)
    if form.validate_on_submit():
        if form.submit.data:
            form.populate_obj(post)
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('main.index', id=id))
        else:
            return redirect(url_for('main.index'))
    return render_template('editpost.html', title='Edit client', form=form, id=id)

@bp.route('/deletepost/<int:id>', methods=['GET', 'POST'])
@login_required
def deletepost(id):
    post = Post.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    flash('Client successfully deleted!')
    return redirect(url_for('main.index'))

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', title='User profile',
                           user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    if not query:
        flash('No search query provided.')
        return redirect(url_for('main.index'))
    if len(query) > 128:
        flash('Search query is too long.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    post_query = Post.query.filter(
        or_(
            Post.clientname.ilike(f'%{query}%'),
            Post.clientemail.ilike(f'%{query}%'),
            Post.clientinfo.ilike(f'%{query}%')
        )
    )
    posts = post_query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.search', q=query, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.search', q=query, page=posts.prev_num) if posts.has_prev else None
    return render_template('search.html', title='Search Results', posts=posts.items, query=query, \
        next_url=next_url, prev_url=prev_url)
