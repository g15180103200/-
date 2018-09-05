from django.http import HttpResponseRedirect

# 判断是否已经登录


def islogin(func):
    def login_fun(request, *args, **kwargs):
        if request.session.get('user_id'):
            return func(request, *args, **kwargs)
        else:
            resp = HttpResponseRedirect('/user/login')
            resp.set_cookie('url', request.get_full_path())
            return resp
    return login_fun


# http://127.0.0.1:8000/200/?type=10
# request.path:表示当前路径,为/200/
# request.get_full_path():表示完整路径, 为/200/?type=10
