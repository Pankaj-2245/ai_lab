import pygame # Core Pygame library for game development
from pygame.locals import * # Import common Pygame constants (e.g., K_LEFT, QUIT)
import time # For time-related functions like sleep and tracking elapsed time
import random # For generating random numbers (e.g., apple position, agent movement)
from datetime import datetime # Although not used for elapsed time, imported for general time needs
import math # For calculating Euclidean distance

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
            self.game_speed = (self.game_speed - 0.04) if (self.snake.length) % 5 == 0 else self.game_speed
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
        # This assumes the tail will move, so the last segment won't be a collision point.
        for i in range(1, self.snake.length): # Iterate from the first body segment (index 1)
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

                    if not pause: # Only allow snake movement if the game is not paused.
                        if event.key == K_LEFT:
                            self.snake.move_left()
                        elif event.key == K_RIGHT:
                            self.snake.move_right()
                        elif event.key == K_UP:
                            self.snake.move_up()
                        elif event.key == K_DOWN:
                            self.snake.move_down()

                elif event.type == QUIT: # User clicked the window close button (X).
                    running = False # Exit the game loop.

            # Agent movement control: Uncomment one of the lines below to activate an agent.
            # if not pause:
                # self.random_agent() # Activate the random agent
                # self.simple_agent() # Activate the simple, greedy agent
        

            # Game logic and rendering executed only if the game is not paused.
            try:
                if not pause:
                    self.play() # Execute one frame of the game (move snake, check collisions, draw).
            except Exception as e:
                # Catch exceptions raised during play (e.g., "Collision Occurred", "Wall Collision!").
                self.show_game_over(str(e)) # Display the specific game over message.
                pause = True # Pause the game after game over.

            # Control game speed using time.sleep().
            # Lower `self.game_speed` value means faster game updates.
            time.sleep(self.game_speed)


# Entry point of the game application.
if __name__ == '__main__':
    game = Game() # Create a Game object.
    game.run() # Start the main game loop.
