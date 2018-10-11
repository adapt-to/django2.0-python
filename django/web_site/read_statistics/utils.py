import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum,ReadDetail


def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = '%s_%s_read' % (ct.model, obj.pk)

    if not request.COOKIES.get(key): #cookies中不存在这个文章所对应的cookie时才将阅读数加1，否则不加
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk) #不存在就创建
        readnum.read_num += 1 #计数加1
        readnum.save() # 保存

        #当天阅读数处理
        date = timezone.now().date()
        readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)# 因为结果时一个元组，等号左边用元组拆包获得了结果
        readDetail.read_num += 1  #计数加1
        readDetail.save() # 保存
    return key

def get_even_week_read_num(content_type):#获得每周阅读数
    today = timezone.now().date()
    read_nums = []
    read_date = []
    for i in range(7,0,-1):# 7到1 循环
        date = today - datetime.timedelta(days = i) #得到日期的差量
        read_date.append(date.strftime('%m-%d'))
        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = read_details.aggregate(read_num_sum=Sum('read_num'))
        read_nums.append(result['read_num_sum'] or 0)
    return read_nums, read_date

def get_today_hot_data(content_type):#获得当天热门阅读数
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num') # 获得today的objects并排序
    return read_details[:6] # 返回read_num字段倒叙排序的结果，即由大到小排序

def get_yesterday_hot_data(content_type):#获得昨天热门阅读数
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days = 1)
    read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num') # 获得today的objects并排序
    return read_details[:6] # 返回read_num字段倒叙排序的结果，即由大到小排序

'''
def get_7_days_hot_data(content_type):#获得前七天热门阅读数
    today = timezone.now().date()
    date = today - datetime.timedelta(days = 7)
    read_details = ReadDetail.objects \
                                    .filter(content_type=content_type, date__lt=today, date__gte=date) \
                                    .values('content_type', 'object_id') \
                                    .annotate(read_num_sum=Sum('read_num')) \
                                    .order_by('-read_num_sum') # 获得小于今天大于前七天日期的排序
    return read_details[:6] # 返回read_num字段倒叙排序的结果，即由大到小排序
'''