import time
import threading
import subprocess
from ctypes import windll

from PIL import Image, ImageOps
import win32gui
import win32ui

import numpy as np

from ahk import AHK

COORDS = dict(
    A=(20, 70, 200, 93),
    B=(20, 70, 200, 90),
    C=(10, 90, 195, 105)
)

RESIZE = dict(
    A=(1200, 300),
    B=(1200, 300),
    C=(1200, 300)
)

RES_KEYS = ['A', 'B', 'C']

DESCENT_KEY = 0
IS_ACTIVE = 0

KO_PATH = "C:\Program Files (x86)\Steam\steamapps\common\Knight Online\Launcher.exe"


class AutoBot():

    def __init__(self, tesseract_fn):
        self.win = None
        self.is_active = False
        self.descent_key = None
        self.coords = None
        self.resize = None
        self.initial_coords = False
        self.tesseract = tesseract_fn
        self.ahk = AHK()
        self.screen_capturer = ScreenCapturer()
        self.current_distance = None

        self.win = self.ahk.find_window(title=b'Knight OnLine Client')

        thread = threading.Thread(target=self.calculate_distance, args=())
        thread.daemon = True
        thread.start()

    def start_knight_online(self):
        print('start_knight_online')
        if self.is_active:
            return False

        if self.win is None:
            subprocess.call(KO_PATH, shell=False)
            return False

        if self.coords is None and self.resize is None:
            self.set_resolution(resolution='A')

        if not self.initial_coords:
            self.config_origin()

        self.is_active = True
        return True

    def set_resolution(self, resolution):
        """
        :param resolution: value A, B or C depending on the resolution of game
        1920x1080, 1600x900, 1366x768 respectively
        :return: Nothing. This is only a set function
        """
        print('start_resolution')
        if resolution not in RES_KEYS:
            resolution = 'A'
        self.coords = COORDS[resolution]
        self.resize = RESIZE[resolution]

    def config_descent_key(self, key):
        """
        :param key: key to be assigned to Descent
        :return: True if key was assigned, False if process is active.
                  The process must be stopped before assign descent key
        """
        print('config_descent_key')
        if self.is_active:
            return False
        self.descent_key = key
        return True

    def config_origin(self):
        """
        :return: True if coordinates were correctly saved. False otherwise
        """
        print('config_origin')
        if self.win is not None:
            print('entrando por window')
            # self.win.activate()
            if self.coords is not None and self.resize is not None:
                print('entrando por coords y resize')
                while not self.initial_coords:
                    print('leyendo coords iniciales')
                    user_coords = self.screen_capturer.get_game_coordinates(
                        coordinates=self.coords,
                        resize=self.resize
                    )
                    readed_string = self.tesseract.image_to_string(user_coords)
                    print(readed_string)
                    self.initial_coords = validate_coordinates(
                        string_to_validate=readed_string
                    )
                print(self.initial_coords)
                return True
            else:
                return False

    def calculate_distance(self):
        print('calculate_distance')
        ind = 0
        cont = [False, False, False]
        while True:
            if self.is_active:
                time.sleep(0.01)
                actual_coords = False
                while not actual_coords:
                    actual_coords = self.screen_capturer.get_game_coordinates(
                        coordinates=self.coords,
                        resize=self.resize
                    )
                    actual_coords = validate_coordinates(
                        self.tesseract.image_to_string(actual_coords)
                    )
                self.current_distance = get_distance(self.initial_coords, actual_coords)
                print(
                    f'PosIni:\t{self.initial_coords}\tPostAct:\t{actual_coords}\tDistance:\t{self.current_distance:.2f}m'
                )
                ind = (ind + 1) % 3
                cont[ind] = self.current_distance > 19.99
                if all(cont):
                    self.ahk.key_press(str(self.descent_key))

    def should_descent(self):
        print('should_descent')
        if self.current_distance > 20:
            return True
        return False


# capture_window_region('Knight OnLine Client', 0, 0, 230, 90).show() full status bar
class ScreenCapturer:

    def __init__(self):
        """
        :param method: set 'active' for on screen game, 'inactive' for background call
        """
        self.app_name = 'Knight OnLine Client'

    def get_rectangle(self, coordinates):
        x, y, width, height = coordinates
        if self.app_name:
            hwnd = win32gui.FindWindow(None, self.app_name)
            left, top, right, bottom = win32gui.GetClientRect(hwnd)
            w = right - left  # windows size
            h = bottom - top  # windows size
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            save_bit_map = win32ui.CreateBitmap()
            save_bit_map.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(save_bit_map)
            windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 1)
            bmp_info = save_bit_map.GetInfo()
            bmp_str = save_bit_map.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmp_info['bmWidth'], bmp_info['bmHeight']),
                bmp_str,
                'raw',
                'BGRX',
                0,
                1
            )
            img = img.crop((x, y, width, height))
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
            return img

    def get_game_coordinates(self, coordinates, resize):
        """
        :param coordinates: coordinates of the game that has the player coordinates
        :param resize: the array to rescale
        :return: Game coordinates (abc, def), if fails returns False
        """
        img = self.get_rectangle(coordinates=coordinates)
        img = ImageOps.invert(img)
        img = img.resize(resize)

        return img

    def get_user_hp(self, coordinates, expand):
        pass

    def get_user_mp(self, coordinates, expand):
        pass


def get_distance(Point1, Point2):
    arr1, arr2 = np.array(Point1), np.array(Point2)
    return np.linalg.norm(arr2 - arr1)


def validate_coordinates(string_to_validate):
    coordinates = ''.join(filter(str.isdigit, string_to_validate))
    if len(coordinates) != 6:
        return False
    else:
        x, y = coordinates[:3], coordinates[3:]
        return int(x), int(y)
