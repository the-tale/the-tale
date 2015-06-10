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
    long_description = open('README.rst').read(),
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

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',

        'Natural Language :: English',
        'Natural Language :: Russian'],
    keywords=['gamedev', 'the-tale', 'game development', 'zpg', 'zero player game'],
    packages=setuptools.find_packages(),
    install_requires=['Django>=1.8.2',
                      'psycopg2>=2.4.5',
                      'kombu>=2.3.2',
                      'postmarkup>=1.2.0',
                      'markdown>=2.2.0',
                      'xlrd>=0.8.0',
                      'mock>=1.0b1',
                      'pylibmc>=1.2.3',
                      'MarkupSafe>=0.15',
                      'boto>=2.15.0',

                      'pynames==0.2.0',
                      'utg==0.1.0',
                      'rels==0.2.2.2',

                      'Dext==0.2.0',
                      'DeWorld==0.2.0',
                      'Questgen==0.2.0'],

    include_package_data=True,
    test_suite = 'tests',
    )
