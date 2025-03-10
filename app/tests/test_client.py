import pytest

from app.tests.utils import handle_mean_count


def test_home(test_client):
    response = test_client.get("/")

    assert response.status_code == 200


@pytest.mark.parametrize(
    "frequency, debug_mode, expected_status_code, expected_message",
    [
        (400, True, 400, "Invalid data"),
        (256, False, 400, "Invalid data"),
        (100, True, 202, None),
        (0, False, 400, "Invalid data"),
        (111, False, 202, None),
        (254, True, 202, None),
        (1000, False, 400, "Invalid data"),
    ],
)
def test_device_config_response(
    test_client, frequency, debug_mode, expected_status_code, expected_message
):
    config_payload = {"frequency": frequency, "debug_mode": debug_mode}

    response = test_client.patch("/config", json=config_payload)
    data = response.json()

    assert response.status_code == expected_status_code

    if expected_message:
        assert data["detail"] == expected_message
    else:
        assert data["frequency"] == frequency
        assert data["debug_mode"] == debug_mode


def test_device_metadata_response_one_message(
    test_client, device_config, sensor_data_record
):
    response = test_client.get("/device")
    data = response.json()

    assert response.status_code == 200
    assert data["debug"] == device_config.debug_mode
    assert data["curr_config"]["frequency"] == device_config.frequency
    assert data["curr_config"]["debug"] == device_config.debug_mode

    # since only one messagae mean last 10 and one record the same value
    assert data["mean_last_10"] == data["latest"]
    assert data["mean_last_10"]["pressure"] == sensor_data_record.pressure
    assert data["mean_last_10"]["temperature"] == sensor_data_record.temperature
    assert data["mean_last_10"]["velocity"] == sensor_data_record.velocity


def test_device_metadata_response_messages(test_client, device_config, get_messages):
    all_messages, latest_message = get_messages
    response = test_client.get("/device")
    data = response.json()

    assert data["debug"] == device_config.debug_mode
    assert data["curr_config"]["frequency"] == device_config.frequency
    assert data["curr_config"]["debug"] == device_config.debug_mode

    assert data["latest"]["pressure"] == latest_message.pressure
    assert data["latest"]["temperature"] == latest_message.temperature
    assert data["latest"]["velocity"] == latest_message.velocity

    avg_pressure, avg_temperature, avg_velocity = handle_mean_count(all_messages)

    assert len(all_messages) == 10
    assert data["mean_last_10"]["pressure"] == avg_pressure
    assert data["mean_last_10"]["temperature"] == avg_temperature
    assert data["mean_last_10"]["velocity"] == avg_velocity


def test_device_metadata_no_config(test_client):
    response = test_client.get("/device")
    data = response.json()

    assert data["detail"] == "No device configuration found"


def test_device_metadata_no_messages(test_client, device_config):
    response = test_client.get("/device")
    data = response.json()

    assert data["detail"] == "No sensor data records have been found"


@pytest.mark.parametrize("limit", [(2), (4), (6), (8)])
def test_message_limit_response(test_client, limit, sensor_data_records):
    response = test_client.get(f"/messages?limit={limit}")
    data = response.json()

    assert isinstance(data["messages"], list)

    assert len(data["messages"]) == limit

    for message in data["messages"]:
        assert "pressure" in message
        assert "temperature" in message
        assert "velocity" in message
        assert "timestamp" in message

    # check if the endpoint receives latest data
    timestamps = [message["timestamp"] for message in data["messages"]]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.parametrize("limit", [(0), (-1), (-20), (-100)])
def test_message_limit_response_below_zero(test_client, limit):
    response = test_client.get(f"/messages?limit={limit}")
    data = response.json()

    assert response.status_code == 400
    assert data["detail"] == "The limit number must be positive"


@pytest.mark.parametrize("limit", [(12), (22), (32), (100)])
def test_message_limit_response_invalid_limit(test_client, limit, sensor_data_records):
    # invalid limit occurs when there are less messages than limit itself
    # fixture takes 10 records
    count_messages = len(sensor_data_records)

    response = test_client.get(f"/messages?limit={limit}")
    data = response.json()

    assert response.status_code == 400
    assert data["detail"] == (
        f"Data base has less that {limit} records " f"Current value: {count_messages}"
    )


def test_start(test_client):
    response = test_client.get("/start")
    data = response.json()

    assert data["message"] == "Data streaming started"

    response = test_client.get("/status")
    data = response.json()

    assert data["streaming"] == True  # noqa: E712


def test_stop(test_client):
    response = test_client.get("/stop")
    data = response.json()

    assert data["message"] == "Data streaming stopped"

    response = test_client.get("/status")
    data = response.json()

    assert data["streaming"] == False  # noqa: E712
