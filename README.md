# jira2things

<p align="center">
  <img src="assets/images/banner.png" alt="Project Banner" height="200">
</p>

A Python application that synchronizes JIRA tickets to your local SQLite database and integrates with Things 3 for task management.

It is the spiritual successor to [hackerdude/jiratotaskmanagers](https://github.com/hackerdude/jiratotaskmanagers) and it follows the same philosophy of the "one tasklist" system. By mapping active tickets to Things Today status it also keeps you sharp on updating your Jira tickets to their correct statuses.

My belief is that we should actively plan our day and what we want to do with our time. This app helps me to sync up Jira to my beloved [Things todo app](https://culturedcode.com/things/)

## Features

- **One-way sync**: Fetch tickets from JIRA → Store in local database → Sync to Things 3
- **Smart status mapping**: Automatically schedule tasks in Things based on JIRA status
- **Incremental updates**: Only syncs changed tickets to minimize calls to Things
- **Robust(ish) sync tracking**: Tracks sync status per ticket ('synced', 'not synced', 'unknown')
- **Flexible configuration**: Configurable status mappings, tags, and projects

## Requirements

This application uses both `xcall` and `pyThings` to work. They are bundled in this repository under `libraries`. We also use the Python Jira module for auth.

- [xcall](https://github.com/martinfinke/xcall)
- [pyThings](https://github.com/lucasjhall/pyThings)
- [Python Jira](https://jira.readthedocs.io/en/latest/)

## Installation

1. Clone the repository with submodules:

```bash
git clone git@github.com:laufwerkcode/jira2things.git
cd jira2things
```

2. Create a `.venv`

```bash
 python3 -m venv .venv
 source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create your configuration file (see Configuration section below)

## Usage

### Command Options

```bash
# Default: Update database from JIRA and sync unsynced tickets to Things
python main.py

# Update database only (fetch from JIRA, no Things sync)
python main.py --update-db

# Sync unsynced tickets to Things only (no JIRA fetch)
python main.py --sync-to-things

# Force resync ALL tickets to Things (regardless of sync status)
python main.py --resync-to-things

# Enable verbose logging
python main.py --verbose

# Use custom config file
python main.py --config my-config
```

## Configuration

1. **Copy the example config file:**
   ```bash
   cp config.example config
   ```

2. **Edit the `config` file** with your actual values (see sections below)

3. **Important**: Never commit your `config` file to version control as it contains sensitive tokens!

### Configuration File Format

The `config` file uses a simple `KEY=VALUE` format. Here are the available options:

### Required JIRA Settings

```ini
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_API_TOKEN=your_api_token_here
JIRA_USER_EMAIL=your.email@company.com
```

### Optional JIRA Settings

```ini
# Custom JQL query (default shown)
JIRA_JQL_QUERY=assignee = currentUser() AND updated >= -14d
```

### Things 3 Integration

```ini
# Required for Things sync
THINGS_AUTH_TOKEN=your_things_auth_token

# Optional Things settings
THINGS_PROJECT=Work Projects
THINGS_TAGS=['jira', 'work']
JIRA_TYPE_TAG=true
```

### Sprint Deadlines

Set task deadlines based on the end dates of Jira sprints. Only active and future sprints are considered.

```ini
JIRA_SPRINT_DEADLINES=true
```

### Status Mapping / Scheduling

Tickets can be scheduled using one of two scheduling modes: `status` or `sprint`.

#### Status Mode

In status mode, tickets are scheduled based soley on their Jira status. This is the default mode.

```ini
SCHEDULING_MODE=status
```

Configure how JIRA statuses map to Things scheduling:

```ini
# Tickets with these statuses go to "Today" in Things
TODAY_STATUS=['In Progress', 'Active', 'Doing']

# Tickets with these statuses go to "Someday" in Things
SOMEDAY_STATUS=['Backlog', 'Future']

# Tickets with these statuses go to "Anytime" in Things (default)
ANYTIME_STATUS=['To Do', 'Open', 'New']

# Tickets with these statuses are marked as completed in Things
COMPLETED_STATUS=['Done', 'Closed', 'Resolved']
```

### Multiple Projects

You can configure additional queries, each mapped to seperate Things projects

Additional projects are defined by adding `THINGS_PROJECT__<name>` and `JIRA_JQL_QUERY__<name>` entries to the config.

For example, to create separate projects for web and API tickets, you can add:

```ini
THINGS_PROJECT__API=API Tickets
JIRA_JQL_QUERY__API=assignee = currentUser() AND updated >= -14d AND project = API

THINGS_PROJECT__WEB=Web Tickets
JIRA_JQL_QUERY__WEB=assignee = currentUser() AND updated >= -14d AND project = WEB
```

Since there's a 1:1 mapping between Jira tickets and Things tasks, tickets can only be assigned to one project at a time. Because of this, these queries should be non-overlapping, both between each other and with the main JIRA_JQL_QUERY.

This can also be used to separate tickets in the active sprint from those in the backlog:

Configure the "main" project/query as the backlog and add a second project/query for the active sprint:

```ini
THINGS_PROJECT=Backlog
JIRA_JQL_QUERY=assignee = currentUser() AND updated >= -14d AND (Sprint IS null OR Sprint NOT IN openSprints())

THINGS_PROJECT__ACTIVE=Current Sprint
JIRA_JQL_QUERY__ACTIVE=assignee = currentUser() AND Sprint IN openSprints()
```

#### Sprint Mode

```ini
SCHEDULING_MODE=sprint
```

In `sprint` mode, tickets are scheduled based on their sprint and status:

- Tickets in an active sprint are scheduled to "Anytime"
- Tickets in past/future sprints are scheduled to "Someday"
- Any tickets with a status in `TODAY_STATUS` are scheduled to "Today"
- Tickets with a status in `COMPLETED_STATUS` are marked as completed in Things

## Status / Scheduling Logic

The app maps JIRA ticket statuses or sprints to Things 3 scheduling areas:

- **Today**: Urgent/active work (appears in Today view)
- **Anytime**: Ready to work on (appears in Anytime list)
- **Someday**: Future/backlog items (appears in Someday list)
- **Completed**: Automatically marked as done in Things

If a status isn't configured, tickets default to **Anytime**.

## Getting JIRA API Token

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a label and copy the token
4. Add it to your config file as `JIRA_API_TOKEN`

## Getting Things Auth Token

1. Enable Things URL scheme in Things 3 preferences
2. Get your token from under the **Manage** button
3. Add it to your config file as `THINGS_AUTH_TOKEN`

## Important Notes

### Tags in Things

If you configure `THINGS_TAGS` or enable `JIRA_TYPE_TAG=true`, you **must create these tags in Things 3 first**. The app cannot create new tags - it can only assign existing ones.

### Database

The app creates a local SQLite database (`jira_tasks.db`) to track tickets and sync status. This enables efficient incremental syncing and offline access to your ticket data.

### Sync Status

Each ticket has a sync status:
- **'not synced'**: Needs to be synced to Things (new or changed tickets)
- **'synced'**: Successfully synced to Things
- **'unknown'**: Sync failed - needs troubleshooting

## Troubleshooting

- **"No issues found"**: Check your JQL query and JIRA permissions
- **Things sync fails**: Verify auth token and ensure tags exist in Things
- **Config errors**: Ensure all required fields are present and properly formatted
- **Use `--verbose`** for detailed logging when debugging issues

## Example Workflow

1. **Initial setup**:
   - Copy `config.example` to `config`
   - Configure JIRA and Things credentials in the `config` file
2. **First run**: `python main.py` (syncs all matching tickets)
3. **Daily use**: Run periodically to sync new/changed tickets
4. **Troubleshooting**: Use `--resync-to-things` if Things gets out of sync

## Prerequisites

- Python 3.7 or higher
- A JIRA account with API token access
- Access to the JIRA instance you want to query
- Things 3 installed on your Mac
- things.py library installed (bundled with this repo in librarys/pyThings)

## JQL Query

By default we use the following query to not overburden the Jira API:

```jql
currentUser() AND updated >= -14d
```

## Database Structure

The SQLite database contains a single table `jira_tickets` with the following columns:

- `ticket_id`: The JIRA issue key (e.g., "PROJ-123")
- `summary`: Issue title
- `description`: Full issue description
- `has_subtasks`: Boolean indicating if the issue has subtasks
- `created_at`: Timestamp when the record was created in the database

## Error Handling

The script includes basic error handling and will print error messages if:

- JIRA connection fails
- Authentication fails
- JQL query is invalid
- Database operations fail

## Contributing

Feel free to submit issues and pull requests for additional features or improvements. I'm looking for testers!

## Ai Disclosure

I used LLMs to enhance the codebase and to check for errors. The banner image is also generated.
