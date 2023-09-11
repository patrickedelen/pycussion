import numpy as np
import time

from src.lighting_controller import DMXUniverse, RGB36


class Lighting:
    def __init__(self):

        self.dmx = DMXUniverse()

        self.fix1 = RGB36(name="fix1", chan_no=1)
        self.fix2 = RGB36(name="fix1", chan_no=10)

        self.is_active = False
        self.closing = False

        self.dmx.start_dmx_thread()
        self.dmx.add_device(self.fix1)
        self.dmx.add_device(self.fix2)

        self.fix1.dimming = 0.5
        self.fix2.dimming = 0.5

        self.strobing_state = False

        self.strobing = False
        self.mark_time = time.time()

    def set_white(self):
        self.fix1.rgb = np.array([1.0, 1.0, 0.6])
        self.fix2.rgb = np.array([1.0, 1.0, 0.6])

    def set_accent(self):
        self.fix1.rgb = np.array([0.9, 0.2, 0])
        self.fix2.rgb = np.array([0.9, 0.2, 0])

    def set_black(self):
        self.fix1.rgb = np.array([0, 0, 0])
        self.fix2.rgb = np.array([0, 0, 0])

    def close(self):
        self.dmx.close()

    def render(self, magnitude, close, switch=False):
        # print('running lights...')

        # if close and not self.closing:
        #     print('closing lights...')
        #     self.closing = True
        #     self.dmx.close()
        #     exit(0)
        
        # if self.closing:
            # return

        self.is_active = not self.is_active
        cur_time = time.time()

        if not self.strobing_state:
            if switch:
                self.set_white()
            else:
                self.set_black()



        if cur_time - self.mark_time < 5:
            # print('resetting')
            pass
        elif magnitude > 0.3 and not self.strobing_state:
            print('trigger strobing')
            self.strobing_state = True
            self.mark_time = time.time()
        elif not self.strobing_state:
            pass
            # print('no trigger')
            # print('magnitude', magnitude)

        if self.strobing_state:
            if cur_time - self.mark_time >= 2:
                self.strobing = False
                self.strobing_state = False
                self.mark_time = time.time()
                print('stop strobe')
                self.set_black()
            else:
                if self.strobing:
                    self.set_black()
                    self.strobing = False
                else:
                    self.strobing = True
                    if switch:
                        self.set_accent()
                    else:
                        self.set_white()




        # if self.is_active:
        #     self.fix1.rgb = np.array([255, 255, 255])
        #     self.fix2.rgb = np.array([255, 255, 255])
        # else:
        #     self.fix1.rgb = np.array([0, 0, 0])
        #     self.fix2.rgb = np.array([0, 0, 0])



