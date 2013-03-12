import re
import json

from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page

import jingo
from waffle import flag_is_active

from wiki.models import DocumentType


def jsonp_is_valid(func):
    func_regex = re.compile(r'^[a-zA-Z_\$][a-zA-Z0-9_\$]*'
        + r'(\[[a-zA-Z0-9_\$]*\])*(\.[a-zA-Z0-9_\$]+(\[[a-zA-Z0-9_\$]*\])*)*$')
    return func_regex.match(func)


def search(request):
    if not flag_is_active(request, 'elasticsearch'):
        """Google Custom Search results page."""
        query = request.GET.get('q', '')
        return jingo.render(request, 'landing/searchresults.html',
                            {'query': query})

    """Performs search or displays the search form."""
    search_query = request.GET.get('q', None)
    search = DocumentType.search()
    if search_query:
        search = search.query(or_={'title': search_query,
                                   'content': search_query}
                             )

    return jingo.render(request, 'search/results.html', {'results': search})


@cache_page(60 * 15)  # 15 minutes.
def suggestions(request):
    """Return empty array until we restore internal search system."""

    mimetype = 'application/x-suggestions+json'

    term = request.GET.get('q')
    if not term:
        return HttpResponseBadRequest(mimetype=mimetype)

    results = []
    return HttpResponse(json.dumps(results), mimetype=mimetype)


@cache_page(60 * 60 * 168)  # 1 week.
def plugin(request):
    """Render an OpenSearch Plugin."""
    site = Site.objects.get_current()
    return jingo.render(request, 'search/plugin.html',
                        {'site': site, 'locale': request.locale},
                        mimetype='application/opensearchdescription+xml')
