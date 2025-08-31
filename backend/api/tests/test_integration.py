import pytest
import time

# This test file will automatically use the `docker_services` and `client` fixtures
# defined in conftest.py

def test_api_is_up(client):
    """
    Test a basic endpoint to ensure the FastAPI service is running.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "Real-Time Chatroom" in response.text

@pytest.mark.parametrize("message_text, expected_mood", [
    ("I am so happy!", "happy"),
    ("I'm feeling very sad today.", "sad"),
    ("I'm just writing a neutral message.", "neutral"),
])
def test_send_message_and_get_analysis(client, message_text, expected_mood):
    """
    Sends a message and then checks the admin analysis endpoints to verify
    the mood and safety labels are correctly stored.
    This is a true end-to-end integration test.
    """
    room_id = "test_integration_room"
    
    # 1. Send the message via the API
    response = client.post(
        f"/chatrooms/{room_id}/messages",
        json={"user": "test_user", "text": message_text}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "message published"
    
    # Give Redis and the LLM time to process the request
    time.sleep(2)
    
    # 2. Query the mood analysis endpoint
    mood_response = client.get("/admin/mood_analysis")
    assert mood_response.status_code == 200
    mood_data = mood_response.json()
    assert room_id in mood_data
    assert mood_data[room_id][expected_mood] > 0
    
    # 3. Query the safety analysis endpoint
    safety_response = client.get("/admin/safety_analysis")
    assert safety_response.status_code == 200
    safety_data = safety_response.json()
    assert room_id in safety_data
    
    # The safety label should always be "safe" for these test messages
    assert safety_data[room_id]["safe"] > 0
    
def test_get_metrics(client):
    """
    Test that the metrics endpoint returns the correct structure.
    """
    response = client.get("/admin/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert "chatrooms" in metrics
    assert "connected_users" in metrics
    assert metrics["chatrooms"] >= 0
    assert metrics["connected_users"] >= 0

