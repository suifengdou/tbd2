# coding: utf-8

import json


from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse


from apps.users.forms import LoginForm

# from pure_pagination import Paginator, EmptyPage, PageNotAnInteger


# class CustomBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             user = UserProfile.objects.get(Q(username=username) | Q(email=username))
#             if user.check_password(password):
#                 return user
#         except Exception as e:
#             return None
# #
#
# class RegisterView(View):
#     def get(self, request):
#         register_form = RegisterForm()
#         return render(request, "register.html", {'register_form': register_form})
#
#     def post(self, request):
#         register_form = RegisterForm(request.POST)
#         if register_form.is_valid():
#             user_name = request.POST.get("email", None)
#             if UserProfile.objects.filter(email=user_name):
#                 return render(request, "register.html", {"register_form": register_form, "msg": "用户已经存在"})
#             pass_word = request.POST.get("password", None)
#             user_profile = UserProfile()
#             user_profile.username = user_name
#             user_profile.email = user_name
#             user_profile.is_active = False
#             user_profile.password = make_password(pass_word)
#             user_profile.save()
#
#             # 写入欢迎注册信息
#             user_message = UserMessage()
#             user_message.user = user_profile.id
#             user_message.message = "欢迎注册TBD"
#             user_message.save()
#
#             send_register_email(user_name, "register")
#             return render(request, "login.html")
#         else:
#
#             return render(request, "register.html", {"register_form": register_form})
#

class IndexView(View):
    """
    TBD首页
    """
    def get(self, request):

        return render(request, "index.html", {})



class LoginView(View):
    def get(self, request):
        return render(request, "auth/auth-sign-in-social.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get("username", None)
            password = request.POST.get("password", None)
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, "auth/auth-sign-in-social.html", {"msg": "用户名未激活"})
            else:
                return render(request, "auth/auth-sign-in-social.html", {"msg": "用户名密码错误"})
        else:
            return render(request, "auth/auth-sign-in-social.html", {"login_form": login_form})



class LogoutView(View):
    def get(self, request):
        logout(request)
        from django.urls import reverse
        return HttpResponseRedirect(reverse("index"))


# class UserInfoView(View):
#     """
#     客户信息中心
#     """
#     def get(self, request):
#         return render(request, "auth/user-profile.html", {})
#
#     def post(self, request):
#         user_info_form = UserInfoForm(request.POST, instance=request.user)
#         if user_info_form.is_valid():
#             user_info_form.save()
#             return HttpResponse('{"status": "success"}', content_type='application/json')
#         else:
#             return HttpResponse(json.dump(user_info_form.errors), content_type='application/json')


# class ForgetPwdView(View):
#     def get(self, request):
#         forget_form = ForgetForm()
#         return render(request, "forgetpwd.html", {"forget_form": forget_form})
#
#     def post(self, request):
#         forget_form = ForgetForm(request.POST)
#         if forget_form.is_valid():
#             email = request.POST.get('email', None)
#             send_register_email(email, "forget")
#             return render(request, "send_success.html")
#         else:
#             return render(request, "forgetpwd.html", {"forget_form": forget_form})
#
#
# class ActiveUserView(View):
#     def get(self, request, active_code):
#         all_records = EmailVerifyRecord.objects.filter(code=active_code)
#         if all_records:
#             for record in all_records:
#                 email = record.email
#                 user = UserProfile.objects.get(email=email)
#                 user.is_active = True
#                 user.save()
#         else:
#             return render(request, "active_fail.html")
#         return render(request, "login.html")
#
#
# class ResetView(View):
#     def get(self, request, active_code):
#         all_records = EmailVerifyRecord.objects.filter(code=active_code)
#         if all_records:
#             for record in all_records:
#                 email = record.email
#                 return render(request, "password_reset.html", {"email": email})
#         else:
#             return render(request, "active_fail.html")
#         return render(request, "login.html")
#
#
# class ModifyPwdView(View):
#     def post(self, request):
#         modify_form = ModifyPwdForm(request.POST)
#         if modify_form.is_valid():
#             pwd1 = request.POST.get("password1", None)
#             pwd2 = request.POST.get("password2", None)
#             email = request.POST.get("email", None)
#             if pwd1 != pwd2:
#                 return render(request, "password_reset.html", {"email": email, "msg": "密码不一致！"})
#             user = UserProfile.objects.get(email=email)
#             user.password = make_password(pwd1)
#             user.save()
#             return render(request, "login.html")
#         else:
#             email = request.POST.get("email", None)
#             return render(request, "password_reset.html", {"email": email, "modify_form": modify_form})
#
#

#
#
#
# class UploadImageView(LoginRequiredMixin, View):
#     """
#     用户修改头像
#     """
#     def post(self, request):
#         image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
#         if image_form.is_valid():
#             image_form.save()
#             return HttpResponse('{"status": "success"}', content_type='application/json')
#         else:
#             return HttpResponse('{"status": "fail"}', content_type='application/json')
#
#
# class UpdatePwdView(LoginRequiredMixin, View):
#     """
#     个人中心修改密码
#     """
#     def post(self, request):
#         modify_form = ModifyPwdForm(request.POST)
#         if modify_form.is_valid():
#             pwd1 = request.POST.get("password1", None)
#             pwd2 = request.POST.get("password2", None)
#
#             if pwd1 != pwd2:
#                 return HttpResponse('{"status": "fail", "msg":"密码不一致"}', content_type='application/json')
#             user = request.user
#             user.password = make_password(pwd1)
#             user.save()
#             return HttpResponse('{"status": "success", "msg":"修改成功"}', content_type='application/json')
#         else:
#             return HttpResponse(json.dump(modify_form.errors), content_type='application/json')
#
#
# class SendEmailCodeView(LoginRequiredMixin, View):
#     """
#     个人中心发送邮箱验证码，修改邮箱
#     """
#     def get(self, request):
#         email = request.GET.get('email', '')
#         if UserProfile.objects.filter(email=email):
#             return HttpResponse('{"email":"邮箱已经存在"}', content_type='application/json')
#         send_register_email(email, "update_email")
#         return HttpResponse('{"status": "success"}', content_type='application/json')
#
#
# class UpdateEmailView(LoginRequiredMixin, View):
#     """
#     个人中心修改邮箱
#     """
#     def post(self, request):
#         email = request.POST.get('email', "")
#         code = request.POST.get("code", "")
#
#         existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type="update_email")
#         if existed_records:
#             user = request.user
#             user.email = email
#             user.save()
#             return HttpResponse('{"status": "success"}', content_type='application/json')
#         else:
#             return HttpResponse('{"email":"验证码出错"}', content_type='application/json')


# class MyMessageView(LoginRequiredMixin, View):
#     """
#     我的消息
#     """
#     def get(self, request):
#         all_message = UserMessage.objects.filter(user=request.user.id)
#
#         # 用户进入个人消息后清空未读消息的记录。
#         all_unread_message = UserMessage.objects.filter(user=request.user.id, has_read=False)
#         for unread_message in all_unread_message:
#             unread_message.has_read = True
#             unread_message.save()
#
#         # 对个人消息进行分页
#         try:
#             page = request.GET.get('page', 1)
#         except PageNotAnInteger:
#             page = 1
#
#         # Provide Paginator with the request object for complete querystring generation
#         p = Paginator(all_message, 3, request=request)
#         messages = p.page(page)
#
#         return render(request, "usercenter-message.html", {
#             "messages": messages,
#         })



#
# def page_not_found(request):
#     # 全局404
#     from django.shortcuts import render_to_response
#     response = render_to_response("404.html", {})
#     response.status_code = 404
#     return response
#
#
# def page_error(request):
#     # 全局500
#     from django.shortcuts import render_to_response
#     response = render_to_response("500.html", {})
#     response.status_code = 500
#     return response
#
#
# def server_error(request):
#
#     from django.shortcuts import render_to_response
#     response = render_to_response("403.html", {})
#     response.status_code = 403
#     return response
