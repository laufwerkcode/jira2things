from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class JiraConfig:
    """Configuration for JIRA connection and queries."""
    base_url: str
    api_token: str
    user_email: str
    jql_query: str = "project = DEMO AND status != Done ORDER BY created DESC"

    @classmethod
    def from_file(cls, filename="config"):
        """Load JIRA configuration from file."""
        config = load_config_vars(filename)
        
        # Validate required fields
        required_fields = ['JIRA_BASE_URL', 'JIRA_API_TOKEN', 'JIRA_USER_EMAIL']
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise ValueError(f"Missing required JIRA configuration fields: {', '.join(missing_fields)}")
        
        return cls(
            base_url=config["JIRA_BASE_URL"],
            api_token=config["JIRA_API_TOKEN"],
            user_email=config["JIRA_USER_EMAIL"],
            jql_query=config.get("JIRA_JQL_QUERY", "project = DEMO AND status != Done ORDER BY created DESC")
        )

@dataclass
class DatabaseConfig:
    """Configuration for SQLite database."""
    db_path: str = "jira_tasks.db" 

def load_config_vars(filename="config"):
    """Load configuration variables from a key=value file."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Configuration file '{filename}' not found")
    
    config = {}
    try:
        with open(filename, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Parse key=value pairs
                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
                else:
                    # Log malformed lines but continue processing
                    print(f"Warning: Malformed line {line_num} in {filename}: {line}")
    except Exception as e:
        raise RuntimeError(f"Error reading configuration file '{filename}': {e}")
    
    return config
