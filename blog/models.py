import markdown

from django.conf import settings

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import strip_tags

from mdeditor.fields import MDTextField


class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=150)
    body = MDTextField()

    created_time = models.DateTimeField()
    modified_time = models.DateTimeField()

    # 文章摘要，可以没有文章摘要，但默认情况下 CharField 要求我们必须存入数据，否则就会报错。
    # 指定 CharField 的 blank=True 参数值后就可以允许空值了。
    excerpt = models.CharField(max_length=600, blank=True)

    # 这是分类与标签，分类与标签的模型我们已经定义在上面。
    # 我们在这里把文章对应的数据库表和分类、标签对应的数据库表关联了起来，但是关联形式稍微有点不同。
    # 我们规定一篇文章只能对应一个分类，但是一个分类下可以有多篇文章，所以我们使用的是 ForeignKey，即一对多的关联关系。
    # 而对于标签来说，一篇文章可以有多个标签，同一个标签下也可能有多篇文章，所以我们使用 ManyToManyField，表明这是多对多的关联关系。
    # 同时我们规定文章可以没有标签，因此为标签 tags 指定了 blank=True。
    # 如果你对 ForeignKey、ManyToManyField 不了解，请看教程中的解释，亦可参考官方文档：
    # https://docs.djangoproject.com/en/1.10/topics/db/models/#relationships
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag, blank=True)

    # 文章作者，这里 User 是从 django.contrib.auth.models 导入的。
    # django.contrib.auth 是 Django 内置的应用，专门用于处理网站用户的注册、登录等流程，User 是 Django 为我们已经写好的用户模型。
    # 这里我们通过 ForeignKey 把文章和 User 关联了起来。
    # 因为我们规定一篇文章只能有一个作者，而一个作者可能会写多篇文章，因此这是一对多的关联关系，和 Category 类似。
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    
    # 新增 views 字段记录阅读量
    views = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})
        
    class Meta:
        ordering = ['-created_time']
        
    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])
        
    def save(self, *args, **kwargs):    
        # 如果没有填写摘要
        if not self.excerpt:
            # 首先实例化一个 Markdown 类，用于渲染 body 的文本
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # 先将 Markdown 文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本摘取前 54 个字符赋给 excerpt
            self.excerpt = strip_tags(md.convert(self.body))[:150]

        # 调用父类的 save 方法将数据保存到数据库中
        super(Post, self).save(*args, **kwargs)