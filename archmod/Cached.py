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
    __cache = {}
       
    # to be implemented by contract in the descendant classes
    def _getitem(self, name):
        raise Exception(NotImplemented)
        
    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except:
            if not self.__cache.has_key(name):
                self.__cache[name] = self._getitem(name)
            return self.__cache[name]
