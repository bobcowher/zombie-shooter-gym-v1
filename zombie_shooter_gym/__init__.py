"""Zombie Shooter Gymnasium Environment."""

from gymnasium.envs.registration import register

from zombie_shooter_gym.envs.zombie_shooter import ZombieShooter

__version__ = "0.1.2"

register(
    id="ZombieShooter-v1",
    entry_point="zombie_shooter_gym.envs:ZombieShooter",
    max_episode_steps=10000,
)

__all__ = ["ZombieShooter"]
