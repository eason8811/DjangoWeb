import hashlib
import datetime
import pandas as pd
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.http import JsonResponse

from .forms import UserForm, RegisterForm
from .models import User, Comment
from .tools.fig_wordCloud import fig_wordcloud
from .tools.match import match_words
from .tools.grab import grab_data
from .tools.fig_out import fig_output_html, fig_pie, fig_kline, fig_calendar, liquid
from tqdm import tqdm
import time

code = 300059


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


# ====================================================================
def main_page(request):
    global code
    data = pd.read_csv(f"Emotional_Analysis/output/data_{code}.csv", index_col=0)
    data = data.sort_values(by=["comment_date"])
    last_comment_text = data.iloc[-1, 0]
    last_comment_date = data.iloc[-1, 1]
    return render(request, 'main_page.html',
                  {'last_comment_text': last_comment_text,
                   'last_comment_date': last_comment_date})


def all_information(request):
    page = request.GET.get('page', type=int, default=1)
    per_page = request.GET.get('limit', type=int, default=10)
    start = (page - 1) * per_page
    end = start + per_page
    comment_text = request.GET.get('comment_text')
    if comment_text is None:
        raw_sql = "select comment_text,comment_date from comment"
        comment_rows = Comment.objects.raw(raw_sql)
    else:
        raw_sql = f"select comment_text,comment_date from comment where comment_text like %s"
        comment_rows = Comment.objects.raw(raw_sql, ['%' + comment_text + '%'])
    rets = comment_rows
    count = len(rets)
    rets = rets[start:end]
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': count,
        'data': [
            {
                'comment_text': ret[0],
                'create_at': ret[1]
            } for ret in rets
        ]
    }


def all_comment(request):
    print(reverse('all_comment'))
    return render(request, 'graphic/all_comment.html')


def kline(request):
    global code
    return render(request, f'graphic/kline_{code}.html')


def get_last_day():
    data = pd.read_csv("Emotional_Analysis/output/rating.csv", index_col=0)
    data = data.sort_values(by=["date"], ascending=False)
    return data.iloc[0, 0]


def main_wordcloud(request):
    # today = time.strftime("%m-%d", time.localtime())
    today = get_last_day()
    return render(request, f'wordcloud/wordcloud_{today}.html')


def main_pie(request):
    return render(request, f'graphic/pie_.html')


total = 100  # 总任务数
current_statue = 0
tasks = range(total)
pbar = tqdm(total=len(tasks))
status = ''


def handle_data(request):
    global status, code, current_statue
    if request.method == 'POST':
        pbar.reset()
        # data = request.json
        data = request.POST
        code = data['input_code']
        last_day = data['last_day']
        print(data)
        last_day_ = datetime.datetime.strptime(last_day, "%Y-%m-%dT%H:%M")
        day = last_day_.strftime("%m-%d")
        pbar.update(10)  # 10%
        current_statue = 10
        status = '初始化'
        # 爬取数据
        status = '爬取数据'
        grab_data(code=code, day=day)
        pbar.update(20)  # 30%
        current_statue = 30
        # 文本分析
        status = '文本分析'
        match_words(code)
        pbar.update(20)  # 50%
        current_statue = 50
        # 作图
        status = '作图'
        fig_output_html()
        liquid()
        fig_kline(code, day)
        fig_wordcloud(code)
        fig_pie()
        fig_calendar()
        pbar.update(10)  # 60%
        current_statue = 60
        # 导入数据库
        status = '导入数据库'
        # db.load_csv(f"./output/data_{code}.csv")
        data_csv = pd.read_csv(f"Emotional_Analysis/output/data_{code}.csv", index_col=0)
        for i in tqdm(range(len(data_csv))):
            list = []
            list.append(str(i))
            for j in range(3):
                list.append(str(data_csv.iloc[i, j]))
            Comment.objects.create(comment_text=list[1], comment_date=list[2], comment_time=list[3])
            print(f'到这里{i}')
            print(list)
            pbar.update(round(40 / len(data_csv), 3))
            current_statue = 60 + i * 40 / len(data_csv)
        pbar.update(1)  # 100%
        current_statue = 100
        status = '爬取完成'
        time.sleep(1)
        current_statue = 101

        pbar.refresh()
        return HttpResponse('股票代码收到')


def progress(resquest):
    """查看进度"""
    global status, code, current_statue, pbar
    response_data = {
        'status': status,
        'n': current_statue,
        'total': pbar.total
    }
    response = JsonResponse(response_data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = '*'
    response['Access-Control-Allow-Methods'] = '*'
    return response
