import unittest

from models.measurementModel import create_random_instance, MeasurementModel


class TestCreateRandomInstance(unittest.TestCase):
    def test_create_random_instance(self):
        # Create a random instance of MeasurementModel
        instance = create_random_instance(MeasurementModel)

        # Verify that the instance is of type MeasurementModel
        self.assertIsInstance(instance, MeasurementModel)

        # Verify that all fields in the instance have valid types
        for field_name, field_type in MeasurementModel.__annotations__.items():
            field_value = getattr(instance, field_name)

            if field_type is int:
                self.assertIsInstance(field_value, int, f"Field {field_name} is not an int")
            elif field_type is float:
                self.assertIsInstance(field_value, float, f"Field {field_name} is not a float")
            else:
                self.fail(f"Unsupported field type {field_type} for field {field_name}")

        # Verify that field values are within the expected range
        for field_name, field_type in MeasurementModel.__annotations__.items():
            field_value = getattr(instance, field_name)
            if field_type is int:
                self.assertTrue(0 <= field_value <= 1000, f"Field {field_name} value out of range: {field_value}")
            elif field_type is float:
                self.assertTrue(0.0 <= field_value <= 1000.0, f"Field {field_name} value out of range: {field_value}")


if __name__ == "__main__":
    unittest.main()
