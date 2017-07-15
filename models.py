"""
define models
"""

import datetime
# from flask_mongoengine import MongoEngine
import flask_login
from config import app
from mongoengine import (BooleanField, DateTimeField, Document, EmailField,
                         EmbeddedDocument, EmbeddedDocumentField, ImageField,
                         ListField, ReferenceField, StringField, connect)
from mongoengine import signals,queryset_manager
from flask_mongoengine import MongoEngine
app.config['MONGODB_SETTINGS'] = {
    'db': 'shumsncms',
    'host': '127.0.0.1',
    'port': 27017
}
db = MongoEngine(app)

# connect('shumsncms',host='127.0.0.1',port=27017)

class User(flask_login.UserMixin, db.Document):
    email = db.EmailField()
    name = db.StringField()
    nickname = db.StringField()
    card_id = db.StringField()
    open_id = db.StringField()
    phone = db.StringField()
    role = db.StringField()
    create_time = db.DateTimeField(default=datetime.datetime.now)
    def __unicode__(self):
        return self.card_id + self.name
    def get_id(self):
        return self.card_id

# class Messages(Document):
#     tittle = StringField()
#     content = StringField()
#     sender = ReferenceField(User)
#     receiver = ReferenceField(User)
#     create_time = DateTimeField(default=datetime.datetime.now)

class Tags(db.Document):
    name = db.StringField(max_length=10)
    def __unicode__(self):
        return self.name

class Comment(db.EmbeddedDocument):
    name = db.StringField(max_length=10)
    content = db.StringField(max_length=450)
    time = db.DateTimeField(default=datetime.datetime.now)

class Post(db.Document):
    title = db.StringField(max_length=120, required=True)
    dist = db.StringField(max_length=100, required=True)
    content = db.StringField(required=True)
    img = db.ImageField(required=True)
    author = db.ReferenceField(User)
    visiable = db.BooleanField(default=True)
    tags = db.ListField(db.ReferenceField(Tags))
    # category = db.StringField()
    comments = db.ListField(db.EmbeddedDocumentField(Comment))
    create_time = db.DateTimeField(default=datetime.datetime.now)
    modify_time = db.DateTimeField(default=datetime.datetime.now)
    meta = {'strict': False}
    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        if document.author == None:
            document.author = User.objects(id=flask_login.current_user.id).first()
    @db.queryset_manager
    def my_posts(doc_cls, queryset):
        print('querysert')
        return queryset.filter(id=flask_login.current_user.id)
db.pre_save.connect(Post.pre_save, sender=Post)
