import random
from typing import Type

from pydantic import BaseModel


class MeasurementModel(BaseModel):
    timestamp: float
    throttle: float
    brakes: int
    cruise_control1_mask_objects_adas: int
    car01_shift_up: int
    car01_shift_down: int
    wheel_position: float
    wheel_adas_position_kp: int
    wheel_adas_position_kd: int
    wheel_adas_velocity_kvff: int
    wheel_adas_velocity_kp: int
    wheel_adas_velocity_ki: int
    wheel_adas_max_velocity_n_max_lw: int
    wheel_adas_max_torque_m_max_lw: int
    wheel_adas_max_acceleration_a_max_lw: int
    wheel_raw_position_adas: int
    wheel_raw_torque_adas: int
    car0_vehicle_pos: float
    car0_vehicle_quat: float
    car0_vehicle_vel: float
    car0_steer_quat: float
    car0_gear: int
    car0_wheel0_pos: float
    car0_wheel0_quat: float
    car0_wheel0_rot_vel: int
    car0_caliper0_quat: float
    car0_wheel1_pos: float
    car0_wheel1_quat: float
    car0_wheel1_rot_vel: int
    car0_caliper1_quat: float
    car0_wheel2_pos: float
    car0_wheel2_quat: float
    car0_wheel2_rot_vel: int
    car0_caliper2_quat: float
    car0_wheel3_pos: float
    car0_wheel3_quat: float
    car0_wheel3_rot_vel: int
    car0_caliper3_quat: float
    car0_engine_rpm: int
    car0_rpm: int
    car0_velocity: int
    car0_velocity_vehicle: int
    car0_engine_load: int
    car0_velocity_driveline: int
    car0_throttle_position: int
    car0_brake_position: int
    car0_wheel0_skid_factor_lat: int
    car0_wheel0_skid_factor_lon: int
    car0_wheel0_surface_type: int
    car0_wheel0_surface_volume: int
    car0_wheel1_skid_factor_lat: int
    car0_wheel1_skid_factor_lon: int
    car0_wheel1_surface_type: int
    car0_wheel1_surface_volume: int
    car0_wheel2_skid_factor_lat: int
    car0_wheel2_skid_factor_lon: int
    car0_wheel2_surface_type: int
    car0_wheel2_surface_volume: int
    car0_wheel3_skid_factor_lat: int
    car0_wheel3_skid_factor_lon: int
    car0_wheel3_surface_type: int
    car0_wheel3_surface_volume: int
    car0_turbo_pressure: int
    car0_turbo_pressure_normalized: int
    car0_turbo_spindle_rpm: int
    car0_engine_torque: int
    lin_vel: float
    lin_acc: float
    rot_acc: float
    car0_engine_max_rpm: int
    engine_rpm: int
    brakes_vol: int


# Define the function to create a random instance of a Pydantic model
def create_random_instance(model: Type[BaseModel]) -> BaseModel:
    random_data = {}
    for field_name, field_type in model.__annotations__.items():
        if field_type is int:
            random_data[field_name] = random.randint(0, 1000)  # Random int in a specified range
        elif field_type is float:
            random_data[field_name] = random.uniform(0.0, 1000.0)  # Random float in a specified range
        else:
            raise ValueError(f"Unsupported field type: {field_type} for field {field_name}")
    return model(**random_data)
