# coding=utf-8
from django.db import models

# Create your models here.


class UserInfo(models.Model):
    uname = models.CharField(max_length=20)
    upwd = models.CharField(max_length=40)
    uemail = models.CharField(max_length=30, unique=True)
    ushou = models.CharField(max_length=20, default='')
    uaddress = models.CharField(max_length=100, default='')
    upostcode = models.CharField(max_length=6, default='')
    uphone = models.CharField(max_length=11, unique=True)
    # default,blank是python 层面的约束,不影响数据表结构

    def __str__(self):
        return self.uname
