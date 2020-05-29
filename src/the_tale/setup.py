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
    long_description='Zero Player Game with indirect character controll',
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
    install_requires=['Django==2.2.10',
                      'argon2_cffi==19.2.0',
                      'Jinja2==2.10.3',
                      'psycopg2==2.8.4',

                      'kombu==4.6.6',
                      'postmarkup==1.2.2',
                      'Markdown==3.1.1',
                      'xlrd==1.2.0',
                      'MarkupSafe==1.1.1',
                      'unicodecsv==0.14.1',
                      'django-redis==4.10.0',
                      'psutil==5.6.7',
                      'requests==2.22.0',
                      'protobuf==3.11.1',
                      'gunicorn==20.0.4',
                      'sentry-sdk==0.14.3',

                      'pynames==0.2.2',
                      'utg==0.3.1',
                      'rels==0.3.1',
                      'smart_imports==0.2.4',

                      'typeguard==2.7.1'],

    include_package_data=True,
    test_suite='tests')
