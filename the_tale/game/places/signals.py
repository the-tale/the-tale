# coding: utf-8

from django import dispatch

place_modifier_reseted = dispatch.Signal(providing_args=['place', 'old_modifier'])
place_person_left = dispatch.Signal(providing_args=['place', 'person'])
place_person_arrived = dispatch.Signal(providing_args=['place', 'person'])
place_race_changed = dispatch.Signal(providing_args=['place', 'old_race', 'new_race'])

building_destroyed_by_amortization = dispatch.Signal(providing_args=['place', 'person'])
