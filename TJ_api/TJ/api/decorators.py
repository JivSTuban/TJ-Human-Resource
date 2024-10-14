from django.shortcuts import redirect
from functools import wraps

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view_func(request, *args, **kwargs):
            if request.user.is_authenticated:
                if hasattr(request.user, 'role') and request.user.role == role:
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect('login')
            else:
                return redirect('login')
        return _wrapped_view_func
    return decorator

manager_required = role_required('MANAGER')
employee_required = role_required('EMPLOYEE')