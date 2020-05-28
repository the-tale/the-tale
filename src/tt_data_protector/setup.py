import setuptools

VERSION = '0.1'

setuptools.setup(
    name='TTDataProtector',
    version=VERSION,
    description='Data protector service for The Tale',
    long_description='Data protector service for The Tale',
    url='https://github.com/Tiendil/the-tale',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    packages=setuptools.find_packages(),
    install_requires=[],
    entry_points={'console_scripts': ['tt_data_protector_process_tasks=tt_data_protector.commands.tt_data_protector_process_tasks:main']},
    include_package_data=True,
    test_suite='tests')
