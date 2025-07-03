import os
import sys
import argparse
import logging
from pathlib import Path

# Check if running in virtual environment
def check_virtual_environment():
    """Check if script is running in the expected virtual environment."""
    venv_path = Path(__file__).parent / ".venv"

    # Check if we're in any virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        if venv_path.exists():
            print("⚠️  Warning: Virtual environment not activated!")
            print(f"   Please run: source {venv_path}/bin/activate")
            print("   Then run the script again.")
            sys.exit(1)
        else:
            print("ℹ️  No virtual environment found - using system Python")
    else:
        # Check if we're in the correct virtual environment
        if venv_path.exists():
            expected_venv = str(venv_path.resolve())
            current_venv = sys.prefix
            if not current_venv.startswith(expected_venv):
                print(f"⚠️  Warning: Using different virtual environment")
                print(f"   Expected: {expected_venv}")
                print(f"   Current:  {current_venv}")
                print(f"   Please run: source {venv_path}/bin/activate")

# Check virtual environment before importing other modules
check_virtual_environment()

from config import JiraConfig, DatabaseConfig
from jira_client import JiraClient
from database import DatabaseManager, JiraTicket

# Add pyThings to path and import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'librarys', 'pyThings')))
from pyThings.tasks import AddTask, UpdateTask

def setup_logging(verbose: bool):
    """Configure logging level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def parse_args():
    parser = argparse.ArgumentParser(description='Sync JIRA tickets to local SQLite database and add to Things')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--config', type=str, default='config', help='Path to config file (default: config)')
    parser.add_argument('--update-db', action='store_true', help='Update database with tickets from JIRA')
    parser.add_argument('--sync-to-things', action='store_true', help='Sync unsynced tickets from database to Things')
    parser.add_argument('--resync-to-things', action='store_true', help='Resync all tickets in database to Things regardless of sync status')
    return parser.parse_args()

def parse_status_set(config, key):
    """Parse status configuration into a set. Returns empty set if key missing."""
    if key not in config:
        return set()
    try:
        import ast
        value = config[key]
        return set(ast.literal_eval(value))
    except Exception:
        # If parsing fails, treat as single value
        return set([value])

def main():
    args = parse_args()
    setup_logging(args.verbose)

    try:
        # Load configuration files
        logging.info("Loading configuration...")
        jira_config = JiraConfig.from_file(args.config)
        db_config = DatabaseConfig()

        # Load extra config vars for Things integration
        from config import load_config_vars
        extra_config = load_config_vars(args.config)

        # Parse status sets for Things scheduling logic
        completed_status = parse_status_set(extra_config, 'COMPLETED_STATUS')
        today_status = parse_status_set(extra_config, 'TODAY_STATUS')
        anytime_status = parse_status_set(extra_config, 'ANYTIME_STATUS')
        someday_status = parse_status_set(extra_config, 'SOMEDAY_STATUS')

        logging.info(f"Using database path: {db_config.db_path}")

        # Initialize JIRA and database connections
        logging.info("Initializing JIRA and database clients...")
        jira_client = JiraClient(jira_config)
        db_manager = DatabaseManager(db_config.db_path, jira_config.base_url)

        # Execute requested operation
        if args.update_db:
            logging.info("Updating database with tickets from JIRA...")
            update_db(db_manager, jira_client, extra_config)
            return

        if args.sync_to_things:
            logging.info("Syncing unsynced tickets from database to Things...")
            sync_to_things(db_manager, extra_config, today_status, anytime_status, someday_status, completed_status)
            return

        if args.resync_to_things:
            logging.info("Resyncing all tickets in database to Things...")
            resync_to_things(db_manager, extra_config, today_status, anytime_status, someday_status, completed_status)
            return

        # Default behavior: full sync workflow
        logging.info("Running full sync: updating database and syncing to Things...")
        update_db(db_manager, jira_client, extra_config)
        sync_to_things(db_manager, extra_config, today_status, anytime_status, someday_status, completed_status)

    except ValueError as e:
        logging.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

def update_db(db_manager: DatabaseManager, jira_client: JiraClient, config: dict):
    """Update database with tickets from JIRA."""
    completed_status = parse_status_set(config, 'COMPLETED_STATUS')

    # Fetch all matching issues from JIRA
    logging.info("Fetching issues from JIRA...")
    issues_by_query = [
      (project_name, jira_client.get_issues(jql_query))
      for project_name, jql_query in _project_queries(config)
    ]

    total_issues = sum(len(issues) for _, issues in issues_by_query)
    logging.debug(f"Retrieved {total_issues} issues from JIRA")

    if total_issues == 0:
        logging.info("No issues found to process")
        return

    # Initialize counters for summary reporting
    added_count = 0
    updated_count = 0
    unchanged_count = 0

    # Process each issue from JIRA
    logging.info("Processing issues...")
    for project_name, issues in issues_by_query:
        for issue in issues:
            issue.things_project = project_name

            existing = db_manager.get_ticket_by_id(issue.ticket_id)

            if existing:
                # Check if ticket content has changed
                has_changes = (existing.summary != issue.summary or
                            existing.description != issue.description or
                            existing.status != issue.status or
                            existing.issue_type != issue.issue_type or
                            existing.things_project != issue.things_project)

                if has_changes:
                    logging.info(f"Updating ticket {issue.ticket_id}: {issue.summary}")
                    updated_count += 1

                    # Handle status change from non-completed to completed
                    status_became_complete = (existing.status != issue.status and
                                            existing.things_id and
                                            existing.status not in completed_status and
                                            issue.status in completed_status)

                    if status_became_complete:
                        try:
                            auth_token = config.get('THINGS_AUTH_TOKEN')
                            if auth_token:
                                UpdateTask(auth_token=auth_token, task_id=existing.things_id, completed=True)
                                logging.info(f"Marked Things task complete for ticket {issue.ticket_id}")
                            else:
                                logging.warning(f"No auth token available to mark ticket {issue.ticket_id} complete in Things")
                        except Exception as e:
                            logging.error(f"Failed to mark Things task complete for ticket {issue.ticket_id}: {e}")
                else:
                    logging.debug(f"Found ticket {issue.ticket_id} but no update needed")
                    unchanged_count += 1
            else:
                logging.info(f"Adding new ticket {issue.ticket_id}: {issue.summary}")
                added_count += 1

            # Save ticket (will only update DB if changes detected)
            db_manager.save_ticket(issue)

    # Report processing summary
    total_processed = added_count + updated_count + unchanged_count
    logging.info(f"Database update complete: {added_count} tickets added, {updated_count} tickets updated, {unchanged_count} unchanged (Total processed: {total_processed})")

def _project_queries(config: dict):
    queries = [
        # Build the main JQL query
        (config.get('THINGS_PROJECT'),
         config.get("JIRA_JQL_QUERY", "project = DEMO AND status != Done ORDER BY created DESC"))
    ]

    for key, value in config.items():
        if key.startswith("JIRA_JQL_QUERY__"):
            project_suffix = key[len("JIRA_JQL_QUERY__"):]
            project_name = config.get(f"THINGS_PROJECT__{project_suffix}", project_suffix)
            queries.append((project_name, value))

    return queries

def _build_things_task_data(ticket: JiraTicket, config: dict, today_status: set, someday_status: set, completed_status: set, jira_base_url: str):
    """Build task data dictionary for Things integration."""
    import ast

    # Basic task information
    title = f"[{ticket.ticket_id}] {ticket.summary}"
    jira_url = f"{jira_base_url}/browse/{ticket.ticket_id}"
    notes = f"{jira_url}\n\n{ticket.description}"

    # Handle tags configuration
    tags = []
    if 'THINGS_TAGS' in config:
        try:
            tags = ast.literal_eval(config['THINGS_TAGS'])
        except Exception:
            tags = [config['THINGS_TAGS']]

    # Add issue type as tag if enabled
    type_tag_enabled = config.get('JIRA_TYPE_TAG', 'false').lower() == 'true'
    if type_tag_enabled and ticket.issue_type:
        tags.append(ticket.issue_type.lower())

    # Build kwargs for Things API
    kwargs = {
        'title': title,
        'notes': notes,
        'tags': tags if tags else None,
        'list_str': ticket.things_project
    }

    # Set scheduling based on ticket status
    if ticket.status in today_status:
        kwargs['when'] = 'today'
    elif ticket.status in someday_status:
        kwargs['when'] = 'someday'
    else:
        kwargs['when'] = 'anytime'

    # Mark as completed if needed
    if ticket.status in completed_status:
        kwargs['completed'] = True

    return kwargs

def sync_to_things(db_manager: DatabaseManager, config: dict, today_status: set, anytime_status: set, someday_status: set, completed_status: set):
    """Sync unsynced tickets from database to Things."""
    unsynced = db_manager.get_unsynced_tickets()

    if not unsynced:
        logging.info("No unsynced tickets found")
        return

    logging.info(f"Found {len(unsynced)} unsynced tickets to process")

    # Separate tickets by whether they already exist in Things
    new_tickets = [t for t in unsynced if not t.things_id]
    update_tickets = [t for t in unsynced if t.things_id]

    logging.info(f"New tickets to add: {len(new_tickets)}, Existing tickets to update: {len(update_tickets)}")

    auth_token = config.get('THINGS_AUTH_TOKEN')

    # Initialize counters
    added_count = 0
    updated_count = 0
    failed_count = 0

    # Process new tickets (AddTask)
    for ticket in new_tickets:
        kwargs = _build_things_task_data(ticket, config, today_status, someday_status, completed_status, db_manager.jira_base_url)

        try:
            # Add to Things using pyThings
            task = AddTask(**kwargs)
            things_id = getattr(task, 'x_things_id', None)

            # Mark as synced and store things_id
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE jira_tickets SET synced_to_things = ?, things_id = ? WHERE ticket_id = ?', ('synced', things_id, ticket.ticket_id))
                conn.commit()
            logging.info(f"Added to Things and marked as synced: {ticket.ticket_id}, Things ID: {things_id}")
            added_count += 1
        except Exception as e:
            # Mark as unknown status for troubleshooting
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE jira_tickets SET synced_to_things = ? WHERE ticket_id = ?', ('unknown', ticket.ticket_id))
                conn.commit()
            logging.error(f"Failed to add {ticket.ticket_id} to Things: {e}")
            failed_count += 1

    # Process existing tickets that need updates (UpdateTask)
    for ticket in update_tickets:
        kwargs = _build_things_task_data(ticket, config, today_status, someday_status, completed_status, db_manager.jira_base_url)

        # Add required parameters for UpdateTask
        kwargs.update({
            'task_id': ticket.things_id,
            'auth_token': auth_token,
            'reveal': False
        })

        if not auth_token:
            logging.warning(f"No auth token available to update ticket {ticket.ticket_id} in Things")
            failed_count += 1
            continue

        try:
            # Update in Things using pyThings
            UpdateTask(**kwargs)

            # Mark as synced
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE jira_tickets SET synced_to_things = ? WHERE ticket_id = ?', ('synced', ticket.ticket_id))
                conn.commit()
            logging.info(f"Updated in Things and marked as synced: {ticket.ticket_id}")
            updated_count += 1
        except Exception as e:
            # Mark as unknown status for troubleshooting
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE jira_tickets SET synced_to_things = ? WHERE ticket_id = ?', ('unknown', ticket.ticket_id))
                conn.commit()
            logging.error(f"Failed to update {ticket.ticket_id} in Things: {e}")
            failed_count += 1

    # Report processing summary
    total_processed = added_count + updated_count + failed_count
    logging.info(f"Things sync complete: {added_count} tickets added, {updated_count} tickets updated, {failed_count} failed (Total processed: {total_processed})")

def resync_to_things(db_manager: DatabaseManager, config: dict, today_status: set, anytime_status: set, someday_status: set, completed_status: set):
    """Resync all tickets from database to Things regardless of sync status."""
    all_tickets = db_manager.get_all_tickets()

    if not all_tickets:
        logging.info("No tickets found in database")
        return

    logging.info(f"Found {len(all_tickets)} tickets to resync")

    # Separate tickets by whether they already exist in Things
    new_tickets = [t for t in all_tickets if not t.things_id]
    update_tickets = [t for t in all_tickets if t.things_id]

    logging.info(f"New tickets to add: {len(new_tickets)}, Existing tickets to update: {len(update_tickets)}")

    auth_token = config.get('THINGS_AUTH_TOKEN')

    # Initialize counters
    added_count = 0
    updated_count = 0
    failed_count = 0

    # Process new tickets (AddTask)
    for ticket in new_tickets:
        kwargs = _build_things_task_data(ticket, config, today_status, someday_status, completed_status, db_manager.jira_base_url)

        try:
            # Add to Things using pyThings
            task = AddTask(**kwargs)
            things_id = getattr(task, 'x_things_id', None)

            # Mark as synced and store things_id
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE jira_tickets SET synced_to_things = ?, things_id = ? WHERE ticket_id = ?', ('synced', things_id, ticket.ticket_id))
                conn.commit()
            logging.info(f"Added to Things and marked as synced: {ticket.ticket_id}, Things ID: {things_id}")
            added_count += 1
        except Exception as e:
            # Mark as unknown status for troubleshooting
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE jira_tickets SET synced_to_things = ? WHERE ticket_id = ?', ('unknown', ticket.ticket_id))
                conn.commit()
            logging.error(f"Failed to add {ticket.ticket_id} to Things: {e}")
            failed_count += 1

    # Process existing tickets that need updates (UpdateTask)
    for ticket in update_tickets:
        kwargs = _build_things_task_data(ticket, config, today_status, someday_status, completed_status, db_manager.jira_base_url)

        # Add required parameters for UpdateTask
        kwargs.update({
            'task_id': ticket.things_id,
            'auth_token': auth_token,
            'reveal': False
        })

        if not auth_token:
            logging.warning(f"No auth token available to update ticket {ticket.ticket_id} in Things")
            failed_count += 1
            continue

        try:
            # Update in Things using pyThings
            UpdateTask(**kwargs)

            # Mark as synced
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE jira_tickets SET synced_to_things = ? WHERE ticket_id = ?', ('synced', ticket.ticket_id))
                conn.commit()
            logging.info(f"Updated in Things and marked as synced: {ticket.ticket_id}")
            updated_count += 1
        except Exception as e:
            # Mark as unknown status for troubleshooting
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE jira_tickets SET synced_to_things = ? WHERE ticket_id = ?', ('unknown', ticket.ticket_id))
                conn.commit()
            logging.error(f"Failed to update {ticket.ticket_id} in Things: {e}")
            failed_count += 1

    # Report processing summary
    total_processed = added_count + updated_count + failed_count
    logging.info(f"Things resync complete: {added_count} tickets added, {updated_count} tickets updated, {failed_count} failed (Total processed: {total_processed})")

if __name__ == "__main__":
    main()
