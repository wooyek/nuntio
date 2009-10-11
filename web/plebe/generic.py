from django.template import loader, RequestContext
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.core.xheaders import populate_xheaders
from django.core.paginator import Paginator, InvalidPage
from django.core.exceptions import ObjectDoesNotExist

def object_list(request, queryset, paginate_by=None, page=None, allow_empty=True,
                template_object_name='object', mimetype=None):
        if paginate_by is None:
            try:
                paginate_by = int(request.GET.get('%s_paginate_by' % template_object_name, 1))
            except ValueError:
                raise HttpResponseBadRequest("Bad %s_paginate_by value" % template_object_name)
        # queryset = queryset._clone() # does not work on GAE                
        paginator = Paginator(queryset, paginate_by, allow_empty_first_page=allow_empty)
        if not page:
            page = request.GET.get('%s_page' % template_object_name, 1)
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                # Page is not 'last', nor can it be converted to an int.
                raise HttpResponseBadRequest("Bad %s_page value" % template_object_name)
        try:
            page_obj = paginator.page(page_number)
        except InvalidPage:
            raise Http404
        return {
            '%s_list' % template_object_name: page_obj.object_list,
            '%s_paginator' % template_object_name: paginator,
            '%s_page_obj' % template_object_name: page_obj
        }
