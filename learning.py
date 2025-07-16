import pygame  # Core Pygame library for game development
from pygame.locals import * # Import common Pygame constants (e.g., K_LEFT, QUIT)
import time  # For time-related functions like sleep and tracking elapsed time
import random  # For generating random numbers (e.g., apple position, agent movement)
from datetime import datetime  # Although not used for elapsed time, imported for general time needs
import math  # For calculating Euclidean distance
import numpy as np  # For Q-table and numerical operations
import pickle  # For saving and loading the Q-table
import os  # For file operations

# --- Game Configuration Constants ---
SIZE = 40  # Size of each block (snake segment, apple) in pixels
BACKGROUND_COLOR = (110, 110, 5)  # A greenish-brown color for fallback background


class Apple:
    """
    Represents the food that the snake eats.
    """

    def __init__(self, parent_screen):
        """
        Initializes the Apple object.
        Args:
            parent_screen (pygame.Surface): The Pygame surface (game window) to draw the apple on.
        """
        self.train_agent= False
        self.agent_play_mode = False
        self.parent_screen = parent_screen
        # Load the apple image. Includes basic error handling for missing image.
        try:
            self.image = pygame.image.load("resources/apple.png").convert_alpha()
        except pygame.error:
            print("Warning: 'resources/apple.png' not found. Using a red square as placeholder.")
            self.image = pygame.Surface((SIZE, SIZE))
            self.image.fill((255, 0, 0))  # Fallback to red color

        # Initial position of the apple.
        # These will be immediately overwritten by the lists in the next lines.
        self.x = 120
        self.y = 120

        # Pre-defined lists of x and y coordinates for apple placement.
        # This makes the apple appear at specific, non-random locations in sequence.
        # The numbers are multiplied by SIZE implicitly in the move function,
        # so these values should be grid indices.
        self.x_list = [320, 160, 680, 280, 400, 240, 960, 80, 40, 760, 720, 880, 400, 680, 480, 480, 520, 160, 760, 480,
                       720, 360, 960, 160, 80, 400, 760, 680, 760, 800]
        self.y_list = [560, 40, 440, 280, 240, 560, 80, 200, 240, 80, 80, 520, 720, 360, 680, 760, 680, 320, 80, 360,
                       720, 120, 280, 280, 320, 680, 320, 40, 520, 600]
        self.count = 0  # Counter to index into x_list and y_list for apple movement.

    def draw(self):
        """Draws the apple on the parent screen at its current (x, y) coordinates."""
        self.parent_screen.blit(self.image, (self.x, self.y))
        pygame.display.flip()  # Update the display to show the newly drawn apple.

    def move(self):
        """
        Moves the apple to the next position defined in x_list and y_list.
        It uses the 'count' to cycle through the pre-defined positions.
        """
        # Set apple's position from the pre-defined lists
        self.x = self.x_list[self.count]
        self.y = self.y_list[self.count]
        # Increment count and use modulo to cycle back to 0 after reaching the end of the lists.
        # Note: The modulo should be applied to `len(self.x_list)` to be robust.
        self.count = (self.count + 1) % len(self.x_list)  # Assumes x_list and y_list have same length

    def move_random(self):
        """
        Moves the apple to a random position on the grid.
        Used for training the learning agent.
        """
        # Calculate grid dimensions
        grid_width = self.parent_screen.get_width() // SIZE
        grid_height = self.parent_screen.get_height() // SIZE

        # Generate random grid coordinates
        grid_x = random.randint(0, grid_width - 1)
        grid_y = random.randint(0, grid_height - 1)

        # Convert to pixel coordinates
        self.x = grid_x * SIZE
        self.y = grid_y * SIZE


class Snake:
    """
    Represents the snake controlled by the player (or agent).
    """

    def __init__(self, parent_screen):
        """
        Initializes the Snake object.
        Args:
            parent_screen (pygame.Surface): The Pygame surface to draw the snake on.
        """
        self.parent_screen = parent_screen
        # Load the snake block image. Includes basic error handling for missing image.
        try:
            self.image = pygame.image.load("resources/block.jpg").convert_alpha()
        except pygame.error:
            print("Warning: 'resources/block.jpg' not found. Using a green square as placeholder.")
            self.image = pygame.Surface((SIZE, SIZE))
            self.image.fill((0, 128, 0))  # Fallback to green color

        self.direction = 'down'  # Initial direction of the snake.
        self.best_time = ""  # To store the best time recorded for eating an apple.

        self.length = 1  # Initial length of the snake (one block).
        # Lists to store the (x, y) coordinates for each segment of the snake.
        self.x = [40]  # Initial x-coordinate of the head.
        self.y = [40]  # Initial y-coordinate of the head.

    def move_left(self):
        """Sets the snake's direction to 'left', preventing immediate U-turns."""
        if self.direction != 'right':
            self.direction = 'left'

    def move_right(self):
        """Sets the snake's direction to 'right', preventing immediate U-turns."""
        if self.direction != 'left':
            self.direction = 'right'

    def move_up(self):
        """Sets the snake's direction to 'up', preventing immediate U-turns."""
        if self.direction != 'down':
            self.direction = 'up'

    def move_down(self):
        """Sets the snake's direction to 'down', preventing immediate U-turns."""
        if self.direction != 'up':
            self.direction = 'down'

    def walk(self):
        """
        Updates the snake's position based on its current direction.
        Each body segment follows the segment in front of it, and the head moves
        according to the current direction.
        """
        # Move body segments: starting from the tail, each segment takes the position of the one in front of it.
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        # Update head position based on current direction.
        if self.direction == 'left':
            self.x[0] -= SIZE
        elif self.direction == 'right':
            self.x[0] += SIZE
        elif self.direction == 'up':
            self.y[0] -= SIZE
        elif self.direction == 'down':
            self.y[0] += SIZE

        self.draw()  # Redraw the snake after moving.

    def draw(self):
        """Draws all segments of the snake on the parent screen."""
        for i in range(self.length):
            self.parent_screen.blit(self.image, (self.x[i], self.y[i]))
        # Note: pygame.display.flip() is called in the Game class's play method
        # to ensure all elements are drawn before updating the screen.

    def increase_length(self):
        """
        Increases the snake's length by adding a new segment.
        The actual position of the new segment will be set in the next walk cycle.
        """
        self.length += 1
        # Append dummy positions; these will be updated by the walk method next frame.
        self.x.append(-1)
        self.y.append(-1)


class QLearningAgent:
    """
    Q-Learning agent that learns to play the Snake game.
    """

    def __init__(self, game, learning_rate=0.1, discount_factor=0.9, epsilon=1.0, epsilon_decay=0.999,
                 # Increased epsilon_decay
                 epsilon_min=0.01):
        """
        Initialize the Q-Learning agent.

        Args:
            game: Reference to the Game object
            learning_rate: How much to update Q-values on each step
            discount_factor: How much to value future rewards
            epsilon: Exploration rate (probability of random action)
            epsilon_decay: How much to decay epsilon after each episode
            epsilon_min: Minimum epsilon value
        """
        self.game = game
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Actions: 0=up, 1=down, 2=left, 3=right
        self.actions = ['up', 'down', 'left', 'right']
        self.n_actions = len(self.actions)

        # Q-table: state -> action values
        self.q_table = {}

        # Training statistics
        self.episode_count = 0
        self.total_reward = 0
        self.episode_rewards = []
        self.episode_lengths = []

        # File to save Q-table
        self.q_table_file = "q_table.pkl"

        # Load existing Q-table if available
        self.load_q_table()

    def get_state(self):
        """
        Get the current state representation.
        State includes:
        - Relative apple position (discretized to -1, 0, 1 for x and y)
        - Danger detection (4 directions: up, down, left, right from head)
        - Current snake direction (0=up, 1=down, 2=left, 3=right)
        """
        snake_head_x, snake_head_y = self.game.snake.x[0], self.game.snake.y[0]
        apple_x, apple_y = self.game.apple.x, self.game.apple.y

        # Relative apple position (discretized)
        apple_relative_x = (apple_x - snake_head_x) // SIZE
        apple_relative_y = (apple_y - snake_head_y) // SIZE

        apple_rel_x_disc = 0
        if apple_relative_x > 0:
            apple_rel_x_disc = 1
        elif apple_relative_x < 0:
            apple_rel_x_disc = -1

        apple_rel_y_disc = 0
        if apple_relative_y > 0:
            apple_rel_y_disc = 1
        elif apple_relative_y < 0:
            apple_rel_y_disc = -1

        # Danger detection (immediate collision in 4 directions from current head)
        # 0: up, 1: down, 2: left, 3: right
        danger_up = 1 if self.game._is_potential_move_colliding(snake_head_x, snake_head_y - SIZE,
                                                                exclude_tail=True) else 0
        danger_down = 1 if self.game._is_potential_move_colliding(snake_head_x, snake_head_y + SIZE,
                                                                  exclude_tail=True) else 0
        danger_left = 1 if self.game._is_potential_move_colliding(snake_head_x - SIZE, snake_head_y,
                                                                  exclude_tail=True) else 0
        danger_right = 1 if self.game._is_potential_move_colliding(snake_head_x + SIZE, snake_head_y,
                                                                   exclude_tail=True) else 0
        dangers = (danger_up, danger_down, danger_left, danger_right)

        # Current direction (0=up, 1=down, 2=left, 3=right)
        direction_map = {'up': 0, 'down': 1, 'left': 2, 'right': 3}
        current_direction = direction_map[self.game.snake.direction]

        state = (apple_rel_x_disc, apple_rel_y_disc, dangers, current_direction)
        return state

    def get_action(self, state):
        """
        Choose an action using epsilon-greedy strategy, considering valid moves.
        """
        valid_actions_indices = self.get_valid_actions()  # Get indices of valid actions

        if random.random() < self.epsilon:
            # Explore: choose random action from *valid* actions
            if not valid_actions_indices:  # Fallback if no valid moves (shouldn't happen often)
                return random.randint(0, self.n_actions - 1)
            return random.choice(valid_actions_indices)
        else:
            # Exploit: choose best action from Q-table among valid actions
            if state not in self.q_table:
                self.q_table[state] = [0.0] * self.n_actions  # Initialize if new state

            # Filter Q-values to only consider valid actions
            q_values_for_valid_actions = [-float('inf')] * self.n_actions  # Initialize with negative infinity
            for i in valid_actions_indices:
                q_values_for_valid_actions[i] = self.q_table[state][i]

            # Find the index of the best Q-value among all actions (invalid ones will be -inf)
            return np.argmax(q_values_for_valid_actions)

    def get_valid_actions(self):
        """
        Get list of valid actions (preventing immediate U-turns).
        """
        current_direction = self.game.snake.direction
        valid_actions = []

        # Map 'up':0, 'down':1, 'left':2, 'right':3
        # Check potential moves for self-collision or wall collision
        for i, action_name in enumerate(self.actions):
            # Prevent immediate U-turns
            if (current_direction == 'up' and action_name == 'down') or \
                    (current_direction == 'down' and action_name == 'up') or \
                    (current_direction == 'left' and action_name == 'right') or \
                    (current_direction == 'right' and action_name == 'left'):
                continue

            # Check if potential move leads to collision
            next_x, next_y = self.game._get_potential_head(action_name)
            if not self.game._is_potential_move_colliding(next_x, next_y,
                                                          exclude_tail=True):  # Exclude tail for immediate movement logic
                valid_actions.append(i)

        # If all "valid" moves lead to immediate death (e.g., trapped), allow any move.
        # This prevents the agent from getting stuck in a loop if it has no "safe" moves.
        if not valid_actions:
            return list(range(self.n_actions))

        return valid_actions

    def execute_action(self, action):
        """
        Execute the chosen action.
        """
        action_name = self.actions[action]

        if action_name == 'up':
            self.game.snake.move_up()
        elif action_name == 'down':
            self.game.snake.move_down()
        elif action_name == 'left':
            self.game.snake.move_left()
        elif action_name == 'right':
            self.game.snake.move_right()

    def get_reward(self, old_state, action, new_state, game_over, ate_apple):
        """
        Calculate reward for the current state transition.
        """
        reward = 0

        if game_over:
            reward = -500  # Large negative reward for dying (Increased magnitude)
        elif ate_apple:
            reward = 1000  # Large positive reward for eating apple (Increased magnitude)
        else:
            # Encouraging movement towards the apple is implicitly handled by the state's apple_relative_x/y.
            # However, direct distance reward can still be useful.
            old_apple_x_diff = old_state[0]  # apple_rel_x_disc
            old_apple_y_diff = old_state[1]  # apple_rel_y_disc

            new_apple_x_diff = new_state[0]
            new_apple_y_diff = new_state[1]

            # A simple way to check if getting closer based on discretized values
            # More direct approach based on Euclidean distance for finer control
            old_dist_sq = (self.game.snake.x[0] - self.game.apple.x) ** 2 + (
                        self.game.snake.y[0] - self.game.apple.y) ** 2
            new_head_x, new_head_y = self.game._get_potential_head(self.actions[action])
            new_dist_sq = (new_head_x - self.game.apple.x) ** 2 + (new_head_y - self.game.apple.y) ** 2

            if new_dist_sq < old_dist_sq:
                reward += 10  # Moving closer to apple
            elif new_dist_sq > old_dist_sq:
                reward -= 15  # Moving away from apple (larger penalty)
            else:
                reward -= 5  # Small penalty for each step to encourage efficiency (Increased magnitude)

            # Penalty for moving into immediate danger (if not leading to apple)
            # This is implicitly handled by the death penalty, but can be added for faster learning.
            # Danger check on *new_state*
            # if new_state[2][self.actions.index(self.game.snake.direction)] == 1: # if next immediate move is dangerous (current direction after move)
            #     reward -= 20 # Already handled by dying later, but can be here.

        return reward

    def update_q_table(self, state, action, reward, next_state, done):
        """
        Update Q-table using Q-learning formula.
        """
        if state not in self.q_table:
            self.q_table[state] = [0.0] * self.n_actions

        if next_state not in self.q_table:
            self.q_table[next_state] = [0.0] * self.n_actions

        # Q-learning update formula
        current_q = self.q_table[state][action]

        if done:
            target_q = reward
        else:
            # Consider only valid actions for the next state's max Q-value
            next_state_valid_actions = self.get_valid_actions_for_state(next_state)
            if next_state_valid_actions:
                max_future_q = max([self.q_table[next_state][i] for i in next_state_valid_actions])
            else:  # If all future moves lead to death, consider it 0 or the death penalty for next state.
                max_future_q = 0  # Or use the death reward

            target_q = reward + self.discount_factor * max_future_q

        self.q_table[state][action] = current_q + self.learning_rate * (target_q - current_q)

    def get_valid_actions_for_state(self, state_tuple):
        """
        Helper to determine valid actions for a given state tuple (for Q-table update).
        This recreates the logic for what moves would be valid *from* that state.
        This is a bit tricky as the original get_valid_actions relies on self.game.snake.direction
        and collision checks. For a general `next_state` tuple, we need to extract direction and danger.

        For simplicity and given the state definition, we'll use the 'dangers' part of the state
        and current_direction to determine valid moves.
        """
        # Unpack the state tuple
        # (apple_rel_x_disc, apple_rel_y_disc, dangers_tuple, current_direction_int)
        _, _, dangers_from_state, current_direction_int_from_state = state_tuple

        # Convert int direction back to string for consistency with snake methods
        direction_map_rev = {0: 'up', 1: 'down', 2: 'left', 3: 'right'}
        current_direction_from_state = direction_map_rev[current_direction_int_from_state]

        valid_actions = []
        for i, action_name in enumerate(self.actions):
            # Prevent immediate U-turns based on the *state's* direction
            if (current_direction_from_state == 'up' and action_name == 'down') or \
                    (current_direction_from_state == 'down' and action_name == 'up') or \
                    (current_direction_from_state == 'left' and action_name == 'right') or \
                    (current_direction_from_state == 'right' and action_name == 'left'):
                continue

            # Check if the danger bit for this action is 0 (not dangerous)
            if dangers_from_state[i] == 0:  # Danger is 0 if no collision
                valid_actions.append(i)

        # If no valid moves are detected from the state, it implies death or being trapped.
        # In Q-learning for a "done" state, max future Q is usually 0.
        # So if next_state is truly a terminal state (all moves lead to danger),
        # this will result in an empty valid_actions list, and max_future_q will be 0.
        return valid_actions

    def train_episode(self):
        """
        Train the agent for one episode.
        """
        self.game.reset()
        self.game.apple.move_random()  # Use random apple placement for training

        episode_reward = 0
        episode_length = 0

        state = self.get_state()

        while True:
            # Choose and execute action
            action = self.get_action(state)

            # Store old state for reward calculation
            old_state = state

            # Execute action (updates snake direction)
            self.execute_action(action)

            ate_apple = False
            game_over_flag = False

            try:
                old_length = self.game.snake.length
                self.game.play()  # This will update snake position, check collisions

                # Check if apple was eaten
                if self.game.snake.length > old_length:
                    ate_apple = True
                    self.game.apple.move_random()  # Move to random position

                # Get new state after game step
                new_state = self.get_state()

            except Exception as e:
                # Game over due to collision (wall or self)
                game_over_flag = True
                new_state = self.get_state()  # Still get state to pass to update_q_table

            # Calculate reward
            reward = self.get_reward(old_state, action, new_state, game_over_flag, ate_apple)

            # Update Q-table
            self.update_q_table(old_state, action, reward, new_state, game_over_flag)

            episode_reward += reward
            episode_length += 1
            state = new_state  # Update current state

            if game_over_flag:
                break

        # Update training statistics
        self.episode_count += 1
        self.episode_rewards.append(episode_reward)
        self.episode_lengths.append(episode_length)

        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # Print training progress
        if self.episode_count % 100 == 0:
            avg_reward = np.mean(self.episode_rewards[-100:])
            avg_length = np.mean(self.episode_lengths[-100:])
            print(
                f"Episode {self.episode_count}: Avg Reward: {avg_reward:.2f}, Avg Length: {avg_length:.2f}, Epsilon: {self.epsilon:.3f}, Q-table size: {len(self.q_table)}")

            # Save Q-table periodically
            self.save_q_table()

    def play_game(self):
        """
        Play the game using the trained agent (no learning).
        """
        # Set epsilon to 0 for pure exploitation
        old_epsilon = self.epsilon
        self.epsilon = 0

        state = self.get_state()

        while True:
            action = self.get_action(state)
            self.execute_action(action)

            try:
                self.game.play()
                state = self.get_state()
                time.sleep(0.1)  # Slow down for visualization
            except Exception as e:
                # When agent loses, return to the main game loop to show game over screen
                self.epsilon = old_epsilon # Restore epsilon
                raise e # Re-raise the exception to be caught by the main run loop

        # Restore epsilon (this line will not be reached if an exception is raised)
        self.epsilon = old_epsilon

    def save_q_table(self):
        """
        Save the Q-table to a file.
        """
        try:
            with open(self.q_table_file, 'wb') as f:
                pickle.dump(self.q_table, f)
            print(f"Q-table saved to {self.q_table_file}")
        except Exception as e:
            print(f"Error saving Q-table: {e}")

    def load_q_table(self):
        """
        Load the Q-table from a file.
        """
        try:
            if os.path.exists(self.q_table_file):
                with open(self.q_table_file, 'rb') as f:
                    self.q_table = pickle.load(f)
                print(f"Q-table loaded from {self.q_table_file}")
            else:
                print("No existing Q-table found. Starting with empty Q-table.")
        except Exception as e:
            print(f"Error loading Q-table: {e}")
            self.q_table = {}


class Game:
    """
    Manages the overall game logic, including initialization,
    game loop, score, time, and collision detection.
    """

    def __init__(self):
        """Initializes the Pygame environment and game components."""
        pygame.init()  # Initialize all the Pygame modules.
        pygame.display.set_caption("Snake Game with Q-Learning Agent")  # Set the window title.

        pygame.mixer.init()  # Initialize the mixer for sound playback.
        self.play_background_music()  # Start playing background music when the game initializes.

        # Set up the display surface (game window) with a resolution of 1000x800 pixels.
        self.surface = pygame.display.set_mode((1000, 800))
        # Initial background fill (this will be overwritten by the background image later).
        self.surface.fill(BACKGROUND_COLOR)

        # Create instances of the Snake and Apple classes, passing the game surface.
        self.snake = Snake(self.surface)
        self.snake.draw()  # Draw the snake's initial position.
        self.apple = Apple(self.surface)
        self.apple.draw()  # Draw the apple's initial position.

        self.elapsed_time = ""  # Stores the formatted total elapsed time when the game ends.

        self.game_speed = 0.30  # Controls how fast the snake moves (lower value = faster).
        self.start_time = time.time()  # Records the timestamp when the current game session starts.

        # Initialize Q-Learning agent
        self.agent = QLearningAgent(self)
        self.training_mode = False

    def play_background_music(self):
        """Loads and plays background music in an infinite loop."""
        try:
            pygame.mixer.music.load('resources/bg_music_1.mp3')
            pygame.mixer.music.play(-1, 0)  # -1 means loop indefinitely, 0 is the starting position.
        except pygame.error:
            print("Warning: 'resources/bg_music_1.mp3' not found. Background music will not play.")

    def play_sound(self, sound_name):
        """
        Plays a specific sound effect based on its name.
        Args:
            sound_name (str): The name of the sound ('crash' or 'ding').
        """
        if self.training_mode:
            return  # Skip sounds during training for speed

        sound = None
        try:
            if sound_name == "crash":
                sound = pygame.mixer.Sound("resources/crash.mp3")
            elif sound_name == 'ding':
                sound = pygame.mixer.Sound("resources/ding.mp3")

            if sound:
                pygame.mixer.Sound.play(sound)
        except pygame.error:
            print(f"Warning: 'resources/{sound_name}.mp3' not found. Sound effect will not play.")

    def reset(self):
        """Resets the game state for a new round after game over."""
        self.snake = Snake(self.surface)  # Recreate a new snake.
        self.apple = Apple(self.surface)  # Recreate a new apple.
        self.elapsed_time = ""  # Clear elapsed time.
        self.snake.best_time = ""  # Clear best time for eating an apple.
        self.start_time = time.time()  # Reset the start time for the new game.

    def is_collision(self, x1, y1, x2, y2):
        """
        Checks for collision between two square objects.
        Args:
            x1, y1 (int): Coordinates (top-left) of the first object.
            x2, y2 (int): Coordinates (top-left) of the second object.
        Returns:
            bool: True if collision occurs, False otherwise.
        """
        # Checks if the bounding boxes overlap using the SIZE constant.
        if x1 >= x2 and x1 < x2 + SIZE:
            if y1 >= y2 and y1 < y2 + SIZE:
                return True
        return False

    def self_collision(self, head_x, head_y):
        """
        Checks if the snake's head (at given coordinates) has collided with any of its own body segments.
        Args:
            head_x (int): The x-coordinate of the snake's head.
            head_y (int): The y-coordinate of the snake's head.
        Returns:
            bool: True if self-collision occurs, False otherwise.
        """
        # Start checking from the 4th segment (index 3) to avoid collision with
        # the immediate segments after a turn, which is typical for snake games.
        # Or, more robustly, check against all body segments *excluding* the very last one (tail),
        # as the tail will move out of the way on the next step.
        for i in range(1, self.snake.length - 1):  # Check all body parts except head and last tail segment
            if self.is_collision(head_x, head_y, self.snake.x[i], self.snake.y[i]):
                return True
        # Special case: check if head collides with the *current* position of the very last segment (tail)
        # but only if length > 1 (a single block snake can't self-collide)
        if self.snake.length > 1 and self.is_collision(head_x, head_y, self.snake.x[self.snake.length - 1],
                                                       self.snake.y[self.snake.length - 1]):
            # This means the head is trying to move into the space currently occupied by the tail.
            # If the snake grows, this is fine, the tail moves. If not, it's a collision.
            # For Q-learning's prediction, we assume the tail moves.
            pass  # We handle this by `exclude_tail=True` in _is_potential_move_colliding
        return False

    def check_wall_collision(self, head_x, head_y):
        """
        Checks if the snake's head (at given coordinates) has collided with any of the screen boundaries (walls).
        Returns:
            bool: True if a wall collision occurs, False otherwise.
        """
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()

        # Check collision with left or right wall.
        if head_x < 0 or head_x >= screen_width:
            return True
        # Check collision with top or bottom wall.
        if head_y < 0 or head_y >= screen_height:
            return True
        return False

    def render_background(self):
        """Loads and blits the background image onto the game surface."""
        if self.training_mode:
            # Skip background rendering during training for speed
            self.surface.fill(BACKGROUND_COLOR)
            return

        try:
            bg = pygame.image.load("resources/background.jpg").convert()
            # It's good practice to scale the background if it doesn't match the screen size exactly:
            # bg = pygame.transform.scale(bg, (self.surface.get_width(), self.surface.get_height()))
            self.surface.blit(bg, (0, 0))
        except pygame.error:
            print("Warning: 'resources/background.jpg' not found. Using solid background color.")
            self.surface.fill(BACKGROUND_COLOR)  # Fallback to solid color if image is missing.

    def play(self):
        """
        Performs one full step of the game:
        1. Renders the background, snake, and apple.
        2. Updates and displays score and time.
        3. Checks for eating apple, self-collision, and wall collision.
        """
        self.render_background()  # Draw the game background.
        self.snake.walk()  # Update and draw the snake's new position.
        self.apple.draw()  # Draw the apple.

        # Ensure score and time are displayed during agent play as well
        self.display_score()
        self.display_time(False)
        pygame.display.flip()  # Update the entire screen to show all drawn elements.


        # Snake eating apple scenario.
        if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.display_time(True)  # Capture the time at which this apple was eaten.
            self.play_sound("ding")  # Play ding sound.
            self.snake.increase_length()  # Increase snake's length.
            # Decrease game speed every 5 apples eaten to increase difficulty.
            if not self.training_mode: # Only decrease speed in manual or agent-playing mode, not training
                if (self.snake.length) % 5 == 0:
                    self.game_speed = max(0.05, self.game_speed - 0.04)  # Ensure it's never negative or too low
            # Apple movement is handled by the agent's train_episode or play_game now
            if not self.training_mode:
                self.apple.move()
            else:
                # In training, the agent's loop calls apple.move_random() after eating.
                pass

        # Snake colliding with itself or wall using current head position
        if self.self_collision(self.snake.x[0], self.snake.y[0]) or \
                self.check_wall_collision(self.snake.x[0], self.snake.y[0]):
            self.play_sound('crash')  # Play crash sound.
            raise Exception("Collision Occurred")  # Raise an exception to trigger game over.

    def display_score(self):
        """Renders and displays the current score on the screen."""
        font = pygame.font.SysFont('arial', 30)  # Define font and size.
        # Score is snake's length minus 1, assuming initial length 1.
        score_text = font.render(f"Score: {self.snake.length - 1}", True,
                                 (200, 200, 200))  # (True for antialiasing, color)
        self.surface.blit(score_text, (850, 10))  # Position the score text in the top-right.

    def display_time(self, score_t=False):
        """
        Renders and displays the elapsed time on the screen.
        Args:
            score_t (bool): If True, captures the current elapsed time as the 'best_time'
                            (time to eat an apple).
        """
        font = pygame.font.SysFont('arial', 30)
        elapsed_seconds = int(time.time() - self.start_time)  # Calculate elapsed time in seconds.
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        time_string = f"{minutes:02d}:{seconds:02d}"  # Format time as MM:SS (e.g., 01:05).
        self.elapsed_time = time_string  # Store the total elapsed time.

        if score_t:
            self.snake.best_time = time_string  # Update best_time when an apple is eaten.

        time_text = font.render(f"Time: {time_string}", True, (200, 200, 200))
        self.surface.blit(time_text, (10, 10))  # Position the time text in the top-left.

    def show_game_over(self, message="Game Over!"):
        """
        Displays the game over screen with the final score, best apple eating time,
        total game time, and instructions to restart/exit.
        """
        # Removed the `if self.training_mode: return` check here
        # so game over screen always displays when a game ends, regardless of mode.

        self.render_background()  # Redraw background for the game over screen.
        self.display_score()
        self.display_time(True)
        font = pygame.font.SysFont('arial', 30)

        # Display game over messages and scores.
        line1 = font.render(f"Game is over! ", True, (255, 255, 255))
        self.surface.blit(line1, (200, 200))
        line1 = font.render(f"Your score = {self.snake.length - 1}", True, (255, 255, 255))
        self.surface.blit(line1, (250, 350))
        line1 = font.render(f"Last Apple Time = {self.snake.best_time}", True, (255, 255, 255))  # Corrected text
        self.surface.blit(line1, (250, 400))
        line1 = font.render(f"Total Game Time = {self.elapsed_time}", True, (255, 255, 255))
        self.surface.blit(line1, (250, 450))
        line2 = font.render("To play again press Enter. To exit press Escape!", True, (255, 255, 255))
        self.surface.blit(line2, (200, 550))

        pygame.mixer.music.pause()  # Pause background music when game is over.
        pygame.display.flip()  # Update the screen to show the game over text.

    def _get_potential_head(self, target_direction):
        """
        Calculates the potential next head position based on a given direction.
        Args:
            target_direction (str): The direction ('left', 'right', 'up', 'down').
        Returns:
            tuple: (next_head_x, next_head_y) coordinates.
        """
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        next_head_x, next_head_y = head_x, head_y

        if target_direction == 'left':
            next_head_x -= SIZE
        elif target_direction == 'right':
            next_head_x += SIZE
        elif target_direction == 'up':
            next_head_y -= SIZE
        elif target_direction == 'down':
            next_head_y += SIZE
        return next_head_x, next_head_y

    def _is_potential_move_colliding(self, next_head_x, next_head_y, exclude_tail=False):
        """
        Checks if a potential next head position would result in a wall or self-collision.
        Does NOT modify the snake's actual position.
        Args:
            next_head_x (int): The potential x-coordinate of the snake's head.
            next_head_y (int): The potential y-coordinate of the snake's head.
            exclude_tail (bool): If True, the very last segment of the snake is ignored
                                 for self-collision check, as it will move.
        Returns:
            bool: True if a collision (wall or self) would occur, False otherwise.
        """
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()

        # Check wall collision
        if not (0 <= next_head_x < screen_width and 0 <= next_head_y < screen_height):
            return True  # Collides with wall

        # Check self-collision against existing body segments
        start_segment = 1  # Start from the first body segment (index 1)
        end_segment = self.snake.length
        if exclude_tail and self.snake.length > 1:
            end_segment -= 1  # Exclude the very last segment if requested

        for i in range(start_segment, end_segment):
            if self.is_collision(next_head_x, next_head_y, self.snake.x[i], self.snake.y[i]):
                return True  # Collides with self (body)

        return False  # No collision

    def _calculate_distance(self, x1, y1, x2, y2):
        """
        Calculates the Euclidean distance between two points.
        Args:
            x1, y1 (int): Coordinates of the first point.
            x2, y2 (int): Coordinates of the second point.
        Returns:
            float: The Euclidean distance.
        """
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def train_agent(self, episodes=1000):  # Increased default episodes for better training
        """
        Train the Q-learning agent for a specified number of episodes.
        Args:
            episodes (int): Number of training episodes.
        """
        print(f"Starting training for {episodes} episodes...")
        self.training_mode = True
        pygame.mixer.music.pause()  # Pause music during training

        for episode in range(episodes):
            self.agent.train_episode()

            # Optional: Show progress every 100 episodes
            if (episode + 1) % 100 == 0:
                print(f"Completed {episode + 1}/{episodes} episodes")

        print("Training completed!")
        self.training_mode = False
        pygame.mixer.music.unpause()  # Resume music after training

        # Save the final Q-table
        self.agent.save_q_table()

    def run(self):
        """
        The main game loop. Handles events, updates game state, and controls game flow.
        """
        running = True  # Controls if the game window is open.
        pause = False  # Controls if the game logic is paused.
        agent_playing = False  # Controls if the agent is playing

        while running:
            # Event handling loop: processes user inputs (keyboard, window close).
            for event in pygame.event.get():
                if event.type == KEYDOWN:  # A key has been pressed.
                    if event.key == K_ESCAPE:
                        running = False  # Set running to False to exit the game loop.

                    if event.key == K_RETURN:  # Enter key pressed.
                        pygame.mixer.music.unpause()  # Resume background music.
                        if pause == True:  # If game was paused (after game over).
                            self.start_time = time.time()  # Reset game start time.
                        pause = False  # Unpause the game.
                        agent_playing = False  # Disable agent
                        self.reset()  # Reset the game state for a new round.

                    # Training controls
                    if event.key == K_t and not pause:  # T key to train agent
                        print("Training agent... (this may take a while)")
                        self.train_agent(10000)  # Train for 10000 episodes for better results
                        print("Training completed! Press 'A' to watch the agent play.")

                    if event.key == K_a and not pause:  # A key to activate agent
                        agent_playing = True
                        self.training_mode = False # Ensure training mode is off when agent plays
                        self.reset()
                        print("Agent is now playing! Press Enter to take control back.")

                    if not pause and not agent_playing:  # Only allow manual snake movement if not paused and agent not playing
                        if event.key == K_LEFT:
                            self.snake.move_left()
                        elif event.key == K_RIGHT:
                            self.snake.move_right()
                        elif event.key == K_UP:
                            self.snake.move_up()
                        elif event.key == K_DOWN:
                            self.snake.move_down()

                elif event.type == QUIT:  # User clicked the window close button (X).
                    running = False  # Exit the game loop.

            # Agent control
            if agent_playing and not pause:
                try:
                    self.agent.play_game()
                except Exception as e:
                    # Game over for agent
                    agent_playing = False
                    pause = True
                    self.show_game_over(str(e))  # Display game over for agent

            # Game logic and rendering executed only if the game is not paused.
            try:
                if not pause and not agent_playing: # This condition now only applies to manual play
                    self.play()  # Execute one frame of the game (move snake, check collisions, draw).
            except Exception as e:
                # Catch exceptions raised during manual play (e.g., "Collision Occurred", "Wall Collision!").
                # This block will now also catch exceptions from agent.play_game
                # because the exception is re-raised in agent.play_game.
                self.show_game_over(str(e))  # Display the specific game over message.
                pause = True  # Pause the game after game over.

            # Control game speed using time.sleep().
            # Lower `self.game_speed` value means faster game updates.
            # This sleep applies to both manual and agent play now.
            if not pause: # Only sleep if the game is not paused (i.e., actively running)
                 time.sleep(self.game_speed if not agent_playing else 0.1)


    def show_instructions(self):
        """
        Display instructions for the Q-learning agent.
        """
        print("\n" + "=" * 60)
        print("SNAKE GAME WITH Q-LEARNING AGENT")
        print("=" * 60)
        print("CONTROLS:")
        print("  Arrow Keys    - Manual control")
        print("  T             - Train the agent (recommended 10000 episodes)")
        print("  A             - Let the agent play")
        print("  Enter         - Restart game / Take control from agent")
        print("  Escape        - Exit game")
        print("\nINSTRUCTIONS:")
        print("1. Press 'T' to train the agent (this will take some time, especially for 10000 episodes)")
        print("2. Once trained, press 'A' to watch the agent play. The agent will aim for the highest score.")
        print("3. The agent learns through trial and error using Q-learning.")
        print("4. The Q-table is automatically saved ('q_table.pkl') and loaded upon startup.")
        print("5. To reset the agent's learning, simply delete the 'q_table.pkl' file.")
        print("=" * 60)


# Entry point of the game application.
if __name__ == '__main__':
    game = Game()  # Create a Game object.
    game.show_instructions()  # Show instructions
    game.run()  # Start the main game loop.