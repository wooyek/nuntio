# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from ragendja.urlsauto import urlpatterns
from ragendja.auth.urls import urlpatterns as auth_patterns
from django.contrib import admin

admin.autodiscover()

handler500 = 'ragendja.views.server_error'

import nuntio

urlpatterns = auth_patterns + patterns('',
    ('^admin/', include(admin.site.urls)),
    #(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'main.html'}),
    # Override the default registration form
    #url(r'^account/register/$', 'registration.views.register', kwargs={'form_class': UserRegistrationForm}, name='registration_register'),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'', include('nuntio.urls')),
) + urlpatterns
