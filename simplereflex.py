import pygame # Core Pygame library for game development
from pygame.locals import * # Import common Pygame constants (e.g., K_LEFT, QUIT)
import time # For time-related functions like sleep and tracking elapsed time
import random # For generating random numbers (e.g., apple position, agent movement)
from datetime import datetime # Although not used for elapsed time, imported for general time needs
import math # For calculating Euclidean distance
import collections
from collections import deque



# --- Game Configuration Constants ---
SIZE = 40 # Size of each block (snake segment, apple) in pixels
BACKGROUND_COLOR = (110, 110, 5) # A greenish-brown color for fallback background


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
            self.image.fill((255, 0, 0)) # Fallback to red color

        # Initial position of the apple.
        # These will be immediately overwritten by the lists in the next lines.
        self.x = 120
        self.y = 120

        # Pre-defined lists of x and y coordinates for apple placement.
        # This makes the apple appear at specific, non-random locations in sequence.
        # The numbers are multiplied by SIZE implicitly in the move function,
        # so these values should be grid indices.
        self.x_list =[320, 160, 680, 280, 400, 240, 960, 80, 40, 760, 720, 880, 400, 680, 480, 480, 520, 160, 760, 480, 720, 360, 960, 160, 80, 400, 760, 680, 760, 800]
        self.y_list =[560, 40, 440, 280, 240, 560, 80, 200, 240, 80, 80, 520, 720, 360, 680, 760, 680, 320, 80, 360, 720, 120, 280, 280, 320, 680, 320, 40, 520, 600]
        self.count = 0 # Counter to index into x_list and y_list for apple movement.

    def draw(self):
        """Draws the apple on the parent screen at its current (x, y) coordinates."""
        self.parent_screen.blit(self.image, (self.x, self.y))
        pygame.display.flip() # Update the display to show the newly drawn apple.

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
        self.count = (self.count + 1) % len(self.x_list) # Assumes x_list and y_list have same length


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
            self.image.fill((0, 128, 0)) # Fallback to green color

        self.direction = 'down' # Initial direction of the snake.
        self.best_time = "" # To store the best time recorded for eating an apple.

        self.length = 1 # Initial length of the snake (one block).
        # Lists to store the (x, y) coordinates for each segment of the snake.
        self.x = [40] # Initial x-coordinate of the head.
        self.y = [40] # Initial y-coordinate of the head.

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
            self.x[i] = self.x[i-1]
            self.y[i] = self.y[i-1]

        # Update head position based on current direction.
        if self.direction == 'left':
            self.x[0] -= SIZE
        elif self.direction == 'right':
            self.x[0] += SIZE
        elif self.direction == 'up':
            self.y[0] -= SIZE
        elif self.direction == 'down':
            self.y[0] += SIZE

        self.draw() # Redraw the snake after moving.

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
        pygame.init() # Initialize all the Pygame modules.
        pygame.display.set_caption("Codebasics Snake And Apple Game") # Set the window title.

        pygame.mixer.init() # Initialize the mixer for sound playback.
        self.play_background_music() # Start playing background music when the game initializes.

        # Set up the display surface (game window) with a resolution of 1000x800 pixels.
        self.surface = pygame.display.set_mode((1000, 800))
        # Initial background fill (this will be overwritten by the background image later).
        self.surface.fill(BACKGROUND_COLOR)

        # Create instances of the Snake and Apple classes, passing the game surface.
        self.snake = Snake(self.surface)
        self.snake.draw() # Draw the snake's initial position.
        self.apple = Apple(self.surface)
        self.apple.draw() # Draw the apple's initial position.

        self.elapsed_time = "" # Stores the formatted total elapsed time when the game ends.

        self.game_speed = 0.30 # Controls how fast the snake moves (lower value = faster).
        self.start_time = time.time() # Records the timestamp when the current game session starts.
        # Add to Game.__init__()
        self.q_table = {}  # Q-Table: key=(state, action), value=Q-value
        self.epsilon = 0.1  # Exploration rate
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.9  # Discount factor

    def play_background_music(self):
        """Loads and plays background music in an infinite loop."""
        try:
            pygame.mixer.music.load('resources/bg_music_1.mp3')
            pygame.mixer.music.play(-1, 0) # -1 means loop indefinitely, 0 is the starting position.
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
        self.snake = Snake(self.surface) # Recreate a new snake.
        self.apple = Apple(self.surface) # Recreate a new apple.
        self.elapsed_time = "" # Clear elapsed time.
        self.snake.best_time = "" # Clear best time for eating an apple.
        self.start_time = time.time() # Reset the start time for the new game.

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
            self.surface.blit(bg, (0,0))
        except pygame.error:
            print("Warning: 'resources/background.jpg' not found. Using solid background color.")
            self.surface.fill(BACKGROUND_COLOR) # Fallback to solid color if image is missing.

    def play(self):
        """
        Performs one full step of the game:
        1. Renders the background, snake, and apple.
        2. Updates and displays score and time.
        3. Checks for eating apple, self-collision, and wall collision.
        """
        self.render_background() # Draw the game background.
        self.snake.walk() # Update and draw the snake's new position.
        self.apple.draw() # Draw the apple.
        self.display_score() # Display the current score.
        self.display_time(False) # Display the elapsed time (False indicates not for scoring time).
        pygame.display.flip() # Update the entire screen to show all drawn elements.

        # Snake eating apple scenario.
        if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.display_time(True) # Capture the time at which this apple was eaten.
            self.play_sound("ding") # Play ding sound.
            self.snake.increase_length() # Increase snake's length.
            # Decrease game speed every 5 apples eaten to increase difficulty.
            # Ensure game_speed does not go below a reasonable minimum (e.g., 0.05 or 0.01)
            # 0.01 would be very fast, effectively almost instant.
            MIN_GAME_SPEED = 0.05  # Define a minimum speed

            # Inside the play method, where you update game_speed:
            if (self.snake.length) % 5 == 0:
                # Calculate the potential new speed
                potential_new_speed = self.game_speed - 0.04
                # Ensure it doesn't go below the minimum
                self.game_speed = max(potential_new_speed, MIN_GAME_SPEED)
            self.apple.move() # Move apple to a new location.

        # Snake colliding with itself.
        if self.self_collision():
            self.play_sound('crash') # Play crash sound.
            raise Exception("Collision Occurred") # Raise an exception to trigger game over.

        # Snake colliding with wall.
        if self.check_wall_collision():
            self.play_sound('crash') # Play crash sound.
            raise Exception("Wall Collision!") # Raise an exception to trigger game over.

    def display_score(self):
        """Renders and displays the current score on the screen."""
        font = pygame.font.SysFont('arial',30) # Define font and size.
        # Score is snake's length minus 1, assuming initial length 1.
        score_text = font.render(f"Score: {self.snake.length - 1}", True, (200,200,200)) # (True for antialiasing, color)
        self.surface.blit(score_text,(850,10)) # Position the score text in the top-right.

    def display_time(self, score_t=False):
        """
        Renders and displays the elapsed time on the screen.
        Args:
            score_t (bool): If True, captures the current elapsed time as the 'best_time'
                            (time to eat an apple).
        """
        font = pygame.font.SysFont('arial', 30)
        elapsed_seconds = int(time.time() - self.start_time) # Calculate elapsed time in seconds.
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        time_string = f"{minutes:02d}:{seconds:02d}" # Format time as MM:SS (e.g., 01:05).
        self.elapsed_time = time_string # Store the total elapsed time.

        if score_t:
            self.snake.best_time = time_string # Update best_time when an apple is eaten.

        time_text = font.render(f"Time: {time_string}", True, (200, 200, 200))
        self.surface.blit(time_text, (10, 10)) # Position the time text in the top-left.

    def show_game_over(self, message="Game Over!"):
        """
        Displays the game over screen with the final score, best apple eating time,
        total game time, and instructions to restart/exit.
        """
        self.render_background() # Redraw background for the game over screen.
        font = pygame.font.SysFont('arial', 30)

        # Display game over messages and scores.
        line1 = font.render(f"Game is over! ", True, (255, 255, 255))
        self.surface.blit(line1, (200, 200))
        line1 = font.render(f"Your score = {self.snake.length - 1}", True, (255, 255, 255))
        self.surface.blit(line1, (250, 350))
        line1 = font.render(f"Last Apple Time = {self.snake.best_time}", True, (255, 255, 255)) # Corrected text
        self.surface.blit(line1, (250, 400))
        line1 = font.render(f"Total Game Time = {self.elapsed_time}", True, (255, 255, 255))
        self.surface.blit(line1, (250, 450))
        line2 = font.render("To play again press Enter. To exit press Escape!", True, (255, 255, 255))
        self.surface.blit(line2, (200, 550))

        pygame.mixer.music.pause() # Pause background music when game is over.
        pygame.display.flip() # Update the screen to show the game over text.

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
            return True # Collides with wall

        # Check self-collision against existing body segments (excluding current head)
        # We need to be careful here: if the snake is about to eat, its tail won't move.
        # But generally, for collision prediction, we assume the tail moves.
        # A more robust check might temporarily remove the tail for prediction if length > 1
        # and not eating, but for "model-based reflex," this simplified check is common.
        for i in range(self.snake.length): # Check all existing segments
            # If the potential head position is the same as any body segment's current position
            # (and it's not the current head itself, which is always safe)
            if i == 0: continue # Don't check against current head
            if self.is_collision(next_head_x, next_head_y, self.snake.x[i], self.snake.y[i]):
                return True # Collides with self (body)

        return False # No collision

    def _calculate_distance(self, x1, y1, x2, y2):
        """
        Calculates the Euclidean distance between two points.
        Args:
            x1, y1 (int): Coordinates of the first point.
            x2, y2 (int): Coordinates of the second point.
        Returns:
            float: The Euclidean distance.
        """
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def vertical_agent(self):
        """
        A simple reflex agent that primarily moves the snake up and down
        to align with the apple's Y-coordinate. If already aligned vertically,
        it will try to move right to reach the apple.
        """
        head_y = self.snake.y[0]
        apple_y = self.apple.y

        # Prioritize vertical movement to align with the apple's Y-coordinate
        if head_y < apple_y:
            # Check if moving down would cause a collision
            next_x, next_y = self._get_potential_head('down')
            if not self._is_potential_move_colliding(next_x, next_y):
                self.snake.move_down()
            # If moving down would collide, try to move horizontally to avoid it (though this is a vertical agent)
            else:
                next_x, next_y = self._get_potential_head('right')
                if not self._is_potential_move_colliding(next_x, next_y):
                    self.snake.move_right()


        elif head_y > apple_y:
            # Check if moving up would cause a collision
            next_x, next_y = self._get_potential_head('up')
            if not self._is_potential_move_colliding(next_x, next_y):
                self.snake.move_up()
            else:
                # If cannot move up, try to move right
                next_x, next_y = self._get_potential_head('right')
                if not self._is_potential_move_colliding(next_x, next_y):
                    self.snake.move_right()

        else: # head_y == apple_y (aligned vertically)
            # If aligned vertically, try to move horizontally towards the apple's X-coordinate.
            head_x = self.snake.x[0]
            apple_x = self.apple.x

            if head_x < apple_x:
                next_x, next_y = self._get_potential_head('right')
                if not self._is_potential_move_colliding(next_x, next_y):
                    self.snake.move_right()
                else:
                    # If moving right is blocked, try moving up or down to find an opening
                    next_x_up, next_y_up = self._get_potential_head('up')
                    next_x_down, next_y_down = self._get_potential_head('down')

                    if not self._is_potential_move_colliding(next_x_up, next_y_up):
                        self.snake.move_up()
                    elif not self._is_potential_move_colliding(next_x_down, next_y_down):
                        self.snake.move_down()

            elif head_x > apple_x:
                # If we are to the right of the apple and vertically aligned, we need to move left.
                # For this agent, let's make it try to move left if possible.
                next_x, next_y = self._get_potential_head('left')
                if not self._is_potential_move_colliding(next_x, next_y):
                    self.snake.move_left()
                else:
                    # If moving left is blocked, try up/down
                    next_x_up, next_y_up = self._get_potential_head('up')
                    next_x_down, next_y_down = self._get_potential_head('down')
                    if not self._is_potential_move_colliding(next_x_up, next_y_up):
                        self.snake.move_up()
                    elif not self._is_potential_move_colliding(next_x_down, next_y_down):
                        self.snake.move_down()
            else: # head_x == apple_x and head_y == apple_y (at apple)
                pass

    def model_based_agent(self):
        """
        A model-based reflex agent that chooses the best move by
        predicting the outcome of each possible move (up, down, left, right)
        and selecting the one that:
        1. Does not result in a wall or self-collision.
        2. Minimizes the Euclidean distance to the apple.
        If multiple moves satisfy these, it prefers a specific order (e.g., right, down, up, left).
        If no move reduces distance but some are safe, it picks a safe one.
        If all moves are unsafe, it might stay put (leading to collision detection by game).
        """
        current_head_x, current_head_y = self.snake.x[0], self.snake.y[0]
        apple_x, apple_y = self.apple.x, self.apple.y
        current_distance = self._calculate_distance(current_head_x, current_head_y, apple_x, apple_y)

        # Define possible moves and their corresponding snake methods
        # Ordered by a preference: right, down, up, left (common for snake behavior)
        possible_moves = {
            'right': self.snake.move_right,
            'down': self.snake.move_down,
            'up': self.snake.move_up,
            'left': self.snake.move_left
        }

        best_move = None
        min_distance = float('inf')
        safe_moves = [] # Store safe moves, even if they don't reduce distance

        for direction, move_method in possible_moves.items():
            potential_x, potential_y = self._get_potential_head(direction)

            # Check if this potential move leads to a collision using the model
            if not self._is_potential_move_colliding(potential_x, potential_y):
                # This move is safe
                safe_moves.append(direction)

                # Calculate the distance to the apple if this move is made
                new_distance = self._calculate_distance(potential_x, potential_y, apple_x, apple_y)

                # If this move reduces the distance AND is better than current best
                if new_distance < min_distance:
                    min_distance = new_distance
                    best_move = direction

        # Decision logic:
        if best_move:
            # Found a safe move that reduces distance to the apple
            possible_moves[best_move]() # Execute the best move
        elif safe_moves:
            # No move reduces distance, but some moves are safe.
            # Pick one of the safe moves (e.g., the first one in our preferred order, or random)
            # For robustness, we can try to maintain current direction if safe and no better alternative
            # or simply pick the first safe one. Let's just pick the first safe one found in order.
            current_dir = self.snake.direction
            # Try to stay in current direction if safe
            if current_dir in safe_moves:
                possible_moves[current_dir]()
            else:
                # Otherwise, pick any safe move based on preference
                for direction in possible_moves.keys():
                    if direction in safe_moves:
                        possible_moves[direction]()
                        break
        # else:
            # No safe moves found. The game will eventually detect collision.
            # The agent essentially waits for inevitable collision here, which is intended
            # for a model-based *reflex* agent that doesn't plan escapes.

    def Pankaj_agent(self):
        """
        A simple reflex agent that moves toward the apple using greedy logic.
        It avoids any move that results in an immediate collision.
        """
        directions = ['up', 'down', 'left', 'right']
        best_direction = None
        min_distance = float('inf')

        for direction in directions:
            next_x, next_y = self._get_potential_head(direction)
            if not self._is_potential_move_colliding(next_x, next_y):
                # Calculate distance from potential head position to apple
                distance = self._calculate_distance(next_x, next_y, self.apple.x, self.apple.y)
                if distance < min_distance:
                    min_distance = distance
                    best_direction = direction

        # Apply the best direction (closest to apple and no immediate collision)
        if best_direction:
            if best_direction == 'up':
                self.snake.move_up()
            elif best_direction == 'down':
                self.snake.move_down()
            elif best_direction == 'left':
                self.snake.move_left()
            elif best_direction == 'right':
                self.snake.move_right()

    def goal_based_agent(self):
        """
        A goal-based agent that uses BFS to find the shortest path to the apple,
        avoiding immediate wall and self collisions.
        """
        directions = ['up', 'down', 'left', 'right']
        move_map = {
            'up': (0, -SIZE),
            'down': (0, SIZE),
            'left': (-SIZE, 0),
            'right': (SIZE, 0),
        }

        head = (self.snake.x[0], self.snake.y[0])
        goal = (self.apple.x, self.apple.y)

        # Visited keeps track of visited positions to prevent loops
        visited = set()
        queue = deque()
        queue.append((head, []))  # Each entry: (position, path_taken)

        while queue:
            current_pos, path = queue.popleft()
            if current_pos == goal:
                if path:
                    next_move = path[0]  # Only do the first move
                    if next_move == 'up':
                        self.snake.move_up()
                    elif next_move == 'down':
                        self.snake.move_down()
                    elif next_move == 'left':
                        self.snake.move_left()
                    elif next_move == 'right':
                        self.snake.move_right()
                return

            for direction in directions:
                dx, dy = move_map[direction]
                new_x = current_pos[0] + dx
                new_y = current_pos[1] + dy
                new_pos = (new_x, new_y)

                # Skip if out of bounds or colliding
                if self._is_potential_move_colliding(new_x, new_y):
                    continue

                if new_pos not in visited:
                    visited.add(new_pos)
                    queue.append((new_pos, path + [direction]))

        # If no path found, fallback to simple agent (to avoid freezing)
        self.Pankaj_agent()

    def Pankaj_goal_based(self):
        """
        A Goal-Based Agent that uses Breadth-First Search (BFS) to find the shortest
        safe path to the apple and executes the first step of that path.

        It considers the snake's body and walls as obstacles.
        """
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        apple_x, apple_y = self.apple.x, self.apple.y

        # Convert pixel coordinates to grid coordinates for pathfinding
        # Assuming SIZE is the grid cell size
        start_node = (head_x // SIZE, head_y // SIZE)
        goal_node = (apple_x // SIZE, apple_y // SIZE)

        # Represent the game board as a grid for pathfinding
        # Create a set of occupied cells (snake body and walls)
        # The tail of the snake is assumed to move, so it's not a permanent obstacle
        # UNLESS the snake is about to eat, in which case the tail position stays.
        occupied_cells = set()
        # Add snake body segments as obstacles. Exclude the head, and potentially the tail
        # if the snake is not about to eat and is long enough.
        # For a simpler goal-based agent, let's treat all current body parts as obstacles
        # except the head itself, for now.
        for i in range(1, self.snake.length):  # Start from the first body segment
            occupied_cells.add((self.snake.x[i] // SIZE, self.snake.y[i] // SIZE))

        # Add wall boundaries as implicit obstacles by checking potential moves

        # BFS implementation
        queue = collections.deque([(start_node, [])])  # Queue stores (current_node, path_to_current_node)
        visited = {start_node}  # Keep track of visited nodes to avoid loops

        # Directions mapping
        directions = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }
        direction_names = ['up', 'down', 'left', 'right']  # Ordered preference (can be randomized too)

        found_path = None

        while queue:
            current_node, path = queue.popleft()

            if current_node == goal_node:
                found_path = path
                break

            # Explore neighbors
            for direction_name in direction_names:
                dx, dy = directions[direction_name]
                neighbor_x_grid, neighbor_y_grid = current_node[0] + dx, current_node[1] + dy

                # Convert grid coords back to pixel for collision check using _is_potential_move_colliding
                neighbor_x_pixel = neighbor_x_grid * SIZE
                neighbor_y_pixel = neighbor_y_grid * SIZE

                neighbor_node = (neighbor_x_grid, neighbor_y_grid)

                # Check if neighbor is valid (within bounds, not in snake body, not visited)
                # We use the existing _is_potential_move_colliding, but need to adapt it
                # since it's designed for the *snake's actual head*.
                # For pathfinding, we need a generalized collision check for *any* potential cell.
                # Let's assume _is_potential_move_colliding is robust enough if we pass
                # the potential new head for the *simulation*.

                # More directly, check against walls and occupied cells:
                screen_width, screen_height = self.surface.get_width(), self.surface.get_height()
                is_wall_collision = not (0 <= neighbor_x_pixel < screen_width and 0 <= neighbor_y_pixel < screen_height)
                is_body_collision = neighbor_node in occupied_cells

                if not is_wall_collision and not is_body_collision and neighbor_node not in visited:
                    visited.add(neighbor_node)
                    new_path = path + [direction_name]
                    queue.append((neighbor_node, new_path))

        if found_path:
            # Execute the first step of the found path
            next_move_direction = found_path[0]
            if next_move_direction == 'up':
                self.snake.move_up()
            elif next_move_direction == 'down':
                self.snake.move_down()
            elif next_move_direction == 'left':
                self.snake.move_left()
            elif next_move_direction == 'right':
                self.snake.move_right()
        else:
            # If no path is found (e.g., apple is unreachable, snake is trapped)
            # The agent should try to find a safe move to stay alive as long as possible,
            # or implement a "survival" strategy.
            # For simplicity, if no path to apple, fall back to model-based reflex:
            self.model_based_agent()

    # Inside Game class
    def _is_cell_occupied(self, cell_x_pixel, cell_y_pixel, snake_body_to_exclude_head=False):
        """
        Checks if a given pixel coordinate cell is occupied by any part of the snake's body
        or a wall.
        Args:
            cell_x_pixel, cell_y_pixel (int): The pixel coordinates of the cell to check.
            snake_body_to_exclude_head (bool): If True, the current head position is not considered
                                               an obstacle (useful for pathfinding to immediate neighbors).
        Returns:
            bool: True if the cell is occupied by a snake segment or a wall, False otherwise.
        """
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()

        # Wall collision check
        if not (0 <= cell_x_pixel < screen_width and 0 <= cell_y_pixel < screen_height):
            return True

        # Snake body collision check
        start_index = 1 if snake_body_to_exclude_head else 0
        for i in range(start_index, self.snake.length):
            # For utility calculation, we're considering where the *potential* head will be.
            # If the current snake's body segment 'i' is where the potential head lands,
            # and 'i' is NOT the tail (which would vacate its spot), then it's a collision.
            # A perfect model would need to predict tail movement for all N steps.
            # For a reflex agent, we approximate: consider all current body parts as obstacles,
            # except the current head, and if length > 1, the tail for a future step.
            # For simplicity in this utility agent, let's treat all current segments (except the one being evaluated if it's the head)
            # as fixed obstacles for the *next* move.

            # This part is crucial for accuracy. When predicting, the tail moves.
            # A common approximation for immediate collision is to check against all
            # segments *except* the head, AND *except* the tail's future position.
            # Simpler: check against all segments that are NOT the current head,
            # and assume the tail position *will* be free.
            # Let's adjust for this in the utility_based_agent's loop instead of here.
            # This helper will only check against existing snake coordinates.
            if self.is_collision(cell_x_pixel, cell_y_pixel, self.snake.x[i], self.snake.y[i]):
                # If the collision is with the last segment of the snake and snake length > 1,
                # it's usually not a collision because the tail moves out.
                # Only if the potential head is the *current* tail position (and snake is not eating,
                # or tail won't move because length is too short)
                # This needs careful handling. For a robust utility agent, we'd need a simulated move.

                # Simplified for reflex: if the cell is any current body part (except the current head), it's occupied.
                # The assumption is that the tail moves, so if the target is the tail, it's ok IF length > 1.
                if self.snake.length > 1 and i == self.snake.length - 1 and \
                        (cell_x_pixel, cell_y_pixel) == (self.snake.x[i], self.snake.y[i]):
                    continue  # This is the tail, and it will move, so it's not a collision spot for the next head.
                else:
                    return True
        return False

    def calculate_utility(self, potential_head_x, potential_head_y, current_snake_direction):
        """
        Calculates the utility score for a given potential next head position.
        Higher score means better utility.
        Args:
            potential_head_x, potential_head_y (int): The pixel coordinates of the potential next snake head.
            current_snake_direction (str): The direction of the snake for this potential move.
        Returns:
            float: The calculated utility score.
        """
        # --- Penalties/Rewards ---
        UTILITY_COLLISION_PENALTY = -1000000  # Very high penalty for collision
        UTILITY_DISTANCE_WEIGHT = -1  # Negative weight for distance (closer is better)
        UTILITY_ALIVE_BONUS = 100  # Bonus for just being alive and making a safe move
        UTILITY_STRAIGHT_PREFERENCE = 1  # Small bonus for continuing straight (less erratic)

        # 1. Collision Check (most important factor)
        # We need a more accurate check that simulates the snake's new body.
        # For a true utility *based* agent that considers "state", we'd simulate the full new snake state.
        # For a reflex agent, we use _is_cell_occupied and _get_potential_head.

        # A slightly more robust collision check for utility evaluation:
        # Get the snake's body parts for *this potential move*.
        # The new body will be: potential_head_x, potential_head_y + snake.x[0:-1] (shifted)
        # And the tail moves if not eating.
        # For a reflex agent, the _is_cell_occupied helper is usually sufficient if carefully applied.

        # Simplified for now: if the *potential head* itself collides with any *current* body part
        # (excluding its own current head position), or a wall.
        if self._is_cell_occupied(potential_head_x, potential_head_y, snake_body_to_exclude_head=True):
            return UTILITY_COLLISION_PENALTY  # This move is fatal

        # 2. Distance to Apple (primary goal)
        apple_x, apple_y = self.apple.x, self.apple.y
        distance_to_apple = self._calculate_distance(potential_head_x, potential_head_y, apple_x, apple_y)
        # Closer distance gives higher utility (since UTILITY_DISTANCE_WEIGHT is negative)
        utility_score = UTILITY_DISTANCE_WEIGHT * distance_to_apple

        # 3. Basic "Alive" Bonus
        utility_score += UTILITY_ALIVE_BONUS

        # 4. Preference for Straight Movement (reduces erratic turns)
        if current_snake_direction == self.snake.direction:
            utility_score += UTILITY_STRAIGHT_PREFERENCE

        # 5. Optional: Avoid getting trapped in dead ends (requires more complex lookahead/model)
        # This is difficult for a pure reflex agent and typically involves looking ahead
        # several steps (e.g., ensuring there's still a path to the tail or an open area).
        # We'll omit this for a pure *reflex* utility agent.

        return utility_score

    def utility_based_agent(self):
        """
        A Utility-Based Agent that chooses the best move by calculating
        the utility of the state resulting from each possible action.
        It prioritizes safety (avoiding collisions) and then proximity to the apple.
        """
        current_head_x, current_head_y = self.snake.x[0], self.snake.y[0]
        current_direction = self.snake.direction

        possible_moves = {
            'right': self.snake.move_right,
            'down': self.snake.move_down,
            'up': self.snake.move_up,
            'left': self.snake.move_left
        }

        best_utility = float('-inf')  # Initialize with a very low utility
        best_move_direction = None

        # Try to maintain the current direction first, if it's a valid move.
        # This reduces jitter and makes behavior more predictable.
        preferred_order = [current_direction]
        for d in ['right', 'down', 'up', 'left']:
            if d not in preferred_order:
                preferred_order.append(d)

        for direction in preferred_order:
            # Predict the next head position for this potential move
            potential_x, potential_y = self._get_potential_head(direction)

            # Calculate the utility of this potential move
            # The calculate_utility function handles collision detection internally
            current_move_utility = self.calculate_utility(potential_x, potential_y, direction)

            if current_move_utility > best_utility:
                best_utility = current_move_utility
                best_move_direction = direction

        # Execute the chosen best move
        if best_move_direction:
            # Check if the best move would lead to an immediate collision
            # (redundant if calculate_utility already assigns very low score for collision,
            # but good as a final safeguard)
            potential_x, potential_y = self._get_potential_head(best_move_direction)
            if best_utility <= self.calculate_utility(current_head_x, current_head_y, current_direction) and \
                    self._is_cell_occupied(potential_x, potential_y, snake_body_to_exclude_head=True):
                # If the chosen best move has a very low utility (meaning it's a collision)
                # AND it's not better than staying put (which isn't really an option for snake, but implies a trap)
                # This could happen if all moves lead to collision.
                # In such cases, the agent effectively "gives up" and the game's
                # main collision detection will end the round.
                pass  # Do nothing, let the game's collision detection handle it
            else:
                if best_move_direction == 'up':
                    self.snake.move_up()
                elif best_move_direction == 'down':
                    self.snake.move_down()
                elif best_move_direction == 'left':
                    self.snake.move_left()
                elif best_move_direction == 'right':
                    self.snake.move_right()
        # If best_move_direction is None (shouldn't happen unless all moves are equally bad
        # and initialized best_utility is never beaten, or list of moves is empty),
        # the snake simply won't move in this frame.

    # Then, modify _is_potential_move_colliding to use this, or better,
    # adapt it for the BFS context. For BFS, you often build an 'obstacle map' first.
    # The provided goal_based_agent directly builds `occupied_cells` in grid format.
    def _get_state(self):
        """
        Encodes the game state into a tuple for use as a Q-table key.
        Simplified to a relative position-based encoding.
        """
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        apple_x, apple_y = self.apple.x, self.apple.y

        # Is apple in each direction?
        apple_left = apple_x < head_x
        apple_right = apple_x > head_x
        apple_up = apple_y < head_y
        apple_down = apple_y > head_y

        # Danger flags
        danger_left = self._is_potential_move_colliding(head_x - SIZE, head_y)
        danger_right = self._is_potential_move_colliding(head_x + SIZE, head_y)
        danger_up = self._is_potential_move_colliding(head_x, head_y - SIZE)
        danger_down = self._is_potential_move_colliding(head_x, head_y + SIZE)

        return (
            apple_left, apple_right, apple_up, apple_down,
            danger_left, danger_right, danger_up, danger_down,
            self.snake.direction
        )

    def learning_agent(self):
        """
        A basic Q-learning agent for the snake game.
        It learns from rewards and updates Q-values accordingly.
        """
        state = self._get_state()
        actions = ['left', 'right', 'up', 'down']

        # ε-greedy action selection
        if random.random() < self.epsilon:
            action = random.choice(actions)
        else:
            q_vals = [self.q_table.get((state, a), 0) for a in actions]
            max_q = max(q_vals)
            best_actions = [a for a, q in zip(actions, q_vals) if q == max_q]
            action = random.choice(best_actions)

        # Execute action
        prev_x, prev_y = self.snake.x[0], self.snake.y[0]

        if action == 'left':
            self.snake.move_left()
        elif action == 'right':
            self.snake.move_right()
        elif action == 'up':
            self.snake.move_up()
        elif action == 'down':
            self.snake.move_down()

        try:
            self.play()
        except Exception:
            reward = -100  # Penalty for dying
            self._update_q_table(state, action, reward, terminal=True)
            raise

        # Reward logic
        new_state = self._get_state()
        if (self.snake.x[0], self.snake.y[0]) == (self.apple.x, self.apple.y):
            reward = 100  # Ate apple
        else:
            reward = -1  # Small penalty for each step to encourage faster solutions

        # Update Q-table
        self._update_q_table(state, action, reward, new_state)

    def _update_q_table(self, state, action, reward, next_state=None, terminal=False):
        """
        Q-learning update rule.
        """
        old_q = self.q_table.get((state, action), 0)
        if terminal:
            new_q = reward
        else:
            future_qs = [self.q_table.get((next_state, a), 0) for a in ['left', 'right', 'up', 'down']]
            max_future_q = max(future_qs)
            new_q = old_q + self.alpha * (reward + self.gamma * max_future_q - old_q)

        self.q_table[(state, action)] = new_q

    def run(self):
        """
        The main game loop. Handles events, updates game state, and controls game flow.
        """
        running = True # Controls if the game window is open.
        pause = False # Controls if the game logic is paused.

        while running:
            # Event handling loop: processes user inputs (keyboard, window close).
            for event in pygame.event.get():
                if event.type == KEYDOWN: # A key has been pressed.
                    if event.key == K_ESCAPE:
                        running = False # Set running to False to exit the game loop.

                    if event.key == K_RETURN: # Enter key pressed.
                        pygame.mixer.music.unpause() # Resume background music.
                        if pause == True: # If game was paused (after game over).
                            self.start_time = time.time() # Reset game start time.
                        pause = False # Unpause the game.
                        self.reset() # Reset the game state for a new round.

                    # Manual control for debugging or testing without agent
                    # if not pause: # Only allow snake movement if the game is not paused.
                    #     if event.key == K_LEFT:
                    #         self.snake.move_left()
                    #     elif event.key == K_RIGHT:
                    #         self.snake.move_right()
                    #     elif event.key == K_UP:
                    #         self.snake.move_up()
                    #     elif event.key == K_DOWN:
                    #         self.snake.move_down()

                elif event.type == QUIT: # User clicked the window close button (X).
                    running = False # Exit the game loop.

            # Agent movement control: Uncomment one of the lines below to activate an agent.
            if not pause:
                # self.vertical_agent() # Activate the simple vertical agent
                # self.random_agent() # Activate the random agent
                #self.model_based_agent() # Activate the model-based reflex agent
                #self.Pankaj_agent() #Simple reflex agent gemini
                self.goal_based_agent() #Chat GPT
                #self.Pankaj_goal_based() #GeMini
                #self.utility_based_agent()
                #self.learning_agent()


            # Game logic and rendering executed only if the game is not paused.
            try:
                if not pause:
                    self.play() # Execute one frame of the game (move snake, check collisions, draw).
                    #self.learning_agent()
            except Exception as e:
                # Catch exceptions raised during play (e.g., "Collision Occurred", "Wall Collision!").
                self.show_game_over(str(e)) # Display the specific game over message.
                #self.reset()
                time.sleep(0.5)  # Short pause before next episode
                pause = True # Pause the game after game over.

            # Control game speed using time.sleep().
            # Lower `self.game_speed` value means faster game updates.
            time.sleep(self.game_speed)


# Entry point of the game application.
if __name__ == '__main__':
    game = Game() # Create a Game object.
    game.run() # Start the main game loop.