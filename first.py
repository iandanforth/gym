#!/usr/bin/python
import gym
import time

if __name__ == '__main__':

    env = gym.make('CannonCartPole-v0')
    env.reset()
    startTime = time.time()
    for i in xrange(60 * 5):
        # time.sleep(0.2)
        if i % 2 == 0:
            action = 1
        else:
            action = 0
        observation, reward, done, info = env.step(action)
        # if done == True:
        #     break
        print observation, reward, done, info
        # if i > 410:
        #     time.sleep(20)
    print time.time() - startTime
    env.render(close=True)
