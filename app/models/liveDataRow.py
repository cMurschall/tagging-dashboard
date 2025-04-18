import random
from dataclasses import dataclass, field, fields
from typing import Type, List, Dict, Any


@dataclass
class LiveDataRow:
    timestamp: float = field(default=0.0)
    brakes_vol: float = field(default=0.0, metadata={'panthera_name': 'brakes_vol', 'panthera_type': 'float'})
    brakes: float = field(default=0.0, metadata={'panthera_name': 'brakes', 'panthera_type': 'float'})
    car0_1shift_down: float = field(default=0.0,
                                    metadata={'panthera_name': 'car0{1}.shift_down', 'panthera_type': 'double'})
    car0_1shift_up: float = field(default=0.0,
                                  metadata={'panthera_name': 'car0{1}.shift_up', 'panthera_type': 'double'})
    car0_brake_position: float = field(default=0.0,
                                       metadata={'panthera_name': 'car0_brake_position', 'panthera_type': 'float'})
    car0_caliper0_quat: List[float] = field(default_factory=list, metadata={'panthera_name': 'car0_caliper0_quat',
                                                                            'panthera_type': 'quaternion'})
    car0_caliper1_quat: List[float] = field(default_factory=list, metadata={'panthera_name': 'car0_caliper1_quat',
                                                                            'panthera_type': 'quaternion'})
    car0_caliper2_quat: List[float] = field(default_factory=list, metadata={'panthera_name': 'car0_caliper2_quat',
                                                                            'panthera_type': 'quaternion'})
    car0_caliper3_quat: List[float] = field(default_factory=list, metadata={'panthera_name': 'car0_caliper3_quat',
                                                                            'panthera_type': 'quaternion'})
    car0_engine_load: float = field(default=0.0,
                                    metadata={'panthera_name': 'car0_engine_load', 'panthera_type': 'float'})
    car0_engine_max_rpm: float = field(default=0.0,
                                       metadata={'panthera_name': 'car0_engine_max_rpm', 'panthera_type': 'float'})
    car0_engine_rpm: float = field(default=0.0, metadata={'panthera_name': 'car0_engine_rpm', 'panthera_type': 'float'})
    car0_engine_torque: float = field(default=0.0,
                                      metadata={'panthera_name': 'car0_engine_torque', 'panthera_type': 'float'})
    car0_gear: int = field(default=0, metadata={'panthera_name': 'car0_gear', 'panthera_type': 'int'})
    car0_indicator_left_trigger: int = field(default=0, metadata={'panthera_name': 'car0_indicator_left_trigger',
                                                                  'panthera_type': 'int'})
    car0_indicator_right_trigger: int = field(default=0, metadata={'panthera_name': 'car0_indicator_right_trigger',
                                                                   'panthera_type': 'int'})
    car0_mask_objects_adas: int = field(default=0,
                                        metadata={'panthera_name': 'car0_mask_objects_adas', 'panthera_type': 'int'})
    car0_mask_objects: int = field(default=0, metadata={'panthera_name': 'car0_mask_objects', 'panthera_type': 'int'})
    car0_rpm: float = field(default=0.0, metadata={'panthera_name': 'car0_rpm', 'panthera_type': 'float'})
    car0_steer_quat: List[float] = field(default_factory=list,
                                         metadata={'panthera_name': 'car0_steer_quat', 'panthera_type': 'quaternion'})
    car0_throttle_position: float = field(default=0.0, metadata={'panthera_name': 'car0_throttle_position',
                                                                 'panthera_type': 'float'})
    car0_turbo_pressure_normalized: float = field(default=0.0,
                                                  metadata={'panthera_name': 'car0_turbo_pressure_normalized',
                                                            'panthera_type': 'float'})
    car0_turbo_pressure: float = field(default=0.0,
                                       metadata={'panthera_name': 'car0_turbo_pressure', 'panthera_type': 'double'})
    car0_turbo_spindle_rpm: float = field(default=0.0, metadata={'panthera_name': 'car0_turbo_spindle_rpm',
                                                                 'panthera_type': 'float'})
    car0_vehicle_pos: List[float] = field(default_factory=list, metadata={'panthera_name': 'car0_vehicle_pos',
                                                                          'panthera_type': 'vector3double'})
    car0_vehicle_quat: List[float] = field(default_factory=list, metadata={'panthera_name': 'car0_vehicle_quat',
                                                                           'panthera_type': 'quaternion'})
    car0_vehicle_vel: List[float] = field(default_factory=list,
                                          metadata={'panthera_name': 'car0_vehicle_vel', 'panthera_type': 'vector3'})
    car0_velocity_cc: float = field(default=0.0,
                                    metadata={'panthera_name': 'car0_velocity_cc', 'panthera_type': 'float'})
    car0_velocity_driveline: float = field(default=0.0, metadata={'panthera_name': 'car0_velocity_driveline',
                                                                  'panthera_type': 'float'})
    car0_velocity_vehicle: float = field(default=0.0,
                                         metadata={'panthera_name': 'car0_velocity_vehicle', 'panthera_type': 'float'})
    car0_velocity: float = field(default=0.0, metadata={'panthera_name': 'car0_velocity', 'panthera_type': 'float'})
    car0_wheel0_pos: List[float] = field(default_factory=list,
                                         metadata={'panthera_name': 'car0_wheel0_pos', 'panthera_type': 'vector3'})
    car0_wheel0_quat: List[float] = field(default_factory=list,
                                          metadata={'panthera_name': 'car0_wheel0_quat', 'panthera_type': 'quaternion'})
    car0_wheel0_rot_vel: float = field(default=0.0,
                                       metadata={'panthera_name': 'car0_wheel0_rot_vel', 'panthera_type': 'float'})
    car0_wheel0_skid_factor_lat: float = field(default=0.0, metadata={'panthera_name': 'car0_wheel0_skid_factor_lat',
                                                                      'panthera_type': 'float'})
    car0_wheel0_skid_factor_lon: float = field(default=0.0, metadata={'panthera_name': 'car0_wheel0_skid_factor_lon',
                                                                      'panthera_type': 'float'})
    car0_wheel0_surface_type: int = field(default=0, metadata={'panthera_name': 'car0_wheel0_surface_type',
                                                               'panthera_type': 'int'})
    car0_wheel0_surface_volume: float = field(default=0.0, metadata={'panthera_name': 'car0_wheel0_surface_volume',
                                                                     'panthera_type': 'float'})
    car0_wheel1_pos: List[float] = field(default_factory=list,
                                         metadata={'panthera_name': 'car0_wheel1_pos', 'panthera_type': 'vector3'})
    car0_wheel1_quat: List[float] = field(default_factory=list,
                                          metadata={'panthera_name': 'car0_wheel1_quat', 'panthera_type': 'quaternion'})
    car0_wheel1_rot_vel: float = field(default=0.0,
                                       metadata={'panthera_name': 'car0_wheel1_rot_vel', 'panthera_type': 'float'})
    car0_wheel1_skid_factor_lat: float = field(default=0.0, metadata={'panthera_name': 'car0_wheel1_skid_factor_lat',
                                                                      'panthera_type': 'float'})
    car0_wheel1_skid_factor_lon: float = field(default=0.0, metadata={'panthera_name': 'car0_wheel1_skid_factor_lon',
                                                                      'panthera_type': 'float'})
    car0_wheel1_surface_type: int = field(default=0, metadata={'panthera_name': 'car0_wheel1_surface_type',
                                                               'panthera_type': 'int'})
    car0_wheel1_surface_volume: float = field(default=0.0, metadata={'panthera_name': 'car0_wheel1_surface_volume',
                                                                     'panthera_type': 'float'})
    car0_wheel2_pos: List[float] = field(default_factory=list,
                                         metadata={'panthera_name': 'car0_wheel2_pos', 'panthera_type': 'vector3'})
    car0_wheel2_quat: List[float] = field(default_factory=list,
                                          metadata={'panthera_name': 'car0_wheel2_quat', 'panthera_type': 'quaternion'})
    car0_wheel2_rot_vel: float = field(default=0.0,
                                       metadata={'panthera_name': 'car0_wheel2_rot_vel', 'panthera_type': 'float'})
    car0_wheel2_skid_factor_lat: float = field(default=0.0, metadata={'panthera_name': 'car0_wheel2_skid_factor_lat',
                                                                      'panthera_type': 'float'})
    car0_wheel2_skid_factor_lon: float = field(default=0.0, metadata={'panthera_name': 'car0_wheel2_skid_factor_lon',
                                                                      'panthera_type': 'float'})
    car0_wheel2_surface_type: int = field(default=0, metadata={'panthera_name': 'car0_wheel2_surface_type',
                                                               'panthera_type': 'int'})
    car0_wheel2_surface_volume: float = field(default=0.0, metadata={'panthera_name': 'car0_wheel2_surface_volume',
                                                                     'panthera_type': 'float'})
    car0_wheel3_pos: List[float] = field(default_factory=list,
                                         metadata={'panthera_name': 'car0_wheel3_pos', 'panthera_type': 'vector3'})
    car0_wheel3_quat: List[float] = field(default_factory=list,
                                          metadata={'panthera_name': 'car0_wheel3_quat', 'panthera_type': 'quaternion'})
    car0_wheel3_rot_vel: float = field(default=0.0,
                                       metadata={'panthera_name': 'car0_wheel3_rot_vel', 'panthera_type': 'float'})
    car0_wheel3_skid_factor_lat: float = field(default=0.0, metadata={'panthera_name': 'car0_wheel3_skid_factor_lat',
                                                                      'panthera_type': 'float'})
    car0_wheel3_skid_factor_lon: float = field(default=0.0, metadata={'panthera_name': 'car0_wheel3_skid_factor_lon',
                                                                      'panthera_type': 'float'})
    car0_wheel3_surface_type: int = field(default=0, metadata={'panthera_name': 'car0_wheel3_surface_type',
                                                               'panthera_type': 'int'})
    car0_wheel3_surface_volume: float = field(default=0.0, metadata={'panthera_name': 'car0_wheel3_surface_volume',
                                                                     'panthera_type': 'float'})
    cruiseControl_1mask_objects_adas: float = field(default=0.0,
                                                    metadata={'panthera_name': 'cruiseControl{1}.mask_objects_adas',
                                                              'panthera_type': 'double'})
    engine_rpm: float = field(default=0.0, metadata={'panthera_name': 'engine_rpm', 'panthera_type': 'float'})
    lin_acc: List[float] = field(default_factory=list,
                                 metadata={'panthera_name': 'lin_acc', 'panthera_type': 'vector3'})
    lin_vel: List[float] = field(default_factory=list,
                                 metadata={'panthera_name': 'lin_vel', 'panthera_type': 'vector3'})
    rot_acc: List[float] = field(default_factory=list,
                                 metadata={'panthera_name': 'rot_acc', 'panthera_type': 'vector3'})
    rot_vel: List[float] = field(default_factory=list,
                                 metadata={'panthera_name': 'rot_vel', 'panthera_type': 'vector3'})
    throttle: float = field(default=0.0, metadata={'panthera_name': 'throttle', 'panthera_type': 'float'})
    wheel_adas_max_acceleration_a_max_LW: int = field(default=0,
                                                      metadata={'panthera_name': 'wheel_adas_max_acceleration_a_max_LW',
                                                                'panthera_type': 'int'})
    wheel_adas_max_torque_M_max_LW: int = field(default=0, metadata={'panthera_name': 'wheel_adas_max_torque_M_max_LW',
                                                                     'panthera_type': 'int'})
    wheel_adas_max_velocity_n_max_LW: int = field(default=0,
                                                  metadata={'panthera_name': 'wheel_adas_max_velocity_n_max_LW',
                                                            'panthera_type': 'int'})
    wheel_adas_position_K_D: int = field(default=0,
                                         metadata={'panthera_name': 'wheel_adas_position_K_D', 'panthera_type': 'int'})
    wheel_adas_position_K_p: int = field(default=0,
                                         metadata={'panthera_name': 'wheel_adas_position_K_p', 'panthera_type': 'int'})
    wheel_adas_velocity_K_i: int = field(default=0,
                                         metadata={'panthera_name': 'wheel_adas_velocity_K_i', 'panthera_type': 'int'})
    wheel_adas_velocity_K_p: int = field(default=0,
                                         metadata={'panthera_name': 'wheel_adas_velocity_K_p', 'panthera_type': 'int'})
    wheel_adas_velocity_K_v_FF: int = field(default=0, metadata={'panthera_name': 'wheel_adas_velocity_K_v_FF',
                                                                 'panthera_type': 'int'})
    wheel_factor_adas: float = field(default=0.0,
                                     metadata={'panthera_name': 'wheel_factor_adas', 'panthera_type': 'double'})
    wheel_position: float = field(default=0.0, metadata={'panthera_name': 'wheel_position', 'panthera_type': 'double'})
    wheel_raw_position_adas: int = field(default=0,
                                         metadata={'panthera_name': 'wheel_raw_position_adas', 'panthera_type': 'int'})
    wheel_raw_torque_adas: int = field(default=0,
                                       metadata={'panthera_name': 'wheel_raw_torque_adas', 'panthera_type': 'int'})

    @staticmethod
    def get_field_mapping():
        mapping = {
            f.metadata.get("panthera_name"): f.name
            for f in fields(LiveDataRow)
            if "panthera_name" in f.metadata
        }
        return {**mapping, 'timestamp': 'timestamp'}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LiveDataRow":
        """
        Create a LoggingRow instance from a dictionary using panthera_name metadata.
        """
        # Prepare field mapping: panthera_name -> dataclass field name
        field_mapping = LiveDataRow.get_field_mapping()

        # Prepare data for the dataclass
        parsed_data = {}
        for key, value in data.items():
            if key in field_mapping:
                field_name = field_mapping[key]
                field_type = next(
                    f for f in fields(LiveDataRow) if f.name == field_name
                ).type

                # Apply custom parsing for specific field types
                if field_type == List[float]:  # Parse lists of floats
                    parsed_data[field_name] = LiveDataRow.parse_vector(value)
                elif field_type == float:  # Parse floats
                    parsed_data[field_name] = float(value)
                elif field_type == int:  # Parse ints
                    if "." in value:  # this is an extra for car0_mask_objects
                        parsed_data[field_name] = int(float(value))
                    else:
                        parsed_data[field_name] = int(value)
                elif field_type == bool:  # Parse bool
                    parsed_data[field_name] = bool(value)
                else:  # Direct assignment for other types
                    parsed_data[field_name] = value

        # Create and return the dataclass instance
        return LiveDataRow(**parsed_data)

    @staticmethod
    def parse_vector(value: str) -> List[float]:
        return list(map(float, value.split(",")))

    @staticmethod
    def create_random_instance() -> "LiveDataRow":

        random_data = {}
        for f in fields(LiveDataRow):
            field_name = f.name
            field_type = f.type

            if field_type == int:
                random_data[field_name] = random.randint(0, 1000)  # Random int in a specified range
            elif field_type == float:
                random_data[field_name] = random.uniform(0.0, 1000.0)  # Random float in a specified range
            elif field_type == List[float]:
                random_data[field_name] = [random.uniform(0.0, 1000.0) for _ in range(3)]  # List of random floats
            else:
                raise ValueError(f"Unsupported field type: {field_type} for field {field_name}")

        return LiveDataRow(**random_data)
