# -*- coding: utf-8 -*-
# Copyright 2008 Janusz Skonieczny
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
This is a set of utilities for faster development with Django templates.

Template loaders that load from the app/template/model directories
'templates' folder when you specify an app prefix ('app/template.html').

It's possible to register global template libraries by adding this to your
settings:
GLOBALTAGS = (
    'myapp.templatetags.cooltags',
)

"""
from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext, add_to_builtins, loader, TemplateDoesNotExist
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.utils import simplejson
from ragendja.apputils import get_app_dirs
import os, logging

def app_model_prefixed_loader(template_name, template_dirs=None):
    """
    Loader for model dependent templates stored in model named
    directories, app/templates/<model_name>/form.html 

    The following defines a template loader that loads templates from a specific
    app based on the prefix of the template path:
    get_template("app/<model_name>_template.html") => app/templates/<model_name>/template.html

    This keeps the code DRY and prevents name clashes.
    """
    packed = template_name.split('/', 1)
    if len(packed) == 2 and packed[0] in app_template_dirs:
        model_prefixed = packed[1].split('_',1)
        model_prefixed = os.path.join(*model_prefixed)
        path = os.path.join(app_template_dirs[packed[0]], model_prefixed)
        logging.debug("Looking for tempalte: %s" % path)
        try:
            return (open(path).read().decode(settings.FILE_CHARSET), path)
        except IOError:
            pass
    raise TemplateDoesNotExist, template_name
app_model_prefixed_loader.is_usable = True

def app_prefixed_defaults_loader(template_name, template_dirs=None):
    """
    Loader for generic model independent templates, eg. form.html

    The following defines a template loader that loads templates from a specific
    app based on the prefix of the template path:
    get_template("app/<model_name>_template.html") => app/templates/template.html

    This keeps the code DRY and prevents name clashes.
    """
    packed = template_name.split('/', 1)
    if len(packed) == 2 and packed[0] in app_template_dirs:
        model_prefixed = packed[1].split('_',1)
        if len(model_prefixed) == 1:
          raise TemplateDoesNotExist, template_name
        path = os.path.join(app_template_dirs[packed[0]], model_prefixed[1])
        logging.debug("Looking for tempalte: %s" % path)
        try:
            return (open(path).read().decode(settings.FILE_CHARSET), path)
        except IOError:
            pass
    raise TemplateDoesNotExist, template_name
app_prefixed_defaults_loader.is_usable = True

# This is needed by app_prefixed_loader.
app_template_dirs = get_app_dirs('templates')        