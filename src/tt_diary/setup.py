# coding: utf-8
import re
import json
import setuptools

VERSION = '0.1'

setuptools.setup(
    name='TTDiary',
    version=VERSION,
    description='Hero Diary storage service for The Tale',
    long_description = 'Hero Diary storage service for The Tale',
    url='https://github.com/Tiendil/the-tale',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    packages=setuptools.find_packages(),
    install_requires=['aiohttp==1.1.1',
                      'cchardet==1.1.1',
                      'aiodns==1.1.1',
                      'aiopg==0.12.0',
                      'Django==1.10.2',
                      'protobuf==3.1.0.post1'],
    entry_points={'console_scripts': ['tt_service=tt_diary.commands.tt_service:main']},
    include_package_data=True,
    test_suite = 'tests' )
