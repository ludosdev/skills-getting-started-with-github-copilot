"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a clean state before each test"""
    # Save original state
    original_activities = {
        "Chess Club": {
            "description": "Join us for soccer practice and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Mondays and Wednesdays, 5:00 PM - 7:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art techniques and create projects",
            "schedule": "Wednesdays, 3:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Drama Club": {
            "description": "Participate in theater productions and improv",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Debate Team": {
            "description": "Engage in debates on various topics and improve public speaking",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Thursdays, 3:00 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
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
        }
    }
    
    # Clear and repopulate
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = ["Chess Club", "Basketball Team", "Art Club", 
                               "Drama Club", "Debate Team", "Science Club",
                               "Programming Class", "Gym Class"]
        
        # Check all expected activities are present
        for activity in expected_activities:
            assert activity in data
    
    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client):
        """Test successfully signing up a new participant"""
        response = client.post(
            "/activities/Art%20Club/signup?email=alice@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant"""
        client.post("/activities/Art%20Club/signup?email=alice@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert "alice@mergington.edu" in data["Art Club"]["participants"]
    
    def test_signup_duplicate_fails(self, client):
        """Test that signing up twice for the same activity fails"""
        email = "bob@mergington.edu"
        
        # First signup
        response1 = client.post(f"/activities/Art%20Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup
        response2 = client.post(f"/activities/Art%20Club/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/signup?email=alice@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_with_existing_participants(self, client):
        """Test signing up for an activity that already has participants"""
        # Programming Class already has emma and sophia
        response = client.post(
            "/activities/Programming%20Class/signup?email=charlie@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify it was added
        response = client.get("/activities")
        data = response.json()
        assert "charlie@mergington.edu" in data["Programming Class"]["participants"]
        assert len(data["Programming Class"]["participants"]) == 3


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        # First sign up
        client.post("/activities/Art%20Club/signup?email=dave@mergington.edu")
        
        # Then unregister
        response = client.post(
            "/activities/Art%20Club/unregister?email=dave@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        # Sign up
        client.post("/activities/Art%20Club/signup?email=eve@mergington.edu")
        
        # Unregister
        client.post("/activities/Art%20Club/unregister?email=eve@mergington.edu")
        
        # Verify removed
        response = client.get("/activities")
        data = response.json()
        assert "eve@mergington.edu" not in data["Art Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering someone not signed up"""
        response = client.post(
            "/activities/Art%20Club/unregister?email=frank@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/unregister?email=grace@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_unregister_from_activity_with_multiple_participants(self, client):
        """Test unregistering from activity with multiple participants"""
        # Programming Class has emma and sophia
        response = client.post(
            "/activities/Programming%20Class/unregister?email=emma@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify
        response = client.get("/activities")
        data = response.json()
        assert "emma@mergington.edu" not in data["Programming Class"]["participants"]
        assert "sophia@mergington.edu" in data["Programming Class"]["participants"]


class TestSignupAndUnregisterFlow:
    """Tests for signup and unregister workflows"""
    
    def test_signup_then_unregister(self, client):
        """Test signing up and then unregistering"""
        email = "henry@mergington.edu"
        activity = "Art%20Club"
        
        # Sign up
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()["Art Club"]["participants"]
        
        # Unregister
        response2 = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response2.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        assert email not in response.json()["Art Club"]["participants"]
    
    def test_signup_again_after_unregister(self, client):
        """Test signing up again after unregistering"""
        email = "iris@mergington.edu"
        activity = "Art%20Club"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Unregister
        client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Sign up again
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify
        response = client.get("/activities")
        assert email in response.json()["Art Club"]["participants"]
