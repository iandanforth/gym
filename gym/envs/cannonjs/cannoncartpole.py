
# Standard Library
import sys
import os
import time
import json
import threading
import signal
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer

# Third Party
import gym
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

class CannonEnvRequestHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)
        # self.path = os.path.dirname(os.path.abspath(__file__))

class CannonCartPoleEnv(gym.Env):
    """
    CannonJS Cart Pole Environment.
    Note: All CannonJS envs must have render() called at least once.
    """
    metadata = {
        'render.modes': ['human']
    }

    def __init__(self):
        self.port = 8181
        self.path = os.path.dirname(os.path.abspath(__file__))

        # Render properties
        self.server = None
        self.driver = None
        self.indexPath = None
        self.jsStepFunctionTemplate = None

    def _jsStep(self, action):
        jsStepFunction = self.jsStepFunctionTemplate.format(stepNum=1)
        stepJSON = self.driver.execute_script(jsStepFunction)
        stepValue = json.loads(stepJSON)
        return stepValue, "foo", "bar", "baz"

    def _step(self, action):
        time.sleep(1)
        return "foo", "bar", "baz", "bing"
        # return self._jsStep(action)

    def _serverShutdown(self):
        self.server.shutdown()
        print("Webserver shutting down...")
        time.sleep(1)

    def _signalHandler(self, signal, frame):
        if self.server:
            self._serverShutdown()

        sys.exit(0)

    def _reset(self):
        return []

    def _render(self, mode='human', close=False):

        if close:
            self._serverShutdown()
            self.driver.quit()
        
        if not self.driver:
            # Register signal handler
            signal.signal(signal.SIGINT, self._signalHandler)

            # Launch a webserver
            self.server = HTTPServer(('', 8181), SimpleHTTPRequestHandler)
            thread = threading.Thread(target=self.server.serve_forever)
            thread.setdaemon = True
            thread.start()

            # Load the function we use to talk to in browser process
            stepJSPath = os.path.join(self.path, 'assets', 'step.js')
            with open(stepJSPath) as fh:
                self.jsStepFunctionTemplate = fh.read()

            # Launch a browser
            self.indexPath = os.path.join(self.path, 'assets', 'index.html')
            try:
                self.driver = webdriver.Firefox()
            except WebDriverException:
                # Requires installing ChromeDriver
                # http://chromedriver.storage.googleapis.com/index.html
                self.driver = webdriver.Chrome()

            self.driver.get("http://127.0.0.1:8181")
