# coding: utf-8

from dext.forms import forms, fields

from the_tale.common.utils import bbcode

from the_tale.blogs.models import Post
from the_tale.blogs.conf import blogs_settings


class PostForm(forms.Form):
    caption = fields.CharField(label=u'Название', max_length=Post.CAPTION_MAX_LENGTH, min_length=Post.CAPTION_MIN_LENGTH)
    text = bbcode.BBField(label=u'Текст', min_length=blogs_settings.MIN_TEXT_LENGTH)
