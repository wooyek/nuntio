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

from google.appengine.api import memcache

from django.core.urlresolvers import reverse
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, delete_object, update_object
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect, HttpResponse, Http404
from django.template.context import RequestContext

from appenginepatch.ragendja.template import render_to_response, render_to_string

from models import *
import forms

def home(request):
    return Page_detail(request,"home")

def Page_detail(request, object_id):
    o = Page.get_by_url_key(object_id)
    if o is None:
        raise Http404, "No %s found matching the query" % (Page._meta.verbose_name)
    homepage = Page.get_by_url_key("home")
    d = {
        "page": o,
        "homepage": homepage,
    }              
    return render_to_response(request, 'nuntio/page/detail.html', d)

def article_details(request, object_id):
    return object_detail(request, Article.all(), object_id)

def page_details(request, object_id):
    return object_detail(request, Page.all(), object_id)

def file_full(request, object_id):
    return image_view(object_id,'file','name')

def image_thumb(request, object_id):
    return image_view(object_id,'thumb','name')

def image_view(object_id, blob_property_name, file_name_property, model=File, ):
    object = memcache.get(object_id)
    if object is None:
      object = model.get(object_id)
      memcache.add(key=object_id, value=object, time=3600)
    else:
      logging.info("Serving cached %s" % object_id)
    if object:
        response = HttpResponse(getattr(object,blob_property_name), mimetype=object.mime_type)
        response['Content-Disposition'] = 'attachment; filename=%s' % getattr(object,file_name_property)
        return response
    return HttpResponseNotFound("File not found")