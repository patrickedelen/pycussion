import sys

try:
    import launchpad_py as launchpad
except ImportError:
    try:
        import launchpad
    except ImportError:
        sys.exit("error loading launchpad.py")


class LaunchPadController:
    def __init__(self, visuals_state):
        self.lp = launchpad.LaunchpadLPX()
        if not self.lp.Open(1):
            raise Exception("Failed to open Launchpad X")
        self.visuals_state = visuals_state
        self.button_to_cube_state = {
            81: 'regular',
            82: 'multi',
            83: 'moving',
            84: 'glitchy'
        }
        self.button_to_background_state = {
            71: 'squares',
            72: 'particles',
            73: 'circles',
            74: 'waveform',
            61: 'triangles',
            62: 'tunnel',
            63: 'black',
            64: 'plane'
        }

        self.button_to_lighting_mode = {
            51: 'on',
            52: 'off',
            53: 'strobe',
            54: 'wash'
        }

        self.button_to_lighting_movement = {
            41: 'all',
            42: 'left',
            43: 'right',
            44: 'front',
            31: 'ltr',
            32: 'rtl',
            33: 'ftb',
            34: 'btf'
        }
        self.button_to_lighting_color = {
            21: 'white',
            22: 'red',
            23: 'green',
            24: 'blue'
        }
        self.button_to_lighting_speed = {
            11: 'slow',
            12: 'med',
            13: 'fast',
            14: 'vfast'
        }

        self.lp.LedSetLayout(0x05)
        self.initialize_buttons()

    def initialize_buttons(self):
        # Set the buttons 81-84 and 71-74 to red
        red_color = (3, 0)  
        for btn in range(81, 85):
            print(f"setting button {btn}")
            self.lp.LedCtrlRaw(btn, 63, 0, 0)

    def button_pressed(self, button):
        print(button)
        if button in self.button_to_cube_state:
            self.lp.LedCtrlRaw(button, 0, 63, 0)
            self.visuals_state['cube'] = self.button_to_cube_state[button]
            print(f'swithcing visual state to: {self.button_to_cube_state[button]}')
        if button in self.button_to_background_state:
            self.lp.LedCtrlRaw(button, 0, 63, 0)
            self.visuals_state['background'] = self.button_to_background_state[button]
            print(f'swithcing visual state to: {self.button_to_background_state[button]}')
        if button in self.button_to_lighting_mode:
            self.lp.LedCtrlRaw(button, 0, 63, 0)
            self.visuals_state['mode'] = self.button_to_lighting_mode[button]
            print(f'swithcing visual state to: {self.button_to_lighting_mode[button]}')
        if button in self.button_to_lighting_movement:
            self.lp.LedCtrlRaw(button, 0, 63, 0)
            self.visuals_state['movement'] = self.button_to_lighting_movement[button]
            print(f'swithcing visual state to: {self.button_to_lighting_movement[button]}')
        if button in self.button_to_lighting_color:
            self.lp.LedCtrlRaw(button, 0, 63, 0)
            self.visuals_state['color'] = self.button_to_lighting_color[button]
            print(f'swithcing visual state to: {self.button_to_lighting_color[button]}')
        if button in self.button_to_lighting_speed:
            self.lp.LedCtrlRaw(button, 0, 63, 0)
            self.visuals_state['speed'] = self.button_to_lighting_speed[button]
            print(f'swithcing visual state to: {self.button_to_lighting_speed[button]}')

    def listen(self):
        buts = self.lp.ButtonStateRaw()
        if buts:
            button = buts[0]
            self.button_pressed(button)

    def run(self):
        self.listen()

    #    +-------+---+-------+---+---+---+---+-------+  +-------+
    #    |  104  |   |  106  |   |   |   |   |  111  |  |  112  |
    #    +-------+---+-------+---+---+---+---+-------+  +-------+
        
    #    +-------+-------+-------+-------+---+---+---+-------+  +-------+
    #    |  reg  |  mul  |  ran  |  gli  |   |   |   |       |  |  089  |
    #    +-------+-------+-------+-------+---+---+---+-------+  +-------+
    #    |  071  |  072  |  073  |  074  |   |   |   |       |  |  079  |
    #    +-------+-------+-------+-------+---+---+---+-------+  +-------+
    #    |  061  |  062  |  063  |  064  |   |   |  67|  068  |  |  069  |
    #    +-------+-------+-------+-------+---+---+---+-------+  +-------+
    #    |  051  |  052  |  053  |  054  |   |   |   |       |  |  059  |
    #    +-------+-------+-------+-------+---+---+---+-------+  +-------+
    #    |  sqr  |  prt  |  cir  |  wvf  |   |   |   |       |  |  049  |
    #    +-------+-------+-------+-------+---+---+---+-------+  +-------+
    #    |  tri  |  tnl  |  033  |  034  |   |   |   |       |  |  039  |
    #    +-------+-------+-------+-------+---+---+---+-------+  +-------+
    #    |  021  |  022  |  023  |  024  |   |   |   |       |  |  029  |
    #    +-------+-------+-------+-------+---+---+---+-------+  +-------+
    #    |  011  |  012  |  013  |  014  |   |   |   |       |  |  019  |
    #    +-------+-------+-------+-------+---+---+---+-------+  +-------+
