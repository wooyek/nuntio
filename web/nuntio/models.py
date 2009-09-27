# coding=utf-8
#
# Copyright 2008 Janusz Skonieczny.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import datetime

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.db import Model as BaseModel

from django.db.models import permalink as permalink
from django.template.defaultfilters import slugify
from django.conf import settings

from appenginepatch.ragendja.dbutils import KeyListProperty

import markdown

LANGUAGES = [item[0] for item in settings.LANGUAGES]

class Topic(BaseModel):
    """ A named article collection """
    name            = db.StringProperty(required=True)
    language_code   = db.StringProperty(choices=LANGUAGES)

    @permalink
    def get_absolute_url(self):
        return ('topic_details', None, { 'object_id': self.key().name() })

    def put(self):
        if not self.is_saved():
            self._key_name = slugify(self.name[0:200])
        BaseModel.put(self)

    def __unicode__(self):
        return u'%s' % self.name

class TopicI18n(BaseModel):
    """ An topic extenstion for language different than default"""
    name            = db.StringProperty(required=True)
    language_code   = db.StringListProperty(choices=LANGUAGES)
    

class Article(BaseModel):
    """ A main content model """
    POST_STATUS_CHOISES = ('draft','private','silent','public')

    title           = db.StringProperty()
    body            = db.TextProperty(required=True,default='')
    body_html       = db.TextProperty(required=False,default='')
    status          = db.StringProperty(required=True, choices=POST_STATUS_CHOISES, default="draft")
    topic           = KeyListProperty(Topic)
    tease           = db.TextProperty(required=False)
    tease_html      = db.TextProperty(required=False)
    language_code   = db.StringProperty(choices=LANGUAGES)
    author          = db.EmailProperty()
    is_short        = db.BooleanProperty(default=False)
    created         = db.DateTimeProperty()#auto_now_add=True)
    edited          = db.DateTimeProperty(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('atricle_details', None, {'object_id': self.key().name() })

    def get_previous_post(self):
        return self.get_previous_by_publish(status__gte=2)

    def get_next_post(self):
        return self.get_next_by_publish(status__gte=2)

    def put(self):
        if self.created is None:
            self.created = datetime.datetime.now()
        self.body_html = markdown.markdown(self.body)
        tease = self.body.split("<!--more-->")[0]
        if self.body.count("<!--more-->") < 1:
            self.is_short = True
        else:
            self.is_short = False
        self.tease = markdown.markdown(tease)
        if self.author is None:
            self.author = users.get_current_user().email()
        if not self.is_saved():
            slug = slugify(self.title[0:50])
            key = "/%d/%02d/%02d/%s" % (self.created.year, self.created.month, self.created.day, slug)
            self._key_name = key
        BaseModel.put(self)

class ArticleI18n(BaseModel):
    """ An extenstion to the one article for language different than default"""
    article          = db.ReferenceProperty(Article)
    language_code   = db.StringProperty(choices=LANGUAGES)
    title           = db.StringProperty()
    body            = db.TextProperty(required=True,default='')
    body_html       = db.TextProperty(required=False,default='')
    tease           = db.TextProperty(required=False)
    tease_html      = db.TextProperty(required=False)

class SimilarArticleSet(BaseModel):
    """ An article collection simliar to the one """
    article          = db.ReferenceProperty(Article)
    articles         = KeyListProperty(Article)

class Folder(BaseModel):
    name            = db.StringProperty(required=True)
    parent_folder   = db.SelfReferenceProperty()

    def __unicode__(self):
        return u'%s/%s' % (('' if self.parent_folder is None else self.parent_folder), self.name)

class File(BaseModel):
    name                = db.StringProperty(required=True)
    title               = db.StringProperty(required=False)
    full                = db.BlobProperty()
    thumb               = db.BlobProperty()
    description         = db.TextProperty()
    description_html    = db.TextProperty()
    mime_type           = db.StringProperty()
    folders             = KeyListProperty(Folder)

    @permalink
    def get_absolute_url(self):
        return ('file_full', None, { 'object_id': self.key().name() })

    @permalink
    def get_thumb_url(self):
        return ('file_thumb', None, { 'object_id': self.key().name() })

    def put(self):
        self.description_html = markdown.markdown(self.description)
        if not self.is_saved():
            slug = slugify(self.name)
            if self.name[0] in "0123456789":
                slug = "file-"+slug
            self._key_name = slug
        BaseModel.put(self)

    def __unicode__(self):
        return u'File: %s' % self.name


class Template(BaseModel):
    """A template file """
    name        = db.StringProperty(required=True)
    file_name   = db.StringProperty(required=True)

class Page(BaseModel):
    name        = db.StringProperty(required=True)
    article     = db.ReferenceProperty(Article)         # A main arcicle for this page
    parent_page = db.SelfReferenceProperty()            # Page tree - TODO, evaluate MPTT use here
    slug        = db.StringProperty()
    template    = db.ReferenceProperty(Template)        # Template to used to render this page
#    lft         = db.IntegerProperty(required=True)
#    rgt         = db.IntegerProperty(required=True)
    folder      = db.ReferenceProperty(Folder)          # A folder with files relevant to this page

    @permalink
    def get_absolute_url(self):
         return ('Page_detail', None, { 'object_id': self.slug })

    @classmethod
    def get_by_url_key(cls, key):
         """Returns a page by the same key used to generate absolute URL"""
         return cls.all().filter("slug = ", key).get()

    def title(self):
        if self.article is not None:
            return self.article.title
        return self.name   

    def put(self):
        if self.slug is None:
            self.slug = slugify(self.name)
        BaseModel.put(self)


    def __unicode__(self):
        return u'%s' % self.name
#        return u'%s%s' % (('/' if self.parent_page is None else self.parent_page.slug), self.slug)
#        return u'%s/%s' % (('' if self.parent_page is None else self.parent_page), self.name)
