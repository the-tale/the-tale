# coding: utf-8

from dext.forms import forms, fields

from common.utils.forms import BBField

from blogs.models import Post


class PostForm(forms.Form):

    caption = fields.CharField(label=u'Название', max_length=Post.CAPTION_MAX_LENGTH, min_length=Post.CAPTION_MIN_LENGTH)
    text = BBField(label=u'Текст')
