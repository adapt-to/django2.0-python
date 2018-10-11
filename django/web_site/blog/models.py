from django.db import models
from django.contrib.auth.models import User # 引入User，记录登录的User名
from ckeditor_uploader.fields import RichTextUploadingField
from read_statistics.models import ReadNumMethod, ReadDetail
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse


class Category(models.Model):#博客分类
    category_name = models.CharField(max_length = 15, verbose_name = '博客类型') # 一篇博客对应一种分类

    def __str__(self):
        return self.category_name

class Blog(models.Model, ReadNumMethod): #博客信息数据表
    title = models.CharField(max_length = 50, verbose_name = '文章标题')
    blog_category = models.ForeignKey(Category, on_delete = models.CASCADE, verbose_name = '博客类型') #这里创建关联字段blog_category并引入了外键Category,也就是上面这个博客类型表，所以要让被引入的放在前面，这样程序读到此处，才能知道引入的外键在哪
    content = RichTextUploadingField() # 富文本编辑字段
    author = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = '发布者') #外键关联到引入User.这里的on_delete是指删除这一篇blog，对外键所进行的操作。这里不进行任何操作，因为删除一篇文章，不用删除用户名
    read_details = GenericRelation(ReadDetail) # 关联到模型ReadDetail
    created_time = models.DateTimeField(auto_now_add = True, verbose_name = '发布时间') # 自动添加当前时间
    last_updated_time = models.DateTimeField(auto_now = True, verbose_name = '最后修改时间') # 自动目前时间

    def get_url(self):   
        return reverse('blog_detail', kwargs={'blog_pk': self.pk})

    def get_email(self):
        return self.author.email

    
    def __str__(self):
        return "<Blog:%s>" % self.title
    
    class Meta:
        ordering = ["-created_time",]