"""Basic usage example of the Zombie Shooter environment."""

import zombie_shooter_gym  # Register the environment
import gymnasium as gym

def main():
    # Create the environment
    env = gym.make('ZombieShooter-v1', render_mode='human')

    print("Starting Zombie Shooter environment...")
    print(f"Observation space: {env.observation_space}")
    print(f"Action space: {env.action_space}")
    print("\nActions:")
    print("  0: No-op")
    print("  1: Move up")
    print("  2: Move down")
    print("  3: Move left")
    print("  4: Move right")
    print("  5: Switch weapon (requires use_shotgun=True)")
    print("  6: Shoot")

    # Reset environment
    observation, info = env.reset()
    print(f"\nInitial observation shape: {observation.shape}")
    print(f"Initial info: {info}")

    # Run for a few episodes
    num_episodes = 3
    for episode in range(num_episodes):
        observation, info = env.reset()
        episode_reward = 0
        done = False

        print(f"\n--- Episode {episode + 1} ---")

        step_count = 0
        while not done and step_count < 1000:
            # Take random action
            action = env.action_space.sample()

            # Step environment
            observation, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            done = terminated or truncated
            step_count += 1

            if done:
                print(f"Episode ended after {step_count} steps")
                print(f"Total reward: {episode_reward}")
                print(f"Final health: {info['health']}")
                print(f"Final shotgun ammo: {info['shotgun_ammo']}")

    env.close()
    print("\nEnvironment closed.")

if __name__ == "__main__":
    main()
