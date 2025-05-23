#!/usr/bin/env python3.8

'''
Set of functions to handle interacting with Things.
Generation of x-callback-urls, and calling of said urls.
Depends on xcall being present.
https://github.com/martinfinke/xcall
'''

import os
import json
import subprocess

def callback_from_obj(obj):
    '''
    Build the callback url with attributes thate are available.
    '''
    callback_url = "things:///{}?".format(obj.__name__)
    for attribute in filter(lambda a: not a.startswith('__'), dir(obj)):
        value = getattr(obj, attribute)
        if value is not None:
            attr = attribute.replace('_', '-')
            callback_url += "&{}={}".format(attr, value)
    return callback_url

def x_call_handler(obj):
    '''
    A basic subprocess call to xcall [required].
    URL encoded x-callback-url is required,
    activate app is optional. (Doesn't seem to work all that well?)
    '''
    x_call_path = "./librarys/xcall/xcall.app/Contents/MacOS/xcall"

    if os.path.exists(x_call_path):
        pass
    else:
        raise FileNotFoundError("No xcall binary found at: {}".format(x_call_path))

    try:
        if obj.activate_app:
            activate_app = "-activateApp YES"
        else:
            activate_app = ""
    except: #pylint: disable=broad-except
        activate_app = ""


    args = [ x_call_path, '-url', obj.callback_url, activate_app ]

    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    response_obj = json.loads(popen.stdout.read())

    # Parse possible responses from Things.

    if 'x-things-id' in response_obj:
        obj.x_things_id = response_obj['x-things-id']
    if 'x-things-ids' in response_obj:
        obj.x_things_ids = response_obj['x-things-ids']
    if 'x-things-scheme-version' in response_obj:
        obj.x_things_scheme_version = response_obj['x-things-scheme-version']
    if 'x-things-client-version' in response_obj:
        obj.x_things_client_version = response_obj['x-things-client-version']

    return obj
