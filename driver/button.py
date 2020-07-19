# This file is part of MaixUI
# Copyright (c) sipeed.com
#
# Licensed under the MIT license:
#   http://www.opensource.org/licenses/mit-license.php
#

import sys
import time

from fpioa_manager import fm
from Maix import FPIOA, GPIO

BACK = 11
ENTER = 10
NEXT = 16

Limit = 1000  # 1s

Match = [[(1, 0), (1, 0)], [(2, 1), None]] # 0 1 1 2 0
#Match = [[None, (1, 0)], [(2, 1), None]]  # 0 1 0 0 2


class cube_button:
    def __init__(self):
        self.home_last, self.next_last, self.back_last = 1, 1, 1
        self.last_time, self.bak_time = 0, 0
        self.cache = {
            'home': 0,
            'next': 0,
            'back': 0,
        }
        self.pause_time = 0

        fm.register(ENTER, fm.fpioa.GPIOHS10)
        self.home_button = GPIO(GPIO.GPIOHS10, GPIO.IN, GPIO.PULL_UP)
        # if self.home_button.value() == 0:
        #     sys.exit()

        fm.register(BACK, fm.fpioa.GPIOHS11)
        self.back_button = GPIO(GPIO.GPIOHS11, GPIO.IN, GPIO.PULL_UP)

        fm.register(NEXT, fm.fpioa.GPIOHS16)
        self.next_button = GPIO(GPIO.GPIOHS16, GPIO.IN, GPIO.PULL_UP)

    def home(self):
        tmp, self.cache['home'] = self.cache['home'], 0
        return tmp

    def next(self):
        tmp, self.cache['next'] = self.cache['next'], 0
        return tmp

    def back(self):
        tmp, self.cache['back'] = self.cache['back'], 0
        return tmp

    def interval(self):
        tmp, self.last_time = self.last_time, 0
        return tmp

    def event(self):
        self.bak_time = time.ticks_ms()

        home_value = self.home_button.value()

        tmp = Match[home_value][self.home_last]
        if tmp:
            self.last_time = time.ticks_ms() - self.bak_time
            self.cache['home'], self.home_last = tmp

        tmp = Match[self.back_button.value()][self.back_last]
        if tmp:
            self.last_time = time.ticks_ms() - self.bak_time
            self.cache['back'], self.back_last = tmp

        tmp = Match[self.next_button.value()][self.next_last]
        if tmp:
            self.last_time = time.ticks_ms() - self.bak_time
            self.cache['next'], self.next_last = tmp

    def expand_event(self):

        tmp = self.home_button.value()
        if tmp == 0 and self.home_last == 1 and self.pause_time < time.ticks_ms():
            self.cache['home'], self.home_last, self.bak_time = 1, 0, time.ticks_ms()

        # (monkey patch) long press home 0 - 1 - 2 - 0 - 1 - 2 - 0
        if self.home_last == 0 and self.bak_time != 0 and time.ticks_ms() - self.bak_time > Limit:
            #print(tmp, self.home_last, self.pause_time, time.ticks_ms())
            self.cache['home'], self.home_last, self.last_time = 2, 1, time.ticks_ms(
            ) - self.bak_time
            self.pause_time = time.ticks_ms() + Limit

        if tmp == 1 and self.home_last == 0 and self.pause_time < time.ticks_ms():
            print(1)
            self.cache['home'], self.home_last, self.last_time = 2, 1, time.ticks_ms(
            ) - self.bak_time

        tmp = self.back_button.value()

        if tmp == 0 and self.back_last == 1:
            self.cache['back'], self.back_last, self.bak_time = 1, 0, time.ticks_ms()

        if self.bak_time != 0 and time.ticks_ms() - self.bak_time > Limit:
            tmp = not tmp

        if tmp == 1 and self.back_last == 0:
            self.cache['back'], self.back_last, self.last_time = 2, 1, time.ticks_ms(
            ) - self.bak_time

        tmp = self.next_button.value()

        if tmp == 0 and self.next_last == 1:
            self.cache['next'], self.next_last, self.bak_time = 1, 0, time.ticks_ms()

        if self.bak_time != 0 and time.ticks_ms() - self.bak_time > Limit:
            tmp = not tmp

        if tmp == 1 and self.next_last == 0:
            self.cache['next'], self.next_last, self.last_time = 2, 1, time.ticks_ms(
            ) - self.bak_time


PIR = 16


class ttgo_button:

    def __init__(self):
        self.home_last = 1
        self.cache = {
            'home': 0,
        }

        fm.register(PIR, fm.fpioa.GPIOHS16)
        self.home_button = GPIO(GPIO.GPIOHS16, GPIO.IN, GPIO.PULL_UP)

    def home(self):
        tmp, self.cache['home'] = self.cache['home'], 0
        return tmp

    def event(self):

        tmp = Match[self.home_button.value()][self.home_last]
        if tmp:
            self.cache['home'], self.home_last = tmp


if __name__ == "__main__":

    #tmp = ttgo_button()
    #while True:
    #tmp.event()
    #time.sleep_ms(200)
    #print(tmp.home())

    tmp = cube_button()
    while True:
        time.sleep_ms(200)
        tmp.event()
        print(tmp.back(), tmp.home(), tmp.next())
        #tmp.expand_event()
        #print(tmp.back(), tmp.home(), tmp.next(), tmp.interval())
