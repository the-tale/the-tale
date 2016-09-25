# coding: utf-8

from django import dispatch

day_started = dispatch.Signal(providing_args=[])
