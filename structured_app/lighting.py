import numpy as np
import time
import random

from src.lighting_controller import DMXUniverse, RGB36, RGB36Mode




class Lighting:
    def __init__(self):

        self.dmx = DMXUniverse()

        self.fix1 = RGB36Mode(name="fix1", chan_no=1)  # right3
        self.fix2 = RGB36Mode(name="fix2", chan_no=10)  # right2

        self.fix3 = RGB36(name="fix3", chan_no=20)  # right1
        self.fix4 = RGB36(name="fix4", chan_no=30)  # left1

        self.fix5 = RGB36Mode(name="fix5", chan_no=40)  # left2
        self.fix6 = RGB36Mode(name="fix6", chan_no=50)  # left3

        self.is_active = False
        self.closing = False

        self.dmx.start_dmx_thread()
        self.dmx.add_device(self.fix1)
        self.dmx.add_device(self.fix2)
        self.dmx.add_device(self.fix3)
        self.dmx.add_device(self.fix4)
        self.dmx.add_device(self.fix5)
        self.dmx.add_device(self.fix6)

        self.fix1.dimming = 250
        self.fix2.dimming = 250

        self.strobing_state = False

        self.strobing = False
        self.mark_time = time.time()

        self.move_animation_ticks = 10
        self.color_animation_ticks = 50

        self.moving = False
        self.move_ticks = 0
        self.cur_move_state = 'white'

        self.active_lights = [False, False, False, False, False, False]
        self.lights = [
            self.fix1,
            self.fix2,
            self.fix3,
            self.fix4,
            self.fix5,
            self.fix6
        ]

        self.active_color = np.array([0.8, 1.0, 1.0])
        self.clear_color = np.array([0, 0, 0])
        self.clear_intensity = 250

        self.active_intensity = 250
        self.cur_intensity_tick = 0
        self.cur_lighting_mode = None
        self.wash_rising = False
        self.strobing = False


    def color_active_lights(self):
        for i, active in enumerate(self.active_lights):
            if active:
                self.lights[i].rgb = self.active_color
                self.lights[i].should_strobe = self.strobing
                self.lights[i].dimming = self.active_intensity
            else:
                self.lights[i].rgb = self.clear_color
                self.lights[i].should_strobe = False
                self.lights[i].dimming = self.clear_intensity

    def movement_ltr_animation(self):
        # if new state, start animation at the first light
        # else, count ticks up until choosing the next light
        # controls which lights are active

        if self.cur_move_state != 'ltr':
            self.cur_move_state = 'ltr'
            self.moving = True
            self.active_lights = [False, False, False, False, False, False]
            self.active_lights[0] = True
            self.move_ticks = 0
        
        self.move_ticks += 1
        if self.move_ticks >= 10:
            self.move_ticks = 0
            active_light_id = self.active_lights.index(True)
            if active_light_id == len(self.active_lights) - 1:
                active_light_id = 0
            else:
                active_light_id += 1
            
            self.active_lights = [False, False, False, False, False, False]
            self.active_lights[active_light_id] = True

    def movement_rtl_animation(self):
        """
            right to left movement animation
        """
        if self.cur_move_state != 'rtl':
            self.cur_move_state = 'rtl'
            self.moving = True
            self.active_lights = [False, False, False, False, False, False]
            self.active_lights[-1] = True
            self.move_ticks = 0
        
        self.move_ticks += 1
        if self.move_ticks >= 10:
            self.move_ticks = 0
            active_light_id = self.active_lights.index(True)
            if active_light_id == 0:
                active_light_id = len(self.active_lights) - 1
            else:
                active_light_id -= 1
            
            self.active_lights = [False, False, False, False, False, False]
            self.active_lights[active_light_id] = True

    def movement_all_on(self):
        self.cur_move_state = 'all'
        self.moving = False
        self.active_lights = [True, True, True, True, True, True]
    
    # def movement_all_off(self):
    #     self.cur_move_state = 'all_off'
    #     self.moving = False
    #     self.active_lights = [False, False, False, False, False, False]

    def movement_left(self):
        self.cur_move_state = 'left'
        self.moving = False
        self.active_lights = [False, False, False, True, True, True]

    def movement_right(self):
        self.cur_move_state = 'right'
        self.moving = False
        self.active_lights = [True, True, True, False, False, False]

    def movement_front(self):
        self.cur_move_state = 'front'
        self.moving = False
        self.active_lights = [False, False, True, True, False, False]

    # move back to front
    def move_btf_animation(self):
        """
            move back to front
        """

        if self.cur_move_state != 'btf':
            self.cur_move_state = 'btf'
            self.moving = True
            self.active_lights = [True, False, False, False, False, True]
            self.move_ticks = 0

        self.move_ticks += 1
        if self.move_ticks >= 10:
            self.move_ticks = 0
            cur_light_idx = self.active_lights.index(True)

            if cur_light_idx == 2:  #light has reached front
                cur_light_idx = 0
            else:
                cur_light_idx += 1

            self.active_lights = [False, False, False, False, False, False]
            self.active_lights[cur_light_idx] = True
            self.active_lights[-(cur_light_idx + 1)] = True




    def move_ftb_animation(self):
        """
            move front to back
        """

        if self.cur_move_state != 'ftb':
            self.cur_move_state = 'ftb'
            self.moving = True
            self.active_lights = [False, False, True, True, False, False]
            self.move_ticks = 0

        self.move_ticks += 1
        if self.move_ticks >= 10:
            self.move_ticks = 0
            cur_light_idx = self.active_lights.index(True)

            if cur_light_idx == 0:  #light has reached front
                cur_light_idx = 2
            else:
                cur_light_idx -= 1

            self.active_lights = [False, False, False, False, False, False]
            self.active_lights[cur_light_idx] = True
            self.active_lights[-(cur_light_idx + 1)] = True


    def move_random_animation(self):
        if self.cur_move_state != 'random':
            self.cur_move_state = 'random'
            self.moving = True
            self.move_ticks = 0
            self.active_lights = [False, False, False, False, False, False]
            
            random_idx = int(random.random() * len(self.active_lights))
            if random_idx < len(self.active_lights):
                self.active_lights[random_idx] = True
            else:
                self.active_lights[0] = True

        self.move_ticks += 1
        if self.move_ticks > 10:
            self.move_ticks = 0
            self.active_lights = [False, False, False, False, False, False]
            random_idx = int(random.random() * len(self.active_lights))
            if random_idx < len(self.active_lights):
                self.active_lights[random_idx] = True
            else:
                self.active_lights[0] = True



    def mode_wash(self):
        if self.cur_lighting_mode != 'wash':
            self.cur_lighting_mode = 'wash'
            self.wash_rising = True
            self.active_intensity = 20
        
        if self.wash_rising and self.active_intensity < 250:
            self.active_intensity += 10
        elif self.wash_rising and self.active_intensity >= 250:
            self.wash_rising = False
            self.active_intensity -= 10
        elif not self.wash_rising and self.active_intensity > 20:
            self.active_intensity -= 10
        else:
            self.wash_rising = True
            self.active_intensity += 10

    def mode_strobe(self):
        self.cur_lighting_mode = 'strobing'
        self.strobing = True
        self.active_intensity = 250

    def mode_on(self):
        self.active_intensity = 250
        self.strobing = False
        self.cur_lighting_mode = 'on'

    def mode_off(self):
        self.active_intensity = 0
        self.strobing = False
        self.cur_lighting_mode = 'off'


    def set_white(self):
        self.fix1.rgb = np.array([1.0, 1.0, 0.6])
        self.fix2.rgb = np.array([1.0, 1.0, 0.6])
        self.fix3.rgb = np.array([1.0, 1.0, 0.6])
        self.fix4.rgb = np.array([1.0, 1.0, 0.6])
        self.fix5.rgb = np.array([1.0, 1.0, 0.6])
        self.fix6.rgb = np.array([1.0, 1.0, 0.6])

    def set_dim(self):
        self.fix1.dimming = 0
        self.fix2.dimming = 0
        self.fix3.dimming = 0
        self.fix4.dimming = 0
        self.fix5.dimming = 0
        self.fix6.dimming = 0

    def set_bright(self):
        self.fix1.dimming = 255
        self.fix2.dimming = 255
        self.fix3.dimming = 255
        self.fix4.dimming = 255
        self.fix5.dimming = 255
        self.fix6.dimming = 255

    def set_accent(self):
        self.fix1.rgb = np.array([0.9, 0.2, 0])
        self.fix2.rgb = np.array([0.9, 0.2, 0])
        self.fix3.rgb = np.array([0.9, 0.2, 0])
        self.fix4.rgb = np.array([0.9, 0.2, 0])
        self.fix5.rgb = np.array([0.9, 0.2, 0])
        self.fix6.rgb = np.array([0.9, 0.2, 0])

    def set_black(self):
        self.fix1.rgb = np.array([0, 0, 0])
        self.fix2.rgb = np.array([0, 0, 0])
        self.fix3.rgb = np.array([0, 0, 0])
        self.fix4.rgb = np.array([0, 0, 0])
        self.fix5.rgb = np.array([0, 0, 0])
        self.fix6.rgb = np.array([0, 0, 0])

    def close(self):
        self.dmx.close()

    def render(self, magnitude, close, switch=False, visuals_state={}):
        mode = visuals_state['mode']
        movement = visuals_state['movement']
        color = visuals_state['color']

        if self.cur_lighting_mode != mode:
            self.cur_lighting_mode = mode

        if self.cur_move_state != movement:
            self.cur_move_state = movement

        match self.cur_lighting_mode:
            case 'on':
                self.mode_on()
            case 'off':
                self.mode_off()
            case 'strobe':
                self.mode_strobe()
            case 'wash':
                self.mode_wash()
        
        match self.cur_move_state:
            case 'all':
                self.movement_all_on()
            case 'left':
                self.movement_left()
            case 'right':
                self.movement_right()
            case 'front':
                self.movement_front()
            case 'ltr':
                self.movement_ltr_animation()
            case 'rtl':
                self.movement_rtl_animation()
            case 'ftb':
                self.move_ftb_animation()
            case 'btf':
                self.move_btf_animation()

        match color:
            case 'white':
                self.active_color = np.array([0.8, 1.0, 1.0])
            case 'red':
                self.active_color = np.array([1.0, 0.3, 0.1])
            case 'green':
                self.active_color = np.array([0.1, 1.0, 0.2])
            case 'blue':
                self.active_color = np.array([0.2, 0.2, 1.0])

        self.color_active_lights()

        # print('running lights...')

        # if close and not self.closing:
        #     print('closing lights...')
        #     self.closing = True
        #     self.dmx.close()
        #     exit(0)
        
        # if self.closing:
            # return

        # self.fix3.rgb = np.array([1.0, 1.0, 0.6])
        # self.fix4.rgb = np.array([1.0, 1.0, 0.6])
        # self.fix5.rgb = np.array([1.0, 1.0, 0.6])
        # self.fix6.rgb = np.array([1.0, 1.0, 0.6])

        # self.is_active = not self.is_active
        # cur_time = time.time()

        # self.move_ticks += 1

        # if self.move_ticks >= 30 and self.cur_move_state == 'white':
        #     self.move_ticks = 0
        #     self.cur_move_state = 'black'
        #     self.set_black()
        # if self.move_ticks >= 30 and self.cur_move_state == 'black':
        #     self.move_ticks = 0
        #     self.cur_move_state = 'white'
        #     self.set_white()

        # self.set_white()
        # if lighting_state["movement"] == 'ltr':
        #     self.movement_ltr_animation()
        
        # self.color_active_lights()

        # if not self.strobing_state:
        # if switch:
        #     self.set_white()
        #     self.set_bright()
        # else:
        #     self.set_dim()
            # self.set_black()



        # if cur_time - self.mark_time < 5:
        #     # print('resetting')
        #     pass
        # elif magnitude > 0.3 and not self.strobing_state:
        #     print('trigger strobing')
        #     self.strobing_state = True
        #     self.mark_time = time.time()
        #     self.set_white()
        # elif not self.strobing_state:
        #     pass
        #     # print('no trigger')
        #     # print('magnitude', magnitude)

        # if self.strobing_state:
        #     if cur_time - self.mark_time >= 2:
        #         self.strobing = False
        #         self.strobing_state = False
        #         self.mark_time = time.time()
        #         print('stop strobe')
        #     else:
        #         if self.strobing:
        #             self.set_dim()
        #             self.strobing = False
        #         else:
        #             self.strobing = True
        #             if switch:
        #                 self.set_accent()
        #             else:
        #                 self.set_bright()




        # if self.is_active:
        #     self.fix1.rgb = np.array([255, 255, 255])
        #     self.fix2.rgb = np.array([255, 255, 255])
        # else:
        #     self.fix1.rgb = np.array([0, 0, 0])
        #     self.fix2.rgb = np.array([0, 0, 0])



