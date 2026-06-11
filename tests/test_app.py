"""
Tests for the Mergington High School API using the AAA pattern (Arrange-Act-Assert)
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to known state before each test"""
    # Store original state
    original_activities = {
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
        "Basketball Team": {
            "description": "Competitive basketball training and league games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "alex@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Soccer practice, drills, and friendly matches",
            "schedule": "Mondays, Wednesdays, Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu", "chris@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "mia@mergington.edu"]
        },
        "Music Band": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "liam@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific discoveries",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["benjamin@mergington.edu", "charlotte@mergington.edu"]
        }
    }
    
    # Clear current activities and restore original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that get_activities returns all activities in the database"""
        # Arrange
        expected_activity_count = 9
        expected_activities = ["Chess Club", "Programming Class", "Gym Class", 
                             "Basketball Team", "Soccer Club", "Art Studio", 
                             "Music Band", "Debate Club", "Science Club"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_activity_count
        assert all(activity in data for activity in expected_activities)
    
    def test_get_activities_includes_participant_lists(self, client):
        """Test that get_activities includes participants for each activity"""
        # Arrange
        # No arrangement needed, using fixture state
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert len(activity_data["participants"]) > 0


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "new_student@mergington.edu"
        initial_participants = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_participants + 1
    
    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up an already registered student returns 400"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up"
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404"""
        # Arrange
        activity_name = "Non Existent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_multiple_different_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        # Arrange
        email = "multi_student@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class"]
        
        # Act & Assert for each signup
        for activity_name in activities_to_join:
            response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
            assert response.status_code == 200
            assert email in activities[activity_name]["participants"]


class TestDeleteParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""
    
    def test_delete_participant_success(self, client):
        """Test successful deletion of a participant from an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_delete_nonexistent_participant_returns_404(self, client):
        """Test that deleting a non-existent participant returns 404"""
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Participant not found in activity"
        assert len(activities[activity_name]["participants"]) == initial_count
    
    def test_delete_from_nonexistent_activity_returns_404(self, client):
        """Test that deleting from a non-existent activity returns 404"""
        # Arrange
        activity_name = "Non Existent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_delete_and_resignup(self, client):
        """Test that a student can sign up again after being deleted"""
        # Arrange
        activity_name = "Programming Class"
        email = "test_student@mergington.edu"
        
        # Act - Sign up
        response_signup = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert response_signup.status_code == 200
        
        # Act - Delete
        response_delete = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        assert response_delete.status_code == 200
        
        # Act - Sign up again
        response_resignup = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert
        assert response_resignup.status_code == 200
        assert email in activities[activity_name]["participants"]


class TestActivityNotFoundCases:
    """Tests for various activity not found scenarios (404)"""
    
    def test_signup_activity_not_found(self, client):
        """Test signup returns 404 for non-existent activity"""
        # Arrange
        activity_name = "Invalid Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Assert
        assert response.status_code == 404
    
    def test_delete_activity_not_found(self, client):
        """Test delete returns 404 for non-existent activity"""
        # Arrange
        activity_name = "Invalid Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        
        # Assert
        assert response.status_code == 404
