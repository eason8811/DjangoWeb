import random
import re
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from django import forms
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse

from Emotional_Analysis.models import UserInfo

session = {'code': None}


def hello_world(request):
    is_login = request.user.is_authenticated
    return render(request, 'index.html', {'is_login': is_login})


###################### 创建UserForm用户校验，输入的内容是否合法##############
class UserForm(forms.Form):
    user = forms.CharField(min_length=5, label='用户名')
    pwd = forms.CharField(min_length=5, widget=widgets.PasswordInput(), label="密码")
    r_pwd = forms.CharField(min_length=5, widget=widgets.PasswordInput(), label="确认密码")
    email = forms.EmailField(min_length=5, label="邮箱")

    # 为每一个字段 input 添加类名 form-control
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filed in self.fields.values():
            filed.widget.attrs.update({'class': 'form-control'})

    def clean_user(self):
        val = self.cleaned_data.get('user')
        user = UserInfo.objects.filter(username=val).first()
        if user:
            raise ValidationError('用户名已存在！')
        else:
            return val

    def clean_pwd(self):
        val = (self.cleaned_data.get('pwd'))
        if val.isdigit():
            raise ValidationError('密码不能为纯数字！')
        else:
            return val

    def clean_email(self):
        val = self.cleaned_data.get('email')
        if re.search("\w+@163.com$", val):
            return val
        else:
            raise ValidationError('邮箱必须是163格式邮箱！')

    def clean(self):  # 全局校验
        pwd = self.cleaned_data.get('pwd')
        r_pwd = self.cleaned_data.get('r_pwd')
        if pwd and r_pwd and pwd != r_pwd:
            # raise ValidationError("两次密码不一致！")

            # 也可以采用以下方法，这样在渲染的时候可以不用特殊处理，全局的错误会在r_pwd中，不再是__all__
            self.add_error("r_pwd", ValidationError('两次密码不一致！'))
        else:
            return self.cleaned_data


####################### 登录  ######################
def login(request):
    if request.method == "GET":
        return render(request, "login.html")

    else:
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        validcode = request.POST.get("validcode")

        res = {"user": None, "error_msg": ""}
        if validcode.upper() == request.session.get("keep_str").upper():
            user_obj = auth.authenticate(username=user, password=pwd)
            if user_obj:
                res["user"] = user
            else:
                res["error_msg"] = "用户名或密码错误！"
        else:
            res["error_msg"] = "验证码错误"

        return JsonResponse(res)


#######################   生成验证码  ################################
def get_valid_img(request):
    def get_random_color():
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # 生成图片
    img = Image.new("RGB", (250, 35), get_random_color())
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("static/font/kumo.ttf", 32)

    keep_str = ''  # 用于存储验证码，用户后台校验

    # 为图片添加随机文本text
    for i in range(6):
        rand_num = str(random.randint(0, 9))
        rand_lowalp = chr(random.randint(97, 122))
        rand_upealp = chr(random.randint(65, 90))

        random_char = random.choice([rand_num, rand_lowalp, rand_upealp])

        draw.text((i * 30 + 50, 0), random_char, get_random_color(), font=font)
        keep_str += random_char

    # --------加噪点和噪线------
    width = 250
    height = 35
    for i in range(3):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=get_random_color())

    for i in range(2):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())

    # 将生成的图片进行读写
    f = BytesIO()  # 写，在内存中创建文件句柄
    img.save(f, "png")  # 将img保存在句柄中

    data = f.getvalue()  # 读取图片字节，返回给img响应

    # 生成的随机字符串，加到sesstion中，传给用户，在用户登录时候进行校验，不能将随机字符串作为全局变量
    request.session["keep_str"] = keep_str

    # 将图片字节 直接响应回图片
    return HttpResponse(data)


##########################  注册  ##########################
def reg(request):
    if request.method == "GET":
        userform = UserForm()
        return render(request, "reg.html", locals())
    else:
        form = UserForm(request.POST)

        res = {"user": None, "err_msg": ""}

        if form.is_valid():
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')

            UserInfo.objects.create_user(username=user, password=pwd, email=email)

            res['user'] = user
        else:
            res['err_msg'] = form.errors

        return JsonResponse(res)
