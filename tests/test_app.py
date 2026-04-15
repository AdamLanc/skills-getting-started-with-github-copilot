"""Integration and unit tests for the Mergington High School API."""

import pytest


class TestRootEndpoint:
    """Tests for the GET / endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that the root endpoint redirects to the static index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, sample_activities):
        """Test that get_activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        # Should contain all predefined activities (9 activities)
        assert len(data) >= 9
    
    def test_get_activities_has_correct_structure(self, client, sample_activities):
        """Test that activities have the correct data structure."""
        response = client.get("/activities")
        data = response.json()
        
        # Check that each activity has the required fields
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_returns_expected_activities(self, client, sample_activities):
        """Test that specific activities are present in the response."""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity in expected_activities:
            assert activity in data


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_valid_activity_and_email(self, client, sample_activities):
        """Test successful signup for an activity."""
        response = client.post("/activities/Soccer Team/signup?email=alice@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "alice@mergington.edu" in data["message"]
        assert "Soccer Team" in data["message"]
    
    def test_signup_adds_student_to_participants(self, client, sample_activities):
        """Test that signup actually adds the student to the participants list."""
        email = "bob@mergington.edu"
        response = client.post(f"/activities/Swimming Club/signup?email={email}")
        assert response.status_code == 200
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Swimming Club"]["participants"]
    
    def test_signup_missing_email_parameter(self, client, sample_activities):
        """Test that signup fails when email parameter is missing."""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # Unprocessable Entity (FastAPI validation error)
    
    def test_signup_nonexistent_activity(self, client, sample_activities):
        """Test that signup fails for a nonexistent activity."""
        response = client.post("/activities/Nonexistent Activity/signup?email=test@example.com")
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email(self, client, sample_activities):
        """Test that signup fails when a student is already signed up."""
        # Chess Club has michael@mergington.edu already signed up
        response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_students_same_activity(self, client, sample_activities):
        """Test that multiple students can sign up for the same activity."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(f"/activities/Art Club/signup?email={email1}")
        assert response1.status_code == 200
        
        response2 = client.post(f"/activities/Art Club/signup?email={email2}")
        assert response2.status_code == 200
        
        # Verify both students are in the activity
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email1 in data["Art Club"]["participants"]
        assert email2 in data["Art Club"]["participants"]
    
    def test_signup_same_student_different_activities(self, client, sample_activities):
        """Test that the same student can sign up for multiple activities."""
        email = "versatile@mergington.edu"
        
        response1 = client.post(f"/activities/Drama Club/signup?email={email}")
        assert response1.status_code == 200
        
        response2 = client.post(f"/activities/Debate Team/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify student is in both activities
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Drama Club"]["participants"]
        assert email in data["Debate Team"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_existing_student(self, client, sample_activities):
        """Test successful unregistration of a student."""
        # Programming Class has emma@mergington.edu
        email = "emma@mergington.edu"
        response = client.delete(f"/activities/Programming Class/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Programming Class" in data["message"]
    
    def test_unregister_removes_student_from_participants(self, client, sample_activities):
        """Test that unregister actually removes the student."""
        email = "michael@mergington.edu"
        
        # Verify student is signed up
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify student was removed
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email not in data["Chess Club"]["participants"]
    
    def test_unregister_missing_email_parameter(self, client, sample_activities):
        """Test that unregister fails when email parameter is missing."""
        response = client.delete("/activities/Chess Club/unregister")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_unregister_nonexistent_activity(self, client, sample_activities):
        """Test that unregister fails for a nonexistent activity."""
        response = client.delete("/activities/Nonexistent Activity/unregister?email=test@example.com")
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_student_not_registered(self, client, sample_activities):
        """Test that unregister fails when a student is not registered."""
        response = client.delete("/activities/Chess Club/unregister?email=notregistered@example.com")
        assert response.status_code == 400
        
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_then_signup_again(self, client, sample_activities):
        """Test that a student can unregister and then sign up again."""
        email = "flexible@mergington.edu"
        activity = "Math Olympiad"
        
        # Sign up
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response3.status_code == 200
        
        # Verify student is registered
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data[activity]["participants"]


class TestIntegrationScenarios:
    """Integration tests combining multiple endpoints."""
    
    def test_full_signup_workflow(self, client, sample_activities):
        """Test a complete signup workflow."""
        # Get activities
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) > 0
        
        # Sign up for an activity
        email = "integration@mergington.edu"
        activity = "Debate Team"
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signup by getting activities
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]
    
    def test_signup_and_unregister_workflow(self, client, sample_activities):
        """Test signup followed by unregister."""
        email = "workflow@mergington.edu"
        activity = "Soccer Team"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregistration
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity]["participants"]
    
    def test_multiple_students_and_activities(self, client, sample_activities):
        """Test multiple students signing up for multiple activities."""
        students = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Each student signs up for each activity
        for student in students:
            for activity in activities:
                response = client.post(f"/activities/{activity}/signup?email={student}")
                assert response.status_code == 200
        
        # Verify all signups
        response = client.get("/activities")
        data = response.json()
        for student in students:
            for activity in activities:
                assert student in data[activity]["participants"]
