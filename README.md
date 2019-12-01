arCHMage
========

arCHMage converts CHM files to HTML, plain text and PDF. CHM is the format used
by Microsoft HTML Help, also known as Compiled HTML.

[![Latest Version](https://img.shields.io/pypi/v/archmage.svg)](https://pypi.python.org/pypi/archmage/)
[![Downloads](https://img.shields.io/pypi/dm/archmage.svg)](https://pypi.python.org/pypi/archmage/)
[![License](https://img.shields.io/github/license/dottedmag/archmage.svg)](https://pypi.python.org/pypi/archmage/)

Usage
=====

Extract CHM content into directory
----------------------------------

    archmage -x <chmfile> [output directory]

Extraction does not overwrite existing directories.

Dump HTML data from CHM
-----------------------

    archmage -d <chmfile>

Convert CHM file into another format
------------------------------------

    archmage -c (html|text|pdf) <chmfile> [output file]

This feature requires `htmldoc(1)`, and `lynx(1)` or `elinks(1)` installed.

Installation
============

    pip install archmage

Requirements
============

arCHMage has the following dependencies:

  * Python 3.5+
  * PyCHM
  * BeautifulSoup4

Optional dependencies:

  * htmldoc - converting to plain text, single HTML, PDF formats
    (Debian/Ubuntu: `htmldoc`)
  * Lynx or ELinks - converting to plain text
    (Debian/Ubuntu: `lynx`)
