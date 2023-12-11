import unittest
from fastapi.testclient import TestClient
from api import app

class TestYourAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        pass

    def test_get_main_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_force_update_endpoint(self):
        response = self.client.get("/force-update/")
        self.assertEqual(response.status_code, 200)

    def test_update_sensor_name_endpoint(self):
        sensor_id = 1
        new_name = "NouveauNom"
        response = self.client.put(f"/sensor/{sensor_id}/update-name", json={"new_name": new_name})
        self.assertEqual(response.status_code, 200)

    def test_delete_sensor_endpoint(self):
        sensor_id = 1
        response = self.client.delete(f"/sensor/{sensor_id}/delete")
        self.assertEqual(response.status_code, 200)

    def test_set_alert_endpoint(self):
        data = {
            "name": "TestAlert",
            "low_humidity": 10,
            "high_humidity": 90,
            "low_temperature": 20,
            "high_temperature": 30,
            "frequence": "daily",
            "last_send": "2023-01-01 00:00:00",
            "email": "test@example.com",
            "user_id": 1,
            "sensor_id": 1,
            "list_alerts_id": []
        }

        response = self.client.post("settings/alert/1", json=data)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()