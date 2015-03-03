# -*- coding: utf-8 -*-
#
# archmage -- CHM decompressor
# Copyright (c) 2009 Basil Shubin <bashu@users.sourceforge.net>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

class Cached(object):
    """Provides caching storage for data access decoration.
    Usage:
        class CachedClass(Cached):
            def _getitem(self, name):
                # implement data getting routine, such as db access

        CachedClass().attribute1 # returns value as if _getitem('attribute1') was called
        CachedClass().attribute2 # returns value as if _getitem('attribute2') was called
        CachedClass().__doc__ # returns real docstring
    """

    def __new__(classtype, *args, **kwargs):
        __instance = object.__new__(classtype, *args, **kwargs)
        __instance.cache = {}
        return __instance

    # to be implemented by contract in the descendant classes
    def _getitem(self, name):
        raise Exception(NotImplemented)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except:
            if not self.cache.has_key(name):
                self.cache[name] = self._getitem(name)
            return self.cache[name]
