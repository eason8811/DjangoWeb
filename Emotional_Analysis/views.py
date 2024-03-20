from django.shortcuts import render
from tools.get_captcha import get_captcha_code_and_content

session = {'code': None}


def hello_world(request):
    is_login = request.user.is_authenticated
    return render(request, 'index.html', {'is_login': is_login})


def login(request):
    return render(request, 'login.html')


def logout(request):
    global session
    captcha_uuid = request.GET.get("captcha_uuid")
    code, content = get_captcha_code_and_content()
    # 3.记录数据到数据库(用session代替)
    session['code'] = code
    resp = make_response(content)
    resp.content_type = "image/png"
    # 4. 返回响应体
    return resp
