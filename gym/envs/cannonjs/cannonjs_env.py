
# Standard Library
import sys
import os
import time
import json
import threading
import signal
import urllib
import posixpath
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer

# Third Party
import gym
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

class CannonEnvRequestHandler(SimpleHTTPRequestHandler):
    """
    SimpleHTTPRequestHandler modified so that it serves files from assets
    subdirectory rather than os.cwd()
    """

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.
        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.
        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        # Serve from assets rather than os.cwd
        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(path, "assets")
        for word in words:
            _, word = os.path.splitdrive(word)
            _, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path


def serversafe(func):
    def _serversafe(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except Exception:
            self.serverShutdown()
            raise
    return _serversafe

class CannonJSEnv(gym.Env):
    """
    CannonJS Physics and WebGL Rendering
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
        jsStepFunction = self.jsStepFunctionTemplate.format(action=str(action))
        stepJSON = self.driver.execute_script(jsStepFunction)
        stepValue = json.loads(stepJSON)
        # print stepValue
        return stepValue, "foo", "bar", "baz"

    def serverShutdown(self):
        if self.driver:
            self.driver.quit()

        if self.server:
            self.server.shutdown()
            print("Webserver shutting down...")
            time.sleep(0.5)

    def _signalHandler(self, signal, frame):
        self.serverShutdown()
        sys.exit(0)

    ##########################################################################
    # Core Methods

    @serversafe
    def step(self, action):
        super(CannonJSEnv, self).step(action)

    @serversafe
    def reset(self):
        super(CannonJSEnv, self).reset()

    @serversafe
    def render(self, *args, **kwargs):
        super(CannonJSEnv, self).render(*args, **kwargs)

    def _step(self, action):
        return self._jsStep(action)

    def _reset(self):
        return []

    def _render(self, mode='human', close=False):

        if close:
            self.serverShutdown()
            self.driver.quit()

        if not self.driver:
            # Register signal handler
            signal.signal(signal.SIGINT, self._signalHandler)

            # Launch a webserver
            self.server = HTTPServer(('', 8181), CannonEnvRequestHandler)
            thread = threading.Thread(target=self.server.serve_forever)
            thread.setdaemon = True
            thread.start()

            # Load the function we use to talk to in browser process
            stepJSPath = os.path.join(self.path, 'assets', 'js', 'step.js')
            with open(stepJSPath) as fh:
                self.jsStepFunctionTemplate = fh.read()

            # Launch a browser
            self.indexPath = os.path.join(self.path, 'assets', 'index.html')
            try:
                self.driver = webdriver.Chrome()
                # self.driver = webdriver.Firefox()
            except WebDriverException:
                # Requires installing ChromeDriver
                # http://chromedriver.storage.googleapis.com/index.html
                self.driver = webdriver.Chrome()

            self.driver.get('http://127.0.0.1:8181')
