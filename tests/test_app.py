"""
Tests for the Mergington High School Activities API
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def unique_email():
    """Generate a unique test email"""
    return f"test_{uuid.uuid4().hex[:8]}@mergington.edu"


@pytest.fixture
def sample_activity(client):
    """Get a sample activity for testing"""
    response = client.get("/activities")
    activities = response.json()
    return list(activities.keys())[0], activities


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that /activities returns a dictionary of activities"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_activity_participants_are_strings(self, client):
        """Test that participants are email strings"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_data in activities.values():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant


class TestRootEndpoint:
    """Tests for the GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_returns_200(self, client, sample_activity, unique_email):
        """Test signing up a new participant returns 200"""
        activity_name = sample_activity[0]
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": unique_email}
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client, sample_activity, unique_email):
        """Test that signup returns a success message"""
        activity_name = sample_activity[0]
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": unique_email}
        )
        data = response.json()
        assert "message" in data
        assert unique_email in data["message"]

    def test_signup_duplicate_participant_returns_400(self, client, sample_activity):
        """Test that signing up a duplicate participant returns 400"""
        activity_name = sample_activity[0]
        activity_data = sample_activity[1][activity_name]
        existing_email = activity_data["participants"][0]
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for nonexistent activity returns 404"""
        response = client.post(
            "/activities/NonexistentActivity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_adds_participant_to_list(self, client, sample_activity, unique_email):
        """Test that signup actually adds participant to the list"""
        activity_name = sample_activity[0]
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Sign up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": unique_email}
        )
        
        # Check count increased
        response = client.get("/activities")
        new_count = len(response.json()[activity_name]["participants"])
        assert new_count == initial_count + 1
        assert unique_email in response.json()[activity_name]["participants"]

    def test_signup_full_activity_returns_400(self, client):
        """Test that signing up for full activity returns 400"""
        # First, let's find or create a full activity
        # At this test level, we just verify the logic works
        # This is a simplified test
        response = client.get("/activities")
        activities = response.json()
        
        # Find an activity with limited spots
        for activity_name, activity_data in activities.items():
            available = activity_data["max_participants"] - len(activity_data["participants"])
            if available == 0:
                # Found a full activity
                response = client.post(
                    f"/activities/{activity_name}/signup",
                    params={"email": "fullactivity@mergington.edu"}
                )
                assert response.status_code == 400
                return
        
        # If no full activity found, test is skipped
        pytest.skip("No full activity found in test data")


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_returns_200(self, client, sample_activity, unique_email):
        """Test unregistering an existing participant returns 200"""
        activity_name = sample_activity[0]
        
        # First sign up a participant
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": unique_email}
        )
        
        # Then unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": unique_email}
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self, client, sample_activity, unique_email):
        """Test that unregister returns a success message"""
        activity_name = sample_activity[0]
        
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": unique_email}
        )
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": unique_email}
        )
        data = response.json()
        assert "message" in data
        assert unique_email in data["message"]

    def test_unregister_nonexistent_participant_returns_400(self, client, sample_activity):
        """Test that unregistering a non-existent participant returns 400"""
        activity_name = sample_activity[0]
        email = "nonexistent@mergington.edu"
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering for nonexistent activity returns 404"""
        response = client.delete(
            "/activities/NonexistentActivity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_removes_participant_from_list(self, client, sample_activity, unique_email):
        """Test that unregister actually removes participant from the list"""
        activity_name = sample_activity[0]
        
        # Sign up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": unique_email}
        )
        
        # Verify signed up
        response = client.get("/activities")
        assert unique_email in response.json()[activity_name]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": unique_email}
        )
        
        # Verify removed
        response = client.get("/activities")
        assert unique_email not in response.json()[activity_name]["participants"]
