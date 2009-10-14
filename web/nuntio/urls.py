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

"""
Urls configuration for the application

See http://www.djangoproject.com/documentation/url_dispatch/
"""

import logging

logging.info("Urls loading")
from django.conf.urls.defaults import *
import views as v

urlpatterns = patterns('',
    url(r'^$', v.home, name='home'),
    url(r'^article/(?P<object_id>[\w-]+)/$', v.Article_detail, name='Article_detail'),
    url(r'^p/(?P<object_id>[\w-]+)/$', v.Page_detail, name='Page_detail'),
    url(r'^t/(?P<object_id>[\w-]+)/$', v.Topic_detail, name='Topic_detail'),

    url(r'^file/(?P<object_id>[\w-]+)/$', v.file_full, name='file_full'),
    url(r'^fthumb/(?P<object_id>[\w-]+)$', v.file_full, name='file_thumb'),

)

logging.info("Urls loaded")
