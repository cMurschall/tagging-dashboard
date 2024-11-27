import random
from typing import Type, List

from pydantic import BaseModel, Field, field_validator


class MeasurementModel(BaseModel):
    cruisecontrol_1_mask_objects_adas: int = Field(alias="cruiseControl{1}.mask_objects_adas")
    car01_shift_up: int = Field(alias="car0{1}.shift_up")
    car01_shift_down: int = Field(alias="car0{1}.shift_down")
    wheel_position: float = Field(alias="wheel_position")
    wheel_adas_position_k_p: int = Field(alias="wheel_adas_position_K_p")
    wheel_adas_position_k_d: int = Field(alias="wheel_adas_position_K_D")
    wheel_adas_velocity_k_v_ff: int = Field(alias="wheel_adas_velocity_K_v_FF")
    wheel_adas_velocity_k_p: int = Field(alias="wheel_adas_velocity_K_p")
    wheel_adas_velocity_k_i: int = Field(alias="wheel_adas_velocity_K_i")
    wheel_adas_max_velocity_n_max_lw: int = Field(alias="wheel_adas_max_velocity_n_max_LW")
    wheel_adas_max_torque_m_max_lw: int = Field(alias="wheel_adas_max_torque_M_max_LW")
    wheel_adas_max_acceleration_a_max_lw: int = Field(alias="wheel_adas_max_acceleration_a_max_LW")
    wheel_raw_position_adas: int = Field(alias="wheel_raw_position_adas")
    wheel_raw_torque_adas: int = Field(alias="wheel_raw_torque_adas")
    car0_vehicle_pos: List[float] = Field(alias="car0_vehicle_pos")
    car0_vehicle_quat: List[float] = Field(alias="car0_vehicle_quat")
    car0_vehicle_vel: List[float] = Field(alias="car0_vehicle_vel")
    car0_steer_quat: List[float] = Field(alias="car0_steer_quat")
    car0_gear: int = Field(alias="car0_gear")
    car0_wheel0_pos: List[float] = Field(alias="car0_wheel0_pos")
    car0_wheel0_quat: List[float] = Field(alias="car0_wheel0_quat")
    car0_wheel0_rot_vel: int = Field(alias="car0_wheel0_rot_vel")
    car0_caliper0_quat: List[float] = Field(alias="car0_caliper0_quat")
    car0_wheel1_pos: List[float] = Field(alias="car0_wheel1_pos")
    car0_wheel1_quat: List[float] = Field(alias="car0_wheel1_quat")
    car0_wheel1_rot_vel: int = Field(alias="car0_wheel1_rot_vel")
    car0_caliper1_quat: List[float] = Field(alias="car0_caliper1_quat")
    car0_wheel2_pos: List[float] = Field(alias="car0_wheel2_pos")
    car0_wheel2_quat: List[float] = Field(alias="car0_wheel2_quat")
    car0_wheel2_rot_vel: int = Field(alias="car0_wheel2_rot_vel")
    car0_caliper2_quat: List[float] = Field(alias="car0_caliper2_quat")
    car0_wheel3_pos: List[float] = Field(alias="car0_wheel3_pos")
    car0_wheel3_quat: List[float] = Field(alias="car0_wheel3_quat")
    car0_wheel3_rot_vel: int = Field(alias="car0_wheel3_rot_vel")
    car0_caliper3_quat: List[float] = Field(alias="car0_caliper3_quat")
    car0_engine_rpm: int = Field(alias="car0_engine_rpm")
    car0_rpm: int = Field(alias="car0_rpm")
    car0_velocity: int = Field(alias="car0_velocity")
    car0_velocity_vehicle: int = Field(alias="car0_velocity_vehicle")
    car0_engine_load: int = Field(alias="car0_engine_load")
    car0_velocity_driveline: int = Field(alias="car0_velocity_driveline")
    car0_throttle_position: int = Field(alias="car0_throttle_position")
    car0_brake_position: int = Field(alias="car0_brake_position")
    car0_wheel0_skid_factor_lat: int = Field(alias="car0_wheel0_skid_factor_lat")
    car0_wheel0_skid_factor_lon: int = Field(alias="car0_wheel0_skid_factor_lon")
    car0_wheel0_surface_type: int = Field(alias="car0_wheel0_surface_type")
    car0_wheel0_surface_volume: int = Field(alias="car0_wheel0_surface_volume")
    car0_wheel1_skid_factor_lat: int = Field(alias="car0_wheel1_skid_factor_lat")
    car0_wheel1_skid_factor_lon: int = Field(alias="car0_wheel1_skid_factor_lon")
    car0_wheel1_surface_type: int = Field(alias="car0_wheel1_surface_type")
    car0_wheel1_surface_volume: int = Field(alias="car0_wheel1_surface_volume")
    car0_wheel2_skid_factor_lat: int = Field(alias="car0_wheel2_skid_factor_lat")
    car0_wheel2_skid_factor_lon: int = Field(alias="car0_wheel2_skid_factor_lon")
    car0_wheel2_surface_type: int = Field(alias="car0_wheel2_surface_type")
    car0_wheel2_surface_volume: int = Field(alias="car0_wheel2_surface_volume")
    car0_wheel3_skid_factor_lat: int = Field(alias="car0_wheel3_skid_factor_lat")
    car0_wheel3_skid_factor_lon: int = Field(alias="car0_wheel3_skid_factor_lon")
    car0_wheel3_surface_type: int = Field(alias="car0_wheel3_surface_type")
    car0_wheel3_surface_volume: int = Field(alias="car0_wheel3_surface_volume")
    car0_turbo_pressure: int = Field(alias="car0_turbo_pressure")
    car0_turbo_pressure_normalized: int = Field(alias="car0_turbo_pressure_normalized")
    car0_turbo_spindle_rpm: int = Field(alias="car0_turbo_spindle_rpm")
    car0_engine_torque: int = Field(alias="car0_engine_torque")
    lin_vel: List[float] = Field(alias="lin_vel")
    lin_acc: List[float] = Field(alias="lin_acc")
    rot_acc: List[float] = Field(alias="rot_acc")
    car0_engine_max_rpm: int = Field(alias="car0_engine_max_rpm")
    engine_rpm: int = Field(alias="engine_rpm")
    brakes: int = Field(alias="brakes")
    brakes_vol: int = Field(alias="brakes_vol")
    timestamp: float = Field(alias="timestamp")

    @staticmethod
    def parse_vector(value: str) -> List[float]:
        return list(map(float, value.split(",")))

    # Validator for vector-like fields
    @field_validator("car0_vehicle_pos","car0_vehicle_quat","car0_vehicle_vel","car0_steer_quat","car0_wheel0_pos",
        "car0_wheel0_quat","car0_caliper0_quat","car0_wheel1_pos","car0_wheel1_quat","car0_caliper1_quat","car0_wheel2_pos",
        "car0_wheel2_quat","car0_caliper2_quat","car0_wheel3_pos","car0_wheel3_quat","car0_caliper3_quat","lin_vel","lin_acc","rot_acc",mode="before")
    def validate_vector(cls, value):
        if isinstance(value, str):  # If input is a string, parse it
            return cls.parse_vector(value)
        return value  # Otherwise, return the value as-is


# Define the function to create a random instance of a Pydantic model
def create_random_instance2(model: Type[BaseModel]) -> BaseModel:
    random_data = {}
    for field_name, field_type in model.__annotations__.items():
        if field_type is int:
            random_data[field_name] = random.randint(0, 1000)  # Random int in a specified range
        elif field_type is float:
            random_data[field_name] = random.uniform(0.0, 1000.0)  # Random float in a specified range
        elif field_type is List[float]:
            random_data[field_name] = [random.uniform(0.0, 1000.0) for _ in range(3)]
        else:
            raise ValueError(f"Unsupported field type: {field_type} for field {field_name}")
    return model(**random_data)


def create_random_instance(model: Type[BaseModel]) -> BaseModel:
    random_data = {}
    for field_name, field_type in model.__annotations__.items():
        field_alias = model.model_fields[field_name].alias  # Get the alias of the field
        if field_type is int:
            random_data[field_alias] = random.randint(0, 1000)  # Random int in a specified range
        elif field_type is float:
            random_data[field_alias] = random.uniform(0.0, 1000.0)  # Random float in a specified range
        elif field_type is List[float]:
            random_data[field_alias] = [random.uniform(0.0, 1000.0) for _ in range(3)]
        else:
            raise ValueError(f"Unsupported field type: {field_type} for field {field_name}")
    return model(**random_data)
