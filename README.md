# Zombie Shooter Gym Environment

A [Gymnasium](https://gymnasium.farama.org/) environment for a top-down zombie shooter game. This environment can be used for reinforcement learning experiments or played by humans.

## Features

- **Gymnasium-compatible environment**: Standard `gym.Env` interface
- **Multiple game levels**: 3 progressively challenging levels with unique wall layouts
- **Weapon system**: Pistol and shotgun with limited ammo
- **Enemy AI**: Zombies with pathfinding and varying speeds
- **Survival mechanics**: Health system, healing items, and treasure chests
- **Human playable**: Play the game yourself using keyboard controls
- **Grayscale observations**: 128x128 grayscale images suitable for RL training

## Installation

### Local Development Installation

Clone the repository and install in editable mode:

```bash
git clone <repository-url>
cd zombie-shooter-gym-v1
pip install -e .
```

### Optional RL Dependencies

For reinforcement learning training (PyTorch, TensorBoard):

```bash
pip install -e ".[rl]"
```

### PyPI Installation (Coming Soon)

```bash
pip install gym-zombie-shooter
```

*Note: Package will be published to PyPI in the future.*

## Quick Start

### Basic Usage (RL)

```python
import gymnasium as gym

# Create the environment
env = gym.make('ZombieShooter-v1', render_mode='human')

# Reset environment
observation, info = env.reset()

# Game loop
done = False
while not done:
    # Take random action (0-6)
    action = env.action_space.sample()

    # Step environment
    observation, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated

env.close()
```

### Human Play

Play the game yourself using keyboard controls:

```bash
# Using CLI command
zombie-shooter-play

# Or run the example script
python examples/human_play.py
```

**Controls:**
- **W/A/S/D**: Move player (up/left/down/right)
- **Space**: Shoot
- **Tab**: Switch weapons (pistol/shotgun)
- **ESC**: Pause/Resume

## Environment Details

### Observation Space

- **Type**: `Box(low=0, high=255, shape=(1, 128, 128), dtype=uint8)`
- **Description**: Grayscale image of the game screen (128x128 pixels)

### Action Space

- **Type**: `Discrete(7)`
- **Actions**:
  - `0`: No-op (do nothing)
  - `1`: Move up
  - `2`: Move down
  - `3`: Move left
  - `4`: Move right
  - `5`: Shoot
  - `6`: Switch weapon

### Rewards

- **+50**: Kill a zombie
- **+25**: Open treasure chest (gain shotgun ammo)
- **+10**: Collect health drop
- **-10**: Take damage from zombie
- **+100**: Complete level
- **-100**: Die (game over)

### Episode Termination

- **Terminated**: Player dies (health reaches 0)
- **Truncated**: Level completed successfully

### Game Mechanics

- **Health**: Start with 100 HP, lose health from zombie bites
- **Weapons**:
  - Pistol: Infinite ammo, single shot
  - Shotgun: Limited ammo (collect from chests), 3-way spread shot
- **Enemies**: Zombies spawn periodically and pursue the player
- **Levels**: 3 levels with increasing difficulty (more zombies, complex layouts)

## Training with Reinforcement Learning

The `validate/` folder contains reference RL training code using Double DQN:

```python
# See validate/train.py for full training script
import gymnasium as gym
from validate.agent import Agent

env = gym.make('ZombieShooter-v1')
agent = Agent(state_size=(1, 128, 128), action_size=7)

# Training loop
for episode in range(num_episodes):
    state, _ = env.reset()
    # ... training logic
```

**Note**: The `validate/` folder is not part of the installed package but serves as a reference implementation for RL training.

## Project Structure

```
zombie-shooter-gym-v1/
├── zombie_shooter_gym/          # Main package
│   ├── envs/                    # Environment implementation
│   ├── core/                    # Game assets and mechanics
│   └── resources/               # Images and sounds
├── validate/                    # Reference RL training code
├── examples/                    # Example scripts
│   ├── basic_usage.py          # Simple RL example
│   └── human_play.py           # Human gameplay
└── tests/                       # Unit tests
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
pip install -e ".[dev]"
black zombie_shooter_gym/
flake8 zombie_shooter_gym/
```

## Requirements

- Python >= 3.8
- pygame >= 2.1.0
- gymnasium >= 0.26.0
- opencv-python >= 4.5.0
- numpy >= 1.20.0

## License

MIT License - see LICENSE file for details.

## Authors & Contributors

**Author:** Robert Cowher

**Contributors:**
- Jason Mosley

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Changelog

### Version 0.1.0 (2025-03-28)
- Initial release
- Gymnasium environment implementation
- 3 game levels
- Human playable mode
- Reference RL training code
