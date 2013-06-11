# coding: utf-8
import string # pylint: disable=W0402
import random

TECHNICAL_SYMBOLS = '!@#$%^&*()-_=+'

def generate_password(len_=8, upper=True, lower=True, digits=True, special=False):

    sources = 0
    if upper: sources += 1
    if lower: sources += 1
    if digits: sources += 1
    if special: sources += 1

    sample_size = len_ // sources

    password = []
    password += random.sample(string.ascii_lowercase, sample_size)
    password += random.sample(string.ascii_uppercase, sample_size)
    password += random.sample(string.digits, sample_size)

    if special:
        password += random.sample(TECHNICAL_SYMBOLS, sample_size)

    delta = len_ - sample_size * sources
    if delta:
        default_source = TECHNICAL_SYMBOLS
        if digits: default_source = string.digits
        if upper: default_source = string.ascii_uppercase
        if lower: default_source = string.ascii_lowercase
        password += random.sample(default_source, delta)

    random.shuffle(password)
    return ''.join(password)
