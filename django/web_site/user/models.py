from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户名")
    nickname = models.CharField(max_length=20, verbose_name="昵称")

    def __str__(self):
        return '<Profile: %s for %s>' % (self.nickname, self.user.username)

def get_nickname(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return ''

def get_nickname_or_username(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        name = " {0}({1}) ".format(self.username, profile.nickname)
        return name # 返回用户名和昵称
    else:
        return self.username # 若不存在昵称则只返回用户名

def has_nickname(self):
    return Profile.objects.filter(user=self).exists()

User.get_nickname = get_nickname
User.get_nickname_or_username = get_nickname_or_username
User.has_nickname = has_nickname 