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

# WARN: Errors in this file will not be logged anywhere

import logging
logging.info("Admin loading...")

from django.contrib import admin

from models import *
import forms

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'tease', 'slug', 'is_short', 'status', 'created', 'edited', 'folder']
    exclude = ['body_html','tease_html', 'tease', 'is_short']
    prepopulated_fields = {"slug": ('title',)}
    fieldsets = (
           (None, {
               'fields': ['title', 'body', 'status','main_on_pages', 'featured_on_pages', 'shown_on_pages', 'topic_set', 'language_code']
           }),
           ('Advanced options', {
               'classes': ['collapse'],
               'fields': ['author', 'slug', 'allow_comments','folder', 'featured_image', 'created', 'edited'],
           }),
       )
    
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {"slug": ('name',)}

class Image(admin.ModelAdmin):
    list_display = ['name', 'title', 'mime_type', ]
    exclude = ['description_html', 'description_html_en']
    ordering = ['name']
    form = forms.FileForm
    fieldsets = (
           (None, {
               'fields': ('full', 'thumb', 'folder')
           }),
           ('Advanced options', {
               'classes': ['collapse'],
               'fields': ['name', 'title', 'description'],
           }),
       )

class PageAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent_page', 'template',]
    ordering = ['slug']
    prepopulated_fields = {"slug": ('name',)}

admin.site.register(Article, ArticleAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(File)
admin.site.register(Folder)
admin.site.register(Page, PageAdmin)
admin.site.register(ArticleSet)
admin.site.register(Template)

logging.info("Admin loaded.")
