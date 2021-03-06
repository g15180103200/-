from django.shortcuts import render
from .models import *
from django.shortcuts import render
from django.core.paginator import Paginator
from df_cart.models import CartInfo
# from __future__ import unicode_literals


# Create your views here.
# 查询每类商品最新的4个和点击率最高的4个
def index(request):
    """
    index函数负责查询页面中需要展示的商品内容,
    主要是每类最新的4种商品和4种点击率最高的商品,
    每类商品需要查询2次
    :param request:
    :return:
    """
    if 'user_id' in request.session:
        count = CartInfo.objects.filter(
            user_id=request.session['user_id']).count()
    else:
        count = 0
    # count = request.session.get('count')

    fruit = GoodsInfo.objects.filter(gtype_id=1).order_by('-id')[:4]
    fruit2 = GoodsInfo.objects.filter(gtype_id=1).order_by('-gclick')[:4]
    fish = GoodsInfo.objects.filter(gtype_id=2).order_by('-id')[:4]
    fish2 = GoodsInfo.objects.filter(gtype_id=2).order_by('-gclick')[:4]
    meat = GoodsInfo.objects.filter(gtype_id=3).order_by('-id')[:4]
    meat2 = GoodsInfo.objects.filter(gtype_id=3).order_by('-gclick')[:4]
    egg = GoodsInfo.objects.filter(gtype_id=4).order_by('-id')[:4]
    egg2 = GoodsInfo.objects.filter(gtype_id=4).order_by('-gclick')[:4]
    vegtables = GoodsInfo.objects.filter(gtype_id=5).order_by('-id')[:4]
    vegtables2 = GoodsInfo.objects.filter(gtype_id=5).order_by('-gclick')[:4]
    frozen = GoodsInfo.objects.filter(gtype_id=6).order_by('-id')[:4]
    frozen2 = GoodsInfo.objects.filter(gtype_id=6).order_by('-gclick')[:4]

    # 构造上下文
    context = {
        'title': '首页', 'fruit': fruit, 'fish': fish, 'meat': meat, 'egg': egg,
        'vegtables': vegtables, 'frozen': frozen,
        'fruit2': fruit2, 'fish2': fish2, 'meat2': meat2, 'egg2': egg2,
        'vegtables2': vegtables2, 'frozen2': frozen2,
        'guest_cart': 1, 'page_name': 0, 'count': count
    }
    # 返回渲染模板
    return render(request, 'df_goods/index.html', context)


# 商品列表
def goodlist(request, typeid, pageid, sort):
    """
    goodlist函数负责展示某类商品的信息.
    url中的参数依次代表
    :param request:
    :param typeid:
    :param pageid:
    :param sort:
    :return:
    """
    count = request.session.get('count')
    # 获取最新发布的商品
    newgood = GoodsInfo.objects.all().order_by('-id')[:2]
    # 根据条件查询所有商品
    if sort == '1':  # 按最新 gtype_id,gtype_id 指typeinfo_id
        sumGoodList = GoodsInfo.objects.filter(gtype_id=typeid).order_by('-id')
    elif sort == '2':  # 按价格排序
        sumGoodList = GoodsInfo.objects.filter(
            gtype_id=typeid).order_by('gprice')
    elif sort == '3':  # 按点击量
        sumGoodList = GoodsInfo.objects.filter(
            gtype_id=typeid).order_by('-gclick')
    # 分页
    paginator = Paginator(sumGoodList, 15)
    goodList = paginator.page(int(pageid))
    pindexlist = paginator.page_range
    print('----------goodlist------------')
    print('pindexlist:', pindexlist)
    # 确定商品类型
    goodtype = TypeInfo.objects.get(id=typeid)
    # 构造上下文
    context = {
        'title': '商品详情', 'list': 1, 'guest_cart': 1, 'goodtype': goodtype,
        'newgood': newgood, 'goodList': goodList, 'typeid': typeid, 'srot': sort,
        'pindexlist': pindexlist, 'pageid': int(pageid), 'count': count
    }
    # 渲染返回结果
    return render(request, 'df_goods/list.html', context)


def detail(request, id):
    goods = GoodsInfo.objects.get(pk=int(id))
    goods.gclick = goods.gclick + 1
    goods.save()
    # 查询当前商品类型
    goodtype = goods.gtype
    count = request.session['count']
    news = goods.gtype.goodsinfo_set.order_by('-id')[0:2]
    print('--------detail--------------')
    print('news[0].title:', news[0].gtitle)
    print('goodtype:', goodtype)
    print('goods.gtype:', goods.gtype)
    context = {
        'title': goods.gtype.title, 'guest_cart': 1,
        'g': goods, 'newgood': news, 'id': id,
        'isDetail': True, 'list': 1, 'goodtype': goodtype, 'count': count
    }
    response = render(request, 'df_goods/detail.html', context)

    # 使用cookies记录最近浏览的商品id
    # 获取cookies
    goods_ids = request.COOKIES.get('goods_ids', '')
    # 获取当前点击商品id
    goods_id = "%d" % goods.id
    # 判断cookies中的商品id是否为空
    if goods_ids != '':
        # 分割出每个商品id
        goods_id_list = goods_ids.split(',')
        # 判断商品是否已经存在于列表
        if goods_id_list.count(goods_id) >= 1:
            # 存在则移出
            goods_id_list.remove(goods_id)
        # 在第一位添加
        goods_id_list.insert(0, goods_id)
        # 判断列表数是否超过五个
        if len(goods_id_list) >= 6:
            # 超过五个则删除第六个
            del goods_id_list[5]
        # 添加商品id到cookies
        goods_ids = ','.join(goods_id_list)
    else:
        # 第一次添加,直接追加
        goods_ids = goods_id
    response.set_cookie('goods_ids', goods_ids)
    return response
