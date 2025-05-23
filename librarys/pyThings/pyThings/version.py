#!/usr/bin/env python3.8

'''
The version of the Things app and URL scheme.
'''

import pyThings.things as t

class Version :#pylint: disable=too-few-public-methods
    '''
    No parameters
    Returns the version of the Things app and URL scheme.
    x-things-scheme-version
    x-things-client-version
    '''
    def __init__(self):
        self.__name__ = "version"

        self.callback_url = t.callback_from_obj(self)

        self = t.x_call_handler(self) #pylint: disable=self-cls-assignment
