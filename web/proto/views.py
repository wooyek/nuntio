# -*- coding: utf-8 -*-
# Copyright 2008 Qualent Software sp. z o.o.
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

import datetime, logging, settings

from django.shortcuts import render_to_response
from django.views.generic.list_detail import object_list, object_detail
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.utils import simplejson
from django.conf import settings
from django.core import serializers
from django.contrib.auth.decorators import login_required

def show_template(request, object_id):
    context_instance = RequestContext(request)
    return render_to_response(object_id+'.html', context_instance=context_instance)
