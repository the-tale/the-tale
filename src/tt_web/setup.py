import setuptools

VERSION = '0.1'

setuptools.setup(
    name='TTWeb',
    version=VERSION,
    description='Web framework for The Tale',
    long_description='Web framework for The Tale',
    url='https://github.com/Tiendil/the-tale',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    packages=setuptools.find_packages(),
    install_requires=['aiohttp==3.6.2',
                      'cchardet==2.1.5',
                      'aiodns==2.0.0',
                      'aiopg==1.0.0',
                      'Django==3.0',
                      'yarl==1.4.2',
                      'protobuf==3.11.1'],
    entry_points={'console_scripts': ['tt_service=tt_web.commands.tt_service:main']},
    include_package_data=True,
    test_suite='tests')
