def patch_http_development_server():
    """
    HACK: without HTTP/1.1, Chrome ignores certain cache headers during development!
     see http://stackoverflow.com/a/28033770/179583 for a bit more discussion.

    You can include this in your wsgi.py file.

    """
    from wsgiref import simple_server

    simple_server.ServerHandler.http_version = "1.1"
