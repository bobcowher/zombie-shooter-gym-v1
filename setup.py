from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gym-zombie-shooter",
    version="0.1.0",
    author="Robert Cowher",
    author_email="",
    description="A Gymnasium environment for a top-down zombie shooter game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    license="MIT",
    packages=find_packages(exclude=["validate", "validate.*", "tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pygame>=2.1.0",
        "gymnasium>=0.26.0",
        "opencv-python>=4.5.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "rl": ["torch>=1.9.0", "tensorboard>=2.8.0"],
        "dev": ["pytest>=7.0.0", "black", "flake8"],
    },
    package_data={
        "zombie_shooter_gym": [
            "resources/images/*.png",
            "resources/sounds/*.wav",
        ],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "zombie-shooter-play=zombie_shooter_gym.cli:main",
        ],
    },
)
