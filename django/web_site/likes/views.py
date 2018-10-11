from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from .models import LikeCount, LikeRecord

def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)



def SuccessResponse(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    return JsonResponse(data)

def like_change(request):
    #获取数据
    user = request.user
    #验证用户登录
    if not user.is_authenticated:
        return ErrorResponse(400, '用户未登录！')

    content_type = request.GET.get('content_type') # 获取这个模型中的个例，如果是在博客中这里就是获取单个blog实例
    object_id = request.GET.get('object_id')
    try:
        content_type = ContentType.objects.get(model=content_type) # 根据模型类型的个例在ContentType中获取这个类型对应的一类模型
        model_class = content_type.model_class() 
        model_obj = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return ErrorResponse(401, '对象不存在')
       
    #处理数据
    if request.GET.get('is_like') == "true":
        #可以点赞
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type,object_id=object_id,user=user)
        if created:
            #新增，之前未点赞
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type,object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            
            return SuccessResponse(like_count.liked_num)
        else:
            #created为false 说明已点赞过，不能再点
            return ErrorResponse(402, '你已经点赞过了，不能重复点赞!')
    else:
        #取消点赞
        if LikeRecord.objects.filter(content_type=content_type,object_id=object_id,user=user).exists():
            #存在，取消点赞
            like_record = LikeRecord.objects.get(content_type=content_type,object_id=object_id,user=user)
            like_record.delete() # 删除对应点赞记录
            # 点赞总数再减一
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type,object_id=object_id)
            if not created:
                like_count.liked_num -= 1
                like_count.save()

                return SuccessResponse(like_count.liked_num)
            else:
                return ErrorResponse(404, '点赞数据错误！')
        
        else:
            #没有点赞过，不能取消点赞
            return ErrorResponse(403, '你还没有点赞！')
    
    