from gym.envs.registration import registry, register, make, spec
# from catcher import Catcher

# Default
register(
    id='Catcher-v0',
    entry_point='gym_fast_envs.gym_fast_envs:FastEnvs',
    kwargs={'game_name': 'Catcher-v0', 'display_screen': False, 'level': 2, 'meta_level': 0},
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
                entry_point='gym_fast_envs.gym_fast_envs:FastEnvs',
                kwargs={'game_name': game, 'display_screen': False,
                        'level': level, 'width': size, 'height': size, 'meta_level': meta_level},
                tags={'wrapper_config.TimeLimit.max_episode_steps': 10000},
                nondeterministic=False,
            )
