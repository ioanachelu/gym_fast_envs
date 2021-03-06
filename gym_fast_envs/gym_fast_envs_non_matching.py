import gym
from gym import spaces
from gym_fast_envs.non_matching import Gridworld_NonMatching
import numpy as np

class FastEnvsGridworldNonMatching(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, game_name='Gridworld', display_screen=False,
                 partial=False, size=5, nb_apples=1, nb_oranges=1, orange_reward=0, deterministic=False, seed=None):

        self.game = Gridworld_NonMatching(partial, size, nb_apples, nb_oranges, orange_reward, seed, deterministic)
        print("Initialize Gridworld_NonMatching: partial={}, size={}, seed={},"
              "nb_apples={}, nb_oranges={}, orange_reward={}, deterministic={}.".format(partial, size, seed,
                                                                      nb_apples, nb_oranges, orange_reward, deterministic))

        self.action_space = spaces.Discrete(self.game.actions)
        self.screen_width, self.screen_height = 200, 200
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(self.screen_width, self.screen_height, 3))
        self.viewer = None

    def _step(self, action):
        observation, obs_big, reward, terminal, info = self.game.step(action)
        return observation, reward, terminal, info

    def _get_image(self):
        return self.game.renderEnv()[1]

    @property
    def _n_actions(self):
        return self.game.actions

    def _reset(self):
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(self.screen_width, self.screen_height, 3))
        observation, _, _, info = self.game.reset()
        return observation, None, None, info

    def _render(self, mode='human', close=False):
        # pass
        # self.game.render()
        # if close:
        #     if self.viewer is not None:
        #         self.viewer.close()
        #         self.viewer = None
        #     return
        # img = self._get_image()
        # if mode == 'rgb_array':
        #     return img
        # elif mode == 'human':
        #     from gym.envs.classic_control import rendering
        #     if self.viewer is None:
        #         self.viewer = rendering.SimpleImageViewer()
        #     self.viewer.imshow(img)
        if close:
            if self.viewer is not None:
                self.viewer.close()
                self.viewer = None
            return
        state, state_big = self.game.renderEnv()
        img = state_big.astype(np.uint8)

        # img = Image.fromarray(state_big, 'RGB')
        # img = screen.resize((512, 512))
        # img = self._get_image()
        if mode == 'rgb_array':
            return img
        elif mode == 'human':
            from gym.envs.classic_control import rendering
            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            self.viewer.imshow(img)

    def _seed(self, seed):
        self.game.set_seed(seed)
