import gym
from gym import spaces
from gym_fast_envs.catcher import Catcher


class FastEnvsCatcher(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, game_name='Catcher', display_screen=False,
                 level=2, width=24, height=24, seed=42, meta_level=0):

        self.game = Catcher(level, width, height, meta_level)
        print("Initialize Catcher-v0: level=%d, angle=%d, size=%dpx meta_level=%d." %
              (level, self.game.ball.angle, width, meta_level))

        self._action_set = self.game.get_action_set()
        self.action_space = spaces.Discrete(len(self._action_set))
        self.screen_width, self.screen_height = self.game.get_screen_dims()
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(self.screen_width, self.screen_height, 3))
        self.viewer = None

    def _step(self, action):
        observation, reward, terminal, info = self.game.step(action)
        return observation, reward, terminal, info

    def _get_image(self):
        return self.game.get_screen()

    @property
    def _n_actions(self):
        return len(self._action_set)

    def _reset(self):
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(self.screen_width, self.screen_height, 3))
        observation, reward, done, info = self.game.reset()
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
