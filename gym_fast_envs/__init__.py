from gym.envs.registration import registry, register, make, spec
# from catcher import Catcher

# Default
register(
    id='Catcher-v0',
    entry_point='gym_fast_envs.gym_fast_envs_catcher:FastEnvsCatcher',
    kwargs={'game_name': 'CatcherFlorin-v0', 'display_screen': False, 'level': 0, 'meta_level': 0},
    tags={'wrapper_config.TimeLimit.max_episode_steps': 10000},
    nondeterministic=False,
)

register(
    id='CatcherPle-v0',
    entry_point='gym_fast_envs.gym_fast_envs_catcher_ple:FastEnvsCatcherPle',
    kwargs={'game_name': 'Catcher', 'display_screen': False},
    tags={'wrapper_config.TimeLimit.max_episode_steps': 10000},
    nondeterministic=False,
)

# Difficulty levels and sizes
for level in range(6):
    for size in (24, 32, 48):
        for meta_level in [0, 1, 2]:
            if size is 24:
                game = 'Catcher-Level%d-MetaLevel%d-v0' % (level, meta_level)
            else:
                game = 'Catcher-Level%d-MetaLevel%d-x%d-v0' % (level, meta_level, size)

            register(
                id=game,
                entry_point='gym_fast_envs.gym_fast_envs_catcher:FastEnvsCatcher',
                kwargs={'game_name': game, 'display_screen': False,
                        'level': level, 'width': size, 'height': size, 'meta_level': meta_level},
                tags={'wrapper_config.TimeLimit.max_episode_steps': 10000},
                nondeterministic=False,
            )

# Default
register(
    id='Gridworld-v0',
    entry_point='gym_fast_envs.gym_fast_envs_gridworld:FastEnvsGridworld',
    kwargs={'game_name': 'Gridworld-v0', 'display_screen': False, 'size': 5, 'orange_reward': 0},
    tags={'wrapper_config.TimeLimit.max_episode_steps': 10000},
    timestep_limit=10000,
    nondeterministic=False,
)

register(
    id='Gridworld-v1',
    entry_point='gym_fast_envs.gym_fast_envs_gridworld:FastEnvsGridworldNonMatching',
    kwargs={'game_name': 'Gridworld-v1', 'display_screen': False, 'size': 5, 'orange_reward': 0},
    tags={'wrapper_config.TimeLimit.max_episode_steps': 100},
    timestep_limit=10000,
    nondeterministic=False,
)


# sizes
for size in (10, 20, 30, 40, 50):
    game = 'Gridworld-x%d-v0' % (size)

    register(
        id=game,
        entry_point='gym_fast_envs.gym_fast_envs_gridworld:FastEnvsGridworld',
        kwargs={'game_name': game, 'display_screen': False, 'orange_reward': 0,
                'size': size},
        tags={'wrapper_config.TimeLimit.max_episode_steps': 10000},
        nondeterministic=False,
    )
