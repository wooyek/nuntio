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
    folders             = KeyListProperty(Folder)
    description         = db.TextProperty()
    description_html    = db.TextProperty()
    mime_type           = db.StringProperty()

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


LANGUAGES = [item[0] for item in settings.LANGUAGES]

class Topic(BaseModel):
    """ A named article collection """
    name            = db.StringProperty(required=True)
    language_code   = db.StringProperty(choices=LANGUAGES)
    slug            =  db.StringProperty()

    @permalink
    def get_absolute_url(self):
        return ('Topic_detail', None, { 'object_id': self.slug })

    def put(self):
        if self.slug is None:
            self.slug = slugify(self.name[0:200])
        BaseModel.put(self)

    def __unicode__(self):
        return u'%s' % self.name

class TopicI18n(BaseModel):
    """ An topic extenstion for language different than default"""
    name            = db.StringProperty(required=True)
    language_code   = db.StringListProperty(choices=LANGUAGES)

class Template(BaseModel):
    """A template file """
    name        = db.StringProperty(required=True)
    file_name   = db.StringProperty(required=True)

    def __unicode__(self):
        return u'%s' % self.name

class Page(BaseModel):
    name                = db.StringProperty(required=True)
    parent_page         = db.SelfReferenceProperty()            # Page tree - TODO, evaluate MPTT use here
    use_article_title   = db.BooleanProperty()
    slug                = db.StringProperty()
    template            = db.ReferenceProperty(Template)        # Template to used to render this page
#    lft         = db.IntegerProperty(required=True)
#    rgt         = db.IntegerProperty(required=True)

    @permalink
    def get_absolute_url(self):
         return ('Page_detail', None, { 'object_id': self.slug })

    @classmethod
    def get_by_url_key(cls, key):
         """Returns a page by the same key used to generate absolute URL"""
         return cls.all().filter("slug = ", key).get()

    def title(self):
        if self.use_article_title and self.article is not None:
            return self.article.title
        return self.name

    def put(self):
        if self.slug is None:
            self.slug = slugify(self.name)
        BaseModel.put(self)

    def article_set(self):
        return Article.all().filter('shown_on_pages =', self.key())

    def featured_article(self):
        return Article.all().filter('featured_on_pages =', self.key()).get()

    def main_article(self):
        return Article.all().filter('main_on_pages =', self.key()).get()

    def __unicode__(self):
        return u'%s' % self.name
#        return u'%s%s' % (('/' if self.parent_page is None else self.parent_page.slug), self.slug)
#        return u'%s/%s' % (('' if self.parent_page is None else self.parent_page), self.name)
  

class Article(BaseModel):
    """ A main content model """
    POST_STATUS_CHOISES = ('draft','private','silent','public')

    title               = db.StringProperty()
    body                = db.TextProperty(required=True,default='')
    body_html           = db.TextProperty(required=False,default='')
    main_article_for    = KeyListProperty(Page)                  
    main_on_pages       = KeyListProperty(Page)
    featured_on_pages   = KeyListProperty(Page)
    shown_on_pages      = KeyListProperty(Page)
    status          	= db.StringProperty(required=True, choices=POST_STATUS_CHOISES, default="draft")
    allow_comments      = db.BooleanProperty(default=True)
    slug                = db.StringProperty()
    topic_set           = KeyListProperty(Topic)
    featured_image      = db.ReferenceProperty(File)
    folder              = db.ReferenceProperty(Folder)          # A folder with files relevant to this article
    tease               = db.TextProperty(required=False)
    tease_html          = db.TextProperty(required=False)
    language_code       = db.StringProperty(choices=LANGUAGES)
    author              = db.EmailProperty()
    is_short            = db.BooleanProperty(default=False)
    created             = db.DateTimeProperty()#auto_now_add=True)
    edited              = db.DateTimeProperty(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('Article_detail', None, {'object_id': self.slug })

    def get_previous_post(self):
        return self.get_previous_by_publish(status__gte=2)

    def get_next_post(self):
        return self.get_next_by_publish(status__gte=2)

    def get_topic_set(self):
        a = Topic.get(self.topic_set)
        logging.debug(a)
        return a

    def put(self, update_mains=True):
        if self.created is None:
            self.created = datetime.datetime.now()
        self.body_html = markdown.markdown(self.body)
        self.tease = self.body.split("<!--more-->")[0]
        if self.body.count("<!--more-->") < 1:
            self.is_short = True
        else:
            self.is_short = False
        self.tease_html = markdown.markdown(self.tease)
        logging.debug("Article %s" % self)
        logging.debug("Article %s" % self.key())
        if update_mains:
            for key in self.main_on_pages:
                logging.debug("Main on %s" % key)
                # seach for curent main atricles on these pages
                # and brak connection if it's this one now
                mains = Article.all().filter('main_on_pages =', key).fetch(5,0)
                logging.debug(len(mains))
                for a in mains:
                    logging.debug("Main on also %s" % type(a) )
                    logging.debug("Main on also %s" % a.key())
                    if a.key() != self.key():
                        logging.debug(a.main_on_pages)
                        a.main_on_pages.remove(key)
                        logging.debug(a.main_on_pages)
                        a.put(False)

        if self.author is None:
            self.author = users.get_current_user().email()
        if self.slug is None:
            self.slug = slugify(self.title).__str__()
        BaseModel.put(self)

class ArticleI18n(BaseModel):
    """ An extenstion to the one article for language different than default"""
    article         = db.ReferenceProperty(Article)
    language_code   = db.StringProperty(choices=LANGUAGES)
    title           = db.StringProperty()
    body            = db.TextProperty(required=True,default='')
    body_html       = db.TextProperty(required=False,default='')
    tease           = db.TextProperty(required=False)
    tease_html      = db.TextProperty(required=False)

class ArticleSet(BaseModel):
    """ An article collection simliar to the one """
    name            = db.StringProperty(required=True)
    articles        = KeyListProperty(Article)



