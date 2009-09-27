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

from django import forms
from django.core.files.uploadedfile import UploadedFile

from models import *

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        exclude = ['description_html', 'description_html']

    def clean(self):
        file = self.cleaned_data.get('file')
        if isinstance(file, UploadedFile):
            name = file.name
            if not self.cleaned_data.get('name'):
                self.cleaned_data['name'] = name
                del self._errors['name']

        return self.cleaned_data

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['body_html','tease_html', 'tease']

    def clean_autor(self):
        file = self.cleaned_data.get('file')
        if isinstance(file, UploadedFile):
            name = file.name
            if not self.cleaned_data.get('name'):
                self.cleaned_data['name'] = name
                del self._errors['name']

        return self.cleaned_data