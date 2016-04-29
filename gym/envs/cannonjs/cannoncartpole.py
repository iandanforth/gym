import os
import math
import gym
import time
import json
from gym import spaces
import numpy as np
from selenium import webdriver

class CannonCartPoleEnv(gym.Env):
    metadata = {
        'render.modes': ['human']
    }

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.path = os.path.dirname(os.path.abspath(__file__))

        # Load javascript step function template
        stepJSPath = os.path.join(self.path, 'assets', 'step.js')
        with open(stepJSPath) as fh:
            self.jsStepFunctionTemplate = fh.read()

        self.indexPath = os.path.join(self.path, 'assets', 'index.html')
        self.driver.get("file://" + self.indexPath)
        time.sleep(1)

    def _jsStep(self, action):
        jsStepFunction = self.jsStepFunctionTemplate.format(stepNum=1)
        stepJSON = self.driver.execute_script(jsStepFunction)
        stepValue = json.loads(stepJSON)
        return stepValue, "foo", "bar", "baz"

    def _step(self, action):
        time.sleep(1)
        return
        return self._jsStep(action)

    def _reset(self):
        return []

    def _render(self, mode='human', close=False):

        if close:
            self.driver.quit()
        else:
            pass
