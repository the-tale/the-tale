# coding: utf-8

from dext.forms import forms, fields

from the_tale.common.utils import bbcode

from the_tale.blogs.models import Post


class PostForm(forms.Form):
    MIN_TEXT_LENGTH = 1000

    caption = fields.CharField(label=u'Название', max_length=Post.CAPTION_MAX_LENGTH, min_length=Post.CAPTION_MIN_LENGTH)
    text = bbcode.BBField(label=u'Текст', min_length=MIN_TEXT_LENGTH)
