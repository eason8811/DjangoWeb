import random
import re
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from django import forms
from django.shortcuts import render, redirect
from .models import User
from .forms import UserForm, RegisterForm
import hashlib
import datetime
from django.conf import settings


def start(request):
    return redirect('index/')


# 密码加密
def hash_code(s, salt='mysite'):
    h = hashlib.sha3_256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


# 主页
def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'index.html', {'is_login': request.session.get('is_login')})


def login(request):
    if request.session.get('is_login', None):  # 不允许重复登录
        return redirect('/index/')
    if request.method == 'POST':
        login_form = UserForm(request.POST)
        message = '请检查填写的内容！'
        if login_form.is_valid():
            # 用户名字符合法性验证
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')

            try:
                user = User.objects.get(name=username)
            except:
                message = '用户名不存在！'
                return render(request, 'login.html', locals())
            if user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/index/')
            else:
                message = '密码不正确！'
                return render(request, 'login.html', locals())

        else:
            return render(request, 'login.html', locals())
    login_form = UserForm()
    return render(request, 'login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')

    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')

            if password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'register.html', locals())
            else:
                # 判断用户是否存在
                same_name_user = User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已经存在'
                    return render(request, 'register.html', locals())

                new_user = User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.save()

                # code = make_confirm_string(new_user)
                # send_mail(email, code)

                return redirect('/login/')
        else:
            return render(request, 'register.html', locals())
    register_form = RegisterForm()
    return render(request, 'register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")

    request.session.flush()
    # 或者使用下面的方法清除缓存数据
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/login/")
