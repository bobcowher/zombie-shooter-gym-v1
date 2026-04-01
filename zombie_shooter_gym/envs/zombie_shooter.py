import pygame
import sys
from zombie_shooter_gym.core.bullet import SingleBullet, ShotgunBullet
from zombie_shooter_gym.core.assets import Player, Zombie, TreasureChest, HealthDrop
import random
from zombie_shooter_gym.core.util import check_collision, get_collision
from zombie_shooter_gym.core.walls import walls_1, walls_2, walls_3
import cv2
import numpy as np
import gymnasium as gym
import os

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

import zombie_shooter_gym.resources.sounds as sounds_pkg


def load_sound(filename):
    """Load a sound from the package resources."""
    sound_file = files(sounds_pkg) / filename
    return str(sound_file)


class ZombieShooter(gym.Env):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": 60,
    }

    def __init__(self, window_width=800, window_height=600, world_height=3000, world_width=3000, fps=60, sound=False, render_mode="human", auto_scale=True, use_shotgun=None):

        # Store base rendering resolution (viewport size)
        self.base_width = window_width
        self.base_height = window_height

        # Physical window size (may be scaled for high-DPI)
        self.physical_width = window_width
        self.physical_height = window_height
        self.scale_factor = 1.0

        # Auto-scale for high-DPI displays
        if auto_scale and render_mode == "human":
            try:
                # Initialize pygame video to get display info
                pygame.init()
                display_info = pygame.display.Info()
                screen_width = display_info.current_w
                screen_height = display_info.current_h

                # Use 70% of screen height for comfortable viewing
                if screen_height > 1200:  # High-DPI display
                    target_height = int(screen_height * 0.7)
                    self.scale_factor = target_height / window_height
                    self.physical_width = int(window_width * self.scale_factor)
                    self.physical_height = target_height
                    print(f"Auto-scaled window to {self.physical_width}x{self.physical_height} (scale: {self.scale_factor:.2f}x)")
                    print(f"Game viewport remains {self.base_width}x{self.base_height}")
            except Exception as e:
                # Fall back to default size if auto-detection fails
                print(f"Auto-scaling failed, using default size: {e}")

        # Use base dimensions for all game logic
        self.window_width = self.base_width
        self.window_height = self.base_height
        self.world_height = world_height
        self.world_width = world_width

        if render_mode == "human":
            self.human = True
            self.sound = sound
        else:
            self.human = False
            self.sound = False
            os.environ["SDL_VIDEODRIVER"] = "dummy" # Set dummy video driver to null route display

        # Set use_shotgun - defaults to False if not explicitly provided
        self.use_shotgun = use_shotgun if use_shotgun is not None else False

        self.treasure_chest = None  # No chest initially
        self.health_drop = None  # No health drop initially

        self.paused = False  # Game starts unpaused

        self.fire_mode = "single"  # Add this to __init__

        pygame.init()

        # Create physical window at scaled size
        self.display = pygame.display.set_mode((self.physical_width, self.physical_height))

        # Create virtual surface at base resolution for rendering
        self.screen = pygame.Surface((self.base_width, self.base_height))

        pygame.display.set_caption('Zombie Shooter')

        self.font = pygame.font.SysFont(None, 36)  # Font size 36

        self.clock = pygame.time.Clock()
        self.fps = fps

        self.background_color = (181, 101, 29) # Light brown
        self.wall_color = (1, 50, 32)
        self.border_color = (255, 0, 0)

        self.announcement_font = pygame.font.SysFont(None, 100)

        self.action_space = gym.spaces.Discrete(7)

        self.observation_space = gym.spaces.Box(
            low=0, high=255, shape=(1, 128, 128), dtype=np.uint8
        )

        self.max_bullets = 20

        self.last_observation = None

        self.reset()

        if self.sound:
            pygame.mixer.pre_init(44100, -16, 2, 64)
            pygame.mixer.init()
            pygame.mixer.music.load(load_sound("background_music.wav"))
            pygame.mixer.music.play(-1, 0.0)

            self.last_walk_play_time = 0

            self.zombie_bite = pygame.mixer.Sound(load_sound("zombie_bite_1.wav"))
            self.zombie_hit = pygame.mixer.Sound(load_sound("zombie_hit.wav"))
            self.shotgun_blast = pygame.mixer.Sound(load_sound("shotgun_blast.wav"))
            self.zombie_snarl = pygame.mixer.Sound(load_sound("zombie_snarl.wav"))
            self.footstep = pygame.mixer.Sound(load_sound("footstep.wav"))
            self.vocals_1 = pygame.mixer.Sound(load_sound("one_of_those_things_got_in.wav"))
            self.vocals_2 = pygame.mixer.Sound(load_sound("virus_infection_alert.wav"))
            self.vocals_3 = pygame.mixer.Sound(load_sound("come_and_see.wav"))
            self.vocals_4 = pygame.mixer.Sound(load_sound("no_escape.wav"))

            self.vocals_1.play()


    def _update_display(self):
        """Scale virtual surface to physical display and update."""
        if self.scale_factor > 1.0:
            # Scale the virtual surface to the physical window
            scaled_surface = pygame.transform.scale(self.screen, (self.physical_width, self.physical_height))
            self.display.blit(scaled_surface, (0, 0))
        else:
            # No scaling needed, blit directly
            self.display.blit(self.screen, (0, 0))
        pygame.display.flip()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.done = False
        self.level = 1
        self.level_goal = 5
        self.max_zombie_count = 5
        self.walls = walls_1
        self.player = Player(world_height=self.world_height, world_width=self.world_width, walls=self.walls)
        self.player.health = 5
        self.max_zombie_count = 5
        self.zombie_top_speed = 1
        self.total_frames = 0
        self.last_bullet_frame = 0
        self.shotgun_ammo = 5  # Start with 10 shotgun shells
        self.out_of_ammo_message_displayed = False  # Initialize in __init__()
        self.gun_type = "single"  # Start with shotgun

        self.bullets = []
        self.zombies = []

        return self._get_obs(), self._get_info()

    def toggle_pause(self):

        self.paused = not self.paused  # Toggle between paused and unpaused

        if self.paused:
            pause_surface = self.announcement_font.render('Game Paused', True, (255, 255, 255))  # White text
            pause_rect = pause_surface.get_rect(center=(self.window_width // 2, self.window_height // 2))
            self.screen.blit(pause_surface, pause_rect)
            self._update_display()  # Update display to show pause message

            # Wait until the player unpauses (ignore everything else)
            while self.paused:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.paused = False  # Unpause the game
                self.clock.tick(10)  # Prevent busy-waiting

    def play_walking_sound(self):
        if self.sound:
            current_time = pygame.time.get_ticks()
            if(current_time - self.last_walk_play_time > 1000):
                self.footstep.play()
                self.last_walk_play_time = current_time

    def start_next_level(self):
        self.level += 1

        if self.level > 3:
            next_level_surface = self.announcement_font.render('You Won!', True, (255, 0, 0))
        else:
            next_level_surface = self.announcement_font.render(f'Starting level {self.level}', True, (255, 0, 0))

        next_level_rect = next_level_surface.get_rect(center=(self.window_width // 2, self.window_height // 2))

        self.zombies = []
        self.bullets = []

        if self.level == 2:
            if self.sound:
                self.vocals_2.play()
            self.walls = walls_2
            self.level_goal = 15
        elif self.level == 3:
            if self.sound:
                self.vocals_3.play()
            self.walls = walls_3
            self.level_goal = 30

        self.screen.blit(next_level_surface, next_level_rect)

        # Spawn treasure chest at a random location
        x, y = random.randint(50, self.world_width - 50), random.randint(50, self.world_height - 50)
        self.treasure_chest = TreasureChest(x, y)

        self.zombie_top_speed += 1
        self.max_zombie_count += 2

        self.player = Player(world_height=self.world_height, world_width=self.world_width, walls=self.walls)

        self._update_display()
        pygame.time.wait(4000)

        if self.level > 3:
            self.done = True

            # if self.human:
            #     pygame.quit()
            #     sys.exit()

    def game_over(self):
        # Render the "You Died" message
        game_over_surface = self.announcement_font.render('You Died', True, (255, 0, 0))  # Red text
        game_over_rect = game_over_surface.get_rect(center=(self.window_width // 2, self.window_height // 2))

        # Blit the message to the screen
        self.screen.blit(game_over_surface, game_over_rect)

        # Update the display to show the message
        self._update_display()

        self.done = True

        if self.sound:
            self.zombie_snarl.play()

        # Pause for 2 seconds (2000 milliseconds) before quitting
        if self.human:
            pygame.time.wait(2000)

            # # Quit the game
            # pygame.quit()
            # sys.exit()

    def fill_background(self):
        self.screen.fill(self.background_color)

        # Display score, health, level, ammo, and gun type
        score_surface = self.font.render(f'Score: {self.player.score}', True, (0, 0, 0))
        self.screen.blit(score_surface, (10, 10))

        health_surface = self.font.render(f'Health: {self.player.health}', True, (0, 0, 0))
        self.screen.blit(health_surface, (10, 35))

        level_surface = self.font.render(f'Level: {self.level}', True, (0, 0, 0))
        self.screen.blit(level_surface, (10, 60))

        # Only show gun info if shotgun switching is enabled
        if self.use_shotgun:
            ammo_surface = self.font.render(f'Shotgun Ammo: {self.shotgun_ammo}', True, (0, 0, 0))
            self.screen.blit(ammo_surface, (10, 85))

            gun_type_surface = self.font.render(f'Gun: {self.gun_type.title()}', True, (0, 0, 0))
            self.screen.blit(gun_type_surface, (10, 110))

            # Display out of ammo message if needed
            if self.out_of_ammo_message_displayed and self.gun_type == "shotgun":
                out_of_ammo_surface = self.font.render(
                    "Out of shotgun ammo! Press TAB to switch to single shot.", True, (255, 0, 0)
                )
                out_of_ammo_rect = out_of_ammo_surface.get_rect(center=(self.window_width // 2, self.window_height // 2))
                self.screen.blit(out_of_ammo_surface, out_of_ammo_rect)

    def fire_single_bullet(self):
        bullet = SingleBullet(self.player.x, self.player.y, self.player.direction)
        self.bullets.append(bullet)

        if self.sound:
            self.shotgun_blast.play()

        # print("Space pressed. Bullet fired")


    def fire_shotgun_bullet(self):
        if self.shotgun_ammo > 0:
            directions = [
                (self.player.direction, 0),    # Main bullet (straight)
                (self.player.direction, -10),  # Left bullet (angled)
                (self.player.direction, 10)    # Right bullet (angled)
            ]

            for direction, angle_offset in directions:
                bullet = ShotgunBullet(self.player.x, self.player.y, direction, angle_offset)
                self.bullets.append(bullet)

            self.shotgun_ammo -= 1  # Decrease ammo
            if self.sound:
                self.shotgun_blast.play()
            # print(f"Shotgun fired. Remaining ammo: {self.shotgun_ammo}")
            self.out_of_ammo_message_displayed = False  # Hide the message
        else:
            # print("Out of shotgun ammo!")
            self.out_of_ammo_message_displayed = True  # Show the message

    def _get_info(self):


        gun_type_num = 1 if "single" in self.gun_type else 2

        return {
            "health" : self.player.health,
            "shotgun_ammo" : self.shotgun_ammo,
            "gun_type" : self.gun_type,
            "gun_type_num" : gun_type_num,
            "bullets": len(self.bullets)
        }


    def _get_obs(self):

        screen_array = pygame.surfarray.pixels3d(self.screen)

        # Transpose to (height, width, channels)
        screen_array = np.transpose(screen_array, (1, 0, 2))

        # Resize to 128x128
        downscaled_image = cv2.resize(screen_array, (128, 128), interpolation=cv2.INTER_NEAREST)

        # Convert to grayscale
        grayscale = cv2.cvtColor(downscaled_image, cv2.COLOR_RGB2GRAY)

        # Add channel dimension and return as numpy array
        observation = np.expand_dims(grayscale, axis=0).astype(np.uint8)

        return observation

    def step(self, action, repeat=4):

        total_reward = 0

        for i in range(repeat):
            reward, done, truncated = self.step_(action)

            total_reward += reward

            if action == 5 or action == 6:
                action = 0 # Take no action

            if done:
                break

        return self._get_obs(), total_reward, done, truncated, self._get_info()

    def step_(self, action):

            # Action Mapping
            # [up, down, left, right, switch gun, fire]
            # [W, S, A, D, TAB, SPACE]

            self.total_frames += 1

            # for i in action:
            #     if(i != 0 and i != 1):
            #         raise Exception("Invalid action entered for the Zombie Shooter environment. Values must be either 0 or 1")

            # if len(action) != self.action_space.n:
            #     raise Exception("Please ensure the action matches the target action space: [6]")

            # 0 indicates no action
            up = True if action == 1 else False
            down = True if action == 2 else False
            left = True if action == 3 else False
            right = True if action == 4 else False
            switch_gun = True if (action == 5 and self.use_shotgun) else False
            fire = True if action == 6 else False
            pause = False

            # up = bool(action[0])
            # down = bool(action[1])
            # left = bool(action[2])
            # right = bool(action[3])
            # switch_gun = bool(action[4])
            # fire = bool(action[5])
            # pause = bool(action[6])

            # Setting up the initial obs variables
            reward, truncated = 0, False

            if switch_gun:
                self.gun_type = "single" if self.gun_type == "shotgun" else "shotgun"
                # print(f"Switched to {self.gun_type} mode")

            if fire and (self.total_frames - self.last_bullet_frame) > 10:
                if self.gun_type == "single":
                    self.fire_single_bullet()
                else:
                    self.fire_shotgun_bullet()

                self.last_bullet_frame = self.total_frames

            # if pause and self.human:
            #     self.toggle_pause()

            if self.paused:
                return  # Skip the rest of the game loop if paused

            if len(self.zombies) < self.max_zombie_count and random.randint(1, 100) < 3:  # 3% chance of spawning a zombie per frame
                self.zombies.append(Zombie(world_height=self.world_height, world_width=self.world_width, size=80, speed=random.randint(1,self.zombie_top_speed)))  # Instantiate a new zombie

            new_player_x = self.player.x
            if left:  # Left
                new_player_x -= self.player.speed
                self.player.direction = "left"
            if right:  # Right
                new_player_x += self.player.speed
                self.player.direction = "right"

            new_player_rect = pygame.Rect(new_player_x, self.player.y, self.player.size, self.player.size)

            collision = check_collision(new_player_rect, self.walls)

            if not collision \
               and self.player.x != new_player_x \
               and (0 <= new_player_x <= self.world_width - self.player.size):
                self.player.x = new_player_x
                self.play_walking_sound()


            new_player_y = self.player.y
            if up:  # Up
                new_player_y -= self.player.speed
                self.player.direction = "up"
            if down:  # Down
                new_player_y += self.player.speed
                self.player.direction = "down"

            new_player_rect = pygame.Rect(self.player.x, new_player_y, self.player.size, self.player.size)

            collision = check_collision(new_player_rect, self.walls)

            if not collision \
               and self.player.y != new_player_y \
               and (0 <= new_player_y <= self.world_height - self.player.size):
                self.player.y = new_player_y
                self.play_walking_sound()

            self.player.rect = pygame.Rect(self.player.x, self.player.y, self.player.size, self.player.size)
            # Check for collision with walls
            collision = False

            # Update camera position (centered on player)
            camera_x = self.player.x - self.window_width // 2
            camera_y = self.player.y - self.window_height // 2

            # Keep camera within world bounds
            camera_x = max(0, min(camera_x, self.world_width - self.window_width))
            camera_y = max(0, min(camera_y, self.world_height - self.window_height))


            # Move self.zombies toward player and check for collisions with self.bullets
            self.zombies_temp = []
            for zombie in self.zombies:
                if check_collision(zombie.rect, self.bullets):
                    bullet = get_collision(zombie.rect, self.bullets)  # Get the bullet causing the collision
                    self.player.score += 1
                    reward += 1
                    self.bullets.remove(bullet)

                    if self.sound:
                        self.zombie_hit.play()

                    # 20% chance to drop a heart
                    if random.randint(1, 100) <= 20:
                        # Drop the heart exactly where the zombie was killed
                        self.health_drop = HealthDrop(zombie.rect.x, zombie.rect.y)
                        # print(f"Heart dropped at ({zombie.rect.x}, {zombie.rect.y}) from zombie!")

                elif check_collision(zombie.rect, [self.player.rect]):
                    self.player.health -= 1
                    reward -= 1
                    if self.sound:
                        self.zombie_bite.play()
                else:
                    self.zombies_temp.append(zombie)

            self.zombies = self.zombies_temp


            for zombie in self.zombies:
                zombie.move_toward_player(self.player.x, self.player.y, self.walls)

            # Drawing
            self.fill_background()


            # Move and draw self.bullets
            for bullet in self.bullets:
                bullet.move()
                bullet.draw(self.screen, camera_x, camera_y)

                if check_collision(bullet.rect, self.walls):
                    self.bullets.remove(bullet)

            # Draw self.zombies
            # for zombie in self.zombies:
            #     zombie.draw(screen, camera_x, camera_y)

            # Draw the player (adjusted for the camera position)
            self.player.draw(self.screen, camera_x, camera_y)

            for zombie in self.zombies:
                zombie.draw(self.screen, camera_x, camera_y)

            # Draw the health drop if it exists
            if self.health_drop:
                self.health_drop.draw(self.screen, camera_x, camera_y)


            # Draw the world boundaries for testing
            pygame.draw.rect(self.screen, self.border_color, (0 - camera_x, 0 - camera_y, self.world_width, self.world_height), 5)

            for wall in self.walls:
                pygame.draw.rect(self.screen, self.wall_color, (wall.x - camera_x, wall.y - camera_y, wall.width, wall.height))

            # Draw the treasure chest
            if self.treasure_chest:
                self.treasure_chest.draw(self.screen, camera_x, camera_y)

            # Check for chest opening and health drop collection
            if self.treasure_chest and self.player.rect.colliderect(self.treasure_chest.rect):
                if not self.treasure_chest.is_opened:
                    self.treasure_chest.is_opened = True
                    reward += 1 # Reward for shotgun shell pickup.

                    # Add shotgun ammo when chest is opened
                    self.shotgun_ammo = min(self.shotgun_ammo + 5, 20)  # Max ammo is 20
                    # print(f"Ammo refilled! Current ammo: {self.shotgun_ammo}")

            if self.health_drop and self.player.rect.colliderect(self.health_drop.rect):
                self.player.health = min(self.player.health + 1, 100)  # Increase health by 1 points
                reward += 1 # Reward for health pickup
                # print("Heart collected! Health increased.")
                self.health_drop = None  # Remove the heart

            # Update the display
            if self.human:
                self._update_display()
            elif self.total_frames % 2 == 0:
                self._update_display()

            if self.player.health <= 0:
                self.game_over()

            # Cap the frame rate
            # if self.human:
            #     self.clock.tick(self.fps)
            # else:
            #     self.clock.tick(1000)
            # self.clock.tick(self.fps)
            if self.human:
                self.clock.tick(self.fps)
            else:
                self.clock.tick()

            if(self.level_goal <= self.player.score):
                self.start_next_level()

            return reward, self.done, truncated
