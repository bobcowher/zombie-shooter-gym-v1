"""Minimal training script to test if the environment works with RL."""

import zombie_shooter_gym
import gymnasium as gym
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
import random

# Simple DQN Network
class SimpleDQN(nn.Module):
    def __init__(self, action_dim=7):
        super(SimpleDQN, self).__init__()

        # Convolutional layers for image processing
        self.conv1 = nn.Conv2d(1, 32, kernel_size=8, stride=4)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, stride=1)

        # Calculate size after convolutions (128x128 input)
        # After conv1: (128-8)/4 + 1 = 31
        # After conv2: (31-4)/2 + 1 = 14
        # After conv3: (14-3)/1 + 1 = 12
        # So: 64 * 12 * 12 = 9216

        self.fc1 = nn.Linear(9216, 512)
        self.fc2 = nn.Linear(512, action_dim)

    def forward(self, x):
        # x should be (batch, 1, 128, 128)
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.relu(self.conv3(x))
        x = x.view(x.size(0), -1)  # Flatten
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


# Simple Replay Buffer
class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            torch.FloatTensor(np.array(states)),
            torch.LongTensor(actions),
            torch.FloatTensor(rewards),
            torch.FloatTensor(np.array(next_states)),
            torch.FloatTensor(dones)
        )

    def __len__(self):
        return len(self.buffer)


def train_dqn():
    """Train a simple DQN on the Zombie Shooter environment."""

    # Hyperparameters
    EPISODES = 10
    MAX_STEPS = 500
    BATCH_SIZE = 32
    GAMMA = 0.99
    EPSILON_START = 1.0
    EPSILON_MIN = 0.1
    EPSILON_DECAY = 0.995
    LEARNING_RATE = 0.0001
    TARGET_UPDATE = 10

    # Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Create environment
    env = gym.make(
        'ZombieShooter-v1',
        window_width=800,
        window_height=600,
        world_width=1200,
        world_height=1200,
        fps=60,
        sound=False,
        render_mode='rgb_array'
    )

    print(f"Environment created")
    print(f"Observation space: {env.observation_space}")
    print(f"Action space: {env.action_space}")

    # Initialize networks
    policy_net = SimpleDQN(action_dim=env.action_space.n).to(device)
    target_net = SimpleDQN(action_dim=env.action_space.n).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()

    optimizer = optim.Adam(policy_net.parameters(), lr=LEARNING_RATE)
    replay_buffer = ReplayBuffer(capacity=10000)

    epsilon = EPSILON_START
    total_steps = 0

    print("\nStarting training...")
    print("-" * 60)

    for episode in range(EPISODES):
        obs, info = env.reset()
        episode_reward = 0
        episode_steps = 0

        for step in range(MAX_STEPS):
            # Epsilon-greedy action selection
            if random.random() < epsilon:
                action = env.action_space.sample()
            else:
                with torch.no_grad():
                    obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(device) / 255.0
                    q_values = policy_net(obs_tensor)
                    action = q_values.max(1)[1].item()

            # Take step
            next_obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            # Store transition
            replay_buffer.push(obs, action, reward, next_obs, done)

            obs = next_obs
            episode_reward += reward
            episode_steps += 1
            total_steps += 1

            # Train if enough samples
            if len(replay_buffer) >= BATCH_SIZE:
                states, actions, rewards, next_states, dones = replay_buffer.sample(BATCH_SIZE)

                # Move to device and normalize
                states = states.to(device) / 255.0
                actions = actions.to(device)
                rewards = rewards.to(device)
                next_states = next_states.to(device) / 255.0
                dones = dones.to(device)

                # Compute Q values
                current_q_values = policy_net(states).gather(1, actions.unsqueeze(1))

                # Compute target Q values
                with torch.no_grad():
                    next_q_values = target_net(next_states).max(1)[0]
                    target_q_values = rewards + (1 - dones) * GAMMA * next_q_values

                # Compute loss
                loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)

                # Optimize
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            if done:
                break

        # Update target network
        if episode % TARGET_UPDATE == 0:
            target_net.load_state_dict(policy_net.state_dict())

        # Decay epsilon
        epsilon = max(EPSILON_MIN, epsilon * EPSILON_DECAY)

        print(f"Episode {episode + 1}/{EPISODES} | "
              f"Steps: {episode_steps:3d} | "
              f"Reward: {episode_reward:6.1f} | "
              f"Epsilon: {epsilon:.3f} | "
              f"Health: {info['health']} | "
              f"Ammo: {info['shotgun_ammo']}")

    print("-" * 60)
    print("Training complete!")

    # Save model
    torch.save(policy_net.state_dict(), 'test_dqn_model.pt')
    print("Model saved to test_dqn_model.pt")

    env.close()


if __name__ == "__main__":
    train_dqn()
