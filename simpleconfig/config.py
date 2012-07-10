# -*- encoding: utf-8 -*-
from os.path import exists
import json

#Exceptions...
class FileNotFound(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self.path

class MissingVar(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

#Base Config class
class Config(object):
    def __init__(self, must_exists = {}, initial_vars = {}):
        self._path = None
        self._vars = None
        self._must_exists = must_exists
        self._vars = {}
        self._initial_vars = initial_vars

    def _create_new(self):
        self._vars = self._initial_vars

    def _test_paths_file(self, name):
        tab = name.split('.')
        next = self._vars
        str_for_name = ''
        for small_name in tab:
            str_for_name += '[%s]' % (small_name)
            if next.has_key(small_name):
                next = next[small_name]
            else:
                raise MissingVar(str_for_name)

    def read(self, path = None):
        if path != None:
            self._path = path
        if not exists( self._path ):
            self._create_new()
            self.write()
        else:
            self._vars = self._raw_read( self._path )
        for name in self._must_exists: self._test_paths_file( name )

    def write(self, path = None):
        if path != None:
            self._path = path
        self._raw_write( self._path, self._vars )

    def __getitem__(self, name):
        try:
            return self._vars[ name ]
        except KeyError:
            return self._initial_vars[name]

    def __setitem__(self, name, value ):
        self._vars[ name ] = value

    def keys(self):
        return self._vars.keys()

    def items(self):
        return self._vars.items()

    def pop(self, key):
        return self._vars.pop( key )
        
    def _raw_read(self, path):
        encoded_data = open(path, 'r').read()
        return json.loads(encoded_data)
    
    def _raw_write(self, path, data):
        encoded_data = json.dumps(data)
        file = open(path, 'w')
        file.write(encoded_data)
        file.close()

class PathsConfig(Config):
    def _test_paths_file(self, name):
        tab = name.split('.')
        next = self._vars
        str_for_name = ''
        external = self._initial_vars
        for small_name in tab:
            str_for_name += '["%s"]' % (small_name)
            if not next.has_key(small_name):
                try:
                    next[small_name] = external[small_name]
                    self.write()
                except KeyError:
                    raise MissingVar(str_for_name)
            next = next[small_name]
            external = external[small_name]
        if self._must_exists[name] and not exists(next):
            raise FileNotFound( next )
