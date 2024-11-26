from liveDataProcess import LiveDataProcess
from recordedDataProcess import RecordedDataProcess


class DataProcessFactory:

    def __init__(self):
        # todo: find better way to find out what process is needed.
        is_live = False
        if is_live:
            self.data_process = LiveDataProcess()
        else:
            self.data_process = RecordedDataProcess()

    def get_data_process(self):
        return self.data_process
