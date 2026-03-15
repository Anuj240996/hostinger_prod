from django.http import HttpResponse
from django.shortcuts import redirect


# def auth_users(view_func):
#     def wrapper(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             return redirect('dashboard-index')
#         else:
#             return view_func(request, *args, **kwargs)
#     return wrapper

def auth_users(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard-index')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper



def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles or request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('user-login')
        return wrapper_func
    return decorator
