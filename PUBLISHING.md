# Publishing Zombie Shooter Gym to PyPI

This guide walks you through publishing the package to PyPI.

## Prerequisites

✅ **Already Completed:**
- Package structure created
- `setup.py` and `pyproject.toml` configured
- Tests passing
- `build` and `twine` installed

**Still Need:**
1. PyPI account: https://pypi.org/account/register/
2. TestPyPI account: https://test.pypi.org/account/register/
3. API tokens for authentication (recommended over passwords)

## Step-by-Step Publishing Process

### Step 1: Pre-Publishing Checklist

Before publishing, verify:

```bash
# 1. All tests pass
pytest tests/ -v

# 2. Package installs locally
pip install -e .

# 3. Environment works
python -c "import zombie_shooter_gym; import gymnasium as gym; env = gym.make('ZombieShooter-v1'); print('✓ Works!')"
```

### Step 2: Update Version Number (if needed)

Edit version in:
- `setup.py` line 7: `version="0.1.0"`
- `pyproject.toml` line 6: `version = "0.1.0"`
- `zombie_shooter_gym/__init__.py` line 5: `__version__ = "0.1.0"`

For subsequent releases, follow semantic versioning:
- Bug fixes: `0.1.0` → `0.1.1`
- New features: `0.1.0` → `0.2.0`
- Breaking changes: `0.1.0` → `1.0.0`

### Step 3: Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info
```

### Step 4: Build Distribution Packages

```bash
# Build both wheel and source distributions
python -m build

# Or use the build script
./build.sh
```

This creates:
- `dist/zombie_shooter_gym-0.1.0-py3-none-any.whl` (wheel)
- `dist/gym-zombie-shooter-0.1.0.tar.gz` (source)

### Step 5: Check the Distribution

```bash
# Verify the built package
twine check dist/*
```

**Note:** You may see a warning about "unrecognized or malformed field 'license-file'". This is a known non-blocking issue between setuptools and twine metadata versions. PyPI will accept the package despite this warning. You can safely proceed to upload.

### Step 6: Test on TestPyPI First (Highly Recommended!)

TestPyPI is a separate instance for testing. Always test here first!

#### 6a. Get TestPyPI API Token

1. Go to https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. Name it (e.g., "gym-zombie-shooter-test")
4. Copy the token (starts with `pypi-`)

#### 6b. Upload to TestPyPI

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*
```

When prompted:
- Username: `__token__`
- Password: (paste your TestPyPI token)

Or configure in `~/.pypirc`:
```ini
[testpypi]
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

#### 6c. Test Installation from TestPyPI

```bash
# Create fresh test environment
conda create -n test-pypi python=3.12
conda activate test-pypi

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ gym-zombie-shooter

# Test it works
python -c "import zombie_shooter_gym; import gymnasium as gym; env = gym.make('ZombieShooter-v1'); print('TestPyPI package works!')"
```

**Note:** The `--extra-index-url` is needed because TestPyPI doesn't have all dependencies.

### Step 7: Publish to Production PyPI

Once TestPyPI installation works:

#### 7a. Get PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name it (e.g., "gym-zombie-shooter")
4. Copy the token

#### 7b. Upload to PyPI

```bash
# Upload to production PyPI
twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: (paste your PyPI token)

Or configure in `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-YOUR_PYPI_TOKEN_HERE
```

#### 7c. Verify on PyPI

1. Visit: https://pypi.org/project/gym-zombie-shooter/
2. Check the page looks correct
3. Test installation:

```bash
# In a fresh environment
pip install gym-zombie-shooter
```

### Step 8: Test the Public Installation

```bash
# Create clean environment
conda create -n test-prod python=3.12
conda activate test-prod

# Install from PyPI
pip install gym-zombie-shooter

# Test it
python -c "import zombie_shooter_gym; import gymnasium as gym; env = gym.make('ZombieShooter-v1'); print('Production package works!')"

# Test examples
pip install gym-zombie-shooter
# Download examples from GitHub or include them in your repo
```

## Post-Publishing

### Update README on PyPI

The README.md is automatically displayed on PyPI. To update:
1. Edit README.md
2. Increment version number
3. Rebuild and re-upload

### Create a GitHub Release

1. Commit all changes
2. Create a git tag:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```
3. Create release on GitHub with release notes

### Announce Your Package

- Tweet about it / share on social media
- Post on r/reinforcementlearning
- Share in Gymnasium Discord/community
- Update your README with PyPI installation instructions

## Common Issues & Solutions

### Issue: "File already exists"
**Solution:** You can't overwrite versions on PyPI. Increment the version number.

### Issue: "Invalid distribution"
**Solution:** Run `twine check dist/*` to see specific errors.

### Issue: "403 Forbidden"
**Solution:** Check your API token is correct and has upload permissions.

### Issue: Package name already taken
**Solution:** Choose a different name (e.g., `zombie-shooter-rl-gym`)

## Security Best Practices

1. **Never commit API tokens** to git
2. **Use API tokens** instead of passwords
3. **Use project-scoped tokens** when possible (after first upload)
4. **Keep tokens in ~/.pypirc** with proper permissions: `chmod 600 ~/.pypirc`

## Version Management

Keep versions synchronized across:
- `setup.py`
- `pyproject.toml`
- `zombie_shooter_gym/__init__.py`

Consider using tools like `bump2version` for automated version management.

## Quick Reference Commands

```bash
# Clean build
rm -rf build/ dist/ *.egg-info

# Build package
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ gym-zombie-shooter

# Install from PyPI
pip install gym-zombie-shooter
```

## Next Release Workflow

For future releases:

1. Make your changes
2. Update CHANGELOG.md
3. Run tests: `pytest tests/ -v`
4. Increment version in all 3 files
5. Clean: `rm -rf build/ dist/ *.egg-info`
6. Build: `python -m build`
7. Check: `twine check dist/*`
8. Test on TestPyPI
9. Upload to PyPI: `twine upload dist/*`
10. Create git tag and GitHub release
11. Announce!

---

Good luck with your publication! 🎉
