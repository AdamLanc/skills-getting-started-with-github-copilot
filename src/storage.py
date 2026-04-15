"""Data persistence layer for activities using JSON file storage."""

import json
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Default activities to initialize the data store
DEFAULT_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Competitive soccer team for all skill levels",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": []
    },
    "Swimming Club": {
        "description": "Learn and practice swimming techniques",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Art Club": {
        "description": "Explore painting, drawing, and sculpture",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Drama Club": {
        "description": "Act, direct, and produce theatrical performances",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "max_participants": 25,
        "participants": []
    },
    "Debate Team": {
        "description": "Practice public speaking and argumentation",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": []
    },
    "Math Olympiad": {
        "description": "Prepare for math competitions and puzzles",
        "schedule": "Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": []
    }
}


class DataStore:
    """Manages persistent storage of activities data in JSON format."""

    def __init__(self, data_file: str = "data/activities.json"):
        """
        Initialize the DataStore.

        Args:
            data_file: Path to the JSON file for storing activities data.
                      Defaults to "data/activities.json" in the project root.
        """
        self.data_file = Path(data_file)
        self._activities: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """
        Load activities from the JSON file.

        If the file doesn't exist, initialize with default activities
        and save them to the file.
        """
        if self.data_file.exists():
            try:
                with open(self.data_file, "r") as f:
                    self._activities = json.load(f)
                logger.info(f"Loaded activities from {self.data_file}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from {self.data_file}: {e}")
                self._activities = DEFAULT_ACTIVITIES.copy()
                self.save()
            except IOError as e:
                logger.error(f"Failed to read {self.data_file}: {e}")
                self._activities = DEFAULT_ACTIVITIES.copy()
        else:
            # Initialize with default activities
            self._activities = DEFAULT_ACTIVITIES.copy()
            self.save()
            logger.info(f"Initialized activities file at {self.data_file}")

    def save(self) -> None:
        """
        Save activities to the JSON file.

        Creates the parent directory if it doesn't exist.
        """
        try:
            # Create parent directory if it doesn't exist
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to a temporary file first, then rename (atomic operation)
            temp_file = self.data_file.with_suffix(".json.tmp")
            with open(temp_file, "w") as f:
                json.dump(self._activities, f, indent=2)
            
            # Atomic rename
            temp_file.replace(self.data_file)
            logger.debug(f"Saved activities to {self.data_file}")
        except IOError as e:
            logger.error(f"Failed to save activities to {self.data_file}: {e}")
            raise

    def get_activities(self) -> Dict[str, Any]:
        """
        Get all activities.

        Returns:
            Dictionary of all activities.
        """
        return self._activities

    def get_activity(self, activity_name: str) -> Dict[str, Any]:
        """
        Get a specific activity by name.

        Args:
            activity_name: Name of the activity to retrieve.

        Returns:
            Activity dictionary.

        Raises:
            KeyError: If activity doesn't exist.
        """
        if activity_name not in self._activities:
            raise KeyError(f"Activity '{activity_name}' not found")
        return self._activities[activity_name]

    def add_participant(self, activity_name: str, email: str) -> None:
        """
        Add a participant (email) to an activity.

        Args:
            activity_name: Name of the activity.
            email: Email address of the participant.

        Raises:
            KeyError: If activity doesn't exist.
            ValueError: If participant is already signed up.
        """
        activity = self.get_activity(activity_name)
        
        if email in activity["participants"]:
            raise ValueError(f"Student already signed up for this activity")
        
        activity["participants"].append(email)
        self.save()

    def remove_participant(self, activity_name: str, email: str) -> None:
        """
        Remove a participant (email) from an activity.

        Args:
            activity_name: Name of the activity.
            email: Email address of the participant.

        Raises:
            KeyError: If activity doesn't exist.
            ValueError: If participant is not registered for the activity.
        """
        activity = self.get_activity(activity_name)
        
        if email not in activity["participants"]:
            raise ValueError(f"Student not registered for this activity")
        
        activity["participants"].remove(email)
        self.save()
