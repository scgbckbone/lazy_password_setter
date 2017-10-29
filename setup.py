import os
import setuptools


def read_(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name), "r") as f:
        lng_description = f.read()
    return lng_description


setuptools.setup(
    name='lazyPWDsetter',
    version='0.0.1',
    url="https://github.com/scgbckbone/lazy_password_setter",
    description='Resetting password on remote hosts via ssh.',
    license="MIT",
    long_description=read_('README'),
    author='Andrej Virgovic',
    author_email='virgovica@gmail.com',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License'
    ],
    packages=[
        'lazy_password_setter',
        'lazy_password_setter/config',
        'lazy_password_setter/docs',
        'lazy_password_setter/log',
        'lazy_password_setter/src',
        'lazy_password_setter/tests',
    ],
    install_requires=[
        'pykeepass',
        'fabric'
    ],
)
