import string
import random
import time
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from django.core.mail import send_mail
from .forms import LoginForm, RegForm, ChangeNicknameForm, BindEmailForm
from .models import Profile

def login(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from',reverse('index'))) #重定向到点击登录之前的页面，如果失败则跳转到首页
    else:
        login_form = LoginForm()
    
    context = {}
    context['login_form'] = login_form
    return render(request, 'user/login.html', context)

def login_for_medal(request):#模态框登录窗口
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def register(request):
    if request.method == "POST":
        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            #注册用户
            user = User.objects.create_user(username, email, password)
            user.save()
            # 登录用户
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
             #跳转到点击注册之前的页面，如果失败则跳转到首页
            return redirect(request.GET.get('from',reverse('index')))
    else:
        reg_form = RegForm()
    context = {}
    context['reg_form'] = reg_form
    return render(request, 'user/register.html', context)

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('index')))

def user_info(request):
    context = {}
    return render(request, 'user/user_info.html', context)    

def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('user_info')) # 修改成功跳转回个人资料页面
    
    if request.method == "POST":
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid(): # 判断新昵称是否合理
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to) #重定向到点击登录之前的页面，如果失败则跳转到首页
    else:
        form = ChangeNicknameForm()
    
    context = {}
    context['page_title'] = '个人资料修改'
    context['form_title'] = '资料修改'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)

def bind_email(request):
    redirect_to = request.GET.get('from', reverse('index'))

    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            return redirect(redirect_to)
    else:
        form = BindEmailForm()

    context = {}
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/bind_email.html', context)

def send_verification_code(request): # 发送验证码给邮箱
    email = request.GET.get('email', '')
    #print(email)
    data = {}

    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 5))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'ERROR'
        else:
            request.session['bind_email_code'] = code
            request.session['send_code_time'] = now
            
            # 发送邮件
            #print ("code = ", code)
            send_mail(
                '绑定邮箱设置~~',
                '你的绑定邮箱的验证码为：%s' % code,
                '493948994@qq.com',
                [email],
                fail_silently = False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)
