from django.shortcuts import render
from django.urls import resolve
from django.conf import settings


class LoginRequiredMiddleware:
    """
    Middleware that redirects unauthenticated users to a custom error page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(
            request, "user"
        ), "The Login Required middleware requires authentication middleware to be installed. Edit your MIDDLEWARE setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware'."

        # Get the current route name
        current_route_name = resolve(request.path_info).url_name

        # Check if the current route is in the exempt routes
        if current_route_name not in settings.LOGIN_EXEMPT_ROUTES:
            if not request.user.is_authenticated:
                return render(request, "page404.html", status=403)

        return None
