import logging
from typing import List
from jira import JIRA
from database import JiraTicket
from config import JiraConfig

class JiraClient:
    """Client for connecting to and retrieving data from JIRA."""

    def __init__(self, config: JiraConfig = None):
        if config is None:
            config = JiraConfig.from_file()
        self.config = config
        self.base_url = config.base_url.rstrip('/')

        logging.debug(f"JIRA Client Init - Server URL: {self.base_url}")
        logging.debug(f"JIRA Client Init - User Email: {self.config.user_email}")
        # Avoid logging token directly for security
        logging.debug(f"JIRA Client Init - API Token is present: {bool(self.config.api_token)}")

        try:
            self.jira = JIRA(
                server=self.base_url,
                basic_auth=(self.config.user_email, self.config.api_token)
            )
            logging.debug("Initialized JIRA client instance.")
            self._verify_connection()
        except Exception as e:
            logging.error(f"Failed to initialize JIRA client: {e}")
            raise

    def _verify_connection(self):
        """Verify connection and authentication with JIRA."""
        try:
            myself = self.jira.myself()
            logging.info(f"Successfully connected to JIRA as: {myself.get('displayName')} ({myself.get('emailAddress')})")
        except Exception as e:
            logging.error(f"Failed to connect to JIRA: {str(e)}")
            raise

    def get_issues(self, jql_query: str) -> List[JiraTicket]:
        """Retrieve issues from JIRA based on given JQL query."""

        # Replace currentUser() placeholder if present
        if 'currentUser()' in jql_query and self.config.user_email:
            jql_query = jql_query.replace('currentUser()', f'"{self.config.user_email}"')

        logging.debug(f"Using JQL query: {jql_query}")

        try:
            fields = self.jira.fields()

            # find sprint field if it exists
            sprint_field = next((field for field in fields if field.get('schema', {}).get('custom', '') == 'com.pyxis.greenhopper.jira:gh-sprint'), None)
        except Exception as e:
            logging.error(f"Error fetching fields from JIRA: {str(e)}")
            raise

        fields = [
            'summary',
            'description',
            'subtasks',
            'status',
            'issuetype',
            sprint_field['id'] if sprint_field else None
        ]

        try:
            issues = self.jira.search_issues(
                jql_query,
                fields=','.join(filter(None, fields)),
                maxResults=100  # Consider making this configurable
            )

            total_issues = len(issues)
            if total_issues == 0:
                logging.warning(f"No issues found matching the JQL query: {jql_query}")
                return []
            else:
                logging.info(f"Retrieved {total_issues} issues from JIRA")

            tickets = []
            for issue in issues:
                # Safely extract field values with defaults
                summary = getattr(issue.fields, 'summary', 'No Summary')
                description = getattr(issue.fields, 'description', '') or ""
                subtasks = getattr(issue.fields, 'subtasks', [])
                status = getattr(issue.fields, 'status', None)
                status_name = status.name if status else ''
                issue_type = getattr(issue.fields, 'issuetype', None)
                issue_type_name = issue_type.name if issue_type else ''

                sprints = getattr(issue.fields, sprint_field['id'], []) if sprint_field else []
                latest_sprint = sorted(
                    sprints,
                    key=lambda s: s.endDate if hasattr(s, 'endDate') else datetime.min.isoformat(),
                    reverse=True
                )[0] if sprints else None
                sprint_name = getattr(latest_sprint, 'name', None)
                sprint_status = getattr(latest_sprint, 'state', None)
                sprint_end_time = getattr(latest_sprint, 'endDate', '').replace('Z', '+00:00')

                ticket = JiraTicket(
                    ticket_id=issue.key,
                    summary=summary,
                    description=description,
                    has_subtasks=len(subtasks) > 0,
                    status=status_name,
                    issue_type=issue_type_name,
                    sprint_name=sprint_name,
                    sprint_status=sprint_status,
                    sprint_end_time=sprint_end_time,
                )
                logging.debug(f"Processing issue {ticket.ticket_id}: {ticket.summary}")
                tickets.append(ticket)

            return tickets

        except Exception as e:
            logging.error(f"Error fetching issues from JIRA: {str(e)}")
            raise
