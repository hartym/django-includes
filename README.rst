django-includes
===============

Experimental software. There is no tests, no documentation, use it are your own risks (or don't).

Currently testing that with django 2 and python 3.5+ only, which will be the only supported target.

Install
:::::::

* Add 'django_includes' to INSTALLED_APPS.
* Add DjangoIncludesExtension to Jinja2 environment.

.. code-block:: python

    from django_includes.jinja2 import DjangoIncludesExtension

    def environment(**options):
        env = Environment(**options)

        # your logic here

        env.add_extension(DjangoIncludesExtension)

        return env

* Use `{{ render_sync(request, 'mused.views.MusicGroupListView', musicgenre=object) }}` in templates.

Now, that's only the "synchronous render",

Install hinclude
::::::::::::::::

If you wanna use hinclude (a simple javascript that loads asynchronously some part of your page):

Add hinclude url to your project:

.. code-block:: python

    from django_includes.views import include_view

    urlpatterns += [
        path('hinclude/<token>', include_view, kwargs={'via': 'hinclude'}, name='hinclude')
    ]

Add hinclude to your layout

.. code-block:: html

    <html lang="en" xmlns:hx="http://purl.org/NET/hinclude">
    <head>
        <script src="{{ static('hinclude.js') }}"></script>

* Use `{{ render_hinclude(request, 'mused.views.MusicGroupListView', musicgenre=object) }}` in templates.

Note that this will use json web tokens to encode the parameters, using your django secret as a "seed" for encryption.