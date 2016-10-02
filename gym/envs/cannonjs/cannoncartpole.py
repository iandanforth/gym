# Third Party
import math
import json
import numpy as np
from gym import spaces
from gym.envs.cannonjs.cannonjs_env import CannonJSEnv

class CannonCartPoleEnv(CannonJSEnv):
    """
    CannonJS Cart Pole Environment.
    """
    metadata = {
        'render.modes': ['human']
    }

    def __init__(self):
        super(CannonCartPoleEnv, self).__init__("cartpole")

        self.gravity = 9.8
        self.masscart = 1.0
        self.masspole = 0.1
        self.total_mass = (self.masspole + self.masscart)
        self.length = 0.5 # actually half the pole's length
        self.polemass_length = (self.masspole * self.length)
        self.force_mag = 10.0
        self.tau = 0.02  # seconds between state updates
        self.state = None

        # Angle at which to fail the episode
        self.theta_threshold_radians = 12 * 2 * math.pi / 360
        self.x_threshold = 2.4
        self.reset()
        self.viewer = None
        self.steps_beyond_done = None

        high = np.array([
            self.x_threshold,
            np.inf,
            self.theta_threshold_radians,
            np.inf]
        )
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(-high, high)

    def _step(self, action):
        assert action==0 or action==1, "%r (%s) invalid" % (action, type(action))
        force = self.force_mag if action==1 else -self.force_mag

        return self._jsStep(action)

    def _reset(self):
        self.state = np.random.uniform(low=-0.05, high=0.05, size=(4,))
        self.steps_beyond_done = None
        print("RESETTING!")
        self.driver.execute_script("reset();")
        return np.array(self.state)

    def _jsStep(self, action):
        jsStepFunction = self.jsStepFunctionTemplate.format(action=str(action))
        stepJSON = self.driver.execute_script(jsStepFunction)
        stepDict = json.loads(stepJSON)
        if not stepDict:
            stepDict = {"x": 0.0, "theta": 0.0}

        x = stepDict["x"]
        theta = stepDict["theta"]
        observation = np.array([x, x, theta, theta])

        # Determine if this episode is terminal
        done = x < -self.x_threshold \
            or x > self.x_threshold \
            or theta < -self.theta_threshold_radians \
            or theta > self.theta_threshold_radians
        done = bool(done)

        if not done:
            reward = 1.0
        elif self.steps_beyond_done is None:
            # Pole just fell!
            self.steps_beyond_done = 0
            reward = 1.0
        else:
            if self.steps_beyond_done == 0:
                print("You are calling 'step()' even though this environment has already returned done = True. You should always call 'reset()' once you receive 'done = True' -- any further steps are undefined behavior.")
            self.steps_beyond_done += 1
            reward = 0.0

        return observation, reward, done, {}
