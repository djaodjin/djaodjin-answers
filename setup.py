# Copyright (c) 2013, The DjaoDjin Team
#   All rights reserved.

from distutils.core import setup

setup(
    name='djaodjin-answers',
    version='0.1',
    author='The DjaoDjin Team',
    author_email='support@djaodjin.com',
    packages=['answers'],
    package_data={'answers': ['templates/answers/*', 'static/img/*']},
    license='BSD',
    description='Q&A forum Django app',
    long_description=open('README.md').read(),
)
