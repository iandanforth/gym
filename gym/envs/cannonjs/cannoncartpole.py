# Third Party
from gym.envs.cannonjs.cannonjs_env import CannonJSEnv

class CannonCartPoleEnv(CannonJSEnv):
    """
    CannonJS Cart Pole Environment.
    """
    metadata = {
        'render.modes': ['human']
    }
