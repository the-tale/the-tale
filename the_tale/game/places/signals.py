# coding: utf-8

from django import dispatch

place_person_arrived = dispatch.Signal(providing_args=['place', 'person'])
place_race_changed = dispatch.Signal(providing_args=['place', 'old_race', 'new_race'])
