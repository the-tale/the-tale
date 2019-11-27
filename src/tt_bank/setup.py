import setuptools

VERSION = '0.1'

setuptools.setup(
    name='TTBank',
    version=VERSION,
    description='Bank service for The Tale',
    long_description='Bank service for The Tale',
    url='https://github.com/Tiendil/the-tale',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    packages=setuptools.find_packages(),
    install_requires=[],
    entry_points={'console_scripts': ['tt_bank_rollback_hanged_transactions=tt_bank.commands.tt_bank_rollback_hanged_transactions:main',
                                      'tt_bank_remove_old_transactions=tt_bank.commands.tt_bank_remove_old_transactions:main']},
    include_package_data=True,
    test_suite='tests')
