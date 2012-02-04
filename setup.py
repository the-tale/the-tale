# coding: utf-8
import setuptools

# find ./ | grep -v \.html'' | grep -v '\.py' | grep -v '\.pyc' | grep -v '\.js' | grep -v '\.css' | grep -v gitignore | grep -v '\.png' | grep -v '\.gif' | grep -v '\.otf' | grep -v '\.ttf' | grep -v '\.jpg' | grep -v '\.sh'


setuptools.setup(
    name = 'TheTale',
    version = '0.1.0',
    author = 'Aleksey Yeletsky',
    author_email = 'a.eletsky@gmail.com',
    packages = setuptools.find_packages(),
    url = 'https://github.com/Tiendil/the-tale',
    license = 'LICENSE',
    description = "MMO with indirect control characters",
    long_description = open('README').read(),
    include_package_data = True # setuptools-git MUST be installed
)
