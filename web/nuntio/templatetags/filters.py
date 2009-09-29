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
logging.info("Filters loading....")

from django import template
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from nuntio import models

register = template.Library()

@register.filter(name='user')
def user(email):
    user = User.all().filter("email =", email).get()
    if user is None:
        return None
    if user.first_name is not None and  user.last_name is not None:
        s = "<a href='#'>%s %s</a>" % (user.first_name, user.last_name)
    else:
        s = "<a href='#'>%s</a>" % user.username.split('@')[0]
    return mark_safe(s)

logging.info("Filters loaded....")
