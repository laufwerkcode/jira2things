#!/usr/bin/env python3.8

"""Create parameters for Tasks and Projects."""

import re
import urllib.parse

# SUPPORT ITEMS FOR PARAMS

def is_string(string, usage):
    '''Verify given variable is a string.'''
    if not isinstance(string, str):
        raise Exception("{} must be a string.".format(usage))
    return True

def is_list(values, usage):
    '''Verify given variable is a list.'''
    if not isinstance(values, list):
        raise Exception("{} must be a string.".format(usage))
    return True

def url_encode(text):
    '''Encode given variable as url encoded string.'''
    return urllib.parse.quote(text)

def is_iso_8601(date, usage):
    '''Check if given variable is a ISO8601 format.'''
    regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$' #pylint: disable=line-too-long
    match_iso8601 = re.compile(regex).match
    try:
        if match_iso8601(date) is not None:
            return True
    except Exception as issue:
        print("{} must be a ISO8601 formatted string.".format(usage))
        raise issue
    return False


# PARAMS

class ActivateApp: #pylint: disable=too-few-public-methods
    '''
    Bool.
    Open Things App.
    Does not seem to work.
    '''
    def __init__(self, activate_app):
        if activate_app is None:
            self.activate_app = None
            return
        if isinstance(activate_app, bool):
            self.activate_app = activate_app
            return

class AddTags: #pylint: disable=too-few-public-methods
    '''
    Comma separated strings corresponding to the titles of tags.
    Adds the specified tags to a project.
    Does not apply a tag if the specified tag doesn’t exist.
    '''
    def __init__(self, add_tags):
        if not add_tags:
            self.add_tags = None
            return
        tags_string = ''
        for tag in add_tags:
            is_string(tag, "Tag {}".format(tag))
            if tags_string == '':
                tags_string += tag
            else:
                tags_string += ','
                tags_string += tag

        self.add_tags = url_encode(tags_string)

class AppendChecklistItems: #pylint: disable=too-few-public-methods
    '''
    Newline (encoded to %0a) separated strings.
    Add checklist items to the end of the list of checklist items
    in the to-do (maximum of 100).
    '''
    def __init__(self, append_checklist_items=None):
        if not append_checklist_items:
            self.append_checklist_items = None
            return
        is_list(append_checklist_items, "ChecklistItems")
        if len(append_checklist_items) > 100:
            raise Exception("Checklist must be less than 100 items.")

        checklist_text = ''
        for item in append_checklist_items:
            if checklist_text == '':
                checklist_text += item
            else:
                checklist_text += "\n"
                checklist_text += item

        checklist_text += "\n"
        self.append_checklist_items = url_encode(checklist_text)

class AppendNotes: #pylint: disable=too-few-public-methods
    '''
    String.
    Text to add after the existing notes of a to-do.
    Maximum unencoded length: 10,000 characters.
    '''
    def __init__(self, append_notes):
        if append_notes is None:
            self.append_notes = None
            return
        is_string(append_notes, "Prepend Notes")
        if len(append_notes) > 10000:
            raise Exception("Notes must be a string less than 10k charachters.")

        new_notes = "\n"
        new_notes += append_notes
        self.append_notes =  url_encode(new_notes)

class Area: #pylint: disable=too-few-public-methods
    '''
    String.
    The title of an area to add to.
    Ignored if area-id is present.
    '''
    def __init__(self, area):
        if area is None:
            self.area = None
            return
        is_string(area, "Area")

        self.area = url_encode(area)

class AreaId: #pylint: disable=too-few-public-methods
    '''
    String.
    The ID of an area to add to.
    Takes precedence over area.
    '''
    def __init__(self, area_id):
        if area_id is None:
            self.area_id = None
            return
        is_string(area_id, "AreaId")

        self.area_id = url_encode(area_id)

class AuthToken: #pylint: disable=too-few-public-methods
    '''
    String.
    The Things URL scheme authorization token.
    Required for modifying actions only.
    '''
    def __init__(self, auth_token):
        is_string(auth_token, "AuthToken")

        self.auth_token =  url_encode(auth_token)

class ChecklistItems: #pylint: disable=too-few-public-methods
    '''
    String separated by new lines (encoded to %0a).
    Checklist items to add to the to-do (maximum of 100).
    '''
    def __init__(self, checklist=None):
        if not checklist:
            self.checklist_items = None
            return
        is_list(checklist, "ChecklistItems")
        if len(checklist) > 100:
            raise Exception("Checklist must be less than 100 items.")

        checklist_text = ''
        for item in checklist:
            if checklist_text == '':
                checklist_text += item
            else:
                checklist_text += "\n"
                checklist_text += item

        self.checklist_items = url_encode(checklist_text)

class Completed: #pylint: disable=too-few-public-methods
    '''
    Boolean.
    Whether or not the to-do should be set to complete.
    Default: false. Ignored if canceled is also set to true.
    '''
    def __init__(self, completed):
        if completed is None:
            self.completed = None
            return
        if isinstance(completed, bool):
            self.completed = completed
        else:
            raise Exception("Completed must be a bool value or None.")

class Canceled: #pylint: disable=too-few-public-methods
    '''
    Boolean.
    Whether or not the to-do should be set to complete.
    Ignored if canceled is also set to true.
    Default: false.
    '''
    def __init__(self, canceled):
        if canceled is None:
            self.canceled = None
            return
        if isinstance(canceled, bool):
            self.canceled = canceled
        else:
            raise Exception("Canceled must be a bool value or None.")

class CompletionDate: #pylint: disable=too-few-public-methods
    '''
    ISO8601 date time string.
    The date to set as the completion date for the to-do in the database.
    Ignored if the to-do is not completed or canceled, or if the date is in the future
    '''
    def __init__(self, completion_date):
        if completion_date is None:
            self.completion_date = None
            return
        is_iso_8601(completion_date, "CompletionDate")

        self.completion_date = completion_date

class CreationDate: #pylint: disable=too-few-public-methods
    '''
    ISO8601 date time string.
    The date to set as the creation date for the to-do in the database.
    Ignored if the date is in the future.
    '''
    def __init__(self, creation_date):
        if creation_date is None:
            self.creation_date = None
            return
        is_iso_8601(creation_date, "CreationDate")

        self.creation_date = creation_date

class Deadline: #pylint: disable=too-few-public-methods
    '''
    Date string.
    The deadline to apply to the to-do.
    '''
    def __init__(self, deadline):
        if deadline is None:
            self.deadline = None
            return
        is_string(deadline, "When")

        self.deadline = url_encode(deadline)

class Duplicate: #pylint: disable=too-few-public-methods
    '''
    Boolean.
    Set to true to duplicate the to-do before updating it,
    leaving the original to-do untouched.
    Repeating to-dos cannot be duplicated.
    Default: false.
    '''
    def __init__(self, duplicate):
        if duplicate is None:
            self.duplicate = None
            return
        if isinstance(duplicate, bool):
            self.duplicate = duplicate
        else:
            raise Exception("Duplicate must be a bool value or None.")

class Heading: #pylint: disable=too-few-public-methods
    '''
    String.
    The title of a heading within a project to add to.
    Ignored if a project is not specified, or if the heading doesn’t exist.
    '''
    def __init__(self, heading):
        if heading is None:
            self.heading = None
            return
        is_string(heading, "Heading")

        self.heading = url_encode(heading)

class List: #pylint: disable=too-few-public-methods
    '''
    String.
    The title of a project or area to add to.
    Ignored if list-id is present.
    '''
    def __init__(self, list_str):
        if list_str is None:
            self.list = None
            return
        is_string(list_str, "List")

        self.list = url_encode(list_str)

class ListId: #pylint: disable=too-few-public-methods
    '''
    String.
    The ID of a project or area to add to.
    Takes precedence over list.
    '''
    def __init__(self, list_id):
        if list_id is None:
            self.list_id = None
            return
        is_string(list_id, "ListId")

        self.list_id = list_id

class Notes: #pylint: disable=too-few-public-methods
    '''
    String.
    The text to use for the notes field of the to-do.
    Maximum unencoded length: 10,000 characters.
    '''
    def __init__(self, notes):
        if notes is None:
            self.notes = None
            return
        is_string(notes, "Notes")
        if len(notes) > 10000:
            raise Exception("Notes must be a string less than 10k charachters.")

        self.notes =  url_encode(notes)


class PrependChecklistItems: #pylint: disable=too-few-public-methods
    '''
    Newline (encoded to %0a) separated strings.
    Add checklist items to the front of the list of checklist items
    in the to-do (maximum of 100).
    '''
    def __init__(self, prepend_checklist_items=None):
        if not prepend_checklist_items:
            self.prepend_checklist_items = None
            return
        is_list(prepend_checklist_items, "ChecklistItems")
        if len(prepend_checklist_items) > 100:
            raise Exception("Checklist must be less than 100 items.")

        checklist_text = ''
        for item in prepend_checklist_items:
            if checklist_text == '':
                checklist_text += item
            else:
                checklist_text += "\n"
                checklist_text += item

        checklist_text += "\n"
        self.prepend_checklist_items = url_encode(checklist_text)

class PrependNotes: #pylint: disable=too-few-public-methods
    '''
    String.
    Text to add before the existing notes of a to-do.
    Maximum unencoded length: 10,000 characters.
    '''
    def __init__(self, prepend_notes):
        if prepend_notes is None:
            self.prepend_notes = None
            return
        is_string(prepend_notes, "Prepend Notes")
        if len(prepend_notes) > 10000:
            raise Exception("Notes must be a string less than 10k charachters.")

        self.prepend_notes =  url_encode(prepend_notes)

class Reveal: #pylint: disable=too-few-public-methods
    '''
    Boolean.
    Whether or not to navigate to and show the newly created to-do.
    If multiple to-dos have been created, the first one will be shown.
    Ignored if show-quick-entry is also set to true.
    Default: false.
    '''
    def __init__(self, reveal):
        if reveal is None:
            self.reveal = None
            return
        if isinstance(reveal, bool):
            self.reveal = reveal
        else:
            raise Exception("Reveal must be a bool value or None.")

class ShowQuickEntry: #pylint: disable=too-few-public-methods
    '''
    Boolean.
    Whether or not to show the quick entry dialog
    (populated with the provided data) instead of adding a new to-do.
    Ignored if titles is specified.
    Default: false.
    '''
    def __init__(self, show_quick_entry):
        if show_quick_entry is None:
            self.show_quick_entry = None
            return
        if isinstance(show_quick_entry, bool):
            self.show_quick_entry = show_quick_entry
        else:
            raise Exception("ShowQuickEntry must be a bool value or None.")

class Tags: #pylint: disable=too-few-public-methods
    '''
    Comma separated strings corresponding to the titles of tags.
    Replaces all current tags.
    Does not apply a tag if the specified tag doesn’t exist.
    '''
    def __init__(self, tags=None):
        if not tags:
            self.tags = None
            return
        tags_string = ''
        for tag in tags:
            is_string(tag, "Tag {}".format(tag))
            if tags_string == '':
                tags_string += tag
            else:
                tags_string += ','
                tags_string += tag

        self.tags = url_encode(tags_string)

class TaskId: #pylint: disable=too-few-public-methods
    '''
    String.
    The ID of the to-do to update.
    Required.
    '''
    def __init__(self, task_id):

        is_string(task_id, "TaskId")

        self.task_id =  url_encode(task_id)

class Title: #pylint: disable=too-few-public-methods
    ''''
    String. The title of the to-do to add.
    Ignored if titles is also specified.
    '''
    def __init__(self, title):
        if title is None:
            self.title = None
            return
        if title is False:
            self.title = ""
            return
        is_string(title, "Title")
        self.title =  url_encode(title)

class Titles: #pylint: disable=too-few-public-methods
    '''
    String separated by new lines (encoded to %0a).
    Use instead of title to create multiple to-dos.
    Takes priority over title and show-quick-entry.
    The other parameters are applied to all the created to-dos.
    '''
    def __init__(self, titles):
        if not titles:
            self.titles = None
            return

        is_list(titles, "Titles")
        titles_text = ''
        for title in titles:
            if titles_text == '':
                titles_text += title
            else:
                titles_text += "\n"
                titles_text += title

        self.titles = url_encode(titles_text)

class ToDos: #pylint: disable=too-few-public-methods
    '''
    String separated by new lines (encoded to %0a).
    Titles of to-dos to create inside the project.
    '''
    def __init__(self, to_dos=None):
        if not to_dos:
            self.to_dos = None
            return
        is_list(to_dos, "ToDos")
        to_dos_text = ''
        for to_do in to_dos:
            if to_dos_text == '':
                to_dos_text += to_do
            else:
                to_dos_text += "\n"
                to_dos_text += to_do

        self.titles = url_encode(to_dos_text)

class When: #pylint: disable=too-few-public-methods
    '''
    String.
    Possible values:
        - today,
        - tomorrow
        - evening
        - anytime
        - someday
        - a date string
        - a date time string
    '''
    def __init__(self, when):
        if when is None:
            self.when = None
            return
        is_string(when, "When")
        # is_date_string(when, "When")

        self.when = url_encode(when)
