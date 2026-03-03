def test_ai_message(client):
    payload = {"message": "How can I book an appointment?"}
    response = client.post("/ai/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data["reply"]
    assert data["source"] in {"mock", "openai"}
