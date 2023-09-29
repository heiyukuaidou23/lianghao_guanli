from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


class Authmiddleware(MiddlewareMixin):
    def process_request(self, request):

        # 如果是登录的界面，直接向后运行
        if request.path_info in ["/login/","/img/code/"]:
            return

        #获取session
        info_dict = request.session.get("info")
        # 未登录
        if not info_dict:
            return redirect('/login/')

            # 已登录
            request.info_dict = info_dict


    # def process_response(self,request,response):
    #     print("process_response")
    #     return response
