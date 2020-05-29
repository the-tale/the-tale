
import setuptools

VERSION = '0.1'

setuptools.setup(
    name='TTPersonalMessages',
    version=VERSION,
    description='Personal Messages service for The Tale',
    long_description='Personal Messages service for The Tale',
    url='https://github.com/Tiendil/the-tale',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    packages=setuptools.find_packages(),
    install_requires=['rels==0.3.0'],
    entry_points={'console_scripts': ['tt_personal_messages_clean=tt_personal_messages.commands.tt_personal_messages_clean:main']},
    include_package_data=True,
    test_suite='tests')
