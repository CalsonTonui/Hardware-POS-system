from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """Redirect users to password change page if they must change password."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check for authenticated users
        if request.user.is_authenticated:
            # Skip for certain paths (password change, logout, static, etc.)
            exempt_paths = [
                reverse('force_password_change'),
                reverse('logout'),
                reverse('profile'),
                '/static/',
                '/media/',
            ]

            path = request.path

            # Skip if path is exempt
            if any(path.startswith(p) for p in exempt_paths):
                return self.get_response(request)

            # Skip admin URLs (Django admin)
            if path.startswith('/admin/'):
                return self.get_response(request)

            # If user must change password, redirect
            if getattr(request.user, 'must_change_password', False):
                return redirect('force_password_change')

        return self.get_response(request)