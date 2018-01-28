
from django import dispatch

on_before_logout = dispatch.Signal(providing_args=[])
