import random
from dataclasses import dataclass, field, fields
from typing import List

get_float = lambda x: float(x.GetFloat()) if x else 0.0
get_double = lambda x: float(x.GetDouble()) if x else 0.0
get_int = lambda x: int(x.GetInt())
get_quaternion = lambda x: [float(y) for y in x.GetQuaternion(0.0, 0.0)] if x else [0.0, 0.0, 0.0, 1.0]
get_vector3 = lambda x: [float(y) for y in x.GetVector3(0.0, 0.0)] if x else [0.0, 0.0, 0.0]
get_vector3d_double = lambda x: [float(y) for y in x.GetVector3Double(0.0, 0.0)] if x else [0.0, 0.0, 0.0]

FIELD_NAME_MAP = [
    ("brakes_vol", get_float),
    ("brakes", get_float),
    ("Car_Status{1}.Car_Status", None),
    ("car0_brake_position", get_float),
    ("car0_caliper0_quat", get_quaternion),
    ("car0_caliper1_quat", get_quaternion),
    ("car0_caliper2_quat", get_quaternion),
    ("car0_caliper3_quat", get_quaternion),
    ("car0_engine_load", get_float),
    ("car0_engine_max_rpm", get_float),
    ("car0_engine_rpm", get_float),
    ("car0_engine_torque", get_float),
    ("car0_gear", get_int),
    ("car0_indicator_left_trigger", get_int),
    ("car0_indicator_right_trigger", get_int),
    ("car0_mask_objects_adas", get_int),
    ("car0_mask_objects", get_int),
    ("car0_rpm", get_float),
    ("car0_steer_quat", get_quaternion),
    ("car0_throttle_position", get_float),
    ("car0_turbo_pressure_normalized", get_float),
    ("car0_turbo_pressure", get_double),
    ("car0_turbo_spindle_rpm", get_float),
    ("car0_vehicle_pos", get_vector3d_double),
    ("car0_vehicle_quat", get_quaternion),
    ("car0_vehicle_vel", get_vector3),
    ("car0_velocity_cc", get_float),
    ("car0_velocity_driveline", get_float),
    ("car0_velocity_vehicle", get_float),
    ("car0_velocity", get_float),
    ("car0_wheel0_pos", get_vector3),
    ("car0_wheel0_quat", get_quaternion),
    ("car0_wheel0_rot_vel", get_float),
    ("car0_wheel0_skid_factor_lat", get_float),
    ("car0_wheel0_skid_factor_lon", get_float),
    ("car0_wheel0_surface_type", get_int),
    ("car0_wheel0_surface_volume", get_float),
    ("car0_wheel1_pos", get_vector3),
    ("car0_wheel1_quat", get_quaternion),
    ("car0_wheel1_rot_vel", get_float),
    ("car0_wheel1_skid_factor_lat", get_float),
    ("car0_wheel1_skid_factor_lon", get_float),
    ("car0_wheel1_surface_type", get_int),
    ("car0_wheel1_surface_volume", get_float),
    ("car0_wheel2_pos", get_vector3),
    ("car0_wheel2_quat", get_quaternion),
    ("car0_wheel2_rot_vel", get_float),
    ("car0_wheel2_skid_factor_lat", get_float),
    ("car0_wheel2_skid_factor_lon", get_float),
    ("car0_wheel2_surface_type", get_int),
    ("car0_wheel2_surface_volume", get_float),
    ("car0_wheel3_pos", get_vector3),
    ("car0_wheel3_quat", get_quaternion),
    ("car0_wheel3_rot_vel", get_float),
    ("car0_wheel3_skid_factor_lat", get_float),
    ("car0_wheel3_skid_factor_lon", get_float),
    ("car0_wheel3_surface_type", get_int),
    ("car0_wheel3_surface_volume", get_float),
    ("car0{1}.shift_down", get_double),
    ("car0{1}.shift_up", get_double),
    ("CL01_DampingFwd", None),
    ("CL01_ForceInputFwd", None),
    ("CL01_FrictionFwd", None),
    ("CL01_PosDemFwd", None),
    ("cruiseControl{1}.mask_objects_adas", get_double),
    ("engine_rpm", get_float),
    ("engine_vol", None),
    ("Error_Suppression{1}.Error_Suppression", None),
    ("Gear_Selector_LEDs{1}.LEDs", None),
    ("Gear_Selector{1}.Buttons_Gearselector", None),
    ("Gear_Selector{1}.Shift_Gearselector", None),
    ("kerbs_vol", None),
    ("kerbs", None),
    ("lights{1}.mask_objects", None),
    ("lin_acc", get_vector3),
    ("lin_vel", get_vector3),
    ("Multiswitch{1}.Horn", None),
    ("Multiswitch{1}.Lane_Departure_Warning", None),
    ("Multiswitch{1}.Light_Switch", None),
    ("Multiswitch{1}.Wiper_Interval", None),
    ("Multiswitch{1}.Wiper_Status", None),
    ("Multiswitch{1}.Wiper_Washer", None),
    ("ntc_time_offset", None),
    ("quat", None),
    ("road_noise_vol", None),
    ("road_noise", None),
    ("rot_acc", get_vector3),
    ("rot_vel", get_vector3),
    ("Shift_CC{1}.CC1", None),
    ("Shift_CC{1}.CC2", None),
    ("Shift_CC{1}.Shift_Paddles", None),
    ("shift_down", None),
    ("shift_up", None),
    ("sim_time", None),
    ("steer_angle", None),
    ("Steering_Wheel_Buttons{1}.Wheel_Buttons", None),
    ("throttle", get_float),
    ("wheel_actual_desired_position", None),
    ("wheel_actual_desired_torque", None),
    ("wheel_adas_max_acceleration_a_max_LW", get_int),
    ("wheel_adas_max_torque_M_max_LW", get_int),
    ("wheel_adas_max_velocity_n_max_LW", get_int),
    ("wheel_adas_position_K_D", get_int),
    ("wheel_adas_position_K_p", get_int),
    ("wheel_adas_velocity_K_i", get_int),
    ("wheel_adas_velocity_K_p", get_int),
    ("wheel_adas_velocity_K_v_FF", get_int),
    ("wheel_analog_input1", None),
    ("wheel_analog_input2", None),
    ("wheel_analog_input3", None),
    ("wheel_desired_position", None),
    ("wheel_digital_inputs", None),
    ("wheel_factor_adas", get_double),
    ("wheel_factor_senso_wheel", None),
    ("wheel_position", get_double),
    ("wheel_raw_encoder_index", None),
    ("wheel_raw_end_stop", None),
    ("wheel_raw_error", None),
    ("wheel_raw_position_adas", get_int),
    ("wheel_raw_position", None),
    ("wheel_raw_status", None),
    ("wheel_raw_torque_adas", get_int),
    ("wheel_raw_torque_senso", None),
    ("wheel_raw_torque", None),
    ("wheel_raw_velocity", None),
    ("world_camera_pos", None),
    ("world_camera_quat", None),
]


def create_random_instance(field_map, generator_map):
    random_instance = {}

    for name, generator in field_map:
        if generator is None:
            continue
        if generator == get_float:
            value = random.uniform(-1000.0, 1000.0)
        elif generator == get_double:
            value = random.uniform(-1e6, 1e6)
        elif generator == get_int:
            value = random.randint(-1000, 1000)
        elif generator == get_quaternion:
            value = [random.uniform(-1, 1) for _ in range(4)]
        elif generator == get_vector3 or generator == get_vector3d_double:
            value = [random.uniform(-1000.0, 1000.0) for _ in range(3)]
        else:
            # fallback, in case generator is unknown
            value = None
        random_instance[name] = value
        
    return random_instance
