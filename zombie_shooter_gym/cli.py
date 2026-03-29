"""Command-line interface for Zombie Shooter."""

import sys
import os

# Add examples directory to path so we can import from it
examples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples')
sys.path.insert(0, examples_dir)


def main():
    """Launch the human play mode."""
    try:
        from examples.human_play import main as play_main
        play_main()
    except ImportError:
        # Fallback if examples aren't available
        print("Error: Could not import human_play module.")
        print("Please run: python examples/human_play.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
