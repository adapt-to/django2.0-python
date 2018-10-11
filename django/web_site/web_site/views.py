import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.urls import reverse
from django.db.models import Sum
from django.core.cache import cache
from read_statistics.utils import get_even_week_read_num, get_today_hot_data, get_yesterday_hot_data
from blog.models import Blog

def get_7_days_hot_data():
    today = timezone.now().date()
    date = today - datetime.timedelta(days = 7)
    blogs = Blog.objects \
                        .filter(read_details__date__lt=today, read_details__date__gte=date) \
                        .values('id', 'title') \
                        .annotate(read_num_sum=Sum('read_details__read_num')) \
                        .order_by('-read_num_sum') # 获得小于今天大于前七天日期的排序
    return blogs[:6] # 返回read_num字段倒叙排序的结果，即由大到小排序

 

def index(request): # 首页
    blog_content_type = ContentType.objects.get_for_model(Blog)
    read_nums,read_date = get_even_week_read_num(blog_content_type)
    
    #获取缓存数据
    seven_days_hot_data = cache.get('seven_days_hot_data')
    if seven_days_hot_data is None: #缓存不存在则计算并存入缓存
        seven_days_hot_data = get_7_days_hot_data()
        cache.set('seven_days_hot_data', seven_days_hot_data, 3600) # 存入缓存，并设置缓存保存时间为一个小时


    context = {}
    context['read_nums'] = read_nums
    context['read_date'] = list(read_date)
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['seven_days_hot_data'] = seven_days_hot_data # 使用缓存
    
    return render(request,"index.html", context)