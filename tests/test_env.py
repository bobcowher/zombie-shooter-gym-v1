"""Basic tests for Zombie Shooter environment."""

import zombie_shooter_gym  # Import to register the environment
import gymnasium as gym
import numpy as np
import pytest


def test_env_creation():
    """Test that the environment can be created."""
    env = gym.make('ZombieShooter-v1', render_mode='rgb_array')
    assert env is not None
    env.close()


def test_observation_space():
    """Test that observation space is correctly defined."""
    env = gym.make('ZombieShooter-v1', render_mode='rgb_array')
    assert env.observation_space is not None
    assert env.observation_space.shape == (1, 128, 128)
    assert env.observation_space.dtype == np.uint8
    env.close()


def test_action_space():
    """Test that action space is correctly defined."""
    env = gym.make('ZombieShooter-v1', render_mode='rgb_array')
    assert env.action_space is not None
    assert env.action_space.n == 7
    env.close()


def test_reset():
    """Test that reset works and returns correct types."""
    env = gym.make('ZombieShooter-v1', render_mode='rgb_array')
    observation, info = env.reset()

    assert observation is not None
    assert isinstance(observation, np.ndarray)
    assert observation.shape == (1, 128, 128)
    assert observation.dtype == np.uint8

    assert info is not None
    assert isinstance(info, dict)
    assert 'health' in info
    assert 'shotgun_ammo' in info
    assert 'gun_type' in info

    env.close()


def test_step():
    """Test that step works and returns correct types."""
    env = gym.make('ZombieShooter-v1', render_mode='rgb_array')
    observation, info = env.reset()

    # Take a step with no-op action
    observation, reward, terminated, truncated, info = env.step(0)

    assert observation is not None
    assert isinstance(observation, np.ndarray)
    assert observation.shape == (1, 128, 128)

    assert isinstance(reward, (int, float))
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)

    assert isinstance(info, dict)
    assert 'health' in info
    assert 'shotgun_ammo' in info

    env.close()


def test_multiple_steps():
    """Test that we can take multiple steps without errors."""
    env = gym.make('ZombieShooter-v1', render_mode='rgb_array')
    observation, info = env.reset()

    for _ in range(100):
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)

        if terminated or truncated:
            observation, info = env.reset()

    env.close()


def test_all_actions():
    """Test that all actions can be taken without errors."""
    env = gym.make('ZombieShooter-v1', render_mode='rgb_array')
    observation, info = env.reset()

    # Test each action
    for action in range(env.action_space.n):
        observation, reward, terminated, truncated, info = env.step(action)
        assert observation is not None
        assert observation.shape == (1, 128, 128)

        if terminated or truncated:
            observation, info = env.reset()

    env.close()


def test_observation_values():
    """Test that observation values are in valid range."""
    env = gym.make('ZombieShooter-v1', render_mode='rgb_array')
    observation, info = env.reset()

    assert np.all(observation >= 0)
    assert np.all(observation <= 255)

    # Take a few steps and check observations
    for _ in range(10):
        observation, reward, terminated, truncated, info = env.step(1)
        assert np.all(observation >= 0)
        assert np.all(observation <= 255)

        if terminated or truncated:
            break

    env.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
