from io import BytesIO

from django import forms
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from web import models
from utils.encrypt import md5
from utils.helper import check_code



@csrf_exempt
class LoginForm(forms.Form):
    username = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': "输入用户名"}),
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={'class': "form-control", 'placeholder': "输入密码"}, render_value=True),
    )
    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': "输入验证码"}),
    )


@csrf_exempt
def login(request):
    """用户登录"""
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {'form': form})

    form = LoginForm(data=request.POST)
    if not form.is_valid():
        return render(request, "login.html", {'form': form})

    # 判断验证码是否正确
    image_code = request.session.get('image_code')
    if not image_code:
        form.add_error("code", "验证码已失效")
        return render(request, "login.html", {'form': form})
    if image_code.upper() != form.cleaned_data['code'].upper():
        form.add_error("code", "验证码错误")
        return render(request, "login.html", {'form': form})

    # 验证码正确，去数据库对比
    user = form.cleaned_data['username']
    pwd = form.cleaned_data['password']
    encrypt_password = md5(pwd)
    # print(user,encrypt_password)
    admin_object = models.Admin.objects.filter(username=user, password=encrypt_password).first()
    if not admin_object:
        return render(request, "login.html", {'form': form, 'error': "用户名或密码错误"})
    request.session['info'] = {"id": admin_object.id, 'name': admin_object.username}
    # 设置一个时间为一周
    request.session.set_expiry(60 * 60 * 24 * 7)

    return redirect('')


# form = LoginForm(data=request.POST)
# if form.is_valid():
#     # 得到一个字典：form.cleaned_data={"username":"11122"}
#     # print(form.cleaned_data)
#     # 拿着这个字典去数据库校验
#     # user_object = models.UserInfo.objects.filter(username=form.cleaned_data['username'],
#     #                                              password=form.cleaned_data['password']).first()
#     user_object = models.UserInfo.objects.filter(**form.cleaned_data).first()
#     if user_object:
#         return HttpResponse("登录成功")
# else:
#     return render(request, 'login.html', {"form": form, 'error': "用户名或密码错误"})


def img_code(request):
    # 1.生成图片
    image_object, code_str = check_code()
    # 2.图片内容写入内存并返回
    stream = BytesIO()
    image_object.save(stream, 'png')
    # 3.将图片的内容存到session中，时间为60s
    request.session['image_code'] = code_str
    request.session.set_expiry(60)

    return HttpResponse(stream.getvalue())


def home(request):
    # request.info_dict
    return render(request,'home.html')

def logout(request):
    request.session.clear()
    return redirect('/login/')
