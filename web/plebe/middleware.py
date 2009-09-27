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
#
# $Id: middleware.py 28 2008-11-23 15:34:46Z WooYek $

"""A ToBeDone midleware do django, general/common request/responce processing."""

__version__ = "$Revision: 28 $"

import logging
from datetime import datetime
logging.info("loaded... %s " % __version__)  
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseForbidden, HttpResponseNotFound


class XHeadersMiddleware(object):
  """
  Adds additional headers to the respose.
  
  X-Current-Location - for detecting redirects with XMLHTTPRequest.
  Inspired by django.core.xhreaders.populate_xheaders
  """

  def process_response(self, request, response):
    response['X-Current-Location'] = request.path
    return response
    
from django.views.debug import technical_500_response
import sys

class UserBasedExceptionMiddleware(object):
    """
    Shows stacktrace do superuser even in if DEBUG is False
    
    Normal users will get your 500.html when debug = False, but If you 
    are logged in as a super user then you get to see the stack trace in all its glory. 
    """
    def process_exception(self, request, exception):
        if request.user.is_superuser:
            return technical_500_response(request, *sys.exc_info())


class StaffOnly(object):
  """
  Only staff gets authorized access. Everyone else is
  forbidden even authernticated properly.

  Usefull during maintenace.
  """

  def process_request(self, request):
      user = request.user
      logging.debug("user.is_authenticated: %s" % user.is_authenticated())
      if user.is_authenticated() and not user.is_staff:
          return HttpResponseForbidden("Sorry, were not open for public yet");


logging.info("loaded...")  
from django.conf import settings

LOGIN_REQUIRED_PREFIXES = getattr(settings, 'LOGIN_REQUIRED_PREFIXES', ())
NO_LOGIN_REQUIRED_PREFIXES = getattr(settings, 'NO_LOGIN_REQUIRED_PREFIXES', ())

class LoginRequiredMiddleware(object):
    """
    Redirects to login page if request path begins with a
    LOGIN_REQURED_PREFIXES prefix. You can also specify
    NO_LOGIN_REQUIRED_PREFIXES which take precedence.
    """
    def process_request(self, request):
        for prefix in NO_LOGIN_REQUIRED_PREFIXES:
            if request.path.startswith(prefix):
                return None
        for prefix in LOGIN_REQUIRED_PREFIXES:
            if request.path.startswith(prefix) and not request.user.is_authenticated():
                logging.debug("redirect_to_login from %s" % request.get_full_path())
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
        return None

logging.info("loaded...")        