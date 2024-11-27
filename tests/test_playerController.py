import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app



@pytest.mark.anyio
async def test_load_data():
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/player/load_csv", json={"file_name": "recording_2024_04_24__12_05_33_mapping_trip_02.csv"})
        assert response.status_code == 200
        assert "CSV data source initialized from" in response.json()["message"]
        assert "recording_2024_04_24__12_05_33_mapping_trip_02.csv" in response.json()["message"]



@pytest.mark.anyio
async def test_play_loaded_data():
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/player/load_csv", json={"file_name": "recording_2024_04_24__12_05_33_mapping_trip_02.csv"})
        assert response.status_code == 200
        response = await client.post("/api/v1/player/play")
        assert response.status_code == 200
        assert "Playback started" in response.json()["message"]