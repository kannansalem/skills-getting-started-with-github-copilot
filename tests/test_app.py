import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


class TestGetActivities:
    def test_returns_all_activities(self, client):
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activity_has_expected_fields(self, client):
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignup:
    def test_signup_success(self, client):
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "newstudent@mergington.edu" in response.json()["message"]
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_nonexistent_activity(self, client):
        response = client.post(
            "/activities/Nonexistent/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_adds_to_participants_list(self, client):
        initial_count = len(activities["Chess Club"]["participants"])
        client.post("/activities/Chess Club/signup?email=new@mergington.edu")
        assert len(activities["Chess Club"]["participants"]) == initial_count + 1


class TestUnregister:
    def test_unregister_success(self, client):
        email = "michael@mergington.edu"
        response = client.delete(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 200
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        response = client.delete(
            "/activities/Nonexistent/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_signed_up(self, client):
        response = client.delete(
            "/activities/Chess Club/signup?email=nobody@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_removes_from_participants(self, client):
        email = "michael@mergington.edu"
        initial_count = len(activities["Chess Club"]["participants"])
        client.delete(f"/activities/Chess Club/signup?email={email}")
        assert len(activities["Chess Club"]["participants"]) == initial_count - 1


class TestRoot:
    def test_root_redirects(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
