"""
URL configuration for DjangoWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from Emotional_Analysis import views

urlpatterns = [
    path('', views.start),
    # 主界面
    path('index/', views.index),
    # 登录注册以及验证码
    path('login/', views.login),
    path('register/', views.register),
    path('logout/', views.logout),
    path('captcha/', include('captcha.urls')),
    # 主页
    path('main_page/', views.main_page),
    path('all_comment/', views.all_comment, name='all_comment'),
    path('kline/', views.kline, name='kline'),
    path('main_wordcloud/', views.main_wordcloud, name='main_wordcloud'),
    path('main_pie/', views.main_pie, name='main_pie'),
]
