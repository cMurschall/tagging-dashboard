from asyncio import Event

import panthera as pt
from dataclasses import asdict, dataclass, field, fields
from typing import Type, List, Dict, Any

import sys
import math
import time
import re
import csv


def process_panthera(stop_event: Event):
    while not stop_event.is_set():
        # todo:
        # 1) get the latest value from the simulator
        # 2) send the value via websocket to the frontend
        sleep_with_event(stop_event, 1)


def sleep_with_event(stop_event, duration):
    """
    Sleeps for the specified duration in small intervals,
    checking the stop_event to terminate early.
    """
    interval = 0.1  # Check every 0.1 seconds
    elapsed = 0
    while elapsed < duration:
        if stop_event.is_set():
            break
        time.sleep(interval)
        elapsed += interval


@dataclass
class MeasurementModel:
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


class Process(pt.Process):
    """ The process class handles all communication with the simulator. """

    def __init__(self, sdk):
        """ Constructor """
        super().__init__(sdk, sys.argv)
        # Step at 10Hz
        self.step = 0.1
        self.SetWaitTimeout(self.step)
        self.t = None
        self.counter = 0
        self.prevState = "stopped"

        self.field_dict = {}

        self.operator = pt.Operator(sdk, "tagging-dashboard")
        self.operator.Connect(self.GetMqttBrokerHostname(), "operator", "operator")
        assert self.operator.IsConnected()

        # Manually send the signals (to reduce latency, send them as soon as their values are set)
        # Done with the `self.SendSignals()` call
        self.StepHandlesSendSignals(False)

        # Add a single field the process sends out
        ns = self.GetNamedStructInterfaceFromProcess().GetNamedStruct()
        # Initialize the field we expect to receive
        self.receive_field = False
        self.rf = ["steer_angle", "car0_gear", "speed", "lin_acc"]

        self.has_written_header = False

    def Run(self):
        """ Main function """
        while self.GetState() != pt.ProcessState_Offline:
            self.Step()

    def ReadSignals(self):
        if self.GetState() != pt.ProcessState_Run: return
        model = MeasurementModel()
        Process.safe_assign(model, "brakes_vol", self.field_dict["brakes_vol"], lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "brakes", self.field_dict["brakes"], lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_brake_position", self.field_dict["car0_brake_position"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_caliper0_quat", self.field_dict["car0_caliper0_quat"],
                            lambda x: [float(y) for y in x.GetQuaternion(0.0, 0.0)])
        Process.safe_assign(model, "car0_caliper1_quat", self.field_dict["car0_caliper1_quat"],
                            lambda x: [float(y) for y in x.GetQuaternion(0.0, 0.0)])
        Process.safe_assign(model, "car0_caliper2_quat", self.field_dict["car0_caliper2_quat"],
                            lambda x: [float(y) for y in x.GetQuaternion(0.0, 0.0)])
        Process.safe_assign(model, "car0_caliper3_quat", self.field_dict["car0_caliper3_quat"],
                            lambda x: [float(y) for y in x.GetQuaternion(0.0, 0.0)])
        Process.safe_assign(model, "car0_engine_load", self.field_dict["car0_engine_load"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_engine_max_rpm", self.field_dict["car0_engine_max_rpm"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_engine_rpm", self.field_dict["car0_engine_rpm"], lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_engine_torque", self.field_dict["car0_engine_torque"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_gear", self.field_dict["car0_gear"], lambda x: int(x.GetInt()))
        Process.safe_assign(model, "car0_indicator_left_trigger", self.field_dict["car0_indicator_left_trigger"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "car0_indicator_right_trigger", self.field_dict["car0_indicator_right_trigger"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "car0_mask_objects_adas", self.field_dict["car0_mask_objects_adas"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "car0_mask_objects", self.field_dict["car0_mask_objects"], lambda x: int(x.GetInt()))
        Process.safe_assign(model, "car0_rpm", self.field_dict["car0_rpm"], lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_steer_quat", self.field_dict["car0_steer_quat"],
                            lambda x: [float(y) for y in x.GetQuaternion(0.0, 0.0)])
        Process.safe_assign(model, "car0_throttle_position", self.field_dict["car0_throttle_position"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_turbo_pressure_normalized", self.field_dict["car0_turbo_pressure_normalized"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_turbo_pressure", self.field_dict["car0_turbo_pressure"],
                            lambda x: float(x.GetDouble()))
        Process.safe_assign(model, "car0_turbo_spindle_rpm", self.field_dict["car0_turbo_spindle_rpm"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_vehicle_pos", self.field_dict["car0_vehicle_pos"],
                            lambda x: [float(y) for y in x.GetVector3Double(0.0, 0.0)])
        Process.safe_assign(model, "car0_vehicle_quat", self.field_dict["car0_vehicle_quat"],
                            lambda x: [float(y) for y in x.GetQuaternion(0.0, 0.0)])
        Process.safe_assign(model, "car0_vehicle_vel", self.field_dict["car0_vehicle_vel"],
                            lambda x: [float(y) for y in x.GetVector3(0.0, 0.0)])
        Process.safe_assign(model, "car0_velocity_cc", self.field_dict["car0_velocity_cc"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_velocity_driveline", self.field_dict["car0_velocity_driveline"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_velocity_vehicle", self.field_dict["car0_velocity_vehicle"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_velocity", self.field_dict["car0_velocity"], lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel0_pos", self.field_dict["car0_wheel0_pos"],
                            lambda x: [float(y) for y in x.GetVector3(0.0, 0.0)])
        Process.safe_assign(model, "car0_wheel0_quat", self.field_dict["car0_wheel0_quat"],
                            lambda x: [float(y) for y in x.GetQuaternion(0.0, 0.0)])
        Process.safe_assign(model, "car0_wheel0_rot_vel", self.field_dict["car0_wheel0_rot_vel"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel0_skid_factor_lat", self.field_dict["car0_wheel0_skid_factor_lat"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel0_skid_factor_lon", self.field_dict["car0_wheel0_skid_factor_lon"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel0_surface_type", self.field_dict["car0_wheel0_surface_type"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "car0_wheel0_surface_volume", self.field_dict["car0_wheel0_surface_volume"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel1_pos", self.field_dict["car0_wheel1_pos"],
                            lambda x: [float(y) for y in x.GetVector3(0.0, 0.0)])
        Process.safe_assign(model, "car0_wheel1_quat", self.field_dict["car0_wheel1_quat"],
                            lambda x: [float(y) for y in x.GetQuaternion(0.0, 0.0)])
        Process.safe_assign(model, "car0_wheel1_rot_vel", self.field_dict["car0_wheel1_rot_vel"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel1_skid_factor_lat", self.field_dict["car0_wheel1_skid_factor_lat"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel1_skid_factor_lon", self.field_dict["car0_wheel1_skid_factor_lon"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel1_surface_type", self.field_dict["car0_wheel1_surface_type"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "car0_wheel1_surface_volume", self.field_dict["car0_wheel1_surface_volume"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel2_pos", self.field_dict["car0_wheel2_pos"],
                            lambda x: [float(y) for y in x.GetVector3(0.0, 0.0)])
        Process.safe_assign(model, "car0_wheel2_quat", self.field_dict["car0_wheel2_quat"],
                            lambda x: [float(y) for y in x.GetQuaternion(0.0, 0.0)])
        Process.safe_assign(model, "car0_wheel2_rot_vel", self.field_dict["car0_wheel2_rot_vel"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel2_skid_factor_lat", self.field_dict["car0_wheel2_skid_factor_lat"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel2_skid_factor_lon", self.field_dict["car0_wheel2_skid_factor_lon"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel2_surface_type", self.field_dict["car0_wheel2_surface_type"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "car0_wheel2_surface_volume", self.field_dict["car0_wheel2_surface_volume"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel3_pos", self.field_dict["car0_wheel3_pos"],
                            lambda x: [float(y) for y in x.GetVector3(0.0, 0.0)])
        Process.safe_assign(model, "car0_wheel3_quat", self.field_dict["car0_wheel3_quat"],
                            lambda x: [float(y) for y in x.GetQuaternion(0.0, 0.0)])
        Process.safe_assign(model, "car0_wheel3_rot_vel", self.field_dict["car0_wheel3_rot_vel"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel3_skid_factor_lat", self.field_dict["car0_wheel3_skid_factor_lat"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel3_skid_factor_lon", self.field_dict["car0_wheel3_skid_factor_lon"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_wheel3_surface_type", self.field_dict["car0_wheel3_surface_type"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "car0_wheel3_surface_volume", self.field_dict["car0_wheel3_surface_volume"],
                            lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "car0_1shift_down", self.field_dict["car0{1}.shift_down"],
                            lambda x: float(x.GetDouble()))
        Process.safe_assign(model, "car0_1shift_up", self.field_dict["car0{1}.shift_up"],
                            lambda x: float(x.GetDouble()))
        Process.safe_assign(model, "cruiseControl_1mask_objects_adas",
                            self.field_dict["cruiseControl{1}.mask_objects_adas"], lambda x: float(x.GetDouble()))
        Process.safe_assign(model, "engine_rpm", self.field_dict["engine_rpm"], lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "lin_acc", self.field_dict["lin_acc"],
                            lambda x: [float(y) for y in x.GetVector3(0.0, 0.0)])
        Process.safe_assign(model, "lin_vel", self.field_dict["lin_vel"],
                            lambda x: [float(y) for y in x.GetVector3(0.0, 0.0)])
        Process.safe_assign(model, "rot_acc", self.field_dict["rot_acc"],
                            lambda x: [float(y) for y in x.GetVector3(0.0, 0.0)])
        Process.safe_assign(model, "rot_vel", self.field_dict["rot_vel"],
                            lambda x: [float(y) for y in x.GetVector3(0.0, 0.0)])
        Process.safe_assign(model, "throttle", self.field_dict["throttle"], lambda x: float(x.GetFloat()))
        Process.safe_assign(model, "wheel_adas_max_acceleration_a_max_LW",
                            self.field_dict["wheel_adas_max_acceleration_a_max_LW"], lambda x: int(x.GetInt()))
        Process.safe_assign(model, "wheel_adas_max_torque_M_max_LW", self.field_dict["wheel_adas_max_torque_M_max_LW"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "wheel_adas_max_velocity_n_max_LW",
                            self.field_dict["wheel_adas_max_velocity_n_max_LW"], lambda x: int(x.GetInt()))
        Process.safe_assign(model, "wheel_adas_position_K_D", self.field_dict["wheel_adas_position_K_D"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "wheel_adas_position_K_p", self.field_dict["wheel_adas_position_K_p"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "wheel_adas_velocity_K_i", self.field_dict["wheel_adas_velocity_K_i"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "wheel_adas_velocity_K_p", self.field_dict["wheel_adas_velocity_K_p"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "wheel_adas_velocity_K_v_FF", self.field_dict["wheel_adas_velocity_K_v_FF"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "wheel_factor_adas", self.field_dict["wheel_factor_adas"],
                            lambda x: float(x.GetDouble()))
        Process.safe_assign(model, "wheel_position", self.field_dict["wheel_position"], lambda x: float(x.GetDouble()))
        Process.safe_assign(model, "wheel_raw_position_adas", self.field_dict["wheel_raw_position_adas"],
                            lambda x: int(x.GetInt()))
        Process.safe_assign(model, "wheel_raw_torque_adas", self.field_dict["wheel_raw_torque_adas"],
                            lambda x: int(x.GetInt()))

        with open("log.csv", mode='w') as f:
            writer = csv.DictWriter(f, fieldnames=[field for field in MeasurementModel.__annotations__])
            if not self.has_written_header:
                self.has_written_header = True
                writer.writeheader()
            writer.writerow(asdict(model))  # Convert dataclass instance to dictionary

    def FindFields(self):
        ns = self.GetNamedStructInterfaceToProcess().GetNamedStruct()
        """ ns = self.GetNamedStructInterfaceToProcess().GetNamedStruct()
        with open("fields.txt", "w") as file:
            print(ns.ListFields(","), file=file) """

        self.field_dict["brakes_vol"] = Process.findFieldChecked('brakes_vol', ns)
        self.field_dict["brakes"] = Process.findFieldChecked('brakes', ns)
        self.field_dict["Car_Status{1}.Car_Status"] = Process.findFieldChecked('Car_Status{1}.Car_Status', ns)
        self.field_dict["car0_brake_position"] = Process.findFieldChecked('car0_brake_position', ns)
        self.field_dict["car0_caliper0_quat"] = Process.findFieldChecked('car0_caliper0_quat', ns)
        self.field_dict["car0_caliper1_quat"] = Process.findFieldChecked('car0_caliper1_quat', ns)
        self.field_dict["car0_caliper2_quat"] = Process.findFieldChecked('car0_caliper2_quat', ns)
        self.field_dict["car0_caliper3_quat"] = Process.findFieldChecked('car0_caliper3_quat', ns)
        self.field_dict["car0_engine_load"] = Process.findFieldChecked('car0_engine_load', ns)
        self.field_dict["car0_engine_max_rpm"] = Process.findFieldChecked('car0_engine_max_rpm', ns)
        self.field_dict["car0_engine_rpm"] = Process.findFieldChecked('car0_engine_rpm', ns)
        self.field_dict["car0_engine_torque"] = Process.findFieldChecked('car0_engine_torque', ns)
        self.field_dict["car0_gear"] = Process.findFieldChecked('car0_gear', ns)
        self.field_dict["car0_indicator_left_trigger"] = Process.findFieldChecked('car0_indicator_left_trigger', ns)
        self.field_dict["car0_indicator_right_trigger"] = Process.findFieldChecked('car0_indicator_right_trigger', ns)
        self.field_dict["car0_mask_objects_adas"] = Process.findFieldChecked('car0_mask_objects_adas', ns)
        self.field_dict["car0_mask_objects"] = Process.findFieldChecked('car0_mask_objects', ns)
        self.field_dict["car0_rpm"] = Process.findFieldChecked('car0_rpm', ns)
        self.field_dict["car0_steer_quat"] = Process.findFieldChecked('car0_steer_quat', ns)
        self.field_dict["car0_throttle_position"] = Process.findFieldChecked('car0_throttle_position', ns)
        self.field_dict["car0_turbo_pressure_normalized"] = Process.findFieldChecked('car0_turbo_pressure_normalized',
                                                                                     ns)
        self.field_dict["car0_turbo_pressure"] = Process.findFieldChecked('car0_turbo_pressure', ns)
        self.field_dict["car0_turbo_spindle_rpm"] = Process.findFieldChecked('car0_turbo_spindle_rpm', ns)
        self.field_dict["car0_vehicle_pos"] = Process.findFieldChecked('car0_vehicle_pos', ns)
        self.field_dict["car0_vehicle_quat"] = Process.findFieldChecked('car0_vehicle_quat', ns)
        self.field_dict["car0_vehicle_vel"] = Process.findFieldChecked('car0_vehicle_vel', ns)
        self.field_dict["car0_velocity_cc"] = Process.findFieldChecked('car0_velocity_cc', ns)
        self.field_dict["car0_velocity_driveline"] = Process.findFieldChecked('car0_velocity_driveline', ns)
        self.field_dict["car0_velocity_vehicle"] = Process.findFieldChecked('car0_velocity_vehicle', ns)
        self.field_dict["car0_velocity"] = Process.findFieldChecked('car0_velocity', ns)
        self.field_dict["car0_wheel0_pos"] = Process.findFieldChecked('car0_wheel0_pos', ns)
        self.field_dict["car0_wheel0_quat"] = Process.findFieldChecked('car0_wheel0_quat', ns)
        self.field_dict["car0_wheel0_rot_vel"] = Process.findFieldChecked('car0_wheel0_rot_vel', ns)
        self.field_dict["car0_wheel0_skid_factor_lat"] = Process.findFieldChecked('car0_wheel0_skid_factor_lat', ns)
        self.field_dict["car0_wheel0_skid_factor_lon"] = Process.findFieldChecked('car0_wheel0_skid_factor_lon', ns)
        self.field_dict["car0_wheel0_surface_type"] = Process.findFieldChecked('car0_wheel0_surface_type', ns)
        self.field_dict["car0_wheel0_surface_volume"] = Process.findFieldChecked('car0_wheel0_surface_volume', ns)
        self.field_dict["car0_wheel1_pos"] = Process.findFieldChecked('car0_wheel1_pos', ns)
        self.field_dict["car0_wheel1_quat"] = Process.findFieldChecked('car0_wheel1_quat', ns)
        self.field_dict["car0_wheel1_rot_vel"] = Process.findFieldChecked('car0_wheel1_rot_vel', ns)
        self.field_dict["car0_wheel1_skid_factor_lat"] = Process.findFieldChecked('car0_wheel1_skid_factor_lat', ns)
        self.field_dict["car0_wheel1_skid_factor_lon"] = Process.findFieldChecked('car0_wheel1_skid_factor_lon', ns)
        self.field_dict["car0_wheel1_surface_type"] = Process.findFieldChecked('car0_wheel1_surface_type', ns)
        self.field_dict["car0_wheel1_surface_volume"] = Process.findFieldChecked('car0_wheel1_surface_volume', ns)
        self.field_dict["car0_wheel2_pos"] = Process.findFieldChecked('car0_wheel2_pos', ns)
        self.field_dict["car0_wheel2_quat"] = Process.findFieldChecked('car0_wheel2_quat', ns)
        self.field_dict["car0_wheel2_rot_vel"] = Process.findFieldChecked('car0_wheel2_rot_vel', ns)
        self.field_dict["car0_wheel2_skid_factor_lat"] = Process.findFieldChecked('car0_wheel2_skid_factor_lat', ns)
        self.field_dict["car0_wheel2_skid_factor_lon"] = Process.findFieldChecked('car0_wheel2_skid_factor_lon', ns)
        self.field_dict["car0_wheel2_surface_type"] = Process.findFieldChecked('car0_wheel2_surface_type', ns)
        self.field_dict["car0_wheel2_surface_volume"] = Process.findFieldChecked('car0_wheel2_surface_volume', ns)
        self.field_dict["car0_wheel3_pos"] = Process.findFieldChecked('car0_wheel3_pos', ns)
        self.field_dict["car0_wheel3_quat"] = Process.findFieldChecked('car0_wheel3_quat', ns)
        self.field_dict["car0_wheel3_rot_vel"] = Process.findFieldChecked('car0_wheel3_rot_vel', ns)
        self.field_dict["car0_wheel3_skid_factor_lat"] = Process.findFieldChecked('car0_wheel3_skid_factor_lat', ns)
        self.field_dict["car0_wheel3_skid_factor_lon"] = Process.findFieldChecked('car0_wheel3_skid_factor_lon', ns)
        self.field_dict["car0_wheel3_surface_type"] = Process.findFieldChecked('car0_wheel3_surface_type', ns)
        self.field_dict["car0_wheel3_surface_volume"] = Process.findFieldChecked('car0_wheel3_surface_volume', ns)
        self.field_dict["car0{1}.shift_down"] = Process.findFieldChecked('car0{1}.shift_down', ns)
        self.field_dict["car0{1}.shift_up"] = Process.findFieldChecked('car0{1}.shift_up', ns)
        self.field_dict["CL01_DampingFwd"] = Process.findFieldChecked('CL01_DampingFwd', ns)
        self.field_dict["CL01_ForceInputFwd"] = Process.findFieldChecked('CL01_ForceInputFwd', ns)
        self.field_dict["CL01_FrictionFwd"] = Process.findFieldChecked('CL01_FrictionFwd', ns)
        self.field_dict["CL01_PosDemFwd"] = Process.findFieldChecked('CL01_PosDemFwd', ns)
        self.field_dict["cruiseControl{1}.mask_objects_adas"] = Process.findFieldChecked(
            'cruiseControl{1}.mask_objects_adas', ns)
        self.field_dict["engine_rpm"] = Process.findFieldChecked('engine_rpm', ns)
        self.field_dict["engine_vol"] = Process.findFieldChecked('engine_vol', ns)
        self.field_dict["Error_Suppression{1}.Error_Suppression"] = Process.findFieldChecked(
            'Error_Suppression{1}.Error_Suppression', ns)
        self.field_dict["Gear_Selector_LEDs{1}.LEDs"] = Process.findFieldChecked('Gear_Selector_LEDs{1}.LEDs', ns)
        self.field_dict["Gear_Selector{1}.Buttons_Gearselector"] = Process.findFieldChecked(
            'Gear_Selector{1}.Buttons_Gearselector', ns)
        self.field_dict["Gear_Selector{1}.Shift_Gearselector"] = Process.findFieldChecked(
            'Gear_Selector{1}.Shift_Gearselector', ns)
        self.field_dict["kerbs_vol"] = Process.findFieldChecked('kerbs_vol', ns)
        self.field_dict["kerbs"] = Process.findFieldChecked('kerbs', ns)
        self.field_dict["lights{1}.mask_objects"] = Process.findFieldChecked('lights{1}.mask_objects', ns)
        self.field_dict["lin_acc"] = Process.findFieldChecked('lin_acc', ns)
        self.field_dict["lin_vel"] = Process.findFieldChecked('lin_vel', ns)
        self.field_dict["Multiswitch{1}.Horn"] = Process.findFieldChecked('Multiswitch{1}.Horn', ns)
        self.field_dict["Multiswitch{1}.Lane_Departure_Warning"] = Process.findFieldChecked(
            'Multiswitch{1}.Lane_Departure_Warning', ns)
        self.field_dict["Multiswitch{1}.Light_Switch"] = Process.findFieldChecked('Multiswitch{1}.Light_Switch', ns)
        self.field_dict["Multiswitch{1}.Wiper_Interval"] = Process.findFieldChecked('Multiswitch{1}.Wiper_Interval', ns)
        self.field_dict["Multiswitch{1}.Wiper_Status"] = Process.findFieldChecked('Multiswitch{1}.Wiper_Status', ns)
        self.field_dict["Multiswitch{1}.Wiper_Washer"] = Process.findFieldChecked('Multiswitch{1}.Wiper_Washer', ns)
        self.field_dict["ntc_time_offset"] = Process.findFieldChecked('ntc_time_offset', ns)
        self.field_dict["quat"] = Process.findFieldChecked('quat', ns)
        self.field_dict["road_noise_vol"] = Process.findFieldChecked('road_noise_vol', ns)
        self.field_dict["road_noise"] = Process.findFieldChecked('road_noise', ns)
        self.field_dict["rot_acc"] = Process.findFieldChecked('rot_acc', ns)
        self.field_dict["rot_vel"] = Process.findFieldChecked('rot_vel', ns)
        self.field_dict["Shift_CC{1}.CC1"] = Process.findFieldChecked('Shift_CC{1}.CC1', ns)
        self.field_dict["Shift_CC{1}.CC2"] = Process.findFieldChecked('Shift_CC{1}.CC2', ns)
        self.field_dict["Shift_CC{1}.Shift_Paddles"] = Process.findFieldChecked('Shift_CC{1}.Shift_Paddles', ns)
        self.field_dict["shift_down"] = Process.findFieldChecked('shift_down', ns)
        self.field_dict["shift_up"] = Process.findFieldChecked('shift_up', ns)
        self.field_dict["sim_time"] = Process.findFieldChecked('sim_time', ns)
        self.field_dict["steer_angle"] = Process.findFieldChecked('steer_angle', ns)
        self.field_dict["Steering_Wheel_Buttons{1}.Wheel_Buttons"] = Process.findFieldChecked(
            'Steering_Wheel_Buttons{1}.Wheel_Buttons', ns)
        self.field_dict["throttle"] = Process.findFieldChecked('throttle', ns)
        self.field_dict["wheel_actual_desired_position"] = Process.findFieldChecked('wheel_actual_desired_position', ns)
        self.field_dict["wheel_actual_desired_torque"] = Process.findFieldChecked('wheel_actual_desired_torque', ns)
        self.field_dict["wheel_adas_max_acceleration_a_max_LW"] = Process.findFieldChecked(
            'wheel_adas_max_acceleration_a_max_LW', ns)
        self.field_dict["wheel_adas_max_torque_M_max_LW"] = Process.findFieldChecked('wheel_adas_max_torque_M_max_LW',
                                                                                     ns)
        self.field_dict["wheel_adas_max_velocity_n_max_LW"] = Process.findFieldChecked(
            'wheel_adas_max_velocity_n_max_LW', ns)
        self.field_dict["wheel_adas_position_K_D"] = Process.findFieldChecked('wheel_adas_position_K_D', ns)
        self.field_dict["wheel_adas_position_K_p"] = Process.findFieldChecked('wheel_adas_position_K_p', ns)
        self.field_dict["wheel_adas_velocity_K_i"] = Process.findFieldChecked('wheel_adas_velocity_K_i', ns)
        self.field_dict["wheel_adas_velocity_K_p"] = Process.findFieldChecked('wheel_adas_velocity_K_p', ns)
        self.field_dict["wheel_adas_velocity_K_v_FF"] = Process.findFieldChecked('wheel_adas_velocity_K_v_FF', ns)
        self.field_dict["wheel_analog_input1"] = Process.findFieldChecked('wheel_analog_input1', ns)
        self.field_dict["wheel_analog_input2"] = Process.findFieldChecked('wheel_analog_input2', ns)
        self.field_dict["wheel_analog_input3"] = Process.findFieldChecked('wheel_analog_input3', ns)
        self.field_dict["wheel_desired_position"] = Process.findFieldChecked('wheel_desired_position', ns)
        self.field_dict["wheel_digital_inputs"] = Process.findFieldChecked('wheel_digital_inputs', ns)
        self.field_dict["wheel_factor_adas"] = Process.findFieldChecked('wheel_factor_adas', ns)
        self.field_dict["wheel_factor_senso_wheel"] = Process.findFieldChecked('wheel_factor_senso_wheel', ns)
        self.field_dict["wheel_position"] = Process.findFieldChecked('wheel_position', ns)
        self.field_dict["wheel_raw_encoder_index"] = Process.findFieldChecked('wheel_raw_encoder_index', ns)
        self.field_dict["wheel_raw_end_stop"] = Process.findFieldChecked('wheel_raw_end_stop', ns)
        self.field_dict["wheel_raw_error"] = Process.findFieldChecked('wheel_raw_error', ns)
        self.field_dict["wheel_raw_position_adas"] = Process.findFieldChecked('wheel_raw_position_adas', ns)
        self.field_dict["wheel_raw_position"] = Process.findFieldChecked('wheel_raw_position', ns)
        self.field_dict["wheel_raw_status"] = Process.findFieldChecked('wheel_raw_status', ns)
        self.field_dict["wheel_raw_torque_adas"] = Process.findFieldChecked('wheel_raw_torque_adas', ns)
        self.field_dict["wheel_raw_torque_senso"] = Process.findFieldChecked('wheel_raw_torque_senso', ns)
        self.field_dict["wheel_raw_torque"] = Process.findFieldChecked('wheel_raw_torque', ns)
        self.field_dict["wheel_raw_velocity"] = Process.findFieldChecked('wheel_raw_velocity', ns)
        self.field_dict["world_camera_pos"] = Process.findFieldChecked('world_camera_pos', ns)
        self.field_dict["world_camera_quat"] = Process.findFieldChecked('world_camera_quat', ns)

        keys_with_none = [key for key, value in self.field_dict.items() if value is None]

        if len(keys_with_none) > 0:
            print(f"Error: Keys with None values({len(keys_with_none)} from {len(self.field_dict)}): {keys_with_none}")

    def Step(self):
        """ Perform one simulation step """
        super().Step()
        self.operator.Step()
        currentState = self.operator.SimulatorStateToString(self.operator.GetSimulatorState())
        # print(currentState)
        self.ReceiveSignals()
        if self.prevState != "run" and currentState == "run":
            self.FindFields()
        if currentState == "run":
            self.ReadSignals()
        # self.WaitForRunState()
        self.prevState = currentState

    @staticmethod
    def findFieldChecked(field_name, ns):
        field = ns.FindField(field_name)
        if not field or not field.IsValid():
            print(field_name)
            return None
        return field

    @staticmethod
    def safe_assign(target, attr, value, transform):
        if value is not None:
            setattr(target, attr, transform(value))


def start_process():
    sdk = pt.Initialize("python_application")
    process = Process(sdk)
    process.Run()
