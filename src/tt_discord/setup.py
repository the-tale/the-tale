import setuptools

VERSION = '0.1'

setuptools.setup(
    name='TTDiscord',
    version=VERSION,
    description='Discord bot service for The Tale',
    long_description='Discord bot service for The Tale',
    url='https://github.com/Tiendil/the-tale',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    packages=setuptools.find_packages(),
    install_requires=['discord.py==1.3.3'],
    entry_points={'console_scripts': []},
    include_package_data=True,
    test_suite='tests')
