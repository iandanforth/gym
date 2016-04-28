import math
import gym
import time
from gym import spaces
import numpy as np
from selenium import webdriver

class CannonCartPoleEnv(gym.Env):
    metadata = {
        'render.modes': ['human']
    }

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://www.google.com")

    def _step(self, action):
        time.sleep(1)
        return [], 0.0, False, {}

    def _reset(self):
        return []

    def _render(self, mode='human', close=False):

        if close:
            self.driver.quit()
        else:
            pass
