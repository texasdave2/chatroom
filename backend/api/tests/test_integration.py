import pytest
import time
import httpx

# Fixtures from conftest.py are automatically available here.

def test_api_is_up(client: httpx.Client):
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
def test_send_message_and_get_analysis(client: httpx.Client, message_text, expected_mood):
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

@pytest.mark.parametrize("message_text, expected_safety", [
    ("This is a safe and friendly chat.", "safe"),
    ("I love this chat!", "safe"),
    ("This is a very unsafe chatroom", "unsafe"),
    ("You are ugly and a bad person.", "unsafe"),
])
def test_safety_analysis(client: httpx.Client, message_text, expected_safety):
    """
    Tests the safety analysis feature by sending safe and unsafe messages
    and verifying the results on the admin panel.
    """
    room_id = "test_safety_room"
    
    # Send the message
    response = client.post(
        f"/chatrooms/{room_id}/messages",
        json={"user": "safety_tester", "text": message_text}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "message published"
    
    # Give the backend time to process the LLM call
    time.sleep(2)
    
    # Query the safety analysis endpoint
    safety_response = client.get("/admin/safety_analysis")
    assert safety_response.status_code == 200
    safety_data = safety_response.json()
    
    assert room_id in safety_data
    assert safety_data[room_id][expected_safety] > 0

def test_get_metrics(client: httpx.Client):
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

