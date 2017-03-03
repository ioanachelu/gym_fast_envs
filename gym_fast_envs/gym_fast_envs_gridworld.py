import gym
from gym import spaces
from gym_fast_envs.gridworld import Gridworld


class FastEnvsGridworld(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, game_name='Gridworld', display_screen=False,
                 partial=False, size=5, seed=None):

        self.game = Gridworld(partial, size, seed)
        print("Initialize Gridworld-v0: partial={}, size={}, seed={}.".format(partial, size, seed))

        self._action_set = self.game.actions()
        self.action_space = spaces.Discrete(len(self.actions))
        self.screen_width, self.screen_height = size, size
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(self.screen_width, self.screen_height, 3))
        self.viewer = None

    def _step(self, action):
        observation, terminal, reward, info = self.game.step(action)
        return observation, reward, terminal, info

    def _get_image(self):
        return self.game.get_screen()

    @property
    def _n_actions(self):
        return len(self._action_set)

    def _reset(self):
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(self.screen_width, self.screen_height, 3))
        observation, done, reward, info = self.game.reset()
        return observation

    def _render(self, mode='human', close=False):
        if close:
            if self.viewer is not None:
                self.viewer.close()
                self.viewer = None
            return
        img = self._get_image()
        if mode == 'rgb_array':
            return img
        elif mode == 'human':
            from gym.envs.classic_control import rendering
            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            self.viewer.imshow(img)

    def _seed(self, seed):
        self.game.set_seed(seed)
