"""Tests for the Mergington High School Activities API."""
import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities(self, client):
        """Test that activities can be retrieved."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball" in data
        assert "Soccer Club" in data
        assert "Chess Club" in data

    def test_activities_structure(self, client):
        """Test that activities have the correct structure."""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Basketball"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity(self, client, reset_activities):
        """Test that a student can sign up for an activity."""
        response = client.post(
            "/activities/Basketball/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "test@mergington.edu" in data["message"]

    def test_signup_appears_in_participants(self, client, reset_activities):
        """Test that a signed-up student appears in participants list."""
        client.post("/activities/Basketball/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        activity = response.json()["Basketball"]
        assert "newstudent@mergington.edu" in activity["participants"]

    def test_duplicate_signup(self, client, reset_activities):
        """Test that duplicate signups are rejected."""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Basketball/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/Basketball/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test that signing up for a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_missing_email(self, client):
        """Test that signup without email fails."""
        response = client.post("/activities/Basketball/signup")
        assert response.status_code == 422  # Unprocessable Entity


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_from_activity(self, client, reset_activities):
        """Test that a student can unregister from an activity."""
        email = "unregister@mergington.edu"
        
        # First, sign up
        client.post(f"/activities/Basketball/signup?email={email}")
        
        # Then, unregister
        response = client.delete(
            f"/activities/Basketball/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]

    def test_unregister_removes_from_participants(self, client, reset_activities):
        """Test that unregistering removes student from participants list."""
        email = "remove@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Basketball/signup?email={email}")
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()["Basketball"]["participants"]
        
        # Unregister
        client.delete(f"/activities/Basketball/unregister?email={email}")
        
        # Verify removed
        response = client.get("/activities")
        assert email not in response.json()["Basketball"]["participants"]

    def test_unregister_not_signed_up(self, client):
        """Test that unregistering a non-signed-up student fails."""
        response = client.delete(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity(self, client):
        """Test that unregistering from non-existent activity fails."""
        response = client.delete(
            "/activities/Nonexistent/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_missing_email(self, client):
        """Test that unregister without email fails."""
        response = client.delete("/activities/Basketball/unregister")
        assert response.status_code == 422  # Unprocessable Entity


class TestActivityParticipantManagement:
    """Tests for overall participant management workflow."""

    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test the complete flow of signing up and unregistering."""
        email = "flow@mergington.edu"
        activity = "Soccer Club"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify participant count increased
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count + 1
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify participant count back to original
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count

    def test_multiple_participants_in_same_activity(self, client, reset_activities):
        """Test that multiple participants can sign up for the same activity."""
        activity = "Art Studio"
        emails = [
            "participant1@mergington.edu",
            "participant2@mergington.edu",
            "participant3@mergington.edu"
        ]
        
        # Sign up multiple participants
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all are in the list
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
