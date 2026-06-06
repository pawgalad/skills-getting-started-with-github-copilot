"""
FastAPI tests for Mergington High School Activities API

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and test client
- Act: Execute the action being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture providing a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Fixture to reset activities to initial state between tests"""
    from src.app import activities
    
    initial_state = {
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
            "description": "Competitive basketball team for interscholastic play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Recreational and competitive tennis",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 10,
            "participants": ["amanda@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater production and performance skills",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["rachel@mergington.edu", "noah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["luna@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and argumentation skills",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["chris@mergington.edu"]
        }
    }
    
    yield
    
    # Reset activities to initial state after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_returns_200(self, client):
        """Test that all activities are successfully retrieved"""
        # Arrange
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == expected_activity_count
    
    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have the correct data structure"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert len(activities_data) > 0
        for activity_name, activity_details in activities_data.items():
            assert isinstance(activity_name, str)
            assert required_fields.issubset(set(activity_details.keys()))
            assert isinstance(activity_details["participants"], list)
            assert isinstance(activity_details["max_participants"], int)
    
    def test_get_activities_includes_chess_club(self, client):
        """Test that Chess Club activity is in the response"""
        # Arrange
        expected_activity = "Chess Club"
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert expected_activity in activities_data
        assert activities_data[expected_activity]["max_participants"] == 12


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_returns_200(self, client, reset_activities):
        """Test that a new student can successfully sign up for an activity"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        # Arrange
        activity_name = "Programming Class"
        new_email = "alice@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup?email={new_email}",
            params={"email": new_email}
        )
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert new_email in activities_data[activity_name]["participants"]
    
    def test_signup_duplicate_student_returns_400(self, client, reset_activities):
        """Test that duplicate signup returns error"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_invalid_activity_returns_404(self, client, reset_activities):
        """Test that signup for non-existent activity returns error"""
        # Arrange
        invalid_activity = "NonExistentClub"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={email}",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404 or response.status_code == 400


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_delete_participant_returns_200(self, client, reset_activities):
        """Test that a participant can be successfully removed"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
    
    def test_delete_removes_participant_from_list(self, client, reset_activities):
        """Test that delete actually removes the participant"""
        # Arrange
        activity_name = "Drama Club"
        email_to_remove = "rachel@mergington.edu"
        
        # Act
        client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert email_to_remove not in activities_data[activity_name]["participants"]
    
    def test_delete_nonexistent_participant_returns_400(self, client, reset_activities):
        """Test that deleting non-existent participant returns error"""
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "nosuchstudent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]
    
    def test_delete_from_invalid_activity_returns_404(self, client, reset_activities):
        """Test that delete from non-existent activity returns error"""
        # Arrange
        invalid_activity = "NonExistentClub"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""
    
    def test_signup_then_delete_flow(self, client, reset_activities):
        """Test complete flow: signup a student, verify they're added, then remove them"""
        # Arrange
        activity_name = "Tennis Club"
        new_email = "integration_test@mergington.edu"
        
        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}",
            params={"email": new_email}
        )
        
        # Assert - Signup successful
        assert signup_response.status_code == 200
        
        # Act - Verify participant added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert new_email in activities_data[activity_name]["participants"]
        
        # Act - Delete participant
        delete_response = client.delete(
            f"/activities/{activity_name}/participants/{new_email}"
        )
        
        # Assert - Delete successful
        assert delete_response.status_code == 200
        
        # Act - Verify participant removed
        final_response = client.get("/activities")
        final_data = final_response.json()
        assert new_email not in final_data[activity_name]["participants"]
    
    def test_multiple_signups_increases_participant_count(self, client, reset_activities):
        """Test that multiple signups correctly increase participant count"""
        # Arrange
        activity_name = "Art Studio"
        new_emails = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        
        # Act - Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act - Sign up multiple students
        for email in new_emails:
            client.post(
                f"/activities/{activity_name}/signup?email={email}",
                params={"email": email}
            )
        
        # Act - Get final count
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        
        # Assert
        assert final_count == initial_count + len(new_emails)
