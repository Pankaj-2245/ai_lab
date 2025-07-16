import pygame
from pygame.locals import *
import time
import random
import math
from collections import deque
import numpy as np

# --- Game Configuration Constants ---
SIZE = 40
BACKGROUND_COLOR = (110, 110, 5)

class Apple:
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        try:
            self.image = pygame.image.load("resources/apple.png").convert_alpha()
        except pygame.error:
            print("Warning: 'resources/apple.png' not found. Using a red square.")
            self.image = pygame.Surface((SIZE, SIZE))
            self.image.fill((255, 0, 0))
        self.x = 120
        self.y = 120
        self.screen_width = parent_screen.get_width()
        self.screen_height = parent_screen.get_height()

    def draw(self):
        self.parent_screen.blit(self.image, (self.x, self.y))

    def move(self, snake_positions):
        # Randomly place apple, ensuring no overlap with snake
        while True:
            self.x = random.randrange(0, self.screen_width, SIZE)
            self.y = random.randrange(0, self.screen_height, SIZE)
            if (self.x, self.y) not in snake_positions:
                break

class Snake:
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        try:
            self.image = pygame.image.load("resources/block.jpg").convert_alpha()
        except pygame.error:
            print("Warning: 'resources/block.jpg' not found. Using a green square.")
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
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]
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
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake Game with Enhanced AI Agents")
        pygame.mixer.init()
        self.play_background_music()
        self.surface = pygame.display.set_mode((1000, 800))
        self.surface.fill(BACKGROUND_COLOR)
        self.snake = Snake(self.surface)
        self.snake.draw()
        self.apple = Apple(self.surface)
        self.apple.move(set((x, y) for x, y in zip(self.snake.x, self.snake.y)))
        self.apple.draw()
        self.elapsed_time = ""
        self.game_speed = 0.30
        self.start_time = time.time()
        self.clock = pygame.time.Clock()
        self.previous_direction = None
        self.simple_agent = SimpleAgent(self)
        self.model_based_agent = ModelBasedAgent(self)
        self.goal_based_agent = GoalBasedAgent(self)
        self.utility_based_agent = UtilityBasedAgent(self)
        self.learning_agent = LearningAgent(self)

    def play_background_music(self):
        try:
            pygame.mixer.music.load('resources/bg_music_1.mp3')
            pygame.mixer.music.play(-1, 0)
        except pygame.error:
            print("Warning: 'resources/bg_music_1.mp3' not found.")

    def play_sound(self, sound_name):
        try:
            sound = pygame.mixer.Sound(f"resources/{sound_name}.mp3")
            pygame.mixer.Sound.play(sound)
        except pygame.error:
            print(f"Warning: 'resources/{sound_name}.mp3' not found.")

    def reset(self):
        self.snake = Snake(self.surface)
        self.apple.move(set((x, y) for x, y in zip(self.snake.x, self.snake.y)))
        self.elapsed_time = ""
        self.snake.best_time = ""
        self.start_time = time.time()
        self.previous_direction = None
        self.learning_agent.reset()

    def is_collision(self, x1, y1, x2, y2):
        return x1 >= x2 and x1 < x2 + SIZE and y1 >= y2 and y1 < y2 + SIZE

    def self_collision(self):
        for i in range(3, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                return True
        return False

    def check_wall_collision(self):
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()
        return head_x < 0 or head_x >= screen_width or head_y < 0 or head_y >= screen_height

    def render_background(self):
        try:
            bg = pygame.image.load("resources/background.jpg").convert()
            self.surface.blit(bg, (0, 0))
        except pygame.error:
            print("Warning: 'resources/background.jpg' not found.")
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
            if (self.snake.length) % 5 == 0:
                self.game_speed = max(0.05, self.game_speed - 0.04)
            self.apple.move(set((x, y) for x, y in zip(self.snake.x, self.snake.y)))
        if self.self_collision():
            self.play_sound('crash')
            raise Exception("Collision Occurred")
        if self.check_wall_collision():
            self.play_sound('crash')
            raise Exception("Wall Collision!")

    def display_score(self):
        font = pygame.font.SysFont('arial', 30)
        score_text = font.render(f"Score: {self.snake.length - 1}", True, (200, 200, 200))
        self.surface.blit(score_text, (850, 10))

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
        texts = [
            (f"Game is over! {message}", (200, 200)),
            (f"Your score = {self.snake.length - 1}", (250, 350)),
            (f"Last Apple Time = {self.snake.best_time}", (250, 400)),
            (f"Total Game Time = {self.elapsed_time}", (250, 450)),
            ("To play again press Enter. To exit press Escape!", (200, 550)),
            ("Press 1-5 to select AI agent:", (200, 600)),
            ("1: Simple  2: Model  3: Goal  4: Utility  5: Learning", (200, 630))
        ]
        for text, pos in texts:
            surface = font.render(text, True, (255, 255, 255))
            self.surface.blit(surface, pos)
        pygame.mixer.music.pause()
        pygame.display.flip()

    def _get_potential_head(self, direction):
        head_x, head_y = self.snake.x[0], self.snake.y[0]
        if direction == 'left':
            return head_x - SIZE, head_y
        elif direction == 'right':
            return head_x + SIZE, head_y
        elif direction == 'up':
            return head_x, head_y - SIZE
        elif direction == 'down':
            return head_x, head_y + SIZE
        return head_x, head_y

    def _is_potential_move_colliding(self, next_x, next_y):
        screen_width, screen_height = self.surface.get_width(), self.surface.get_height()
        if not (0 <= next_x < screen_width and 0 <= next_y < screen_height):
            return True
        for i in range(1, self.snake.length):
            if self.is_collision(next_x, next_y, self.snake.x[i], self.snake.y[i]):
                return True
        return False

    def _calculate_manhattan_distance(self, x1, y1, x2, y2):
        return abs(x2 - x1) // SIZE + abs(y2 - y1) // SIZE

    def run(self):
        running = True
        pause = False
        current_agent = None
        while running:
            delta_time = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_RETURN:
                        pygame.mixer.music.unpause()
                        if pause:
                            self.start_time = time.time()
                        pause = False
                        self.reset()
                    if event.key == K_1:
                        current_agent = self.simple_agent
                        print("Simple Agent activated")
                    elif event.key == K_2:
                        current_agent = self.model_based_agent
                        print("Model-Based Agent activated")
                    elif event.key == K_3:
                        current_agent = self.goal_based_agent
                        print("Goal-Based Agent activated")
                    elif event.key == K_4:
                        current_agent = self.utility_based_agent
                        print("Utility-Based Agent activated")
                    elif event.key == K_5:
                        current_agent = self.learning_agent
                        print("Learning Agent activated")
                    if not pause and current_agent is None:
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
            if not pause and current_agent is not None:
                current_agent.make_move()
            try:
                if not pause:
                    self.play()
            except Exception as e:
                self.show_game_over(str(e))
                pause = True
                current_agent = None
            time.sleep(max(0, self.game_speed - delta_time))

# Note: Only agent classes are updated; Game, Snake, Apple remain as in previous version

class SimpleAgent:
    def __init__(self, game):
        self.game = game

    def count_escape_routes(self, x, y):
        count = 0
        for direction in ['left', 'right', 'up', 'down']:
            next_x, next_y = self.game._get_potential_head(direction)
            if not self.game._is_potential_move_colliding(next_x, next_y):
                count += 1
        return count

    def make_move(self):
        head_x, head_y = self.game.snake.x[0], self.game.snake.y[0]
        apple_x, apple_y = self.game.apple.x, self.game.apple.y
        directions = ['left', 'right', 'up', 'down']
        if self.game.snake.direction == 'left':
            directions.remove('right')
        elif self.game.snake.direction == 'right':
            directions.remove('left')
        elif self.game.snake.direction == 'up':
            directions.remove('down')
        elif self.game.snake.direction == 'down':
            directions.remove('up')
        safe_directions = []
        for direction in directions:
            next_x, next_y = self.game._get_potential_head(direction)
            if not self.game._is_potential_move_colliding(next_x, next_y):
                safe_directions.append(direction)
        if not safe_directions:
            return
        best_direction = safe_directions[0]
        best_score = -float('inf')
        for direction in safe_directions:
            next_x, next_y = self.game._get_potential_head(direction)
            distance = self.game._calculate_manhattan_distance(next_x, next_y, apple_x, apple_y)
            escape_routes = self.count_escape_routes(next_x, next_y)
            score = -distance + escape_routes * 2
            if direction == self.game.snake.direction:
                score += 1
            if score > best_score:
                best_score = score
                best_direction = direction
        if best_direction == 'left':
            self.game.snake.move_left()
        elif best_direction == 'right':
            self.game.snake.move_right()
        elif best_direction == 'up':
            self.game.snake.move_up()
        elif best_direction == 'down':
            self.game.snake.move_down()

class ModelBasedAgent:
    def __init__(self, game):
        self.game = game
        self.move_history = deque(maxlen=10)
        self.danger_zones = set()

    def update_model(self):
        self.danger_zones.clear()
        screen_width, screen_height = self.game.surface.get_width(), self.game.surface.get_height()
        for i in range(1, self.game.snake.length - 1):
            self.danger_zones.add((self.game.snake.x[i], self.game.snake.y[i]))

    def evaluate_direction(self, direction):
        next_x, next_y = self.game._get_potential_head(direction)
        if self.game._is_potential_move_colliding(next_x, next_y):
            return -1000
        score = 0
        apple_distance = self.game._calculate_manhattan_distance(next_x, next_y, self.game.apple.x, self.game.apple.y)
        score -= apple_distance * 5  # Increased weight for apple pursuit
        if (next_x, next_y) in self.danger_zones:
            score -= 20  # Reduced penalty
        if (next_x, next_y) in self.move_history:
            score -= 10
        if direction == self.game.snake.direction:
            score += 10  # Increased continuity bonus
        # Bonus for aligning with apple's row or column
        if next_x == self.game.apple.x or next_y == self.game.apple.y:
            score += 15
        return score

    def make_move(self):
        self.update_model()
        directions = ['left', 'right', 'up', 'down']
        if self.game.snake.direction == 'left':
            directions.remove('right')
        elif self.game.snake.direction == 'right':
            directions.remove('left')
        elif self.game.snake.direction == 'up':
            directions.remove('down')
        elif self.game.snake.direction == 'down':
            directions.remove('up')
        best_direction = directions[0]
        best_score = self.evaluate_direction(best_direction)
        for direction in directions[1:]:
            score = self.evaluate_direction(direction)
            if score > best_score:
                best_score = score
                best_direction = direction
        self.move_history.append((self.game.snake.x[0], self.game.snake.y[0]))
        if best_direction == 'left':
            self.game.snake.move_left()
        elif best_direction == 'right':
            self.game.snake.move_right()
        elif best_direction == 'up':
            self.game.snake.move_up()
        elif best_direction == 'down':
            self.game.snake.move_down()

class GoalBasedAgent:
    def __init__(self, game):
        self.game = game

    def get_grid_position(self, x, y):
        return x // SIZE, y // SIZE

    def get_pixel_position(self, grid_x, grid_y):
        return grid_x * SIZE, grid_y * SIZE

    def is_valid_position(self, grid_x, grid_y):
        x, y = self.get_pixel_position(grid_x, grid_y)
        if x < 0 or x >= self.game.surface.get_width() or y < 0 or y >= self.game.surface.get_height():
            return False
        for i in range(self.game.snake.length - 1):  # Exclude tail
            if x == self.game.snake.x[i] and y == self.game.snake.y[i]:
                return False
        return True

    def count_available_space(self, x, y):
        visited = set()
        stack = [(x, y)]
        count = 0
        while stack and count < 100:
            curr_x, curr_y = stack.pop()
            if (curr_x, curr_y) in visited:
                continue
            if (curr_x < 0 or curr_x >= self.game.surface.get_width() or
                curr_y < 0 or curr_y >= self.game.surface.get_height()):
                continue
            collision = False
            for i in range(self.game.snake.length - 1):
                if curr_x == self.game.snake.x[i] and curr_y == self.game.snake.y[i]:
                    collision = True
                    break
            if collision:
                continue
            visited.add((curr_x, curr_y))
            count += 1
            for dx, dy in [(SIZE, 0), (-SIZE, 0), (0, SIZE), (0, -SIZE)]:
                next_pos = (curr_x + dx, curr_y + dy)
                if next_pos not in visited:
                    stack.append(next_pos)
        return count

    def find_path_to_apple(self):
        head_x, head_y = self.game.snake.x[0], self.game.snake.y[0]
        apple_x, apple_y = self.game.apple.x, self.game.apple.y
        start = self.get_grid_position(head_x, head_y)
        goal = self.get_grid_position(apple_x, apple_y)
        if start == goal:
            return []
        queue = deque([(start, [])])
        visited = set([start])
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        direction_names = ['down', 'up', 'right', 'left']
        max_depth = 30  # Reduced depth
        depth = 0
        while queue and depth < max_depth:
            depth += 1
            (current_x, current_y), path = queue.popleft()
            for i, (dx, dy) in enumerate(directions):
                next_x, next_y = current_x + dx, current_y + dy
                if (next_x, next_y) == goal:
                    return path + [direction_names[i]]
                if (next_x, next_y) not in visited and self.is_valid_position(next_x, next_y):
                    visited.add((next_x, next_y))
                    queue.append(((next_x, next_y), path + [direction_names[i]]))
        return []

    def make_move(self):
        path = self.find_path_to_apple()
        if path:
            next_direction = path[0]
            next_x, next_y = self.game._get_potential_head(next_direction)
            if not self.game._is_potential_move_colliding(next_x, next_y):
                if next_direction == 'left':
                    self.game.snake.move_left()
                elif next_direction == 'right':
                    self.game.snake.move_right()
                elif next_direction == 'up':
                    self.game.snake.move_up()
                elif next_direction == 'down':
                    self.game.snake.move_down()
                return
        # Improved fallback: prioritize apple distance, then space
        directions = ['left', 'right', 'up', 'down']
        if self.game.snake.direction == 'left':
            directions.remove('right')
        elif self.game.snake.direction == 'right':
            directions.remove('left')
        elif self.game.snake.direction == 'up':
            directions.remove('down')
        elif self.game.snake.direction == 'down':
            directions.remove('up')
        best_direction = directions[0]
        best_score = -float('inf')
        for direction in directions:
            next_x, next_y = self.game._get_potential_head(direction)
            if not self.game._is_potential_move_colliding(next_x, next_y):
                distance = self.game._calculate_manhattan_distance(next_x, next_y, self.game.apple.x, self.game.apple.y)
                space = self.count_available_space(next_x, next_y)
                score = -distance * 5 + space  # Prioritize apple distance
                if direction == self.game.snake.direction:
                    score += 5
                if score > best_score:
                    best_score = score
                    best_direction = direction
        if best_direction == 'left':
            self.game.snake.move_left()
        elif best_direction == 'right':
            self.game.snake.move_right()
        elif best_direction == 'up':
            self.game.snake.move_up()
        elif best_direction == 'down':
            self.game.snake.move_down()

class UtilityBasedAgent:
    def __init__(self, game):
        self.game = game
        self.previous_direction = None

    def count_escape_routes(self, x, y):
        count = 0
        for direction in ['left', 'right', 'up', 'down']:
            next_x, next_y = self.game._get_potential_head(direction)
            if not self.game._is_potential_move_colliding(next_x, next_y):
                count += 1
        return count

    def calculate_utility(self, direction):
        next_x, next_y = self.game._get_potential_head(direction)
        if self.game._is_potential_move_colliding(next_x, next_y):
            return -10000
        utility = 0
        apple_distance = self.game._calculate_manhattan_distance(next_x, next_y, self.game.apple.x, self.game.apple.y)
        utility -= apple_distance * 20  # Increased apple pursuit
        escape_routes = self.count_escape_routes(next_x, next_y)
        utility += escape_routes * 10  # Reduced escape route weight
        screen_width, screen_height = self.game.surface.get_width(), self.game.surface.get_height()
        wall_distances = [next_x, screen_width - next_x, next_y, screen_height - next_y]
        min_wall_distance = min(wall_distances) // SIZE
        utility += min_wall_distance * 3  # Reduced wall distance weight
        if direction == self.previous_direction:
            utility += 2
        if direction == self.game.snake.direction:
            utility += 5
        if self.game.snake.length > 10:  # Apply tail penalty only for long snakes
            tail_x, tail_y = self.game.snake.x[-1], self.game.snake.y[-1]
            tail_distance = self.game._calculate_manhattan_distance(next_x, next_y, tail_x, tail_y)
            if tail_distance < 3:
                utility -= 20  # Reduced tail penalty
        return utility

    def make_move(self):
        directions = ['left', 'right', 'up', 'down']
        if self.game.snake.direction == 'left':
            directions.remove('right')
        elif self.game.snake.direction == 'right':
            directions.remove('left')
        elif self.game.snake.direction == 'up':
            directions.remove('down')
        elif self.game.snake.direction == 'down':
            directions.remove('up')
        best_direction = directions[0]
        best_utility = self.calculate_utility(best_direction)
        for direction in directions[1:]:
            utility = self.calculate_utility(direction)
            if utility > best_utility:
                best_utility = utility
                best_direction = direction
        if best_direction == 'left':
            self.game.snake.move_left()
        elif best_direction == 'right':
            self.game.snake.move_right()
        elif best_direction == 'up':
            self.game.snake.move_up()
        elif best_direction == 'down':
            self.game.snake.move_down()
        self.previous_direction = best_direction

class LearningAgent:
    def __init__(self, game):
        self.game = game
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.2  # Reduced initial exploration
        self.epsilon_decay = 0.99  # Faster decay
        self.min_epsilon = 0.01
        self.last_state = None
        self.last_action = None
        self.last_score = 0
        self.episodes = 0
        # Initialize Q-table with Simple Agent-like heuristics
        self.pretrain_q_table()

    def pretrain_q_table(self):
        # Simulate Simple Agent behavior: prefer moves toward apple, avoid collisions
        for apple_dx in [-1, 0, 1]:
            for apple_dy in [-1, 0, 1]:
                for dangers in [(0,0,0,0), (1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1)]:
                    for length_cat in range(4):
                        for tail_dist in range(4):
                            state = (apple_dx, apple_dy, dangers, length_cat, tail_dist)
                            for action in range(4):
                                if dangers[action] == 1:  # Collision
                                    self.q_table[(state, action)] = -100
                                else:
                                    # Reward moves toward apple
                                    if (action == 0 and apple_dx < 0) or (action == 1 and apple_dx > 0) or \
                                       (action == 2 and apple_dy < 0) or (action == 3 and apple_dy > 0):
                                        self.q_table[(state, action)] = 10
                                    else:
                                        self.q_table[(state, action)] = 0

    def get_state(self):
        head_x, head_y = self.game.snake.x[0], self.game.snake.y[0]
        apple_x, apple_y = self.game.apple.x, self.game.apple.y
        tail_x, tail_y = self.game.snake.x[-1], self.game.snake.y[-1]
        apple_dx = 1 if apple_x > head_x else (-1 if apple_x < head_x else 0)
        apple_dy = 1 if apple_y > head_y else (-1 if apple_y < head_y else 0)
        tail_distance = self.game._calculate_manhattan_distance(head_x, head_y, tail_x, tail_y)
        tail_distance_discrete = min(tail_distance // SIZE, 3)
        screen_width, screen_height = self.game.surface.get_width(), self.game.surface.get_height()
        wall_distance = min(head_x, screen_width - head_x, head_y, screen_height - head_y) // SIZE
        wall_distance_discrete = min(wall_distance, 3)
        dangers = []
        for direction in ['left', 'right', 'up', 'down']:
            next_x, next_y = self.game._get_potential_head(direction)
            dangers.append(1 if self.game._is_potential_move_colliding(next_x, next_y) else 0)
        length_category = min(self.game.snake.length // 5, 3)
        return (apple_dx, apple_dy, tuple(dangers), length_category, tail_distance_discrete, wall_distance_discrete)

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def get_best_action(self, state):
        actions = [0, 1, 2, 3]
        current_dir = self.game.snake.direction
        if current_dir == 'left':
            actions.remove(1)
        elif current_dir == 'right':
            actions.remove(0)
        elif current_dir == 'up':
            actions.remove(3)
        elif current_dir == 'down':
            actions.remove(2)
        if not actions:
            return 0
        best_action = actions[0]
        best_q_value = self.get_q_value(state, best_action)
        for action in actions[1:]:
            q_value = self.get_q_value(state, action)
            if q_value > best_q_value:
                best_q_value = q_value
                best_action = action
        return best_action

    def choose_action(self, state):
        if random.random() < self.epsilon:
            actions = [0, 1, 2, 3]
            current_dir = self.game.snake.direction
            if current_dir == 'left' and 1 in actions:
                actions.remove(1)
            elif current_dir == 'right' and 0 in actions:
                actions.remove(0)
            elif current_dir == 'up' and 3 in actions:
                actions.remove(3)
            elif current_dir == 'down' and 2 in actions:
                actions.remove(2)
            return random.choice(actions) if actions else 0
        return self.get_best_action(state)

    def get_reward(self):
        current_score = self.game.snake.length - 1
        reward = -1  # Step penalty
        if current_score > self.last_score:
            reward = 100  # Apple eaten
        head_x, head_y = self.game.snake.x[0], self.game.snake.y[0]
        apple_x, apple_y = self.game.apple.x, self.game.apple.y
        distance = self.game._calculate_manhattan_distance(head_x, head_y, apple_x, apple_y)
        reward += max(0, 2 - distance * 0.5)  # Reward for approaching apple
        screen_width, screen_height = self.game.surface.get_width(), self.game.surface.get_height()
        min_wall_distance = min(head_x, screen_width - head_x, head_y, screen_height - head_y) // SIZE
        if min_wall_distance < 2:
            reward -= 5
        if self.game.snake.length > 5:
            tail_x, tail_y = self.game.snake.x[-1], self.game.snake.y[-1]
            tail_distance = self.game._calculate_manhattan_distance(head_x, head_y, tail_x, tail_y)
            if tail_distance < 3:
                reward -= 5
        self.last_score = current_score
        return reward

    def update_q_table(self, old_state, action, reward, new_state):
        old_q_value = self.get_q_value(old_state, action)
        future_q_value = max(self.get_q_value(new_state, a) for a in [0, 1, 2, 3])
        new_q_value = old_q_value + self.learning_rate * (
            reward + self.discount_factor * future_q_value - old_q_value
        )
        self.q_table[(state, action)] = new_q_value

    def make_move(self):
        current_state = self.get_state()
        action = self.choose_action(current_state)
        if self.last_state is not None:
            reward = self.get_reward()
            self.update_q_table(self.last_state, self.last_action, reward, current_state)
        actions = ['left', 'right', 'up', 'down']
        direction = actions[action]
        next_x, next_y = self.game._get_potential_head(direction)
        if self.game._is_potential_move_colliding(next_x, next_y):
            if self.last_state is not None:
                self.update_q_table(self.last_state, self.last_action, -50, current_state)
            for safe_direction in actions:
                next_x, next_y = self.game._get_potential_head(safe_direction)
                if not self.game._is_potential_move_colliding(next_x, next_y):
                    if safe_direction == 'left':
                        self.game.snake.move_left()
                    elif safe_direction == 'right':
                        self.game.snake.move_right()
                    elif safe_direction == 'up':
                        self.game.snake.move_up()
                    elif safe_direction == 'down':
                        self.game.snake.move_down()
                    break
        else:
            if direction == 'left':
                self.game.snake.move_left()
            elif direction == 'right':
                self.game.snake.move_right()
            elif direction == 'up':
                self.game.snake.move_up()
            elif direction == 'down':
                self.game.snake.move_down()
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        self.last_state = current_state
        self.last_action = action

    def reset(self):
        self.last_state = None
        self.last_action = None
        self.last_score = 0
        self.episodes += 1
        if self.episodes % 10 == 0:
            print(f"Episode {self.episodes}, Epsilon: {self.epsilon:.3f}, Q-table size: {len(self.q_table)}")

if __name__ == '__main__':
    game = Game()
    game.run()