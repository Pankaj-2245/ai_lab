import pygame
from pygame.locals import *
import time
import random
from datetime import datetime
import math
from collections import deque

# --- Game Configuration Constants ---
SIZE = 40
BACKGROUND_COLOR = (110, 110, 5)


class Apple:
    """
    Represents the food that the snake eats.
    """
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        try:
            self.image = pygame.image.load("resources/apple.png").convert_alpha()
        except pygame.error:
            print("Warning: 'resources/apple.png' not found. Using a red square as placeholder.")
            self.image = pygame.Surface((SIZE, SIZE))
            self.image.fill((255, 0, 0))

        self.x = 120
        self.y = 120

        self.x_list =[320, 160, 680, 280, 400, 240, 960, 80, 40, 760, 720, 880, 400, 680, 480, 480, 520, 160, 760, 480, 720, 360, 960, 160, 80, 400, 760, 680, 760, 800]
        self.y_list =[560, 40, 440, 280, 240, 560, 80, 200, 240, 80, 80, 520, 720, 360, 680, 760, 680, 320, 80, 360, 720, 120, 280, 280, 320, 680, 320, 40, 520, 600]
        self.count = 0

    def draw(self):
        self.parent_screen.blit(self.image, (self.x, self.y))
        pygame.display.flip()

    def move(self):
        self.x = self.x_list[self.count]
        self.y = self.y_list[self.count]
        self.count = (self.count + 1) % len(self.x_list)


class Snake:
    """
    Represents the snake controlled by the player (or agent).
    """
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        try:
            self.image = pygame.image.load("resources/block.jpg").convert_alpha()
        except pygame.error:
            print("Warning: 'resources/block.jpg' not found. Using a green square as placeholder.")
            self.image = pygame.Surface((SIZE, SIZE))
            self.image.fill((0, 128, 0))

        self.direction = 'down'
        self.best_time = ""

        self.length = 1
        self.x = [40]
        self.y = [40]

    def move_left(self):
        if self.direction != 'right':
            self.direction = 'left'

    def move_right(self):
        if self.direction != 'left':
            self.direction = 'right'

    def move_up(self):
        if self.direction != 'down':
            self.direction = 'up'

    def move_down(self):
        if self.direction != 'up':
            self.direction = 'down'

    def walk(self):
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i-1]
            self.y[i] = self.y[i-1]

        if self.direction == 'left':
            self.x[0] -= SIZE
        elif self.direction == 'right':
            self.x[0] += SIZE
        elif self.direction == 'up':
            self.y[0] -= SIZE
        elif self.direction == 'down':
            self.y[0] += SIZE

        self.draw()

    def draw(self):
        for i in range(self.length):
            self.parent_screen.blit(self.image, (self.x[i], self.y[i]))

    def increase_length(self):
        self.length += 1
        self.x.append(-1)
        self.y.append(-1)


class Game:
    """
    Manages the overall game logic, including initialization,
    game loop, score, time, and collision detection.
    """
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Codebasics Snake And Apple Game")

        pygame.mixer.init()
        self.play_background_music()

        self.surface = pygame.display.set_mode((1000, 800))
        self.surface.fill(BACKGROUND_COLOR)

        self.snake = Snake(self.surface)
        self.snake.draw()
        self.apple = Apple(self.surface)
        self.apple.draw()

        self.elapsed_time = ""
        self.game_speed = 0.30
        self.start_time = time.time()

    def play_background_music(self):
        try:
            pygame.mixer.music.load('resources/bg_music_1.mp3')
            pygame.mixer.music.play(-1, 0)
        except pygame.error:
            print("Warning: 'resources/bg_music_1.mp3' not found. Background music will not play.")

    def play_sound(self, sound_name):
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
        self.snake = Snake(self.surface)
        self.apple = Apple(self.surface)
        self.elapsed_time = ""
        self.snake.best_time = ""
        self.start_time = time.time()

    def is_collision(self, x1, y1, x2, y2):
        if x1 >= x2 and x1 < x2 + SIZE:
            if y1 >= y2 and y1 < y2 + SIZE:
                return True
        return False

    def self_collision(self):
        for i in range(3, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                return True
        return False

    def check_wall_collision(self):
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()

        if head_x < 0 or head_x >= screen_width:
            return True
        if head_y < 0 or head_y >= screen_height:
            return True
        return False

    def render_background(self):
        try:
            bg = pygame.image.load("resources/background.jpg").convert()
            self.surface.blit(bg, (0,0))
        except pygame.error:
            print("Warning: 'resources/background.jpg' not found. Using solid background color.")
            self.surface.fill(BACKGROUND_COLOR)

    def play(self):
        self.render_background()
        self.snake.walk()
        self.apple.draw()
        self.display_score()
        self.display_time(False)
        pygame.display.flip()

        if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.display_time(True)
            self.play_sound("ding")
            self.snake.increase_length()
            # Increase speed but keep it above minimum threshold
            if (self.snake.length) % 5 == 0:
                self.game_speed = max(0.05, self.game_speed - 0.04)
            self.apple.move()

        if self.self_collision():
            self.play_sound('crash')
            raise Exception("Collision Occurred")

        if self.check_wall_collision():
            self.play_sound('crash')
            raise Exception("Wall Collision!")

    def display_score(self):
        font = pygame.font.SysFont('arial',30)
        score_text = font.render(f"Score: {self.snake.length - 1}", True, (200,200,200))
        self.surface.blit(score_text,(850,10))

    def display_time(self, score_t=False):
        font = pygame.font.SysFont('arial', 30)
        elapsed_seconds = int(time.time() - self.start_time)
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        time_string = f"{minutes:02d}:{seconds:02d}"
        self.elapsed_time = time_string

        if score_t:
            self.snake.best_time = time_string

        time_text = font.render(f"Time: {time_string}", True, (200, 200, 200))
        self.surface.blit(time_text, (10, 10))

    def show_game_over(self, message="Game Over!"):
        self.render_background()
        font = pygame.font.SysFont('arial', 30)

        line1 = font.render(f"Game is over! ", True, (255, 255, 255))
        self.surface.blit(line1, (200, 200))
        line1 = font.render(f"Your score = {self.snake.length - 1}", True, (255, 255, 255))
        self.surface.blit(line1, (250, 350))
        line1 = font.render(f"Last Apple Time = {self.snake.best_time}", True, (255, 255, 255))
        self.surface.blit(line1, (250, 400))
        line1 = font.render(f"Total Game Time = {self.elapsed_time}", True, (255, 255, 255))
        self.surface.blit(line1, (250, 450))
        line2 = font.render("To play again press Enter. To exit press Escape!", True, (255, 255, 255))
        self.surface.blit(line2, (200, 550))

        pygame.mixer.music.pause()
        pygame.display.flip()

    def _get_potential_head(self, current_direction):
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
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()

        if not (0 <= next_head_x < screen_width and 0 <= next_head_y < screen_height):
            return True

        for i in range(1, self.snake.length):
            if self.is_collision(next_head_x, next_head_y, self.snake.x[i], self.snake.y[i]):
                return True

        return False

    def _calculate_distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def random_agent(self):
        day_number = random.randint(1, 4)
        if day_number == 1:
            self.snake.move_left()
        elif day_number == 2:
            self.snake.move_right()
        elif day_number == 3:
            self.snake.move_up()
        elif day_number == 4:
            self.snake.move_down()
    
    def agent_bikram(self):
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        apple_x, apple_y = self.apple.x, self.apple.y

        if head_x-apple_x == 0:
            if head_y-apple_y >= 0:
                self.snake.move_up()
            else:
                self.snake.move_down()
        elif head_x-apple_x >= 0:
            self.snake.move_left()
        elif head_x-apple_x <= 0:
            self.snake.move_right()

    def smart_agent_bfs(self):
        """
        Advanced AI agent using BFS pathfinding with safety checks and fallback strategies.
        This agent tries to find the safest path to the apple while avoiding collisions.
        """
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        apple_x, apple_y = self.apple.x, self.apple.y
        
        # Available directions and their corresponding movements
        directions = ['left', 'right', 'up', 'down']
        direction_moves = {
            'left': (-SIZE, 0),
            'right': (SIZE, 0),
            'up': (0, -SIZE),
            'down': (0, SIZE)
        }
        
        # Filter out directions that would cause immediate collision or reverse direction
        valid_directions = []
        for direction in directions:
            # Prevent immediate U-turns
            if (self.snake.direction == 'left' and direction == 'right') or \
               (self.snake.direction == 'right' and direction == 'left') or \
               (self.snake.direction == 'up' and direction == 'down') or \
               (self.snake.direction == 'down' and direction == 'up'):
                continue
                
            # Check if this direction would cause immediate collision
            dx, dy = direction_moves[direction]
            next_x, next_y = head_x + dx, head_y + dy
            
            if not self._is_potential_move_colliding(next_x, next_y):
                valid_directions.append(direction)
        
        if not valid_directions:
            # Emergency: no safe moves, try to survive by moving in current direction
            return
        
        # Use BFS to find the best path to the apple
        best_direction = self._bfs_pathfind(head_x, head_y, apple_x, apple_y, valid_directions, direction_moves)
        
        if best_direction:
            # Execute the best direction found
            if best_direction == 'left':
                self.snake.move_left()
            elif best_direction == 'right':
                self.snake.move_right()
            elif best_direction == 'up':
                self.snake.move_up()
            elif best_direction == 'down':
                self.snake.move_down()
        else:
            # Fallback: use safety-first approach
            self._safety_first_agent(valid_directions, direction_moves)

    def _bfs_pathfind(self, start_x, start_y, target_x, target_y, valid_directions, direction_moves):
        """
        Uses BFS to find the shortest safe path to the target.
        Returns the first direction to take, or None if no path exists.
        """
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()
        
        # BFS setup
        queue = deque()
        visited = set()
        
        # Add starting positions for each valid direction
        for direction in valid_directions:
            dx, dy = direction_moves[direction]
            next_x, next_y = start_x + dx, start_y + dy
            queue.append((next_x, next_y, direction, 1))  # (x, y, first_direction, depth)
            visited.add((next_x, next_y))
        
        max_depth = 15  # Limit search depth to prevent lag
        
        # Define possible directions locally
        directions = ['left', 'right', 'up', 'down']

        while queue:
            current_x, current_y, first_direction, depth = queue.popleft()
            
            # Check if we reached the target
            if current_x == target_x and current_y == target_y:
                return first_direction
            
            # Limit search depth
            if depth >= max_depth:
                continue
            
            # Explore neighbors
            for direction in directions:
                dx, dy = direction_moves[direction]
                next_x, next_y = current_x + dx, current_y + dy
                
                # Skip if already visited
                if (next_x, next_y) in visited:
                    continue
                
                # Skip if out of bounds
                if not (0 <= next_x < screen_width and 0 <= next_y < screen_height):
                    continue
                
                # Skip if collides with snake body (simplified check)
                collision = False
                for i in range(1, self.snake.length):
                    if self.is_collision(next_x, next_y, self.snake.x[i], self.snake.y[i]):
                        collision = True
                        break
                
                if not collision:
                    queue.append((next_x, next_y, first_direction, depth + 1))
                    visited.add((next_x, next_y))
        
        return None  # No path found

    def _utility_score(self, next_x, next_y, apple_x, apple_y):
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()
        score = 0

        # Factor 1: Distance to apple (closer is better)
        distance_to_apple = self._calculate_distance(next_x, next_y, apple_x, apple_y)
        score += max(0, 1000 - distance_to_apple)

        # Factor 2: Distance from walls (farther is better)
        wall_distances = [
            next_x,
            screen_width - next_x - SIZE,
            next_y,
            screen_height - next_y - SIZE
        ]
        min_wall_distance = min(wall_distances)
        score += min_wall_distance * 2  # Emphasize wall safety

        # Factor 3: Distance from snake body (farther is better)
        min_body_distance = float('inf')
        for i in range(1, self.snake.length):
            body_distance = self._calculate_distance(next_x, next_y, self.snake.x[i], self.snake.y[i])
            min_body_distance = min(min_body_distance, body_distance)

        if min_body_distance != float('inf'):
            score += min_body_distance * 3

        # Factor 4: Available space (more is better)
        available_space = self._count_available_space(next_x, next_y)
        score += available_space * 5

        return score

    def _safety_first_agent(self, valid_directions, direction_moves):
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        apple_x, apple_y = self.apple.x, self.apple.y

        best_direction = None
        best_score = -1

        for direction in valid_directions:
            dx, dy = direction_moves[direction]
            next_x, next_y = head_x + dx, head_y + dy

            score = self._utility_score(next_x, next_y, apple_x, apple_y)

            if score > best_score:
                best_score = score
                best_direction = direction

        if best_direction == 'left':
            self.snake.move_left()
        elif best_direction == 'right':
            self.snake.move_right()
        elif best_direction == 'up':
            self.snake.move_up()
        elif best_direction == 'down':
            self.snake.move_down()

    def _count_available_space(self, start_x, start_y, max_depth=8):
        """
        Counts available space using a limited flood fill algorithm.
        This helps the snake avoid getting trapped in small spaces.
        """
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()
        visited = set()
        queue = deque([(start_x, start_y, 0)])
        visited.add((start_x, start_y))
        
        count = 0
        directions = [(-SIZE, 0), (SIZE, 0), (0, -SIZE), (0, SIZE)]
        
        while queue:
            x, y, depth = queue.popleft()
            count += 1
            
            if depth >= max_depth:
                continue
            
            for dx, dy in directions:
                next_x, next_y = x + dx, y + dy
                
                if (next_x, next_y) in visited:
                    continue
                
                # Check bounds
                if not (0 <= next_x < screen_width and 0 <= next_y < screen_height):
                    continue
                
                # Check collision with snake body
                collision = False
                for i in range(self.snake.length):
                    if self.is_collision(next_x, next_y, self.snake.x[i], self.snake.y[i]):
                        collision = True
                        break
                
                if not collision:
                    visited.add((next_x, next_y))
                    queue.append((next_x, next_y, depth + 1))
        
        return count

    def run(self):
        running = True
        pause = False

        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

                    if event.key == K_RETURN:
                        pygame.mixer.music.unpause()
                        if pause == True:
                            self.start_time = time.time()
                        pause = False
                        self.reset()

                    if not pause:
                        if event.key == K_LEFT:
                            self.snake.move_left()
                        elif event.key == K_RIGHT:
                            self.snake.move_right()
                        elif event.key == K_UP:
                            self.snake.move_up()
                        elif event.key == K_DOWN:
                            self.snake.move_down()

                elif event.type == QUIT:
                    running = False

            # Agent movement control: Use the improved AI agent
            if not pause:
                self.smart_agent_bfs()  # Use the new improved AI agent
                #self.agent_bikram()    # Original simple agent
                #self.random_agent()    # Random agent

            try:
                if not pause:
                    self.play()
            except Exception as e:
                self.show_game_over(str(e))
                pause = True

            time.sleep(self.game_speed)


if __name__ == '__main__':
    game = Game()
    game.run()