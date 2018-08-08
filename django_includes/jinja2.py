import html

import jwt
from django.conf import settings
from django.urls import reverse
from django.utils.module_loading import import_string
from jinja2.ext import Extension
from markupsafe import Markup

from django_includes.settings import DEBUG_INCLUDES


def get_view_class(view_or_callable):
    try:
        return view_or_callable.view_class
    except AttributeError as e:
        return type(view_or_callable)


def get_markup(view, response, via="render"):
    # headers
    headers = "<br>".join("{} = {}".format(k, v) for k, v in response.items())
    if headers:
        headers = "<br>" + headers

    # render
    if hasattr(response, "render"):
        response.render()

    if DEBUG_INCLUDES:
        return Markup(
            (
                '<div style="outline: 1px solid #B9B280; padding: 1em; position: relative;">'
                '  <em style="color: white; position: absolute; right: -1px; top: -1px; padding: 0.15em 0.5em; font-size: 10px; background-color: #B9B280">'
                "    {} ({}){}"
                "  </em>"
                "  {} "
                "</div>"
            ).format(
                html.escape(get_view_class(view).__name__),
                via,
                headers,
                response.render().content.decode(encoding="utf-8"),
            )
        )

    return Markup(response.content.decode(encoding="utf-8"))


def render(request, view, *args, **kwargs):
    if isinstance(view, str):
        view = import_string(view)

    if hasattr(view, "as_view"):
        view = view.as_view()
    elif hasattr(type(view), "as_view"):
        view = type(view).as_view()

    response = view(request, *args, **kwargs)
    request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"

    return get_markup(view, response, "render")


def include_tag(route, request, view_name, view_args, view_kwargs):
    if route == "hinclude":
        tag = "hx:include"
    elif route == "esi":
        tag = "esi:include"
    else:
        raise ValueError("Unsupported inclusion type.")

    return Markup(
        '<{} src="{}" />'.format(
            tag,
            request.build_absolute_uri(
                reverse(
                    route,
                    kwargs={
                        "token": jwt.encode(
                            {"v": view_name, "a": view_args, "k": view_kwargs}, settings.SECRET_KEY
                        ).decode("utf-8")
                    },
                )
            ),
        )
    )


def render_hinclude(request, view_name, *args, **kwargs):
    return include_tag("hinclude", request, view_name, args, kwargs)


def render_esi(request, view_name, *args, **kwargs):
    return include_tag("esi", request, view_name, args, kwargs)


class DjangoIncludesExtension(Extension):
    def __init__(self, environment):
        super(DjangoIncludesExtension, self).__init__(environment)
        environment.globals["render_sync"] = render
        environment.globals["render_hinclude"] = render_hinclude
        environment.globals["render_esi"] = render_esi
