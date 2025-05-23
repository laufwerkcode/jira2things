#!/usr/bin/env python3.8

'''
Show issue in app.
'''

# YMMV, seen issues where xcall won't trigger for some reason.

import pyThings.parameters as p
import pyThings.things as t

class Show: #pylint: disable=too-few-public-methods
    '''
    Either id or query must be specified;
    filter is optional.
    '''
    def __init__(
        self,
        item_id=None,
        query=None,
        t_filter=None):

        self.__name__ = "show"

        if item_id or query is not None:
            if query is None:
                self.query = None
            else:
                self.query = p.url_encode(query)

            if item_id is None:
                self.item_id = None
            else:
                self.id = p.url_encode(item_id) #pylint: disable=invalid-name
        else:
            raise Exception("Either item_id or query must be specified.")

        if t_filter is None:
            self.t_filter = None
        else:
            self.t_filter = p.url_encode(t_filter)

        self.callback_url = t.callback_from_obj(self)

        self = t.x_call_handler(self) #pylint: disable=self-cls-assignment
