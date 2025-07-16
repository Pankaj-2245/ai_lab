import pygame  # Core Pygame library for game development
from pygame.locals import *  # Import common Pygame constants (e.g., K_LEFT, QUIT)
import time  # For time-related functions like sleep and tracking elapsed time
import random  # For generating random numbers (e.g., apple position, agent movement)
from datetime import datetime  # Although not used for elapsed time, imported for general time needs
import math  # For calculating Euclidean distance
import collections
from collections import deque

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


class Game:
    """
    Manages the overall game logic, including initialization,
    game loop, score, time, and collision detection.
    """

    def __init__(self):
        """Initializes the Pygame environment and game components."""
        pygame.init()  # Initialize all the Pygame modules.
        pygame.display.set_caption("Codebasics Snake And Apple Game")  # Set the window title.

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
        self.previous_direction = None  # Track previous direction to penalize repetition

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
        self.snake = Snake(self.surface)
        self.apple = Apple(self.surface)
        self.elapsed_time = ""
        self.snake.best_time = ""
        self.start_time = time.time()
        self.previous_direction = None  # Reset previous direction

        # Reset learning agent if it exists
        if hasattr(self, 'q_table'):
            self.reset_learning_agent()

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

    def self_collision(self):
        """
        Checks if the snake's head has collided with any of its own body segments.
        Returns:
            bool: True if self-collision occurs, False otherwise.
        """
        # Start checking from the 4th segment (index 3) to avoid collision with
        # the immediate segments after a turn, which is typical for snake games.
        for i in range(3, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                return True
        return False

    def check_wall_collision(self):
        """
        Checks if the snake's head has collided with any of the screen boundaries (walls).
        Returns:
            bool: True if a wall collision occurs, False otherwise.
        """
        head_x, head_y = self.snake.x[0], self.snake.y[0]
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
        self.display_score()  # Display the current score.
        self.display_time(False)  # Display the elapsed time (False indicates not for scoring time).
        pygame.display.flip()  # Update the entire screen to show all drawn elements.

        # Snake eating apple scenario.
        if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.display_time(True)  # Capture the time at which this apple was eaten.
            self.play_sound("ding")  # Play ding sound.
            self.snake.increase_length()  # Increase snake's length.
            # Decrease game speed every 5 apples eaten to increase difficulty.
            if (self.snake.length) % 5 == 0:
                self.game_speed = max(0.05, self.game_speed - 0.04)
            self.apple.move()  # Move apple to a new location.

        # Snake colliding with itself.
        if self.self_collision():
            self.play_sound('crash')  # Play crash sound.
            raise Exception("Collision Occurred")  # Raise an exception to trigger game over.

        # Snake colliding with wall.
        if self.check_wall_collision():
            self.play_sound('crash')  # Play crash sound.
            raise Exception("Wall Collision!")  # Raise an exception to trigger game over.

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
        self.render_background()  # Redraw background for the game over screen.
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

    def _get_potential_head(self, current_direction):
        """
        Calculates the potential next head position based on a given direction.
        Args:
            current_direction (str): The direction ('left', 'right', 'up', 'down').
        Returns:
            tuple: (next_head_x, next_head_y) coordinates.
        """
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        next_head_x, next_head_y = head_x, head_y

        if current_direction == 'left':
            next_head_x -= SIZE
        elif current_direction == 'right':
            next_head_x += SIZE
        elif current_direction == 'up':
            next_head_y -= SIZE
        elif current_direction == 'down':
            next_head_y += SIZE
        return next_head_x, next_head_y

    def _is_potential_move_colliding(self, next_head_x, next_head_y):
        """
        Checks if a potential next head position would result in a wall or self-collision.
        Does NOT modify the snake's actual position.
        Args:
            next_head_x (int): The potential x-coordinate of the snake's head.
            next_head_y (int): The potential y-coordinate of the snake's head.
        Returns:
            bool: True if a collision (wall or self) would occur, False otherwise.
        """
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()

        # Check wall collision
        if not (0 <= next_head_x < screen_width and 0 <= next_head_y < screen_height):
            return True  # Collides with wall

        # Check self-collision against existing body segments (excluding current head)
        # This assumes the tail will move, so the last segment won't be a collision point.
        for i in range(1, self.snake.length):  # Iterate from the first body segment (index 1)
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

    def run(self):
        """
        The main game loop. Handles events, updates game state, and controls game flow.
        """
        running = True  # Controls if the game window is open.
        pause = False  # Controls if the game logic is paused.

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
                        self.reset()  # Reset the game state for a new round.

                    if not pause:  # Only allow snake movement if the game is not paused.
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

            # Agent movement control: Uncomment one of the lines below to activate an agent.
            # Agent movement control - Choose ONE of these:
            if not pause:
                 #self.random_agent()           # 1. Random movement (baseline)
                 #self.simple_agent()           # 2. Simple reflex agent
                # self.goal_based_agent()       # 3. Goal-based agent
                self.utility_agent()  # 4. Utility-based agent
                #self.learning_agent()  # 5. Learning agent (Q-learning)
            # Game logic and rendering executed only if the game is not paused.
            try:
                if not pause:
                    self.play()  # Execute one frame of the game (move snake, check collisions, draw).
            except Exception as e:
                # Catch exceptions raised during play (e.g., "Collision Occurred", "Wall Collision!").
                self.show_game_over(str(e))  # Display the specific game over message.
                pause = True  # Pause the game after game over.

            # Control game speed using time.sleep().
            # Lower `self.game_speed` value means faster game updates.
            time.sleep(self.game_speed)

    def simple_agent(self):
        """
        Simple reflex agent that makes decisions based on current state.

        Rules:
        1. If there's an immediate collision threat, avoid it
        2. Otherwise, move toward the apple using the shortest path
        3. Prefer horizontal movement over vertical when distance is equal
        """
        # Safety check - ensure snake exists and has at least one segment
        if not hasattr(self, 'snake') or not self.snake or len(self.snake.x) == 0:
            return

        # Get current snake head position
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        apple_x, apple_y = self.apple.x, self.apple.y

        # Calculate differences to apple
        dx = apple_x - head_x
        dy = apple_y - head_y

        # Define possible moves and their priorities
        possible_moves = []

        # Determine preferred directions based on distance to apple
        if abs(dx) > abs(dy):  # Apple is further horizontally
            if dx > 0:
                possible_moves = ['right', 'down' if dy > 0 else 'up', 'left']
            else:
                possible_moves = ['left', 'down' if dy > 0 else 'up', 'right']
        else:  # Apple is further vertically or equal distance
            if dy > 0:
                possible_moves = ['down', 'right' if dx > 0 else 'left', 'up']
            else:
                possible_moves = ['up', 'right' if dx > 0 else 'left', 'down']

        # Add the remaining direction
        all_directions = ['left', 'right', 'up', 'down']
        for direction in all_directions:
            if direction not in possible_moves:
                possible_moves.append(direction)

        # Try each move in order of preference
        for direction in possible_moves:
            # Skip if this would be an immediate U-turn (already handled by move methods)
            if ((direction == 'left' and self.snake.direction == 'right') or
                    (direction == 'right' and self.snake.direction == 'left') or
                    (direction == 'up' and self.snake.direction == 'down') or
                    (direction == 'down' and self.snake.direction == 'up')):
                continue

            # Get potential next head position
            try:
                next_head_x, next_head_y = self._get_potential_head(direction)

                # Check if this move would cause collision
                if not self._is_potential_move_colliding(next_head_x, next_head_y):
                    # Safe move found - execute it
                    if direction == 'left':
                        self.snake.move_left()
                    elif direction == 'right':
                        self.snake.move_right()
                    elif direction == 'up':
                        self.snake.move_up()
                    elif direction == 'down':
                        self.snake.move_down()
                    return
            except (IndexError, AttributeError):
                # Handle potential errors gracefully
                continue

        # If no safe move found, continue in current direction (last resort)
        # This shouldn't happen often with a well-designed agent

    from collections import deque

    def utility_agent(self):
        """
        Advanced utility-based agent that combines:
        1. Goal-based reasoning (primary goal: reach apple, secondary: survive)
        2. BFS pathfinding for optimal path calculation
        3. Multi-criteria utility evaluation
        """
        # Define possible actions
        actions = ['left', 'right', 'up', 'down']
        opposite_dirs = {'left': 'right', 'right': 'left', 'up': 'down', 'down': 'up'}

        # Goal-based reasoning: Determine current goals and priorities
        goals = self._determine_goals()

        # Filter valid actions (no immediate reversals)
        valid_actions = [action for action in actions if action != opposite_dirs.get(self.snake.direction)]

        best_action = None
        best_utility = -float('inf')

        # Evaluate each possible action
        for action in valid_actions:
            utility = self._evaluate_action_utility(action, goals)

            if utility > best_utility:
                best_utility = utility
                best_action = action

        # Execute the best action
        if best_action:
            self._execute_action(best_action)
        else:
            # Emergency fallback - try any action that doesn't cause immediate death
            for action in actions:
                next_x, next_y = self._get_potential_head(action)
                if not self._is_potential_move_colliding(next_x, next_y):
                    self._execute_action(action)
                    break

    def _determine_goals(self):
        """
        Goal-based reasoning: Determine current goals based on game state
        Returns a dictionary of goals with their importance weights
        """
        goals = {}

        # Primary goal: Reach the apple
        goals['reach_apple'] = 1.0

        # Secondary goal: Avoid immediate death
        goals['avoid_death'] = 0.8

        # Tertiary goal: Maintain maneuverability (avoid getting trapped)
        goals['maintain_space'] = 0.6

        # Quaternary goal: Efficient movement (minimize unnecessary moves)
        goals['efficient_movement'] = 0.3

        # Adjust goal weights based on game state
        head_x, head_y = self.snake.x[0], self.snake.y[0]

        # If snake is long, prioritize safety more
        if self.snake.length > 10:
            goals['avoid_death'] = 0.9
            goals['maintain_space'] = 0.7

        # If very close to walls, prioritize safety
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()
        wall_distances = [head_x, screen_width - head_x - SIZE, head_y, screen_height - head_y - SIZE]
        min_wall_distance = min(wall_distances)

        if min_wall_distance < SIZE * 3:
            goals['avoid_death'] = 1.0
            goals['maintain_space'] = 0.8

        return goals

    def _evaluate_action_utility(self, action, goals):
        """
        Evaluate the utility of an action based on multiple criteria and goals
        """
        next_x, next_y = self._get_potential_head(action)

        # Check if action leads to immediate death
        if self._is_potential_move_colliding(next_x, next_y):
            return -float('inf')  # Immediate death has infinite negative utility

        total_utility = 0

        # 1. GOAL: Reach Apple
        if 'reach_apple' in goals:
            apple_utility = self._calculate_apple_utility(next_x, next_y)
            total_utility += apple_utility * goals['reach_apple']

        # 2. GOAL: Avoid Death
        if 'avoid_death' in goals:
            safety_utility = self._calculate_safety_utility(next_x, next_y)
            total_utility += safety_utility * goals['avoid_death']

        # 3. GOAL: Maintain Space
        if 'maintain_space' in goals:
            space_utility = self._calculate_space_utility(next_x, next_y)
            total_utility += space_utility * goals['maintain_space']

        # 4. GOAL: Efficient Movement
        if 'efficient_movement' in goals:
            efficiency_utility = self._calculate_efficiency_utility(action)
            total_utility += efficiency_utility * goals['efficient_movement']

        return total_utility

    def _calculate_apple_utility(self, next_x, next_y):
        """
        Calculate utility for reaching the apple using BFS pathfinding
        """
        # Use BFS to find shortest path to apple
        path_length = self._bfs_shortest_path(next_x, next_y, self.apple.x, self.apple.y)

        if path_length is None:
            return -1000  # No path to apple - very bad

        # Utility is inversely proportional to path length
        # Shorter paths have higher utility
        base_utility = 1000 / (path_length + 1)

        # Additional bonus for direct moves toward apple
        current_distance = self._calculate_distance(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y)
        new_distance = self._calculate_distance(next_x, next_y, self.apple.x, self.apple.y)

        if new_distance < current_distance:
            base_utility += 100  # Bonus for getting closer

        return base_utility

    def _calculate_safety_utility(self, next_x, next_y):
        """
        Calculate utility for safety (avoiding walls and self-collision)
        """
        utility = 0
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()

        # Distance to walls
        wall_distances = [
            next_x,  # Left wall
            screen_width - next_x - SIZE,  # Right wall
            next_y,  # Top wall
            screen_height - next_y - SIZE  # Bottom wall
        ]
        min_wall_distance = min(wall_distances)

        # Utility increases with distance from walls
        utility += min_wall_distance * 0.1

        # Penalty for being too close to walls
        if min_wall_distance < SIZE * 2:
            utility -= 200

        # Distance to body segments
        min_body_distance = float('inf')
        for i in range(1, self.snake.length):
            body_distance = self._calculate_distance(next_x, next_y, self.snake.x[i], self.snake.y[i])
            min_body_distance = min(min_body_distance, body_distance)

        if min_body_distance < SIZE * 2:
            utility -= 300  # Heavy penalty for being close to body
        else:
            utility += min_body_distance * 0.05  # Small bonus for being far from body

        return utility

    def _calculate_space_utility(self, next_x, next_y):
        """
        Calculate utility for maintaining maneuvering space
        """
        # Use BFS to count accessible spaces
        accessible_spaces = self._bfs_accessible_spaces(next_x, next_y)

        # More accessible spaces = higher utility
        return accessible_spaces * 2

    def _calculate_efficiency_utility(self, action):
        """
        Calculate utility for movement efficiency
        """
        utility = 0

        # Small bonus for continuing in same direction (smoother movement)
        if action == self.snake.direction:
            utility += 10

        # Bonus for moving toward apple in Manhattan distance
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        current_manhattan = abs(head_x - self.apple.x) + abs(head_y - self.apple.y)

        next_x, next_y = self._get_potential_head(action)
        new_manhattan = abs(next_x - self.apple.x) + abs(next_y - self.apple.y)

        if new_manhattan < current_manhattan:
            utility += 20

        return utility

    def _bfs_shortest_path(self, start_x, start_y, target_x, target_y):
        """
        BFS implementation to find shortest path length between two points
        Returns path length or None if no path exists
        """
        if start_x == target_x and start_y == target_y:
            return 0

        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()
        queue = deque([(start_x, start_y, 0)])  # (x, y, distance)
        visited = set()
        visited.add((start_x, start_y))

        directions = [(SIZE, 0), (-SIZE, 0), (0, SIZE), (0, -SIZE)]
        max_iterations = 200  # Prevent infinite loops
        iterations = 0

        while queue and iterations < max_iterations:
            iterations += 1
            x, y, dist = queue.popleft()

            # Check all adjacent positions
            for dx, dy in directions:
                next_x, next_y = x + dx, y + dy

                # Check if we reached the target
                if next_x == target_x and next_y == target_y:
                    return dist + 1

                # Check bounds
                if not (0 <= next_x < screen_width and 0 <= next_y < screen_height):
                    continue

                # Check if already visited
                if (next_x, next_y) in visited:
                    continue

                # Check if position is blocked by snake body
                blocked = False
                for i in range(1, self.snake.length):  # Skip head
                    if next_x == self.snake.x[i] and next_y == self.snake.y[i]:
                        blocked = True
                        break

                if not blocked:
                    visited.add((next_x, next_y))
                    queue.append((next_x, next_y, dist + 1))

        return None  # No path found

    def _bfs_accessible_spaces(self, start_x, start_y):
        """
        BFS implementation to count accessible empty spaces
        """
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()
        queue = deque([(start_x, start_y)])
        visited = set()
        visited.add((start_x, start_y))

        directions = [(SIZE, 0), (-SIZE, 0), (0, SIZE), (0, -SIZE)]
        accessible_count = 0
        max_iterations = 100  # Limit to prevent performance issues

        while queue and accessible_count < max_iterations:
            x, y = queue.popleft()
            accessible_count += 1

            for dx, dy in directions:
                next_x, next_y = x + dx, y + dy

                # Check bounds
                if not (0 <= next_x < screen_width and 0 <= next_y < screen_height):
                    continue

                # Check if already visited
                if (next_x, next_y) in visited:
                    continue

                # Check if position is blocked by snake body
                blocked = False
                for i in range(1, self.snake.length):  # Skip head
                    if next_x == self.snake.x[i] and next_y == self.snake.y[i]:
                        blocked = True
                        break

                if not blocked:
                    visited.add((next_x, next_y))
                    queue.append((next_x, next_y))

        return accessible_count

    def _execute_action(self, action):
        """Execute the chosen action"""
        if action == 'left':
            self.snake.move_left()
        elif action == 'right':
            self.snake.move_right()
        elif action == 'up':
            self.snake.move_up()
        elif action == 'down':
            self.snake.move_down()

    def learning_agent(self):
        """
        Learning agent that uses Q-learning to improve its performance over time.

        State representation: (relative_apple_x, relative_apple_y, danger_left, danger_right, danger_up, danger_down)
        Actions: left, right, up, down
        """
        # Initialize Q-table and learning parameters if not exists
        if not hasattr(self, 'q_table'):
            self.q_table = {}
            self.learning_rate = 0.1
            self.discount_factor = 0.95
            self.epsilon = 0.1  # Exploration rate
            self.last_state = None
            self.last_action = None
            self.episode_reward = 0
            self.episodes_played = 0

        # Safety check
        if not hasattr(self, 'snake') or not self.snake or len(self.snake.x) == 0:
            return

        head_x, head_y = self.snake.x[0], self.snake.y[0]
        apple_x, apple_y = self.apple.x, self.apple.y

        # Get current state
        current_state = self._get_state_representation(head_x, head_y, apple_x, apple_y)

        # Calculate reward based on previous action
        reward = self._calculate_reward(head_x, head_y, apple_x, apple_y)

        # Update Q-table if we have a previous state and action
        if self.last_state is not None and self.last_action is not None:
            self._update_q_table(self.last_state, self.last_action, reward, current_state)

        # Choose action using epsilon-greedy policy
        action = self._choose_action(current_state)

        # Execute action
        if action:
            self._execute_action(action)
            self.last_state = current_state
            self.last_action = action

    def _get_state_representation(self, head_x, head_y, apple_x, apple_y):
        """
        Convert game state to a simplified representation for Q-learning.
        """
        # Relative position to apple (discretized)
        rel_apple_x = self._discretize_position(apple_x - head_x)
        rel_apple_y = self._discretize_position(apple_y - head_y)

        # Danger in each direction
        danger_left = 1 if self._is_direction_blocked(head_x, head_y, 'left') else 0
        danger_right = 1 if self._is_direction_blocked(head_x, head_y, 'right') else 0
        danger_up = 1 if self._is_direction_blocked(head_x, head_y, 'up') else 0
        danger_down = 1 if self._is_direction_blocked(head_x, head_y, 'down') else 0

        return (rel_apple_x, rel_apple_y, danger_left, danger_right, danger_up, danger_down)

    def _discretize_position(self, pos):
        """
        Discretize position to reduce state space.
        """
        if pos < -SIZE:
            return -1
        elif pos > SIZE:
            return 1
        else:
            return 0

    def _calculate_reward(self, head_x, head_y, apple_x, apple_y):
        """
        Calculate reward for the current state.
        """
        reward = 0

        # Small negative reward for each step (encourages efficiency)
        reward -= 1

        # Large positive reward for eating apple
        if self.is_collision(head_x, head_y, apple_x, apple_y):
            reward += 100

        # Negative reward for getting closer to walls
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()
        min_wall_dist = min(head_x, head_y, screen_width - head_x, screen_height - head_y)
        if min_wall_dist < SIZE * 2:
            reward -= 10

        # Reward for getting closer to apple
        dist_to_apple = self._calculate_distance(head_x, head_y, apple_x, apple_y)
        if hasattr(self, 'last_apple_distance'):
            if dist_to_apple < self.last_apple_distance:
                reward += 2
            else:
                reward -= 1

        self.last_apple_distance = dist_to_apple

        return reward

    def _update_q_table(self, state, action, reward, next_state):
        """
        Update Q-table using Q-learning algorithm.
        """
        # Initialize Q-values if not exists
        if state not in self.q_table:
            self.q_table[state] = {'left': 0, 'right': 0, 'up': 0, 'down': 0}

        if next_state not in self.q_table:
            self.q_table[next_state] = {'left': 0, 'right': 0, 'up': 0, 'down': 0}

        # Q-learning update rule
        old_q = self.q_table[state][action]
        max_next_q = max(self.q_table[next_state].values())

        new_q = old_q + self.learning_rate * (reward + self.discount_factor * max_next_q - old_q)
        self.q_table[state][action] = new_q

    def _choose_action(self, state):
        """
        Choose action using epsilon-greedy policy.
        """
        # Initialize Q-values if not exists
        if state not in self.q_table:
            self.q_table[state] = {'left': 0, 'right': 0, 'up': 0, 'down': 0}

        # Get valid actions (not blocked and not U-turns)
        valid_actions = []
        for direction in ['left', 'right', 'up', 'down']:
            # Skip U-turns
            if ((direction == 'left' and self.snake.direction == 'right') or
                    (direction == 'right' and self.snake.direction == 'left') or
                    (direction == 'up' and self.snake.direction == 'down') or
                    (direction == 'down' and self.snake.direction == 'up')):
                continue

            # Check if move is safe
            next_x, next_y = self._get_potential_head(direction)
            if not self._is_potential_move_colliding(next_x, next_y):
                valid_actions.append(direction)

        if not valid_actions:
            return None

        # Epsilon-greedy action selection
        if random.random() < self.epsilon:
            # Explore: choose random valid action
            return random.choice(valid_actions)
        else:
            # Exploit: choose action with highest Q-value
            best_action = None
            best_q = -float('inf')

            for action in valid_actions:
                q_value = self.q_table[state][action]
                if q_value > best_q:
                    best_q = q_value
                    best_action = action

            return best_action if best_action else random.choice(valid_actions)

    def reset_learning_agent(self):
        """
        Reset learning agent state when game restarts.
        """
        if hasattr(self, 'episodes_played'):
            self.episodes_played += 1
            # Decay exploration rate over time
            self.epsilon = max(0.01, self.epsilon * 0.995)

            # Reset episode-specific variables
            self.last_state = None
            self.last_action = None
            self.episode_reward = 0

            # Print learning progress every 10 episodes
            if self.episodes_played % 10 == 0:
                print(f"Episode {self.episodes_played}, Epsilon: {self.epsilon:.3f}, Q-table size: {len(self.q_table)}")

    def auto_reset_learning_agent(self):
        if self.game_over:
            self.reset_game()
            self.learning_agent.reset()  # Only if episodic reset is needed

    def goal_based_agent(self):
        """
        Goal-based agent that maintains multiple goals and plans ahead.

        Goals (in priority order):
        1. Immediate survival (avoid collisions)
        2. Maintain escape routes (avoid getting trapped)
        3. Collect apple efficiently
        4. Maximize available space
        """
        # Safety check
        if not hasattr(self, 'snake') or not self.snake or len(self.snake.x) == 0:
            return

        # Initialize goals if not exists
        if not hasattr(self, 'current_goal'):
            self.current_goal = 'collect_apple'

        if not hasattr(self, 'planned_path'):
            self.planned_path = []

        # Get current state
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        apple_x, apple_y = self.apple.x, self.apple.y

        # Evaluate current situation and set goals
        goals = self._evaluate_goals(head_x, head_y, apple_x, apple_y)

        # Find the best action based on current goals
        best_action = self._plan_action(goals, head_x, head_y, apple_x, apple_y)

        # Execute the action
        if best_action:
            self._execute_action(best_action)

    def _evaluate_goals(self, head_x, head_y, apple_x, apple_y):
        """
        Evaluate and prioritize goals based on current game state.
        Returns a list of goals in order of priority.
        """
        goals = []

        # Goal 1: Immediate survival check
        immediate_danger = self._assess_immediate_danger(head_x, head_y)
        if immediate_danger:
            goals.append(('avoid_collision', 1.0))

        # Goal 2: Maintain escape routes
        escape_routes = self._count_escape_routes(head_x, head_y)
        if escape_routes <= 2:
            goals.append(('maintain_space', 0.8))

        # Goal 3: Collect apple
        goals.append(('collect_apple', 0.6))

        # Goal 4: Explore/maintain position
        goals.append(('explore', 0.3))

        return goals

    def _assess_immediate_danger(self, head_x, head_y):
        """
        Check if there's immediate danger in the next 2-3 moves.
        """
        danger_count = 0
        directions = ['left', 'right', 'up', 'down']

        for direction in directions:
            if self._is_direction_blocked(head_x, head_y, direction):
                danger_count += 1

        # If 3 or more directions are blocked, we're in immediate danger
        return danger_count >= 3

    def _count_escape_routes(self, head_x, head_y):
        """
        Count available escape routes (safe directions).
        """
        safe_routes = 0
        directions = ['left', 'right', 'up', 'down']

        for direction in directions:
            if not self._is_direction_blocked(head_x, head_y, direction):
                safe_routes += 1

        return safe_routes

    def _is_direction_blocked(self, head_x, head_y, direction):
        """
        Check if a direction is blocked by walls or snake body.
        """
        next_x, next_y = self._get_potential_head(direction)
        return self._is_potential_move_colliding(next_x, next_y)

    def _plan_action(self, goals, head_x, head_y, apple_x, apple_y):
        """
        Plan the best action based on current goals.
        """
        # Get all possible actions
        possible_actions = []
        directions = ['left', 'right', 'up', 'down']

        for direction in directions:
            # Skip U-turns
            if ((direction == 'left' and self.snake.direction == 'right') or
                    (direction == 'right' and self.snake.direction == 'left') or
                    (direction == 'up' and self.snake.direction == 'down') or
                    (direction == 'down' and self.snake.direction == 'up')):
                continue

            # Check if move is safe
            next_x, next_y = self._get_potential_head(direction)
            if not self._is_potential_move_colliding(next_x, next_y):
                possible_actions.append((direction, next_x, next_y))

        if not possible_actions:
            return None

        # Score each action based on goals
        best_action = None
        best_score = -float('inf')

        for action, next_x, next_y in possible_actions:
            score = 0

            # Evaluate action against each goal
            for goal, weight in goals:
                if goal == 'avoid_collision':
                    # Higher score for actions that maintain more escape routes
                    future_routes = self._count_future_escape_routes(next_x, next_y)
                    score += weight * future_routes * 10

                elif goal == 'maintain_space':
                    # Prefer moves that keep us in open areas
                    space_score = self._evaluate_space_availability(next_x, next_y)
                    score += weight * space_score

                elif goal == 'collect_apple':
                    # Score based on distance to apple
                    current_dist = self._calculate_distance(head_x, head_y, apple_x, apple_y)
                    new_dist = self._calculate_distance(next_x, next_y, apple_x, apple_y)
                    if new_dist < current_dist:
                        score += weight * (current_dist - new_dist)

                elif goal == 'explore':
                    # Small bonus for exploring new areas
                    score += weight * 2

            # Update best action
            if score > best_score:
                best_score = score
                best_action = action

        return best_action

    def _count_future_escape_routes(self, x, y):
        """
        Count how many escape routes will be available from a future position.
        """
        escape_routes = 0
        directions = ['left', 'right', 'up', 'down']

        for direction in directions:
            if direction == 'left':
                next_x, next_y = x - SIZE, y
            elif direction == 'right':
                next_x, next_y = x + SIZE, y
            elif direction == 'up':
                next_x, next_y = x, y - SIZE
            elif direction == 'down':
                next_x, next_y = x, y + SIZE

            # Check if this future position would be safe
            screen_width, screen_height = self.surface.get_width(), self.surface.get_height()
            if (0 <= next_x < screen_width and 0 <= next_y < screen_height):
                # Check against snake body (excluding tail which will move)
                collision = False
                for i in range(1, min(self.snake.length - 1, len(self.snake.x) - 1)):
                    if self.is_collision(next_x, next_y, self.snake.x[i], self.snake.y[i]):
                        collision = True
                        break

                if not collision:
                    escape_routes += 1

        return escape_routes

    def _evaluate_space_availability(self, x, y):
        """
        Evaluate how much open space is available around a position.
        """
        open_space = 0
        search_radius = 3  # Check 3 blocks in each direction

        for dx in range(-search_radius, search_radius + 1):
            for dy in range(-search_radius, search_radius + 1):
                check_x = x + dx * SIZE
                check_y = y + dy * SIZE

                # Check if position is within bounds
                screen_width, screen_height = self.surface.get_width(), self.surface.get_height()
                if (0 <= check_x < screen_width and 0 <= check_y < screen_height):
                    # Check if position is not occupied by snake body
                    occupied = False
                    for i in range(len(self.snake.x)):
                        if self.is_collision(check_x, check_y, self.snake.x[i], self.snake.y[i]):
                            occupied = True
                            break

                    if not occupied:
                        open_space += 1

        return open_space

    def _execute_action(self, action):
        """
        Execute the chosen action.
        """
        if action == 'left':
            self.snake.move_left()
        elif action == 'right':
            self.snake.move_right()
        elif action == 'up':
            self.snake.move_up()
        elif action == 'down':
            self.snake.move_down()

    def random_agent(self):
        """
        Random agent that moves in random directions while avoiding immediate collisions.
        Useful for comparison with the simple reflex agent.
        """
        directions = ['left', 'right', 'up', 'down']
        safe_directions = []

        # Filter out directions that would cause immediate collision or U-turns
        for direction in directions:
            # Skip U-turns
            if ((direction == 'left' and self.snake.direction == 'right') or
                    (direction == 'right' and self.snake.direction == 'left') or
                    (direction == 'up' and self.snake.direction == 'down') or
                    (direction == 'down' and self.snake.direction == 'up')):
                continue

            # Check if move is safe
            next_head_x, next_head_y = self._get_potential_head(direction)
            if not self._is_potential_move_colliding(next_head_x, next_head_y):
                safe_directions.append(direction)

        # Choose random safe direction
        if safe_directions:
            chosen_direction = random.choice(safe_directions)
            if chosen_direction == 'left':
                self.snake.move_left()
            elif chosen_direction == 'right':
                self.snake.move_right()
            elif chosen_direction == 'up':
                self.snake.move_up()
            elif chosen_direction == 'down':
                self.snake.move_down()


# Entry point of the game application.
if __name__ == '__main__':
    game = Game()  # Create a Game object.
    game.run()  # Start the main game loop.