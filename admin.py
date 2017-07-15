"""
Define all api
"""

import datetime
import json
import os.path as op
import random

from flask import (Flask, Response, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.mongoengine import ModelView
from flask_admin.contrib.mongoengine.filters import (BaseMongoEngineFilter,
                                                     BooleanEqualFilter)
from flask_admin.form import rules
from flask_admin.menu import MenuCategory, MenuLink, MenuView
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from wtforms import TextAreaField
from wtforms.widgets import TextArea

from client import *
from config import CACHE, app
from models import *

class AuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

class NotAuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return not flask_login.current_user.is_authenticated

class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('analytics_index.html')
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()
 
class UserView(ModelView): 
    column_filters = ['card_id'] 
    column_searchable_list = ('card_id',)
    # def is_accessible(self):
    #     return flask_login.current_user.is_authenticated
    def is_accessible(self):
        return flask_login.current_user.is_authenticated and flask_login.current_user.role == 'superadmin'

# class FilterMyPost(BaseMongoEngineFilter):
#     def apply(self, query, value):
#         user = User.objects(card_id=flask_login.current_user.card_id).first()
#         return query.filter(author=user)

class PageAdmin(ModelView):
    def get_query(self):
        user = User.objects(card_id=flask_login.current_user.card_id).first()
        return self.model.objects(author=user)
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']
    form_create_rules = ('title','dist', 'content', 'img', 'tags')
    # column_filters = ['author', 'title']
    column_searchable_list = ['title']
    column_editable_list = ['title',]
    column_exclude_list = ['content', 'author', 'modify_time']
    # form_edit_rules = ('title','content', 'img', 'tags', 'category', '')
    form_overrides = {
        'content': CKTextAreaField
    }
    form_ajax_refs = {
        'tags': {
            'fields': ['name']
        }
    }
    form_args = {
        'title': {
            'label': '标题'
        },
        'content': {
            'label': '正文'
        }, 
        'dist': {
            'label': '摘要'
        }, 
        'img': {
            'label': '题图'
        },
        'tags': {
            'label': '标签'
        },
        'author': {
            'label': '作者'
        },
        'category': {
            'label': '分类'
        },
        'visiable':{
            'label': '可见'
        }
    }
    form_subdocuments = {
        'comments': {
            'form_subdocuments': {
                None: {
                    'form_rules': ('name', 'content', rules.HTML('<hr>')),
                    'form_widget_args': {
                        'name': {
                            'style': 'color: red'
                        }
                    }
                }
            }
        }
    }
    def is_accessible(self):
        return flask_login.current_user.is_authenticated
    can_export = True


class PostView(ModelView):
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']
    form_overrides = dict(content=CKTextAreaField)
    # form_create_rules = ('title', rules.Text('Foobar'), 'content', 'image')
    column_searchable_list = ('title',)
    column_exclude_list = ['content', 'author', 'modify_time']
    form_ajax_refs = {
        'author': {
            'fields': ['card_id']
        }
    }
    def is_accessible(self):
        return flask_login.current_user.is_authenticated and flask_login.current_user.role == 'superadmin'
    
class TagsView(ModelView):
    can_delete = False
    can_edit = False
    def is_accessible(self):
        return flask_login.current_user.is_authenticated
