# coding: utf-8
import re
import json
import setuptools



with open('./the_tale/meta_config.json') as f:
    config = json.loads(f.read())
    VERSION = re.search('((\d+\.?)+)', config['version']).group(0)


setuptools.setup(
    name='TheTale',
    version=VERSION,
    description='Zero Player Game with indirect character controll',
    long_description = 'Zero Player Game with indirect character controll',
    url='https://github.com/Tiendil/the-tale',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',

        'Topic :: Games/Entertainment',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',

        'Natural Language :: English',
        'Natural Language :: Russian'],
    keywords=['gamedev', 'the-tale', 'game development', 'zpg', 'zero player game'],
    packages=setuptools.find_packages(),
    install_requires=['Django==1.9.6',
                      'Jinja2==2.6',
                      'psycopg2==2.6.2',
                      'kombu==3.0.35',
                      'postmarkup==1.2.2',
                      'markdown==2.2.0',
                      'xlrd==0.8.0',
                      'mock==1.0b1',
                      'MarkupSafe==0.15',
                      'boto3==1.4.0',
                      'unicodecsv==0.14.1'],

    include_package_data=True,
    test_suite = 'tests' )
