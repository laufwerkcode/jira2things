# pyThings

## About

A Python library to systematically create and call x-callback-urls for [Cultured Code's Things](https://culturedcode.com/things/) application. The entire Things URL Scheme is available [here](https://culturedcode.com/things/support/articles/2803573/) as well as a ["Link Builder"](https://culturedcode.com/things/support/articles/2803573/#link-builder) which this library seeks to emulate in a pythonic way.

### Requirements

[xcall](https://github.com/martinfinke/xcall)

> Call X-Callback-URLs From the Command Line. Outputs the x-success and x-error responses to stdout/stderr.

[Things](https://culturedcode.com/things/) running on the macOS device utilizing this library.

#### A write only environment

[Things Callback URL Scheme](https://culturedcode.com/things/support/articles/2803573/) is robust, but  _write_ oriented. It is not currently possible to get anything from Things as far as I could find, aside from an associated `x-things-id`. Which is needed to update any Task or project as touched on [below](#finding-a-task-id).

This greatly impedes the ability to systematically update tasks that may be propagated from another source of truth, like a web based, API driven, project management suite.

#### Use of auth_token

Modification of existing Tasks and Projects require an auth token, which can be generated via the app. `Things > Preferences > General > Enable Things URLs`

#### Finding a Task ID

Right click on a task, `Share > Copy Link` paste that link, `things:///show?id=$value` where `$value` is the id of the task/project.

## Examples

### Tasks

#### Add Task

Create a task:

```python
>>> from pyThings.tasks import AddTask
>>> AddTask(title='A New Task')
```

#### Update Task

Perquisites:

- [`auth_token`](#a-note-on-auth_token)
- [`task_id`](#finding-a-task-id)

Update an existing task:

```python
>>> from pyThings.tasks import UpdateTask
>>> UpdateTask(auth_token=auth_token, task_id='ID_STRING', completed=True)
```

### Projects

#### Add Project

Create a project:

```python
>>> from pyThings.projects import AddProject
>>> AddProject(title='My New Project')
```

#### Update Project

Perquisites:

- [`auth_token`](#a-note-on-auth_token)
- [`task_id`](#finding-a-task-id)

Update an existing project:

```python
>>> from pyThings.projects import UpdateProject
>>> UpdateProject(auth_token=auth_token, task_id='ID_STRING', completed=True)
```

### Other Features

#### Search

Query and and show the search:

```python
>>> from pyThings.search import Search
>>> Search('search')
```

```text
things:///search?&query=search
```

#### Show

> Navigate to and show an area, project, tag or to-do, or one of the built-in lists, optionally filtering by one or more tags. - [show](https://culturedcode.com/things/support/articles/2803573/#show)

```python
>>> from pyThings.show import Show
>>> Show(query="search")
```

Which should generate and call:

```text
things:///show?&query=search
```

#### Version

Get the version of the Things app and URL scheme:

```python
>>> from pyThings.version import Version
>>> Version()
<pyThings.version.Version object at 0x102c93850>
```

Which looks like:

```python
{
    'x-things-client-version': '31309505',
    'x-things-scheme-version': '2'
}
```

#### JSON

>Things also has an advanced, JSON-based add command that allows more control over the projects and to-dos imported into Things. This command is intended to be used by app developers or other people familiar with scripting or programming. - [json](https://culturedcode.com/things/support/articles/2803573/#json)

```python
>>> from pyThings.json import Json
>>> task = Json(
      data=[
      {
        "type": "to-do",
        "attributes": {
          "title": "Buy milk"
        }
      },
      {
        "type": "to-do",
        "attributes": {
          "title": "Buy eggs"
        }
      }
    ])
```
