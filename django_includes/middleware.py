import re
from http.cookiejar import split_header_words

import requests

esi_include_re = re.compile(b'<esi:include src="([^"]+)" />')


class EdgeSideIncludesMiddleware(object):
    """
    This middleware is intended to resolve edge side includes, as would do a system side middleware like Varnish. It is
    by no mean complete, efficient or secure, please consider using a real implementation if running in production.

    Please note that this is a WSGI middleware, and not a django middleware. Use it by patching your wsgi.py file to
    decorate the django application.

    """

    def __init__(self, application, session=None):
        self.application = application
        self.environ = None
        self.session = session or requests.Session()

    def include(self, match):
        # cookies forwarding is required, especially for session and csrf
        cookies = self.environ.get("HTTP_COOKIE", "") or None

        if cookies:
            cookies = dict(split_header_words([cookies])[0])

        response = self.session.get(match.group(1), cookies=cookies)
        return response.content

    def __call__(self, environ, start_response):
        self.environ = environ
        for x in self.application(environ, start_response):
            yield esi_include_re.sub(self.include, x)
