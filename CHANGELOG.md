# Changelog

All notable changes to gym-zombie-shooter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-03-28

### Added
- 3-second controls instruction screen for human players on first step
- Controls screen displays: WASD movement, SPACE fire, TAB gun switch, ESC pause

### Fixed
- Re-enabled gun switching (TAB key) for human players
- Gun switching remains disabled for RL agents (action 5 has no effect for AI)

## [0.1.1] - 2026-03-28

### Added
- Auto-scaling feature for high-DPI displays (4K/5K monitors)
- Detects screen resolution and scales window to 70% of screen height for displays > 1200p
- New `auto_scale` parameter (default: True) to control auto-scaling behavior
- Graceful fallback to default window size if auto-detection fails

### Changed
- Window size now dynamically adjusts based on display resolution
- Improved user experience on high-resolution monitors

### Removed
- Cleaned up old training files from main repo (moved to validate/ or examples repo)
- Removed: agent.py, buffer.py, main.py, model.py, test.py, train.py, test_training.py

## [0.1.0] - 2026-03-27

### Added
- Initial pip-installable package structure
- Gymnasium environment registration as "ZombieShooter-v1"
- Package resources using importlib.resources for proper asset loading
- Comprehensive setup.py with package metadata and dependencies
- PyPI-ready configuration (pyproject.toml, MANIFEST.in, setup.cfg)
- MIT License
- Complete README with installation and usage instructions
- Test suite for environment validation
- Console entry point: `zombie-shooter-play`

### Changed
- Migrated from standalone project to pip-installable package
- Restructured as zombie_shooter_gym package
- Fixed missing observation_space definition
- Added proper metadata dict to environment
- Changed observation returns from torch tensors to numpy arrays
- Updated all asset loading to use package resources instead of hardcoded paths

### Fixed
- Added missing observation_space (Box with shape (1, 128, 128))
- Fixed resource loading for images and sounds in packaged environment

## Project Structure

```
zombie-shooter-gym-v1/           # Main package repository
├── zombie_shooter_gym/          # Installable package
│   ├── __init__.py             # Environment registration
│   ├── envs/                   # Environment implementations
│   ├── core/                   # Game mechanics (assets, bullets, walls, utils)
│   └── resources/              # Images and sounds
├── validate/                    # RL training code (reference, not installed)
├── tests/                      # Test suite
└── examples/                   # Usage examples (in separate repo)

gym-zombie-shooter-examples/    # Separate examples repository
├── 01_basic_usage.py
├── 02_random_agent.py
├── 03_train_dqn.py
├── 04_test_model.py
└── 05_human_play.py
```

## Development Workflow

**Branch Strategy:**
- `main` - Stable releases
- `develop` - Active development

**Release Process:**
1. Make changes on develop branch
2. Update version in setup.py and __init__.py
3. Commit with descriptive message
4. Build: `python setup.py sdist bdist_wheel`
5. Verify: `twine check dist/*`
6. Push to GitHub: `git push origin develop`
7. Upload to TestPyPI: `twine upload --repository testpypi dist/*`

**TestPyPI Location:**
https://test.pypi.org/project/gym-zombie-shooter/

**GitHub Repository:**
https://github.com/bobcowher/zombie-shooter-gym-v1

**Examples Repository:**
https://github.com/bobcowher/gym-zombie-shooter-examples

## Key Decisions

1. **Package Naming**: gym-zombie-shooter (PyPI) / zombie_shooter_gym (Python import)
   - Follows RL community convention (gym-super-mario-bros pattern)

2. **validate/ Folder**: RL training code stays outside main package
   - Users can reference it but it's not installed
   - Keeps base package lightweight (~100MB vs heavy torch dependencies)

3. **MIT License**: Permissive open source license

4. **Resource Loading**: importlib.resources for proper package resource management
   - Works correctly when installed via pip
   - No hardcoded paths

5. **Human vs RL Modes**:
   - Human mode: render_mode="human", full features including gun switching
   - RL mode: render_mode=None or "rgb_array", gun switching disabled

6. **Auto-scaling**: Enabled by default for better UX on modern displays
   - Can be disabled with auto_scale=False parameter

## Installation

**From TestPyPI (for testing):**
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple gym-zombie-shooter
```

**Development (local):**
```bash
cd zombie-shooter-gym-v1
pip install -e .
```

**With training dependencies:**
```bash
pip install -e ".[rl]"
```

## Usage

```python
import gymnasium as gym
import zombie_shooter_gym

# Create environment
env = gym.make('ZombieShooter-v1', render_mode='human')

# Reset and play
obs, info = env.reset()
for _ in range(1000):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        obs, info = env.reset()

env.close()
```

## Next Steps

- Continue iterative improvements on develop branch
- Add more features as requested
- Eventually publish to main PyPI (when ready)
- Consider additional documentation or tutorials

## Author

Robert Cowher (with contributions from Jason Mosley)
