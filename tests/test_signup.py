from fastapi.testclient import TestClient

from src.app import activities


def test_signup_adds_participant(client: TestClient) -> None:
    # Arrange
    activity_name = "Soccer Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    activity = client.get("/activities").json()[activity_name]
    assert email in activity["participants"]


def test_signup_rejects_unknown_activity(client: TestClient) -> None:
    # Arrange
    activity_name = "Unknown Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_existing_participant(client: TestClient) -> None:
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    initial_participants = list(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    activity = client.get("/activities").json()[activity_name]
    assert activity["participants"] == initial_participants


def test_signup_rejects_full_activity(client: TestClient) -> None:
    # Arrange
    activity_name = "Basketball Club"
    activity = activities[activity_name]
    activity["participants"] = [
        f"student{index}@mergington.edu"
        for index in range(activity["max_participants"])
    ]
    email = "waitlisted@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}
    updated_activity = client.get("/activities").json()[activity_name]
    assert email not in updated_activity["participants"]
    assert len(updated_activity["participants"]) == activity["max_participants"]


def test_signup_requires_email(client: TestClient) -> None:
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422
    assert any(
        error["loc"] == ["query", "email"]
        for error in response.json()["detail"]
    )