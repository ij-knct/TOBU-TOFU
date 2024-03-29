import pyxel
from enum import Enum, auto
import random

from sensor import *

sen = Sensor()

class STATE(Enum):
    NONE = auto()
    WALKING = auto()
    FLYING = auto()
    FALL = auto()
    GLIDE = auto()


class SELECT(Enum):
    NONE = auto()
    DISTANCE = auto()
    TEMPERATURE = auto()
    LIGHT = auto()
    PRESSURE = auto()


class SHOWMODE(Enum):
    SceneChange = auto()
    Start = auto()
    Title = auto()
    Main = auto()
    End = auto()


class SCENECHANGE(Enum):
    FIRST = auto()
    SECOND = auto()
    THIRD = auto()
    FOURTH = auto()
    FIFTH = auto()

class NEAR_BLOCK(Enum):
    BLOCK1 = auto()
    BLOCK2 = auto()
    BLOCK3 = auto()

class App:
    FIELD_Y = 102

    def __init__(self):
        pyxel.init(200, 150, caption="TOBU!TOFU!", fps=60)
        self.init()
        self.init_player()
        self.init_ending()
        self.stage = Stage()
        pyxel.run(self.update, self.draw)

    def init(self):
        # loading image
        pyxel.load("resource/kogemikan.pyxres")
        # initialize dictionary for color pallet
        self.COLOR_PALLET = {
            "BLACK": 0,
            "DARK_BLUE": 1,
            "RED_PURPLE": 2,
            "GREEN": 3,
            "BROWN": 4,
            "GLAY": 5,
            "SILVER": 6,
            "WHITE": 7,
            "RED": 8,
            "ORANGE": 9,
            "YELLOW": 10,
            "LIGHT_GREEN": 11,
            "BLUE": 12,
            "PURPLE": 13,
            "PINK": 14,
            "FLESH": 15,
        }
        # initialize status what player does
        self.player_state = STATE.NONE
        self.now_gamemode = SHOWMODE.Title
        self.was_gamemode = None
        self.selected_sensor = SELECT.NONE
        # initialize count
        self.title_count = 0
        self.was_data = 0
        self.sec_count = 0
        self.now_frame = 0
        self.scene_change_p = None
        # initialize flags
        self.is_sensing = False
        self.is_dead = False
        self.is_on_ground = True
        self.is_top_passed = False
        self.once_called = False
        self.is_moss = None
        # initialize colors
        self.BACKGROUND = self.COLOR_PALLET["BLACK"]
        self.GAMEMESSAGE = self.COLOR_PALLET["GLAY"]
        self.STAGE_GROUND = self.COLOR_PALLET["GREEN"]
        self.FLASH = self.COLOR_PALLET["YELLOW"]
        self.RECT_COLOR = self.COLOR_PALLET["BLACK"]
        self.GRID_COLOR = self.COLOR_PALLET["BLACK"]
        # initialize image's constant number
        self.TOFU = 0
        self.LOGO = 1
        self.DOT_16 = 0
        self.TOFU_NONE = 48
        self.TOFU_FLY = 64
        self.TOFU_GLIDE = 80
        self.BLOCK_NORMAL = 96
        self.BLOCK_MOSS = 128

    def init_player(self):
        # initialize player information
        self.player_x = 32
        self.player_y = self.FIELD_Y - 16
        self.vector_y = 1
        self.player_size_x = 16
        self.player_size_y = 16
        self.player_colkey = self.COLOR_PALLET["BLACK"]
        self.hit_counter = 0
        self.is_game_clear = False
        # initialize threshold value for decide what's going on
        # self.NOSIE should be sensor.mapped_data()
        # bcuz it's default value for sensing
        self.NOISE = 5
        self.WALK = 40
        self.GLIDE = 90
        # flags for is_on_ground
        self.flag_a = False
        self.flag_b = False
        self.flag_c = False
        self.flag_d = False
        self.flag_A = False
        self.flag_B = False
        self.flag_C = False
        self.flag_D = False
        # DELETE AS PRODUCT
        self.TEST_INT = 0

    def update(self):
        if pyxel.btn(pyxel.KEY_ESCAPE) or pyxel.btn(pyxel.KEY_Q):
            Sensor.close_spi()
            Esc()

        if self.now_gamemode == SHOWMODE.SceneChange:
            self.update_scenechange()
        elif self.now_gamemode == SHOWMODE.Title:
            self.update_title()
        elif self.now_gamemode == SHOWMODE.Main:
            self.update_main()
        elif self.now_gamemode == SHOWMODE.Start:
            self.update_start()
        elif self.now_gamemode == SHOWMODE.End:
            self.update_ending()

    def update_scenechange(self):
        if not self.once_called:
            self.once_called = True
            self.now_frame = pyxel.frame_count % 180
        if (pyxel.frame_count - self.now_frame) % 180 < 30:
            self.scene_change_p = SCENECHANGE.FIRST
        elif (pyxel.frame_count - self.now_frame) % 180 < 60:
            self.scene_change_p = SCENECHANGE.SECOND
        elif (pyxel.frame_count - self.now_frame) % 180 < 90:
            self.scene_change_p = SCENECHANGE.THIRD
        elif (pyxel.frame_count - self.now_frame) % 180 < 120:
            self.scene_change_p = SCENECHANGE.FOURTH
        elif (pyxel.frame_count - self.now_frame) % 180 < 150:
            self.scene_change_p = SCENECHANGE.FIFTH
        if (pyxel.frame_count - self.now_frame) % 50 == 0:
            self.sec_count += 1
            if self.sec_count == 4:
                self.scene_change_p = None
                self.sec_count = 0
                self.now_frame = 0
                self.once_called = False
                if self.was_gamemode == SHOWMODE.Title:
                    self.now_gamemode = SHOWMODE.Start
                elif self.was_gamemode == SHOWMODE.Main and self.is_game_clear:
                    self.now_gamemode = SHOWMODE.End
                elif self.was_gamemode == SHOWMODE.Main:
                    self.now_gamemode = SHOWMODE.Title


    def update_start(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.was_gamemode == SHOWMODE.Title:
                self.was_gamemode = SHOWMODE.Start
                self.now_gamemode = SHOWMODE.Main
            else:
                self.was_gamemode = SHOWMODE.Start
                self.now_gamemode = SHOWMODE.Title

    def update_title(self):
        global sen
        if pyxel.btn(pyxel.KEY_D):
            self.is_sensing = True
            self.selected_sensor = SELECT.DISTANCE
        elif pyxel.btn(pyxel.KEY_T):
            self.is_sensing = True
            self.selected_sensor = SELECT.TEMPERATURE
        elif pyxel.btn(pyxel.KEY_L):
            self.is_sensing = True
            self.selected_sensor = SELECT.LIGHT
        elif pyxel.btn(pyxel.KEY_P):
            self.is_sensing = True
            self.selected_sensor = SELECT.PRESSURE
        elif pyxel.btn(pyxel.KEY_SPACE) and self.is_sensing:
            self.is_dead = False
            if self.selected_sensor == SELECT.DISTANCE:
                sen = Sensor.generate(Sensors.DISTANCE, 3)
                pass
            elif self.selected_sensor == SELECT.TEMPERATURE:
                sen = Sensor.generate(Sensors.TEMPERATURE, 1)
                #print(sensor)
                pass
            elif self.selected_sensor == SELECT.LIGHT:
                #print('through LIGHT GENERATOR')
                sen = Sensor.generate(Sensors.LIGHT, 2)
                #print(sensor)
                pass
            elif self.selected_sensor == SELECT.PRESSURE:
                sen = Sensor.generate(Sensors.TOUCH, 0)
                pass
            self.init_player()
            self.stage.init_stage()
            self.was_gamemode = SHOWMODE.Title
            self.now_gamemode = SHOWMODE.SceneChange

    def update_main(self):
        #'sensor debug''''
        print(sen)
        a = sen.read_data()
        b = sen.mapped_data()
        print(str(a) + '/' + str(b))

        #'''
        # FLAG : player is on ground or not
        if self.stage.block_1_pos[0] <= self.player_x + self.player_size_x and self.player_x < self.stage.block_1_pos[
            0] + self.stage.block_1_size[0] * 16:
            self.flag_a = True
        else:
            self.flag_a = False
        if self.stage.block_2_pos[0] <= self.player_x + self.player_size_x and self.player_x < self.stage.block_2_pos[
            0] + self.stage.block_2_size[0] * 16:
            self.flag_b = True
        else:
            self.flag_b = False
        if self.stage.block_3_pos[0] <= self.player_x + self.player_size_x and self.player_x < self.stage.block_3_pos[
            0] + self.stage.block_3_size[0] * 16:
            self.flag_c = True
        else:
            self.flag_c = False
        if self.stage.spawn_size[0] <= self.player_x + self.player_size_x and self.player_x < self.stage.spawn_pos[
            0] + self.stage.spawn_size[0] * 16:
            self.flag_d = True
        else:
            self.flag_d = False
        if self.stage.block_1_pos[1] == self.player_y + self.player_size_y:
            self.flag_A = True
        else:
            self.flag_A = False
        if self.stage.block_2_pos[1] == self.player_y + self.player_size_y:
            self.flag_B = True
        else:
            self.flag_B = False
        if self.stage.block_3_pos[1] == self.player_y + self.player_size_y:
            self.flag_C = True
        else:
            self.flag_C = False
        if self.stage.spawn_pos[1] == self.player_y + self.player_size_y:
            self.flag_D = True
        else:
            self.flag_D = False
        if (self.flag_a and self.flag_A) or (self.flag_b and self.flag_B) or (self.flag_c and self.flag_C) or (
                self.flag_d and self.flag_D):
            self.is_on_ground = True
            self.hit_counter  = 0
        else:
            self.is_on_ground = False
        # do gravity if player is not on ground
        if not self.is_on_ground:
            self.player_y += self.vector_y
        # FLAG : data is increasing or not
        if sen.mapped_data() < self.was_data:
            self.is_top_passed = True
        #if self.TEST_INT < self.was_data:
        #    self.is_top_passed = True
        elif self.is_on_ground:
            self.is_top_passed = False

        # this is temporary code for testing
        # delete or disable after testing
        # #input flag
        # if self.NOISE < self.TEST_INT:
        # #flying flag
        #     if self.WALK < self.TEST_INT and not self.is_top_passed:
        #         self.player_state = STATE.FLYING
        #         if 0 <= self.player_y:
        #             self.stage.move_stage(-2)
        #             self.player_y -= 2
        # #glide flag
        #     elif self.GLIDE < self.TEST_INT and self.is_top_passed:
        #         self.player_state = STATE.GLIDE
        #         if not self.is_on_ground:
        #             self.stage.move_stage(-2)
        #             self.player_y += 1
        #     elif self.TEST_INT < self.WALK and self.is_on_ground:
        #         self.player_state = STATE.WALKING
        #         self.stage.move_stage(-2)
        # else:
        #     if self.is_on_ground:
        #         self.player_state = STATE.NONE
        #     else:
        #         self.player_state = STATE.FALL

        if self.is_on_ground:
            if sen.mapped_data() < self.NOISE:
                self.player_state = STATE.NONE
            elif sen.mapped_data() < self.WALK:
                self.player_state = STATE.WALKING
                self.stage.move_stage(-1)
            elif self.WALK < sen.mapped_data():
                self.player_state = STATE.FLYING

        if self.player_state == STATE.FLYING and 0 <= self.player_y:
            self.stage.move_stage(-1)
            self.player_y -= 2
            if not self.is_top_passed:
                self.player_state = STATE.FLYING
            elif self.GLIDE < sen.mapped_data():
                self.player_state = STATE.GLIDE
            elif sen.mapped_data() < self.NOISE:
                self.player_state = STATE.FALL

        if self.player_state == STATE.GLIDE:
            if self.stage.near_block == NEAR_BLOCK.BLOCK1:
                if self.stage.block_1_pos[0] == self.player_x+self.player_size_x and self.stage.block_1_pos[1] < self.player_y+self.player_size_y:
                    self.player_state = STATE.FALL
                else:
                    self.stage.move_stage(-1)
            if self.stage.near_block == NEAR_BLOCK.BLOCK2:
                if self.stage.block_2_pos[0] == self.player_x+self.player_size_x and self.stage.block_2_pos[1] < self.player_y+self.player_size_y:
                    self.player_state = STATE.FALL
                else:
                    self.stage.move_stage(-1)
            if self.stage.near_block == NEAR_BLOCK.BLOCK3:
                if self.stage.block_3_pos[0] == self.player_x+self.player_size_x and self.stage.block_3_pos[1] < self.player_y+self.player_size_y:
                    self.player_state = STATE.FALL
                else:
                    self.stage.move_stage(-1)

        if self.player_y < 1:
            self.hit_counter += 1
            if 30 < self.hit_counter:
                self.player_state = STATE.FALL

        self.stage.update_stage()

        self.was_data = sen.mapped_data()
        # RELOAD POSITION TO DEBUG
        if 150 < self.player_y:
            self.init_player()
            self.stage.init_stage()

        # screen transition
        if pyxel.btn(pyxel.KEY_R):
            self.is_dead = True
            self.is_sensing = False
        else:
            self.is_dead = False
        if self.is_dead:
            # del sen
            self.stage.init_stage()
            self.title_count += 1
            self.selected_sensor = SELECT.NONE
            self.was_gamemode = SHOWMODE.Main
            self.now_gamemode = SHOWMODE.SceneChange

        if self.player_x+self.player_size_x == self.stage.goal_pos[0]+16 or pyxel.btn(pyxel.KEY_K):
            self.is_game_clear = True
            self.init_ending()
            self.was_gamemode = SHOWMODE.Main
            self.now_gamemode = SHOWMODE.SceneChange

    def init_ending(self):
        self.grats_x = [i for i in range(200, 270, 5)]
        self.grats_y = [72 + random.randint(-1, 1) for i in range(14)]
        self.seconds = 0
        self.GUIDE_QUIT = False

    def update_ending(self):
        if not self.once_called:
            self.once_called = True
            self.now_frame = pyxel.frame_count % 10
        if self.grats_x[0] > 64:
            if (pyxel.frame_count - self.now_frame)%10 == 0:
                for i in range(14):
                    self.grats_x[i] -= 10
                    self.grats_y[i] += random.randint(-1, 1)
        else:
            for i in range(14):
                self.grats_y[i] = 72
        if (pyxel.frame_count - self.now_frame)%60 == 0:
            self.seconds += 1
        if self.seconds >= 7:
            self.GUIDE_QUIT = True
        else:
            self.GUIDE_QUIT = False
    def draw(self):
        if self.now_gamemode == SHOWMODE.SceneChange:
            self.draw_scene_change()
        elif self.now_gamemode == SHOWMODE.Title:
            self.draw_title()
        elif self.now_gamemode == SHOWMODE.Main:
            self.draw_main()
        elif self.now_gamemode == SHOWMODE.Start:
            self.draw_start()
        elif self.now_gamemode == SHOWMODE.End:
            self.draw_ending()

    def draw_scene_change(self):
        if self.scene_change_p == SCENECHANGE.FIRST:
            # clipping short side
            pyxel.rect(0, 15, 20, 120, self.RECT_COLOR)
            pyxel.rect(180, 15, 20, 120, self.RECT_COLOR)
            # clipping long side
            pyxel.rect(0, 0, 200, 15, self.RECT_COLOR)
            pyxel.rect(0, 135, 200, 15, self.RECT_COLOR)
        elif self.scene_change_p == SCENECHANGE.SECOND:
            # clipping short side
            pyxel.rect(20, 30, 20, 90, self.RECT_COLOR)
            pyxel.rect(160, 30, 20, 90, self.RECT_COLOR)
            # clipping long side
            pyxel.rect(20, 15, 160, 15, self.RECT_COLOR)
            pyxel.rect(20, 120, 160, 15, self.RECT_COLOR)
        elif self.scene_change_p == SCENECHANGE.THIRD:
            # clipping short side
            pyxel.rect(40, 45, 20, 60, self.RECT_COLOR)
            pyxel.rect(140, 45, 20, 60, self.RECT_COLOR)
            # clipping long side
            pyxel.rect(40, 30, 120, 15, self.RECT_COLOR)
            pyxel.rect(40, 105, 120, 15, self.RECT_COLOR)
        elif self.scene_change_p == SCENECHANGE.FOURTH:
            # clipping short side
            pyxel.rect(60, 60, 20, 30, self.RECT_COLOR)
            pyxel.rect(120, 60, 20, 30, self.RECT_COLOR)
            # clipping long side
            pyxel.rect(60, 45, 80, 15, self.RECT_COLOR)
            pyxel.rect(60, 90, 80, 15, self.RECT_COLOR)
        elif self.scene_change_p == SCENECHANGE.FIFTH:
            # clipping long side
            pyxel.rect(80, 60, 40, 30, self.RECT_COLOR)

    def draw_start(self):
        pyxel.cls(self.BACKGROUND)
        if not self.is_dead:
            pyxel.text(60, 120, "PRESS SPACE TO START", self.COLOR_PALLET["BLUE"])
        else:
            pyxel.text(58, 120, "PRESS SPACE TO RE:SET", self.COLOR_PALLET["RED"])

    def draw_title(self):
        pyxel.cls(self.BACKGROUND)
        if self.was_gamemode == SHOWMODE.Main:
            pyxel.text(25, 20, "NEW GAME+", 8)
        pyxel.blt(80, 20, self.TOFU, 25, 0, 63, 16, self.BACKGROUND)
        # show sentence for introducing
        pyxel.text(35, 50, "SELECT SENSORS WHAT YOU WANNA PLAY",
                   self.random_color(self.GAMEMESSAGE, self.title_count + 1, self.BACKGROUND))
        pyxel.text(50, 70, "D:Distance, T:Temperature,",
                   self.random_color(self.GAMEMESSAGE, self.title_count + 2, self.BACKGROUND))
        pyxel.text(62, 80, "L:Light, P:Pressure",
                   self.random_color(self.GAMEMESSAGE, self.title_count + 2, self.BACKGROUND))
        pyxel.text(60, 95, "PRESS SPACE TO READY",
                   self.random_color(self.GAMEMESSAGE, self.title_count + 3, self.BACKGROUND))
        # show images for introducing
        # show candle
        pyxel.blt(110, 113, self.LOGO, 0, 0, 32, 32, self.BACKGROUND)
        if self.selected_sensor == SELECT.LIGHT and pyxel.frame_count % 60 >= 30:
            pyxel.blt(110, 108, self.LOGO, 32, 28, 32, 4, self.BACKGROUND)
            pyxel.blt(110, 145, self.LOGO, 32, 28, 32, 4, self.BACKGROUND)
        # show ruler
        pyxel.blt(20, 123, self.LOGO, 0, 40, 32, 16, self.BACKGROUND)
        if self.selected_sensor == SELECT.DISTANCE and pyxel.frame_count % 60 >= 30:
            pyxel.blt(20, 108, self.LOGO, 32, 28, 32, 4, self.BACKGROUND)
            pyxel.blt(20, 145, self.LOGO, 32, 28, 32, 4, self.BACKGROUND)
        # show thermometer
        pyxel.blt(70, 113, self.LOGO, 8, 64, 16, 32, self.BACKGROUND)
        if self.selected_sensor == SELECT.TEMPERATURE and pyxel.frame_count % 60 >= 30:
            pyxel.blt(66, 108, self.LOGO, 32, 28, 24, 4, self.BACKGROUND)
            pyxel.blt(66, 145, self.LOGO, 32, 28, 24, 4, self.BACKGROUND)
        # show hand
        pyxel.blt(160, 113, self.LOGO, 0, 96, 32, 32, self.BACKGROUND)
        if self.selected_sensor == SELECT.PRESSURE and pyxel.frame_count % 60 >= 30:
            pyxel.blt(157, 108, self.LOGO, 32, 28, 32, 4, self.BACKGROUND)
            pyxel.blt(157, 145, self.LOGO, 32, 28, 32, 4, self.BACKGROUND)

    def draw_main(self):
        pyxel.cls(self.BACKGROUND)
        # green back for debugging
        # pyxel.rect(0, self.FIELD_Y, pyxel.width, pyxel.height - self.FIELD_Y, self.STAGE_GROUND)
        self.stage.draw_stage()
        if self.player_state == STATE.NONE and self.is_on_ground:
            if pyxel.frame_count % 60 < 15:
                self.DOT_16 = 0
            elif pyxel.frame_count % 60 < 30:
                self.DOT_16 = 1
            elif pyxel.frame_count % 60 < 45:
                self.DOT_16 = 2
            elif pyxel.frame_count % 60 < 59:
                self.DOT_16 = 3
            pyxel.blt(self.player_x, self.player_y, self.TOFU, 16 * self.DOT_16, self.TOFU_NONE, self.player_size_x,
                      self.player_size_y, self.player_colkey)

        elif self.player_state == STATE.WALKING:
            if pyxel.frame_count % 60 < 15:
                self.DOT_16 = 0
            elif pyxel.frame_count % 60 < 30:
                self.DOT_16 = 1
            elif pyxel.frame_count % 60 < 45:
                self.DOT_16 = 2
            elif pyxel.frame_count % 60 < 60:
                self.DOT_16 = 3
            pyxel.blt(self.player_x, self.player_y, self.TOFU, 16 * self.DOT_16, self.TOFU_NONE, self.player_size_x,
                      self.player_size_y, self.player_colkey)

        elif self.player_state == STATE.FLYING:
            if pyxel.frame_count % 60 < 20:
                self.DOT_16 = 1
            elif pyxel.frame_count % 60 < 40:
                self.DOT_16 = 2
            elif pyxel.frame_count % 60 < 60:
                self.DOT_16 = 3
            pyxel.blt(self.player_x, self.player_y, self.TOFU, 16 * self.DOT_16, self.TOFU_FLY, self.player_size_x,
                      self.player_size_y, self.player_colkey)

        elif self.player_state == STATE.GLIDE:
            if not self.is_on_ground:
                if pyxel.frame_count % 60 < 20:
                    self.DOT_16 = 0
                elif pyxel.frame_count % 60 < 40:
                    self.DOT_16 = 1
                elif pyxel.frame_count % 60 < 60:
                    self.DOT_16 = 2
            pyxel.blt(self.player_x, self.player_y, self.TOFU, 16 * self.DOT_16, self.TOFU_GLIDE, self.player_size_x,
                      self.player_size_y, self.player_colkey)

        elif self.player_state == STATE.FALL:
            if pyxel.frame_count % 60 < 15:
                self.DOT_16 = 3
            elif pyxel.frame_count % 60 < 30:
                self.DOT_16 = 2
            elif pyxel.frame_count % 60 < 45:
                self.DOT_16 = 1
            elif pyxel.frame_count % 60 < 60:
                self.DOT_16 = 0
            pyxel.blt(self.player_x, self.player_y, self.TOFU, 16 * self.DOT_16, self.TOFU_NONE, 16, 16,
                      self.player_colkey)

    def draw_ending(self):
        pyxel.cls(self.COLOR_PALLET["BLACK"])
        #C O N G R A T U L A T I O N's are drawn by blt
        pyxel.text(self.grats_x[0], self.grats_y[0],"C", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[1], self.grats_y[1], "O", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[2], self.grats_y[2], "N", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[3], self.grats_y[3], "G", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[4], self.grats_y[4], "R", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[5], self.grats_y[5], "A", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[6], self.grats_y[6], "T", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[7], self.grats_y[7], "U", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[8], self.grats_y[8], "L", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[9], self.grats_y[9], "A", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[10], self.grats_y[10], "T", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[11], self.grats_y[11], "I", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[12], self.grats_y[12], "O", self.COLOR_PALLET["WHITE"])
        pyxel.text(self.grats_x[13], self.grats_y[13], "N", self.COLOR_PALLET["WHITE"])
        if self.GUIDE_QUIT:
            pyxel.text(57, 120, "PUSH Q TO QUIT GAME", self.COLOR_PALLET["RED"])

    def random_color(self, def_num, rand_index, back_col):
        def_num += rand_index
        if back_col == def_num:
            def_num += 1
            return def_num
        else:
            return def_num


class Stage:
    def __init__(self):
        self.temp_x = 0
        self.temp_y = 0
        self.temp_gap = 0
        self.is_early = True
        self.BACKGROUND = 0
        self.GROUND = 102
        self.GAP_Y_LENGTH = 48
        self.COLUMS_3 = [[0, 10, 10, 6], [16, 10, 8, 6], [24, 10, 6, 6], [32, 10, 4, 6], [40, 10, 2, 6]]
        self.COLUMS_2 = [[48, 12, 10, 4], [64, 12, 8, 4], [72, 12, 6, 4], [80, 12, 4, 4], [88, 12, 2, 4]]
        self.COLUMS_1 = [[96, 14, 10, 2], [112, 14, 8, 2], [120, 14, 6, 2], [128, 14, 4, 2], [136, 14, 2, 2]]
        self.init_stage()

    def init_stage(self):
        self.spawn_size = [4, 3]
        self.spawn_pos = [0, 102]
        self.is_goal = False
        self.goal_size = [3, 3]
        self.goal_pos = [0, 102]
        self.goal_gap_size = 5
        self.goal_gap_pos = 0
        self.near_block = NEAR_BLOCK.BLOCK1
        self.gen_times = 0
        self.set_random()
        self.gap_1_size = self.temp_gap
        self.gap_1_pos = self.spawn_pos[0] + self.spawn_size[0] * 16
        self.block_1_size = [self.temp_x, self.temp_y]
        self.block_1_pos = [self.gap_1_pos + self.gap_1_size * 16, 150 - self.temp_y * 16]
        if self.temp_y == 3:
            self.block_1_tile = self.COLUMS_3[5 - self.temp_x]
        elif self.temp_y == 2:
            self.block_1_tile = self.COLUMS_2[5 - self.temp_x]
        elif self.temp_y == 1:
            self.block_1_tile = self.COLUMS_1[5 - self.temp_x]
        self.set_random()
        self.gap_2_size = self.temp_gap
        self.gap_2_pos = self.block_1_pos[0] + self.block_1_size[0] * 16
        self.block_2_size = [self.temp_x, self.temp_y]
        self.block_2_pos = [self.gap_2_pos + self.gap_2_size * 16, 150 - self.temp_y * 16]
        if self.temp_y == 3:
            self.block_2_tile = self.COLUMS_3[5 - self.temp_x]
        elif self.temp_y == 2:
            self.block_2_tile = self.COLUMS_2[5 - self.temp_x]
        elif self.temp_y == 1:
            self.block_2_tile = self.COLUMS_1[5 - self.temp_x]
        self.set_random()
        self.gap_3_size = self.temp_gap
        self.gap_3_pos = self.block_2_pos[0] + self.block_2_size[0] * 16
        self.block_3_size = [self.temp_x, self.temp_y]
        self.block_3_pos = [self.gap_3_pos + self.gap_3_size * 16, 150 - self.temp_y * 16]
        if self.temp_y == 3:
            self.block_3_tile = self.COLUMS_3[5 - self.temp_x]
        elif self.temp_y == 2:
            self.block_3_tile = self.COLUMS_2[5 - self.temp_x]
        elif self.temp_y == 1:
            self.block_3_tile = self.COLUMS_1[5 - self.temp_x]

    def set_random(self):
        self.temp_gap = random.randint(3, 8)
        self.temp_x = random.randint(1, 5)
        self.temp_y = random.randint(1, 3)

    def update_stage(self):
        if not self.is_goal:
            if self.spawn_pos[0] + self.spawn_size[0] * 16 < 0:
                self.is_early = False
            else:
                self.is_early = True
            if self.gap_1_pos + self.gap_1_size * 16 < 0:
                self.set_random()
                self.gap_1_size = self.temp_gap
                self.gap_1_pos = self.block_3_pos[0] + self.block_3_size[0] * 16
            elif self.block_1_pos[0] + self.block_1_size[0] * 16 < 0:
                self.set_random()
                self.block_1_size = [self.temp_x, self.temp_y]
                self.block_1_pos = [self.gap_1_pos + self.gap_1_size * 16, 150 - self.temp_y * 16]
                if self.temp_y == 3:
                    self.block_1_tile = self.COLUMS_3[5 - self.temp_x]
                elif self.temp_y == 2:
                    self.block_1_tile = self.COLUMS_2[5 - self.temp_x]
                elif self.temp_y == 1:
                    self.block_1_tile = self.COLUMS_1[5 - self.temp_x]
            elif self.gap_2_pos + self.gap_2_size * 16 < 0:
                self.set_random()
                self.gap_2_size = self.temp_gap
                self.gap_2_pos = self.block_1_pos[0] + self.block_1_size[0] * 16
            elif self.block_2_pos[0] + self.block_2_size[0] * 16 < 0:
                self.set_random()
                self.block_2_size = [self.temp_x, self.temp_y]
                self.block_2_pos = [self.gap_2_pos + self.gap_2_size * 16, 150 - self.temp_y * 16]
                if self.temp_y == 3:
                    self.block_2_tile = self.COLUMS_3[5 - self.temp_x]
                elif self.temp_y == 2:
                    self.block_2_tile = self.COLUMS_2[5 - self.temp_x]
                elif self.temp_y == 1:
                    self.block_2_tile = self.COLUMS_1[5 - self.temp_x]
            elif self.gap_3_pos + self.gap_3_size * 16 < 0:
                self.set_random()
                self.gap_3_size = self.temp_gap
                self.gap_3_pos = self.block_2_pos[0] + self.block_2_size[0] * 16
            elif self.block_3_pos[0] + self.block_3_size[0] * 16 < 0:
                self.set_random()
                self.block_3_size = [self.temp_x, self.temp_y]
                self.block_3_pos = [self.gap_3_pos + self.gap_3_size * 16, 150 - self.temp_y * 16]
                self.gen_times += 1
                if self.temp_y == 3:
                    self.block_3_tile = self.COLUMS_3[5 - self.temp_x]
                elif self.temp_y == 2:
                    self.block_3_tile = self.COLUMS_2[5 - self.temp_x]
                elif self.temp_y == 1:
                    self.block_3_tile = self.COLUMS_1[5 - self.temp_x]

        if self.block_1_pos[0]+16 == 16:
            self.near_block = NEAR_BLOCK.BLOCK2
        if self.block_2_pos[0]+16 == 16:
            self.near_block = NEAR_BLOCK.BLOCK3
        if self.block_3_pos[0]+16 == 16:
            self.near_block = NEAR_BLOCK.BLOCK1

        if self.gen_times == 1:
            self.is_goal = True
            self.goal_gap_pos = self.block_3_pos[0]+self.block_3_size[0]*16
            self.goal_pos[0] = self.goal_gap_pos+self.goal_gap_size*16


        ''''
        #block size monitor
        if pyxel.frame_count % 60 == 0:
            print('-----')
            print('gap_1: ' + str(self.gap_1_size))
            print('blc_1: ' + str(self.block_1_size))
            print('     : ' + str(self.block_1_tile))
            print('gap_2: ' + str(self.gap_2_size))
            print('blc_2: ' + str(self.block_2_size))
            print('     : ' + str(self.block_2_tile))
            print('gap_3: ' + str(self.gap_3_size))
            print('blc_3: ' + str(self.block_3_size))
            print('     : ' + str(self.block_3_tile))
        '''


    def draw_stage(self):
        # spawn point
        if self.is_early:
            pyxel.bltm(self.spawn_pos[0], self.spawn_pos[1], 0, 0, 0, 8, 6, self.BACKGROUND)
        # pyxel.blt()
        pyxel.bltm(self.block_1_pos[0], self.block_1_pos[1], 0, self.block_1_tile[0], self.block_1_tile[1],
                   self.block_1_tile[2], self.block_1_tile[3], self.BACKGROUND)
        pyxel.rect(self.gap_1_pos, self.GROUND, self.gap_1_size * 16, self.GAP_Y_LENGTH, self.BACKGROUND)
        pyxel.bltm(self.block_2_pos[0], self.block_2_pos[1], 0, self.block_2_tile[0], self.block_2_tile[1],
                   self.block_2_tile[2], self.block_2_tile[3], self.BACKGROUND)
        pyxel.rect(self.gap_2_pos, self.GROUND, self.gap_2_size * 16, self.GAP_Y_LENGTH, self.BACKGROUND)
        pyxel.bltm(self.block_3_pos[0], self.block_3_pos[1], 0, self.block_3_tile[0], self.block_3_tile[1],
                   self.block_3_tile[2], self.block_3_tile[3], self.BACKGROUND)
        pyxel.rect(self.gap_3_pos, self.GROUND, self.gap_3_size * 16, self.GAP_Y_LENGTH, self.BACKGROUND)
        if self.is_goal:
            #goal gap
            pyxel.rect(self.goal_gap_pos, self.GROUND, self.goal_gap_size*16, self.GAP_Y_LENGTH, self.BACKGROUND)
            #goal block
            pyxel.bltm(self.goal_pos[0], self.goal_pos[1], 0, 144, 10, 6, 6, self.BACKGROUND)
            #goal flag
            pyxel.blt(self.goal_pos[0]+16, 6, 0, 0, 160, 16, 96, self.BACKGROUND)

    def move_stage(self, dx):
        self.spawn_pos[0] += dx
        self.block_1_pos[0] += dx
        self.gap_1_pos += dx
        self.block_2_pos[0] += dx
        self.gap_2_pos += dx
        self.block_3_pos[0] += dx
        self.gap_3_pos += dx
        if self.is_goal:
            self.goal_pos[0] += dx
            self.goal_gap_pos += dx


App()
