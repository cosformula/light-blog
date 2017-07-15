"""
Define all api
"""

import datetime
import json
import os.path as op
import random

from flask import (Flask, Response, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_admin import Admin

from flask_babelex import Babel
# from flask.ext.babelex import Babel
import admin as am
from client import *
from config import CACHE, app
from models import *

app.config.from_pyfile('config.py')

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(card_id):
    return User.objects(card_id=card_id).first()

babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'

admin = Admin(app, name='SHUMSN', template_mode='bootstrap3')
admin.add_view(am.UserView(User, name='用户管理'))
admin.add_view(am.TagsView(Tags, name='标签管理',))
admin.add_view(am.PageAdmin(Post, name='我的文章',endpoint="my_post"))
admin.add_view(am.PostView(Post,name='全部文章', endpoint="all_post"))
admin.add_link(am.NotAuthenticatedMenuLink(name='登录',
                                            endpoint='login_view'))
# admin.add_link(MenuLink(name='Google', category='Links', url='http://www.google.com/'))
# admin.add_link(MenuLink(name='Mozilla', category='Links', url='http://mozilla.org/'))

# path = op.join(op.dirname(__file__), 'static')
# admin.add_view(FileAdmin(path, '/static/', name='Static Files'))
# admin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))
# admin.add_view(LoginView(name='Login', endpoint='account'))
admin.add_link(am.AuthenticatedMenuLink(name='注销',
                                         endpoint='logout_view'))


def validate(card_id, password):
    client = Services()
    client.card_id = card_id
    client.password = password
    if client.login() and client.get_data():
        result = {
            'success': True,
            'name': client.data['name'],
            'card_id': card_id
        }
    else:
        result = {
            'success': False
        }
    return result


@app.route('/')
def index():
    return redirect('/posts/1')

@app.route('/image/<oid>')
def get_image(oid):
    post = Post.objects(id=oid).first()
    img = post.img.read()
    content_type = post.img.content_type
    return Response(img, mimetype=content_type)

@app.route('/post/<oid>')
def get_post(oid):
    post = Post.objects(id=oid).first()
    return render_template('article.html', post=post)

@app.route('/posts')
def redirect_posts():
    return redirect('/posts/1')

@app.route('/posts/<page>')
def view_posts(page=1):
    paginated_posts = Post.objects.paginate(page=int(page), per_page=2)
    return render_template('articles.html', paginated_posts=paginated_posts)

@app.route('/protected') 
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.get_id()

@app.route('/login', methods=['GET','POST'])
def login_view():
    if request.method == 'POST':
            card_id = request.form['card_id']
            password = request.form['password']
            user = User.objects(card_id=card_id).first()
            result = validate(card_id, password)
            if result['success']:
                if user == None:
                    user = User(name=result['name'], card_id=card_id,role='student')
                    user.save()
                flask_login.login_user(user)
            else:
                user = User()
            return redirect('/admin')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout_view():
    flask_login.logout_user()
    return redirect(url_for('admin.index'))


if __name__ == '__main__':
    app.debug = True
    app.run()
