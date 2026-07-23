import os
import re
from setuptools import find_packages, setup

package='mptauth'

def get_version():
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)
    
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='mpt-django-oauth',
    version=get_version(),
    url='https://github.com/mpt-ai/mpt-django-oauth',
    packages=find_packages(),
    package_data={
        'mptauth': ['templates/**/*.html']
    },
    include_package_data=True,
    license='MIT License',
    description='A simple way to use Custom authentication in django application. for MPT',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Magnecomp PCL',
    author_email='contact@magnecomp.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
       'social-auth-app-django==6.0.0',
       'djangorestframework-simplejwt==5.5.1',
       'Pillow==12.3.0'
    ]
)