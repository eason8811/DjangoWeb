from django.db import models


# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)

    # 帮助人性化显示对象信息
    def __str__(self):
        return self.name


class Comment(models.Model):
    comment_num = models.AutoField(primary_key=True)
    comment_text = models.CharField(max_length=300, blank=False, null=False)
    comment_date = models.CharField(max_length=50, default=None)
    comment_time = models.CharField(max_length=50, default=None)

