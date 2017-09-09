import gym

env = gym.make('FxEnv-v0')

Episodes = 1

obs = []

for _ in range(Episodes):
    observation = env.reset()
    done = False
    count = 0
    while not done:
        action = env.action_space.sample()  # random
        observation, reward, done, info = env.step(action)
        obs = obs + [observation]
        # print observation,reward,done,info
        count += 1
        if done:
            print(reward)
            print(count)

df = env.sim.to_df()

df.head()
df.tail()

buyhold = lambda x, y: 2
df = env.run_strat(buyhold)

df10 = env.run_strats(buyhold, Episodes)
