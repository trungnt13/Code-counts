#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

with open('README.md') as readme_file:
  readme = readme_file.read()

setup(
  author='Trung Ngo',
  author_email='anonymouswork90@gmail.com',
  classifiers=[
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.7',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
  ],
  description="Code counts for Nerd "
              "(a.k.a doctoral student in computer science)",
  long_description=readme,
  long_description_content_type='text/markdown',
  scripts=['bin/coconerd'],
  setup_requires=['pip>=19.0'],
  install_requires=['tqdm>=4.61.2'],
  license="MIT license",
  include_package_data=True,
  keywords='coconerd',
  name='coconerd',
  packages=find_packages(),
  test_suite='tests',
  url='https://github.com/trungnt13/Code-counts',
  version=0.1,
  zip_safe=False,
)
