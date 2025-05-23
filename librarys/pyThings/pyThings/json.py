#!/usr/bin/env python3.8

'''
Take given json and return a url scheme.
'''

import json
import urllib.parse
import pyThings.things as t

class Json: #pylint: disable=too-few-public-methods
    '''
    Data, required.
    An array of JSON formatted data.
    More: https://culturedcode.com/things/support/articles/2803573/
    '''
    def __init__(self, data):
        self.__name__ = "json"

        try:
            for item in data:
                json.dumps(item)
        except ValueError as err:
            raise Exception("Data must be valid JSON. Error: {}".format(err)) from err

        # For whatever reason these need to be the actual characters
        self.data = urllib.parse.quote(str(json.dumps(data)), safe=':,')

        self.callback_url = t.callback_from_obj(self)

        self = t.x_call_handler(self) #pylint: disable=self-cls-assignment
