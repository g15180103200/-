import json
import hashlib
import random
import re
import urllib
import http.client

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from hashlib import sha1
from .islogin import *
from df_goods.models import *
from df_order.models import OrderInfo
from df_cart.models import *

# Create your views here.


def register(request):
    context = {'title': '用户注册'}
    return render(request, 'df_user/register.html', context)


# 处理注册
def register_handle(request):
    # 接收用户输入数据
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    uphone = post.get('user_phone')
    uemail = post.get('email')
    code = post.get("code")
    # 密码加密
    s1 = sha1()
    s1.update(upwd.encode('utf8'))  # 指定编码格式,否则会报错
    upwd_jm = s1.hexdigest()
    # 创建对象
    user = UserInfo()
    user.uname = uname
    user.uphone = uphone
    user.upwd = upwd_jm
    user.uemail = uemail
    if code == request.session.get("message_code", None):
        user.save()
        # 注册成功转到登录页面
        return redirect('/user/login/')
    return redirect('/user/register')


# 判断用户名或手机号或邮箱是否已经存在
def register_exist(request):
    dic = {}
    # 验证用户名是否已存在
    if 'uname' in request.GET:
        uname = request.GET['uname']
        # 判断用户名是否有特殊字符,防止sql注入
        L = re.findall(r'[\w-]+', uname)
        print(L)
        if L[0] != uname:
            dic['status'] = 2
        else:
            # count()返回查询的结果数,要么是0要么是1
            count = UserInfo.objects.filter(uname=uname).count()
            dic['status'] = count
        return HttpResponse(json.dumps(dic))
    # 验证手机号是否已存在,发送短信验证码
    elif 'uphone' in request.GET:
        uphone = request.GET['uphone']
        count = UserInfo.objects.filter(uphone=uphone).count()
        print(uphone)
        dic['status'] = count
        return HttpResponse(json.dumps(dic))

    elif 'uemail' in request.GET:
        uemail = request.GET['uemail']
        count = UserInfo.objects.filter(uemail=uemail).count()
        dic['status'] = count
        return HttpResponse(json.dumps(dic))


# 验证码
def check_code(request):
    host = "106.ihuyi.com"
    sms_send_uri = "/webservice/sms.php?method=Submit"
    # 用户名是登录ihuyi.com账号名（例如：cf_demo123）
    account = "C61395953"
    # 密码 查看密码请登录用户中心->验证码、通知短信->帐户及签名设置->APIKEY
    password = "56cf431c085a18ee77f19ad2b492324f"
    uphone = request.GET['uphone']
    # 定义一个字符串,存储生成的6位数验证码
    message_code = ''
    for i in range(6):
        i = random.randint(0, 9)
        message_code += str(i)

    # 拼接成发出的短信
    text = "您的验证码是：" + message_code + "。请不要把验证码泄露给其他人。"
    # 把请求参数编码
    params = urllib.parse.urlencode(
        {'account': account,
         'password': password,
         'content': text,
         'mobile': uphone,
         'format': 'json'})
    # 请求头
    headers = {
        "Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    # 通过全局的host去连接服务器
    conn = http.client.HTTPConnection(host, port=80, timeout=30)
    # 向连接后的服务器发送post请求,路径sms_send_uri是全局变量,参数,请求头
    conn.request("POST", sms_send_uri, params, headers)
    # 得到服务器的响应
    response = conn.getresponse()
    # 获取响应的数据
    response_str = response.read()
    # 关闭连接
    conn.close()
    # 把验证码放进session中
    request.session['message_code'] = message_code
    print("哈哈哈")
    print(response_str.decode())
    print(eval(response_str.decode()))
    # 使用eval把字符串转为json数据返回
    return JsonResponse(eval(response_str.decode()))


# 登录页面
def login(request):
    uname = request.COOKIES.get('userlogin', '')
    context = {'title': '用户登录', 'error_pwd': 1, 'userlogin': uname}
    return render(request, 'df_user/login.html', context)


# 登录处理
def login_handle(request):
    # 接收数据
    userlogin = request.POST['userlogin']
    leng = len(userlogin)
    print(userlogin)
    upwd = request.POST['pwd']
    jizhu = request.POST.get('jizhu', 0)
    print(upwd)
    print(jizhu)
    # 创建加密对象
    s1 = sha1()
    s1.update(upwd.encode('utf8'))
    upwd = s1.hexdigest()

    if re.findall(r'^1\d{10}', userlogin):
        user = UserInfo.objects.filter(uphone=userlogin, upwd=upwd)
    elif re.findall(r'^\w+$', userlogin):
        user = UserInfo.objects.filter(uname=userlogin, upwd=upwd)
    else:
        user = UserInfo.objects.filter(uemail=userlogin, upwd=upwd)
    print("-----------------------")
    print('user', user)
    if not user:
        context = {'title': '用户登录', 'error_pwd': 0, 'userlogin': userlogin}
        return render(request, 'df_user/login.html', context)
    else:
        # 登录成功去往主页
        resp = HttpResponseRedirect('/')
        count = CartInfo.objects.filter(user_id=user[0].id).count()
        if jizhu != 0:
            resp.set_cookie('userlogin', userlogin)
        else:
            resp.set_cookie('userlogin', '', max_age=-1)
        request.session['user_id'] = user[0].id
        request.session['user_name'] = user[0].uname
        request.session['count'] = count
        return resp


# 登录用户中心
@islogin
def info(request):
    user_email = UserInfo.objects.get(id=request.session['user_id']).uemail

    # 最近浏览
    goods_ids = request.COOKIES.get('goods_ids', '')
    goods_id_list = goods_ids.split(',')
    goods_list = []
    if len(goods_ids):
        for goods_id in goods_id_list:
            goods_list.append(GoodsInfo.objects.get(id=int(goods_id)))

    context = {'title': '用户中心',
               'user_email': user_email,
               'user_name': request.session['user_name'],
               'page_name': 1,
               'info': 1,
               'goods_list': goods_list}
    return render(request, 'df_user/user_center_info.html', context)


# 订单
@islogin
def order(request):
    context = {'title': '用户中心', 'page_name': 1, 'order': 1}
    return render(request, 'df_user/user_center_order.html', context)


# 收货地址
@islogin
def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        post = request.POST
        user.ushou = post.get('ushou')
        user.uaddress = post.get('uaddress')
        user.uphone = post.get('uphone')
        user.upostcode = post.get('uyoubian')
        user.save()

    context = {'title': '用户中心', 'user': user, 'page_name': 1, 'site': 1}
    return render(request, 'df_user/user_center_site.html', context)


def logout(request):
    # 清除会话数据，在存储中删除会话的整条数据
    request.session.flush()
    return redirect('/')


@islogin
def user_center_order(request, pageid):
    """
    此页面向用户展示用户提交的订单,由购物车页面下单后转调过来，也可以从个人信息页面查看
    根据用户订单是否支付、下单顺序进行排序
    :param request:
    :param pageid:
    :return:
    """
    uid = request.session.get('user_id')
    # 订单信息,根据是否支付,下单顺序进行排序
    orderinfos = OrderInfo.objects.filter(
        user_id=uid).order_by('zhifu', '-oid')

    # 分页
    # 获取orderinfos list 以两个为一页的list
    paginator = Paginator(orderinfos, 2)
    # 获取上面集合的第pageid 个值
    orderlist = paginator.page(int(pageid))
    # 获取一共多少页
    plist = paginator.page_range
    # 3页分页显示
    qian1 = 0
    hou = 0
    hou2 = 0
    qian2 = 0
    dd = int(pageid)
    lenn = len(plist)
    if dd > 1:
        qian1 = dd - 1
    if dd >= 3:
        qian2 = dd - 2
    if dd < lenn:
        hou = dd + 1

    if dd+2 <= lenn:
        hou2 = dd + 2

    # 构造上下文
    context = {'page_name': 1, 'title': '全部订单', 'pageid': int(pageid),
               'order': 1, 'orderlist': orderlist, 'plist': plist,
               'pre': qian1, 'next': hou, 'pree': qian2, 'lenn': lenn, 'nextt': hou2}
    return render(request, 'df_user/user_center_order.html', context)
