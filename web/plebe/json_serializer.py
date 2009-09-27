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

import datetime
import logging
from StringIO import StringIO

from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.python import Deserializer as PythonDeserializer
from django.utils.encoding import smart_str, smart_unicode
from django.utils import datetime_safe
from django.utils import simplejson

from django.core.serializers.json import Serializer as JsonSerializer

class Serializer(JsonSerializer):
    """
    A JSON serializer suporting get_absolute_url serialization.
    """  
    extra_methods = {"get_absolute_url":"absolute_url"}
    
    def serialize(self, queryset, **options):
        """
        Serialize a queryset.
        """
        logging.debug(queryset)
        self.options = options

        self.stream = options.get("stream", StringIO())
        self.selected_fields = options.get("fields")

        self.start_serialization()
        for obj in queryset:
            self.start_object(obj)
            for field in obj._meta.local_fields:
                if field.serialize:
                    if field.rel is None:
                        if self.selected_fields is None or field.attname in self.selected_fields:
                            self.handle_field(obj, field)
                    else:
                        if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
                            self.handle_fk_field(obj, field)
            for field in obj._meta.many_to_many:
                if field.serialize:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_m2m_field(obj, field)
            for method_name in self.extra_methods:
                  if self.selected_fields is None or method_name in self.selected_fields:
                      self.handle_method(obj, method_name, self.extra_methods[method_name])
            self.end_object(obj)
        self.end_serialization()
        return self.getvalue()

    def handle_method(self, obj, method_name, data_name):
        logging.debug(method_name)
        method = getattr(obj, method_name, None)
        if method is None:
            return
            
        data = method()
        logging.debug(data)
        if isinstance(data, (list, tuple)):
            serialized = [smart_unicode(item, strings_only=True) for item in data]
        else:
            serialized = smart_unicode(data, strings_only=True)
        self._current[data_name] = serialized        