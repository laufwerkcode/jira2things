#!/usr/bin/env python3.8

'''
Search Things and display.
'''

import pyThings.things as t

class Search: #pylint: disable=too-few-public-methods
    '''
    Search Things, a query is required.
    '''
    def __init__(self, query):
        self.__name__ = "search"
        if isinstance(query, str):
            self.query = query
        else:
            raise "Search params must be valid strings."

        self.callback_url = t.callback_from_obj(self)

        self = t.x_call_handler(self) #pylint: disable=self-cls-assignment
