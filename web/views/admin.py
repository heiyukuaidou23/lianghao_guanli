from django.http import JsonResponse
from django.shortcuts import render, redirect
from django import forms
from web import models

from utils.encrypt import md5


def admin_list(request):
    """ 用户列表 """
    queryset = models.Admin.objects.all().order_by("-id")
    # for row in queryset:
    return render(request, "admin_list.html", {"queryset": queryset})


class AdminModelForm(forms.ModelForm):
    class Meta:
        model = models.Admin
        # fields = "__all__"
        fields = ['username', 'password', 'age', 'gender', 'depart']
        widgets = {
            'username': forms.TextInput(attrs={'class': "form-control"}),
            'password': forms.PasswordInput(attrs={'class': "form-control"}),
            'age': forms.TextInput(attrs={'class': "form-control"}),
            'gender': forms.Select(attrs={'class': "form-control"}),
            'depart': forms.Select(attrs={'class': "form-control"}),
        }

    # def __init_(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     # 自定义操作，找到所有的字段
    #     for name, field_object in self.fields.items():
    #         field_object.widget.attrs = {"class": "form-control"}


def admin_add(request):
    if request.method == "GET":
        form = AdminModelForm()
        return render(request, 'admin_form.html', {"form": form})

    form = AdminModelForm(data=request.POST)
    if not form.is_valid():
        return render(request, 'admin_form.html', {"form": form})

    # 在保存前读取到密码并更新成md5密文再保存到数据库
    form.instance.password = md5(form.instance.password)

    # 保存到数据库
    form.save()
    return redirect('/admin/list/')


# 为编辑页面创建的类，目的是编辑时不显示密码选项
class AdminEditModelForm(forms.ModelForm):
    class Meta:
        model = models.Admin
        # fields = "__all__"
        fields = ['username', 'age', 'gender', 'depart']
        widgets = {
            'username': forms.TextInput(attrs={'class': "form-control"}),
            'age': forms.TextInput(attrs={'class': "form-control"}),
            'gender': forms.Select(attrs={'class': "form-control"}),
            'depart': forms.Select(attrs={'class': "form-control"}),

        }


def admin_edit(request, aid):
    admin_object = models.Admin.objects.filter(id=aid).first()
    if request.method == "GET":
        form = AdminEditModelForm(instance=admin_object)
        return render(request, 'admin_form.html', {"form": form})

    form = AdminEditModelForm(instance=admin_object, data=request.POST)
    if not form.is_valid():
        return render(request, 'admin_form.html', {"form": form})

    # 此时并非保存，而是更新，铜通过id来更新修改的内容
    form.save()
    return redirect('/admin/list/')


def admin_delete(request):
    aid = request.GET.get('aid')
    models.Admin.objects.filter(id=aid).delete()

    return JsonResponse({"status": True})
