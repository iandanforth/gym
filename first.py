#!/usr/bin/python
import gym

if __name__ == '__main__':

    env = gym.make('CannonCartPole-v0')
    env.reset()
    for _ in xrange(100):
        print env.step("foo")
    env.render(close=True)
