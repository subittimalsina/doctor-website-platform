def test_contact_submission(client):
    response = client.post(
        "/contact",
        data={
            "full_name": "Test Contact",
            "email": "test-contact@example.com",
            "phone": "555-000-1234",
            "subject": "General",
            "message": "This is a complete contact message for testing.",
        },
    )
    assert response.status_code == 200
    assert "submitted" in response.text.lower()
