from threading import local


_thread_locals = local()


def get_current_request():
    """ returns the request object for this thread
        @:return Request object
    """
    return getattr(_thread_locals, "request", None)


def get_current_user():
    """ returns the current user, if it exists, otherwise returns None """
    request = get_current_request()
    if request:
        return getattr(request, "user", None)


class ThreadLocalMiddleware:
    """ Simple middleware that adds the request object in thread local storage."""
    def process_request(self, request):
        _thread_locals.request = request
