import datetime
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator # 引入分页器
from django.conf import settings #引入全局设置
from .models import Blog, Category
from random import choice
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from read_statistics.utils import read_statistics_once_read, get_today_hot_data

def get_30_days_hot_data():
    today = timezone.now().date()
    date = today - datetime.timedelta(days = 30)
    blogs = Blog.objects \
                        .filter(read_details__date__lt=today, read_details__date__gte=date) \
                        .values('id', 'title') \
                        .annotate(read_num_sum=Sum('read_details__read_num')) \
                        .order_by('-read_num_sum') # 获得小于今天大于前30天日期的排序
    return blogs[:7] # 返回read_num字段倒叙排序的结果，即由大到小排序

def blog_list(request): # 文章列表页
    blogs_all_list = Blog.objects.all()
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_OF_BLOGS_NUMBERS) # 每8页进行分页,在setting文件中设置
    page_number = request.GET.get("page", 1) # 获取url的页码参数 (GET请求)
    page_of_blogs = paginator.get_page(page_number)
    currentr_page_num = page_of_blogs.number #获取当前页码
    page_of_range = \
    [i+currentr_page_num for i in range(-2,3) if i+currentr_page_num >=1 and i+currentr_page_num <= paginator.num_pages] # 列表推导式

    if page_of_range[0] >= 3:
        page_of_range.insert(0, '...')
    
    if page_of_range[-1] <= paginator.num_pages - 2:
        page_of_range.append('...')

    if page_of_range[0] != 1:
        page_of_range.insert(0, 1)

    if page_of_range[-1] != paginator.num_pages:
        page_of_range.append(paginator.num_pages)
    
    #获取博客不同分类对应的数量
    #Category.objects.annotate(blog_count = Count('blog')) 这句话也可以统计，与下面代码功能类似
    '''
        blog_category_numbers = Category.objects.all()
        blog_category_numbers_list = []
        for blog_category_number in blog_category_numbers:
            blog_category_number.blog_count = Blog.objects.filter(blog_category = blog_category_number).count() # for循环中加入一个新的属性blog_count去记录对应的数量，再放入列表中
            blog_category_numbers_list.append(blog_category_number)
    '''   
    #获取日期归档数量
    blog_times = Blog.objects.dates("created_time", "month", order="DESC")
    blog_times_dict = {}
    for blog_time in blog_times:
        blog_count = Blog.objects.filter(created_time__year = blog_time.year, 
                                                created_time__month = blog_time.month).count()
        blog_times_dict[blog_time] = blog_count

    
    blog_content_type = ContentType.objects.get_for_model(Blog)
    
    #获取缓存数据
    seven_days_hot_data = cache.get('seven_days_hot_data')
    if seven_days_hot_data is None: #缓存不存在则计算并存入缓存
        seven_days_hot_data = get_30_days_hot_data()
        cache.set('seven_days_hot_data', seven_days_hot_data, 60) # 存入缓存，并设置缓存保存时间为一个小时
    
    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['catrgory'] = Category.objects.annotate(blog_count = Count('blog'))
    context['page_of_blogs'] = page_of_blogs
    context['page_of_range'] = page_of_range
    context['blog_datetime'] = blog_times_dict
    context['random_blog'] = choice(blogs_all_list)

    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['seven_days_hot_data'] = seven_days_hot_data # 使用缓存获取当月热门
    return render(request,"blog/blog_list.html", context)

def blog_detail(request, blog_pk): # 文章详情页
    blog = get_object_or_404(Blog, pk = blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)
    
    context = {}
    context['blog'] = blog
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()  #上一篇博客(比当前博客发布时间大的博客中的最后一条)因为数据库中的博客是按发布时间倒叙排列的
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first() #下一篇博客
    response =  render(request, "blog/blog_detail.html", context) # 针对请求所返回的相应
    response.set_cookie(read_cookie_key, 'true')  # 阅读 cookie 标记
    return response

def blog_category(request, blog_category_pk): # 寻找分类文章的函数
    blog_category1 = get_object_or_404(Category, pk = blog_category_pk)
    blogs_all_list = Blog.objects.filter(blog_category = blog_category1)
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_OF_BLOGS_NUMBERS) # 每8页进行分页
    page_number = request.GET.get("page", 1) # 获取url的页码参数 (GET请求)
    page_of_blogs = paginator.get_page(page_number)
    
    currentr_page_num = page_of_blogs.number #获取当前页码
    
    page_of_range = \
    [i+currentr_page_num for i in range(-2,3) if i+currentr_page_num >=1 and i+currentr_page_num <= paginator.num_pages] # 列表推导式

    if page_of_range[0] >= 3:
        page_of_range.insert(0, '...')
    
    if page_of_range[-1] <= paginator.num_pages - 2:
        page_of_range.append('...')

    if page_of_range[0] != 1:
        page_of_range.insert(0, 1)

    if page_of_range[-1] != paginator.num_pages:
        page_of_range.append(paginator.num_pages)

    blog_content_type = ContentType.objects.get_for_model(Blog)
    #获取缓存数据
    seven_days_hot_data = cache.get('seven_days_hot_data')
    if seven_days_hot_data is None: #缓存不存在则计算并存入缓存
        seven_days_hot_data = get_30_days_hot_data()
        cache.set('seven_days_hot_data', seven_days_hot_data, 60) # 存入缓存，并设置缓存保存时间为一个小时
    #获取日期归档数量
    blog_times = Blog.objects.dates("created_time", "month", order="DESC")
    blog_times_dict = {}
    for blog_time in blog_times:
        blog_count = Blog.objects.filter(created_time__year = blog_time.year, 
                                                created_time__month = blog_time.month).count()
        blog_times_dict[blog_time] = blog_count

    context = {}
    context['blog'] = blog_category1
    context['blogs'] = page_of_blogs.object_list
    context['catrgory'] = Category.objects.annotate(blog_count = Count('blog'))
    context['page_of_blogs'] = page_of_blogs
    context['page_of_range'] = page_of_range
    context['blog_datetime'] = blog_times_dict
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['seven_days_hot_data'] = seven_days_hot_data # 使用缓存获取当月热门
    return render(request, "blog/blog_category.html", context)

def blog_datetime(request, year, month):
    
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_OF_BLOGS_NUMBERS) # 每8页进行分页
    page_number = request.GET.get("page", 1) # 获取url的页码参数 (GET请求)
    page_of_blogs = paginator.get_page(page_number)

    currentr_page_num = page_of_blogs.number #获取当前页码
    
    page_of_range = \
    [i+currentr_page_num for i in range(-2,3) if i+currentr_page_num >=1 and i+currentr_page_num <= paginator.num_pages] # 列表推导式

    if page_of_range[0] >= 3:
        page_of_range.insert(0, '...')
    
    if page_of_range[-1] <= paginator.num_pages - 2:
        page_of_range.append('...')

    if page_of_range[0] != 1:
        page_of_range.insert(0, 1)

    if page_of_range[-1] != paginator.num_pages:
        page_of_range.append(paginator.num_pages)

    blog_content_type = ContentType.objects.get_for_model(Blog)
    #获取缓存数据
    seven_days_hot_data = cache.get('seven_days_hot_data')
    if seven_days_hot_data is None: #缓存不存在则计算并存入缓存
        seven_days_hot_data = get_30_days_hot_data()
        cache.set('seven_days_hot_data', seven_days_hot_data, 60) # 存入缓存，并设置缓存保存时间为一个小时
    #获取日期归档数量
    blog_times = Blog.objects.dates("created_time", "month", order="DESC")
    blog_times_dict = {}
    for blog_time in blog_times:
        blog_count = Blog.objects.filter(created_time__year = blog_time.year, 
                                                created_time__month = blog_time.month).count()
        blog_times_dict[blog_time] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['catrgory'] = Category.objects.annotate(blog_count = Count('blog'))
    context['page_of_blogs'] = page_of_blogs
    context['page_of_range'] = page_of_range
    context['blog_datetime'] = blog_times_dict
    context['blog_date'] = "%s年%s月" %(year, month)
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['seven_days_hot_data'] = seven_days_hot_data # 使用缓存获取当月热门

    return render(request, "blog/blog_date.html", context) 
