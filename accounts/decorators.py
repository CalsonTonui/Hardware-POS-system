from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.role != 'admin':
            messages.error(
                request,
                'You do not have permission to access the administrator area.'
            )

            return redirect('dashboard')

        return view_func(request, *args, **kwargs)

    return wrapper