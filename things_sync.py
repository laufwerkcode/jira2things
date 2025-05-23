import logging
import os
import sys
import argparse

# Add the libraries folder to Python path - more robust path resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
libraries_path = os.path.join(current_dir, 'libraries')
if libraries_path not in sys.path:
    sys.path.insert(0, libraries_path)

#from pyThings.json import Json
from dotenv import load_dotenv
from database import DatabaseManager
from config import DatabaseConfig

class ThingsSyncer:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def update_things_id(self, ticket_id: str, things_id: str):
        """Update the Things ID for a given ticket"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE jira_tickets 
                SET things_id = ? 
                WHERE ticket_id = ?
            ''', (things_id, ticket_id))
            conn.commit()
            logging.info(f"Updated Things ID for ticket {ticket_id}")

    def get_unsynced_tickets(self):
        """Get all tickets that haven't been synced to Things yet"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ticket_id, summary, description, has_subtasks 
                FROM jira_tickets 
                WHERE things_id IS NULL
            ''')
            return cursor.fetchall()

    def create_things_todo(self, ticket_id: str, summary: str, description: str):
        """Create a new todo in Things and return its ID"""
        # Create the todo with JIRA ticket reference in notes
        jira_url = f"{self.db_manager.jira_base_url}/browse/{ticket_id}"
        notes = f"{jira_url}\n\n{description}"
        
        # Create the task data
        task_data = [{
            "type": "to-do",
            "attributes": {
                "title": f"[{ticket_id}] {summary}",
                "notes": notes,
                "tags": ["jira"],
                "list": "inbox"
            }
        }]
        
        # Use pyThings Json class to create the todo
        logging.debug(f"Creating Things todo: {task_data[0]['attributes']['title']}")
        task = Json(data=task_data)
        
        # Get the Things ID from the response
        things_id = task.response.get('x-things-ids')
        if things_id:
            logging.debug(f"Received Things ID: {things_id}")
            return things_id
        else:
            logging.warning("No Things ID received from Things 3")
            return None

    def sync_tickets(self):
        """Sync all unsynced tickets to Things"""
        logging.info("Starting Things sync...")
        unsynced_tickets = self.get_unsynced_tickets()
        
        for ticket in unsynced_tickets:
            ticket_id, summary, description, has_subtasks = ticket
            logging.info(f"Syncing ticket {ticket_id} to Things...")
            
            try:
                # Create the todo in Things
                sync_status = self.create_things_todo(ticket_id, summary, description)
                
                # Update the database with sync status
                self.update_things_id(ticket_id, sync_status)
                
                logging.info(f"Successfully synced ticket {ticket_id} to Things")
            except Exception as e:
                logging.error(f"Error syncing ticket {ticket_id}: {str(e)}")

def parse_args():
    parser = argparse.ArgumentParser(description='Sync JIRA tickets from SQLite to Things 3')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    return parser.parse_args()

def main():
    args = parse_args()
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    try:
        # Load configuration
        load_dotenv()
        jira_base_url = os.getenv("JIRA_BASE_URL")
        if not jira_base_url:
            raise ValueError("JIRA_BASE_URL environment variable is required")

        # Initialize database with jira_base_url
        db_config = DatabaseConfig()
        db_manager = DatabaseManager(db_config.db_path, jira_base_url)
        
        # Initialize and run syncer
        syncer = ThingsSyncer(db_manager)
        syncer.sync_tickets()
        
        logging.info("Things sync completed successfully")
        
    except Exception as e:
        logging.error(f"Error during Things sync: {str(e)}")

if __name__ == "__main__":
    main() 