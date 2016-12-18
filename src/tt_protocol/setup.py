# coding: utf-8
import re
import json
import setuptools

VERSION = '0.1'

setuptools.setup(
    name='TTProtocol',
    version=VERSION,
    description='The Tale protocol buffers communication protocol desctiption',
    long_description = 'The Tale protocol buffers communication protocol desctiption',
    url='https://github.com/Tiendil/the-tale',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    packages=setuptools.find_packages(),
    install_requires=[],
    include_package_data=True,
    entry_points={'console_scripts': ['tt_regenerate_protocol=tt_protocol.commands.tt_regenerate_protocol:main']},
    test_suite = 'tests' )
