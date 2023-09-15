import time
import random
import threading
from pyftdi.ftdi import Ftdi
import numpy as np

def map_to(val, min, max):
    assert max > min
    val = np.clip(val, 0, 1)
    return int(round(min + val * (max - min)))



class DMXUniverse:
    """
    Interface to an ENTTEC OpenDMX (FTDI) DMX interface
    """
    def __init__(self, url='ftdi://ftdi:232:B000E5ZK/1'):
        self.url = url
        self.port = Ftdi.create_from_url('ftdi://ftdi:232:B000E5ZK/1')
        self.port.reset()
        self.port.set_baudrate(baudrate=250000)
        self.port.set_line_property(bits=8, stopbit=2, parity='N', break_=False)
        assert self.port.is_connected

        # The 0th byte must be 0 (start code)
        # 513 bytes are sent in total
        self.data = bytearray(513 * [0])

        self.devices = []

        self._dmx_thread = None
        self._stop_event = threading.Event()

    def __del__(self):
        # if self._dmx_thread is not None:
        #     self._stop_event.set()
        #     self._dmx_thread.join()
        #     self._dmx_thread = None
        self.port.close()
    
    def close(self):
        if self._dmx_thread is not None:
            self._stop_event.set()
            self._dmx_thread.join()
            self._dmx_thread = None
        self.port.close()

    def __setitem__(self, idx, val):
        assert (idx >= 1)
        assert (idx <= 512)
        assert isinstance(val, int)
        assert (val >= 0 and val <= 255)
        self.data[idx] = val

    def set_float(self, start_chan, chan_no, val, min=0, max=255):
        assert (chan_no >= 1)

        # If val is an array of values
        if hasattr(val, '__len__'):
            for i in range(len(val)):
                int_val = map_to(val[i], min, max)
                self[start_chan + chan_no - 1 + i] = int_val
        else:
            int_val = map_to(val, min, max)
            self[start_chan + chan_no - 1] = int_val

    def set_int(self, start_chan, chan_no, val):
        self[start_chan + chan_no - 1] = val

    def add_device(self, device):
        # Check for partial channel overlaps between devices, which
        # are probably an error
        for other in self.devices:
            # Two devices with the same type and the same channel are probably ok
            if device.chan_no == other.chan_no and type(device) == type(other):
                continue

            if device.chan_overlap(other):
                raise Exception('partial channel overlap between devices "{}" and "{}"'.format(device.name, other.name))

        self.devices.append(device)
        return device

    def start_dmx_thread(self):
        """
        Thread to write channel data to the output port
        """

        def dmx_thread_fn():
            while not self._stop_event.is_set():
                for dev in self.devices:
                    dev.update(self)

                self.port.set_break(True)
                self.port.set_break(False)
                self.port.write_data(self.data)

                # The maximum update rate for the Enttec OpenDMX is 40Hz
                time.sleep(8/1000.0)

        self._dmx_thread = threading.Thread(target=dmx_thread_fn, args=(), daemon=True)
        self._dmx_thread.start()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class DMXDevice:
    def __init__(self, name, chan_no, num_chans):
        assert (chan_no >= 1)
        self.name = name
        self.chan_no = chan_no
        self.num_chans = num_chans

    def chan_overlap(this, that):
        """
        Check if two devices have overlapping channels
        """

        this_last = this.chan_no + (this.num_chans - 1)
        that_last = that.chan_no + (that.num_chans - 1)

        return (
            (this.chan_no >= that.chan_no and this.chan_no <= that_last) or
            (that.chan_no >= this.chan_no and that.chan_no <= this_last)
        )

    def update(self, dmx):
        raise NotImplementedError



class RGB36(DMXDevice):
    def __init__(self, name, chan_no):
        super().__init__(name, chan_no, num_chans=8)
        self.dimming = 250
        self._rgb = np.array([0, 0, 0])
        self.target_rgb = np.array([0, 0, 0])
        self.start_rgb = np.array([0, 0, 0])
        self.transition_start_time = None
        self.strobe = 0
        self.anim_speed = 0
        self.should_strobe = False
        self.transition_speed = 100

    @property
    def rgb(self):
        return self._rgb

    @rgb.setter
    def rgb(self, value):
        self.start_rgb = self._rgb
        self.target_rgb = np.array(value)
        self.transition_start_time = time.time()

    def interpolate_rgb(self):
        if self.transition_start_time is None:
            return self._rgb
        
        elapsed = (time.time() - self.transition_start_time) * 1000  # time in ms
        if elapsed >= self.transition_speed:
            self._rgb = self.target_rgb
            self.transition_start_time = None  # End the transition
        else:
            t = elapsed / self.transition_speed  # Percentage of transition completed
            self._rgb = (1 - t) * self.start_rgb + t * self.target_rgb
        
        return self._rgb

    def update(self, dmx):
        current_rgb = self.interpolate_rgb()
        
        dmx.set_int(self.chan_no, 1, self.dimming)
        dmx.set_float(self.chan_no, 2, current_rgb)

        if self.should_strobe:
            dmx.set_int(self.chan_no, 5, 25)
        else:
            dmx.set_int(self.chan_no, 5, 1)



# class RGB36(DMXDevice):
#     """
#     RGB fixture with 36 LEDs, 6 channels
#     CH1: total dimming
#     CH2: R 0-255
#     CH3: G 0-255
#     CH4: B 0-255
#     CH5: strobe speed (0-255)
#     CH6: color change speed (0-255)
#     """

#     def __init__(self, name, chan_no):
#         super().__init__(name, chan_no, num_chans=8)
#         self.dimming = 1
#         self.rgb = np.array([0, 0, 0])
#         self.strobe = 0
#         self.anim_speed = 0

#         self.should_strobe = False

#     def update(self, dmx):
#         dmx.set_int(self.chan_no, 1, 250)
#         dmx.set_float(self.chan_no, 2, self.rgb)

#         if self.should_strobe:
#             dmx.set_int(self.chan_no, 5, 25)
#         else:
#             dmx.set_int(self.chan_no, 5, 1)
#         # dmx.set_int(self.chan_no, 6, 160)
#         # dmx.set_float(self.chan_no, 7, 0, 0, 255)

class RGB36Mode(DMXDevice):
    def __init__(self, name, chan_no):
        super().__init__(name, chan_no, num_chans=8)
        self.dimming = 250
        self.rgb = np.array([0, 0, 0])
        self.strobe = 0
        self.anim_speed = 0

        self.should_strobe = False

    def update(self, dmx):
        dmx.set_int(self.chan_no, 1, self.dimming)
        dmx.set_float(self.chan_no, 2, self.rgb)
        # dmx.set_float(self.chan_no, 5, self.strobe, 0, 255)
        if self.should_strobe:
            dmx.set_int(self.chan_no, 6, 240)
        else:
            dmx.set_int(self.chan_no, 6, 0)
        dmx.set_int(self.chan_no, 7, 0)
