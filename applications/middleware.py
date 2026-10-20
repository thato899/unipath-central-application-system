from django.middleware.csrf import CsrfViewMiddleware


class BearerAwareCsrfViewMiddleware(CsrfViewMiddleware):
    """Skip cookie CSRF checks only for API calls authenticated by explicit bearer credentials."""

    def process_view(self, request, callback, callback_args, callback_kwargs):
        authorization = request.headers.get("Authorization", "")
        if request.path.startswith("/api/") and authorization.lower().startswith("bearer "):
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)
