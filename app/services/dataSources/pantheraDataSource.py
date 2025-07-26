import logging
import os
import sys

import panthera as pt

from ...models.liveDataRow import FIELD_NAME_MAP


# Suppress stdout and stderr output
# we use this to prevent panthera from printing to the console
class SuppressStdoutStderr:
    def __init__(self):
        self.devnull = os.devnull
        self.fnull = None
        self.old_stdout_fd = None
        self.old_stderr_fd = None

    def __enter__(self):
        # Open null device
        self.fnull = open(self.devnull, 'w')

        # Save original file descriptors
        self.old_stdout_fd = os.dup(1)
        self.old_stderr_fd = os.dup(2)

        # Redirect stdout and stderr to null device
        os.dup2(self.fnull.fileno(), 1)
        os.dup2(self.fnull.fileno(), 2)

        return self  # optional, not used usually

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original stdout and stderr
        os.dup2(self.old_stdout_fd, 1)
        os.dup2(self.old_stderr_fd, 2)

        # Close everything
        os.close(self.old_stdout_fd)
        os.close(self.old_stderr_fd)
        self.fnull.close()


class Process(pt.Process):
    """ The process class handles all communication with the simulator. """

    def __init__(self, sdk, update_measurement_callback=None):
        """ Constructor """
        super().__init__(sdk, sys.argv)

        self.logger = logging.getLogger("uvicorn.error")

        # Step at 10Hz
        self.step = 0.1
        self.SetWaitTimeout(self.step)
        self.t = None
        self.counter = 0
        self.prevState = "stopped"

        self.update_measurement_callback = update_measurement_callback

        self.resolved_fields = {}

        self.operator = pt.Operator(sdk, "tagging-dashboard")
        self.operator.Connect(self.GetMqttBrokerHostname(), "operator", "operator")
        assert self.operator.IsConnected()

        # Manually send the signals (to reduce latency, send them as soon as their values are set)
        # Done with the `self.SendSignals()` call
        self.StepHandlesSendSignals(False)

    def run(self):
        """ Main function """
        while self.GetState() != pt.ProcessState_Offline:
            self.step()

    def step(self):
        """ Perform one simulation step """
        super().Step()
        self.operator.Step()
        currentState = self.operator.SimulatorStateToString(self.operator.GetSimulatorState())
        # print(currentState)
        self.ReceiveSignals()
        if self.prevState != "run" and currentState == "run":
            self.find_fields()
        if currentState == "run":
            self.read_signals()
        # self.WaitForRunState()
        self.prevState = currentState

    def read_signals(self):
        """ Read the signals from the simulator and update the measurement data """
        if self.GetState() != pt.ProcessState_Run:
            return

        data = {}

        for field_name, field in self.resolved_fields.items():
            transform = dict(FIELD_NAME_MAP).get(field_name)
            self.safe_assign(data, field_name, field, transform)

        data["timestamp"] = self.GetCurrentTime()

        if self.update_measurement_callback:
            self.update_measurement_callback(data)

    def find_fields(self):
        """ Find the fields in the named struct interface to the process """
        with SuppressStdoutStderr():
            ns = self.GetNamedStructInterfaceToProcess().GetNamedStruct()

        self.resolved_fields = {}

        for field_name, _ in FIELD_NAME_MAP:
            field = self.findFieldChecked(field_name, ns)
            if field:
                self.resolved_fields[field_name] = field

        missing = [f for f, _ in FIELD_NAME_MAP if f not in self.resolved_fields]
        if missing:
            self.logger.warning(f"Missing Panthera fields: {missing}")

    def safe_assign(self, target_dict, key, field, transform):
        """ Safely assign a field to a dictionary, handling errors and logging """
        if field is None:
            self.logger.warning(f"Cannot assign {key} - field is None.")
            return

        if transform is None:
            self.logger.warning(f"Cannot assign {field} to {key} - no transform provided.")
            return

        try:
            target_dict[key] = transform(field)
        except Exception as e:
            self.logger.warning(f"Transform error on field {key}: {e}")

    @staticmethod
    def findFieldChecked(field_name, ns):
        with SuppressStdoutStderr():
            field = ns.FindField(field_name)
        if not field or not field.IsValid():
            # print(field_name)
            return None
        return field


def start_process(update_measurement_callback=None):
    sdk = pt.Initialize("python_application")
    process = Process(sdk, update_measurement_callback)
    process.run()
