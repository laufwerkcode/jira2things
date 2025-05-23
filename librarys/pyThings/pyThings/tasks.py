#!/usr/bin/env python3.8

"""Add or modify Tasks."""

import pyThings.parameters as p
import pyThings.things as t

class AddTask: #pylint: disable=too-many-instance-attributes, too-few-public-methods
    '''
    Create a call to add a Task to Things.
    All parameters are optional.
    If neither the when nor list-id are specified, the to-do will be added to the inbox.
    '''
    def __init__( #pylint: disable=too-many-arguments, too-many-locals
        self,
        title=None,
        titles=None,
        notes=None,
        when=None,
        deadline=None,
        tags=None,
        checklist_items=None,
        list_id=None,
        list_str=None,
        heading=None,
        completed=None,
        canceled=None,
        show_quick_entry=None,
        reveal=None,
        creation_date=None,
        completion_date=None,
        activate_app=None):

        self.__name__ = "add"
        self.title = p.Title(title).title
        self.titles = p.Titles(titles).titles
        self.notes = p.Notes(notes).notes
        self.when = p.When(when).when
        self.deadline = p.Deadline(deadline).deadline
        self.tags = p.Tags(tags).tags
        self.checklist_items = p.ChecklistItems(checklist_items).checklist_items
        self.list_id = p.ListId(list_id).list_id
        self.list = p.List(list_str).list
        self.heading = p.Heading(heading).heading
        self.completed = p.Completed(completed).completed
        self.canceled = p.Canceled(canceled).canceled
        self.show_quick_entry = p.ShowQuickEntry(show_quick_entry).show_quick_entry
        self.reveal = p.Reveal(reveal).reveal
        self.creation_date = p.CreationDate(creation_date).creation_date
        self.completion_date = p.CompletionDate(completion_date).completion_date
        self.activate_app = p.ActivateApp(activate_app).activate_app

        self.callback_url = t.callback_from_obj(self)

        self = t.x_call_handler(self) #pylint: disable=self-cls-assignment


class UpdateTask: #pylint: disable=too-many-instance-attributes, too-few-public-methods
    '''
    Create a call to update a Task in Things.
    id and auth-token must be specified.
    All other parameters are optional.
    Including a parameter with an equals sign (=)
    but without a value will clear that value.
    '''

    def __init__( #pylint: disable=too-many-arguments, too-many-locals
        self,
        auth_token,
        task_id,
        title=None,
        titles=None,
        notes=None,
        prepend_notes=None,
        append_notes=None,
        when=None,
        deadline=None,
        tags=None,
        add_tags=None,
        checklist_items=None,
        prepend_checklist_items=None,
        append_checklist_items=None,
        list_id=None,
        list_str=None,
        heading=None,
        completed=None,
        canceled=None,
        show_quick_entry=None,
        reveal=None,
        duplicate=False,
        creation_date=None,
        completion_date=None):

        self.__name__ = "update"
        self.id = p.TaskId(task_id).task_id #pylint: disable=invalid-name
        self.auth_token = p.AuthToken(auth_token).auth_token
        self.title = p.Title(title).title
        self.titles = p.Titles(titles).titles
        self.notes = p.Notes(notes).notes
        self.prepend_notes = p.PrependNotes(prepend_notes).prepend_notes
        self.append_notes = p.AppendNotes(append_notes).append_notes
        self.when = p.When(when).when
        self.deadline = p.Deadline(deadline).deadline
        self.tags = p.Tags(tags).tags
        self.add_tags = p.AddTags(add_tags).add_tags
        self.checklist_items = p.ChecklistItems(checklist_items).checklist_items
        self.prepend_checklist_items = p.PrependChecklistItems(
            prepend_checklist_items).prepend_checklist_items
        self.append_checklist_items = p.AppendChecklistItems(
            append_checklist_items).append_checklist_items
        self.list_id = p.ListId(list_id).list_id
        self.list = p.List(list_str).list
        self.heading = p.Heading(heading).heading
        self.completed = p.Completed(completed).completed
        self.canceled = p.Canceled(canceled).canceled
        self.show_quick_entry = p.ShowQuickEntry(show_quick_entry).show_quick_entry
        self.reveal = p.Reveal(reveal).reveal
        self.duplicate = p.Duplicate(duplicate).duplicate
        self.creation_date = p.CreationDate(creation_date).creation_date
        self.completion_date = p.CompletionDate(completion_date).completion_date

        self.callback_url = t.callback_from_obj(self)

        self = t.x_call_handler(self) #pylint: disable=self-cls-assignment
