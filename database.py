import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class JiraTicket:
    """Data class representing a JIRA ticket."""
    ticket_id: str
    summary: str
    description: str
    has_subtasks: bool
    status: str
    issue_type: str = None
    sprint_name: Optional[str] = None
    sprint_status: Optional[str] = None
    sprint_end_time: Optional[str] = None
    things_id: str = None
    present_in_last_fetch: bool = True
    things_project: Optional[str] = None
    last_updated: str = None

class DatabaseManager:
    """Manages SQLite database operations for JIRA tickets."""

    def __init__(self, db_path: str, jira_base_url: str):
        self.db_path = db_path
        self.jira_base_url = jira_base_url.rstrip('/')  # Remove trailing slash if present
        logging.debug(f"Initializing database at {db_path}")
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections with automatic cleanup."""
        logging.debug("Opening database connection")
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
            logging.debug("Closed database connection")

    def _init_db(self) -> None:
        """Initialize the database schema with proper constraints."""
        logging.info(f"Initializing database at path: {self.db_path}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jira_tickets (
                    ticket_id TEXT PRIMARY KEY,
                    summary TEXT NOT NULL,
                    description TEXT,
                    has_subtasks BOOLEAN NOT NULL,
                    status TEXT,
                    issue_type TEXT,
                    sprint_name TEXT,
                    sprint_status TEXT,
                    sprint_end_time TIMESTAMP,
                    things_id TEXT,
                    things_project TEXT,
                    added_to_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    present_in_last_fetch BOOLEAN NOT NULL DEFAULT 1,
                    synced_to_things TEXT DEFAULT 'not synced' CHECK(synced_to_things IN ('synced', 'not synced', 'unknown')),
                    last_updated TIMESTAMP
                )
            ''')

            # We don't have a full schema migration system, so this just attempts to add
            # any new columns from after the 1.0 release and skips if they already exist.
            for field in ['sprint_name TEXT', 'sprint_status TEXT', 'sprint_end_time TEXT', 'things_project TEXT', 'present_in_last_fetch BOOLEAN NOT NULL DEFAULT 1']:
                try:
                    cursor.execute(f"ALTER TABLE jira_tickets ADD COLUMN {field};")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        raise

                    logging.debug(f"Column '{field}' already exists, skipping addition")

            conn.commit()
            logging.info("Database initialization complete")

    def save_ticket(self, ticket: JiraTicket) -> None:
        """Save or update a ticket in the database.

        Only updates timestamps and sync status when actual changes are detected.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT summary, description, status, issue_type, sprint_name, sprint_status, sprint_end_time, things_id, things_project, synced_to_things
                FROM jira_tickets WHERE ticket_id = ?
            ''', (ticket.ticket_id,))
            row = cursor.fetchone()
            things_id = ticket.things_id

            if row:
                # Ticket exists - check for content changes
                (existing_summary, existing_description, existing_status, existing_issue_type,
                    existing_sprint_name, existing_sprint_status, existing_sprint_end_time,
                    existing_things_id, existing_things_project, existing_synced) = row
                if not things_id:
                    things_id = existing_things_id

                # Compare all relevant fields for changes
                has_changes = (
                    existing_summary != ticket.summary or
                    existing_description != ticket.description or
                    existing_status != ticket.status or
                    existing_issue_type != ticket.issue_type or
                    existing_sprint_name != ticket.sprint_name or
                    existing_sprint_status != ticket.sprint_status or
                    existing_sprint_end_time != ticket.sprint_end_time or
                    existing_things_project != ticket.things_project
                )

                if not has_changes:
                    # No changes detected - exit early without DB writes
                    logging.debug(f"No changes detected for ticket {ticket.ticket_id}, preserving sync status")
                    return
                else:
                    # Changes detected - update ticket and mark as unsynced
                    logging.info(f"Changes detected for ticket {ticket.ticket_id}, marking as not synced")
                    cursor.execute('''
                        UPDATE jira_tickets
                        SET summary = ?, description = ?, has_subtasks = ?, status = ?,
                            issue_type = ?, sprint_name = ?, sprint_status = ?, sprint_end_time = ?,
                            things_id = ?, things_project = ?, synced_to_things = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE ticket_id = ?
                    ''', (ticket.summary, ticket.description, ticket.has_subtasks, ticket.status,
                          ticket.issue_type, ticket.sprint_name, ticket.sprint_status, ticket.sprint_end_time,
                          things_id, ticket.things_project, 'not synced', ticket.ticket_id))
            else:
                # New ticket - insert with current timestamps
                logging.debug(f"Inserting new ticket {ticket.ticket_id}")
                cursor.execute('''
                    INSERT INTO jira_tickets
                    (ticket_id, summary, description, has_subtasks, status, issue_type,
                     sprint_name, sprint_status, sprint_end_time,
                     things_id, things_project, synced_to_things, added_to_db, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (ticket.ticket_id, ticket.summary, ticket.description, ticket.has_subtasks,
                      ticket.status, ticket.issue_type, ticket.sprint_name, ticket.sprint_status,
                      ticket.sprint_end_time, things_id, ticket.things_project, 'not synced'))

            conn.commit()

    def get_all_tickets(self) -> List[JiraTicket]:
        """Retrieve all tickets from the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            logging.debug("Retrieving all tickets from database")
            cursor.execute('''
                SELECT ticket_id, summary, description, has_subtasks, status, issue_type, sprint_name,
                sprint_status, sprint_end_time, things_id, present_in_last_fetch, things_project, last_updated FROM jira_tickets
            ''')
            return [JiraTicket(*row) for row in cursor.fetchall()]

    def get_unsynced_tickets(self) -> List[JiraTicket]:
        """Get tickets that haven't been synced to Things (status = 'not synced')."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                    SELECT ticket_id, summary, description, has_subtasks, status,
                        issue_type, sprint_name, sprint_status, sprint_end_time,
                        things_id, present_in_last_fetch, things_project, last_updated
                    FROM jira_tickets
                    WHERE synced_to_things = 'not synced'
                '''
            )
            return [JiraTicket(*row) for row in cursor.fetchall()]

    def get_ticket_by_id(self, ticket_id: str) -> Optional[JiraTicket]:
        """Retrieve a specific ticket by its ID. Returns None if not found."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                    SELECT ticket_id, summary, description, has_subtasks, status, issue_type, sprint_name,
                        sprint_status, sprint_end_time, things_id, present_in_last_fetch, things_project, last_updated
                    FROM jira_tickets WHERE ticket_id = ?
                ''',
                (ticket_id,)
            )
            row = cursor.fetchone()
            if row:
                return JiraTicket(*row)
            return None

    def mark_present(self, all_issues: List[JiraTicket]):
        """Mark the given issues as present in the last fetch, updating sync status as necessary."""
        with self.get_connection() as conn:
            ticket_ids = [ticket.ticket_id for ticket in all_issues]
            if not ticket_ids:
                return

            cursor = conn.cursor()

            cursor.execute(
                '''
                    UPDATE jira_tickets
                    SET present_in_last_fetch = ticket_id IN ({}),
                        synced_to_things = CASE
                            WHEN synced_to_things = 'synced' AND present_in_last_fetch != (ticket_id IN ({})) THEN 'not synced'
                            ELSE synced_to_things
                        END
                '''.format(
                    ','.join('?' * len(ticket_ids)),
                    ','.join('?' * len(ticket_ids))
                ),
                ticket_ids + ticket_ids
            )

            conn.commit()
