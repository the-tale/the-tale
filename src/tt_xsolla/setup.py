import setuptools

VERSION = '0.1'

setuptools.setup(
    name='TTXSolla',
    version=VERSION,
    description='XSolla hooks service for The Tale',
    long_description='XSolla hooks service for The Tale',
    url='https://github.com/Tiendil/the-tale',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    packages=setuptools.find_packages(),
    install_requires=[],
    entry_points={'console_scripts': ['tt_xsolla_create_fake_invoice=tt_xsolla.commands.tt_xsolla_create_fake_invoice:main']},
    include_package_data=True,
    test_suite='tests')
