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
