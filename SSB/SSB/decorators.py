from django.shortcuts import redirect
from functools import wraps


def role_permission(user_type):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_type_str = user_type.lower()
            if request.user.is_superuser:
                if user_type_str == 'admin':
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect('redirect')
            elif request.user.profile.user_type == user_type_str:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('redirect')
        return wrapper
    return decorator
