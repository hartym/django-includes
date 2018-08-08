import hashlib
from datetime import timedelta

import jwt
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotModified
from django.utils import timezone
from django.utils.http import http_date
from django.utils.module_loading import import_string
from django.views.generic import TemplateView

from django_includes.jinja2 import get_markup


def include_view(request, token, via):
    data = jwt.decode(token, settings.SECRET_KEY)
    view = import_string(data["v"])
    if hasattr(view, "as_view"):  # xxx not a good idea, better use already constructed views.
        view = view.as_view()

    # build wrapped response
    request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
    wrapped_response = view(request, *data["a"], **data["k"])
    if wrapped_response.status_code >= 300:
        return wrapped_response

    response = HttpResponse(get_markup(view, wrapped_response, via))

    for k, v in wrapped_response.items():
        response[k] = v

    return response


class CacheableTemplateView(TemplateView):
    template_name = "promised_views_app/cacheable.html"
    use_etag = True
    cache_control = "private"
    max_age = 86400

    _etag = None

    def get_etag(self):
        if not self.use_etag:
            return None

        if not self._etag:
            # self.etag = hashlib.sha1(repr(args).encode('utf-8') + b';' + repr(sorted(kwargs.items())).encode('utf-8')).hexdigest()
            self._etag = hashlib.sha1(repr(type(self)).encode()).hexdigest()
        return self._etag

    def dispatch(self, request, *args, **kwargs):
        # if we're using etag and the browser knows about the actual page etag, we can bypass dispatching the request
        # for real and just tell the browser its cache is up to date.
        etag = self.get_etag()
        if etag and etag == request.META.get("HTTP_IF_NONE_MATCH", None):
            return HttpResponseNotModified()

        # time to get to work, my dear.
        response = super().dispatch(request, *args, **kwargs)

        # only cache if secondary request
        if request.is_ajax():
            # build expires header. Not used in http 1.1, but maybe useful for older browsers? Or maybe completely
            # useless, but also harmless.
            if self.max_age:
                response["Expires"] = http_date((timezone.now() + timedelta(seconds=self.max_age)).timestamp())

            # build cache-control header
            if self.cache_control:
                cache_control = [self.cache_control]
                if self.max_age and not self.cache_control.startswith("no-"):
                    cache_control.append("max-age={}".format(self.max_age))
                response["Cache-Control"] = ", ".join(cache_control)

            if etag:
                response["ETag"] = etag

        return response


cacheable_view = CacheableTemplateView.as_view()
