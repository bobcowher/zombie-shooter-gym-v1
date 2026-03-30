"""Play Zombie Shooter as a human using keyboard controls.

Controls:
    W/A/S/D: Move player (up/left/down/right)
    Space: Shoot
    Tab: Switch weapons (pistol/shotgun)
    ESC: Pause/Resume
"""

import zombie_shooter_gym  # Register the environment
import pygame
import sys
import gymnasium as gym


def main():
    # Constants
    WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
    WORLD_WIDTH, WORLD_HEIGHT = 1800, 1200
    FPS = 60

    # Create the environment with human rendering and sound enabled
    env = gym.make(
        'ZombieShooter-v1',
        window_width=WINDOW_WIDTH,
        window_height=WINDOW_HEIGHT,
        world_width=WORLD_WIDTH,
        world_height=WORLD_HEIGHT,
        fps=FPS,
        sound=True,
        render_mode="human"
    )

    print("Starting Zombie Shooter - Human Play Mode")
    print("\nControls:")
    print("  W/A/S/D: Move player")
    print("  Space: Shoot")
    print("  Tab: Switch weapons")
    print("  ESC: Pause/Resume")
    print("\nGood luck!\n")

    # Reset environment
    observation, info = env.reset()

    # Game loop
    while True:
        # Action Mapping
        # 0: No-op
        # 1: Move up (W)
        # 2: Move down (S)
        # 3: Move left (A)
        # 4: Move right (D)
        # 5: Switch weapon (TAB) - only if use_shotgun=True
        # 6: Shoot (SPACE)
        action = 0

        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    action = 6  # Shoot
                elif event.key == pygame.K_TAB:
                    action = 5  # Switch weapon (if enabled)
                elif event.key == pygame.K_ESCAPE:
                    env.unwrapped.toggle_pause()

        # Handle continuous key presses for movement
        keys = pygame.key.get_pressed()

        if action == 0:  # Only check movement if no other action taken
            if keys[pygame.K_w]:
                action = 1  # Move up
            elif keys[pygame.K_s]:
                action = 2  # Move down
            elif keys[pygame.K_a]:
                action = 3  # Move left
            elif keys[pygame.K_d]:
                action = 4  # Move right

        # Step the environment
        observation, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        # Print debug info when something happens
        if reward != 0:
            print(f"Reward: {reward}, Health: {info['health']}, " +
                  f"Score: {info.get('score', 'N/A')}, Ammo: {info['shotgun_ammo']}")

        # Check if episode is done
        if done:
            print("\nEpisode ended!")
            print(f"Final stats: Health={info['health']}, Ammo={info['shotgun_ammo']}")

            # Wait a moment before resetting
            pygame.time.wait(2000)

            # Ask user if they want to play again
            print("\nPlay again? (Y/N)")
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        env.close()
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_y:
                            observation, info = env.reset()
                            waiting = False
                        elif event.key == pygame.K_n:
                            env.close()
                            pygame.quit()
                            sys.exit()

    env.close()


if __name__ == "__main__":
    main()
