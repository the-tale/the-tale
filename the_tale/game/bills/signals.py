# coding: utf-8

from django import dispatch

bill_created = dispatch.Signal(providing_args=['bill'])
bill_edited = dispatch.Signal(providing_args=['bill'])
bill_processed = dispatch.Signal(providing_args=['bill'])
