#!/usr/bin/python
import gym
import time

if __name__ == '__main__':

    env = gym.make('CannonCartPole-v0')
    env.reset()
    env.render()
    startTime = time.time()
    for i in xrange(60 * 10):
        env.step(i)
        # if i > 10:
        #     time.sleep(20)
    print time.time() - startTime
    env.render(close=True)
