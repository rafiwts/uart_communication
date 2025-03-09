def test_home(test_client):
    response = test_client.get("/")

    assert response.status_code == 200


def test_configure_device(test_client, config_payload):
    response = test_client.patch("/config", json=config_payload)
    data = response.json()

    assert response.status_code == 202
    assert data["frequency"] == config_payload["frequency"]
    assert data["debug_mode"] == config_payload["debug_mode"]
