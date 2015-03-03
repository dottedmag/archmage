#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "archmage",
    fullname = "arCHMage",
    version = "0.2.4",
    description = "CHM(Compiled HTML) Decompressor",
    maintainer = "Basil Shubin",
    maintainer_email = "bashu@users.sourceforge.net",
    author = "Eugeny Korekin",
    author_email = "az@ftc.ru",
    url = "archmage.sf.net",
    license = "GPL",
    keywords = ["chm", "HTML Help", "Compiled HTML", "Compressed HTML"],
    long_description = "arCHMage is an extensible reader and decompiler for files in the CHM format. arCHMage is written in the Python programming language and uses PyCHM - python bindings for CHMLIB from GnoCHM project.",
    packages=find_packages(),
    entry_points={
        'console_scripts': ['archmage = archmod.cli:main'],
    },
    package_data={
        'archmod': ['*.conf', 'templates/*.html', 'templates/*.css',
                    'templates/icons/*.gif'],
    }
)
