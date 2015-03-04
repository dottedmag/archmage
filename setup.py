#!/usr/bin/env python

from setuptools import setup, find_packages
import version

long_desc='''arCHMage is a reader and decompressor for CHM format'''

classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
    'Topic :: Text Processing :: Filters',
]

setup(
    name='archmage',
    version=version.getVersion(),
    description='CHM decompressor',
    maintainer='Mikhail Gusarov',
    maintainer_email='dottedmag@dottedmag.net',
    url='https://github.com/dottedmag/archmage',
    license='GPLv2+',
    keywords=['chm', 'HTML Help', 'Compiled HTML', 'Compressed HTML'],
    classifiers=classifiers,
    long_description=long_desc,
    packages=find_packages(),
    install_requires=[
        'pychm',
        'BeautifulSoup',
    ],
    entry_points={
        'console_scripts': ['archmage = archmod.cli:main'],
    },
    package_data={
        'archmod': ['*.conf', 'templates/*.html', 'templates/*.css',
                    'templates/icons/*.gif'],
    }
)
