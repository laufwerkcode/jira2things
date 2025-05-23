#!/usr/bin/env python3.8

"""Add or modify Projects."""

import pyThings.parameters as p
import pyThings.things as t

class AddProject: #pylint: disable=too-many-instance-attributes, too-few-public-methods
    '''
    Create a call to add a project.
    All parameters are optional.
    '''
    def __init__( #pylint: disable=too-many-arguments, too-many-locals
        self,
        title=None,
        titles=None,
        notes=None,
        when=None,
        deadline=None,
        tags=None,
        area_id=None,
        area=None,
        to_dos=None,
        completed=None,
        canceled=None,
        reveal=None,
        creation_date=None,
        completion_date=None):

        self.__name__ = "add-project"
        self.title = p.Title(title).title
        self.titles = p.Titles(titles).titles
        self.notes = p.Notes(notes).notes
        self.when = p.When(when).when
        self.deadline = p.Deadline(deadline).deadline
        self.tags = p.Tags(tags).tags
        self.area_id = p.AreaId(area_id).area_id
        self.area = p.Area(area).area
        self.to_dos = p.ToDos(to_dos).to_dos
        self.completed = p.Completed(completed).completed
        self.canceled = p.Canceled(canceled).canceled
        self.reveal = p.Reveal(reveal).reveal
        self.creation_date = p.CreationDate(creation_date).creation_date
        self.completion_date = p.CompletionDate(completion_date).completion_date

        self.callback_url = t.callback_from_obj(self)

        self = t.x_call_handler(self) #pylint: disable=self-cls-assignment

class UpdateProject: #pylint: disable=too-many-instance-attributes, too-few-public-methods
    '''
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
        notes=None,
        prepend_notes=None,
        append_notes=None,
        when=None,
        deadline=None,
        tags=None,
        add_tags=None,
        area_id=None,
        area=None,
        completed=None,
        canceled=None,
        reveal=None,
        duplicate=False,
        creation_date=None,
        completion_date=None):

        self.__name__ = "update-project"
        self.id = p.TaskId(task_id).task_id #pylint: disable=invalid-name
        self.auth_token = p.AuthToken(auth_token).auth_token
        self.title = p.Title(title).title
        self.notes = p.Notes(notes).notes
        self.prepend_notes = p.PrependNotes(prepend_notes).prepend_notes
        self.append_notes = p.AppendNotes(append_notes).append_notes
        self.when = p.When(when).when
        self.deadline = p.Deadline(deadline).deadline
        self.tags = p.Tags(tags).tags
        self.add_tags = p.AddTags(add_tags).add_tags
        self.area_id = p.AreaId(area_id).area_id
        self.area = p.Area(area).area
        self.completed = p.Completed(completed).completed
        self.canceled = p.Canceled(canceled).canceled
        self.reveal = p.Reveal(reveal).reveal
        self.duplicate = p.Duplicate(duplicate).duplicate
        self.creation_date = p.CreationDate(creation_date).creation_date
        self.completion_date = p.CompletionDate(completion_date).completion_date

        self.callback_url = t.callback_from_obj(self)

        self = t.x_call_handler(self) #pylint: disable=self-cls-assignment
