import pygame
from pygame.locals import *
import random
pygame.init()
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Snake - Joueur vs IA')
font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 25)
cell_size = 10
bg = (255, 200, 150)
food_col = (200, 50, 50)
class Snake:
    def __init__(self, name, start_pos, start_direction, body_outer, body_inner, head_color, score_color, is_ai=False):
        self.name = name
        self.pos = start_pos.copy()
        self.direction = start_direction
        self.score = 0
        self.alive = True
        self.body_outer = body_outer
        self.body_inner = body_inner
        self.head_color = head_color
        self.score_color = score_color
        self.is_ai = is_ai
    def move(self):
        self.pos = self.pos[-1:] + self.pos[:-1]
        if self.direction == 1:  # Haut
            self.pos[0][0] = self.pos[1][0]
            self.pos[0][1] = self.pos[1][1] - cell_size
        elif self.direction == 3:  # Bas
            self.pos[0][0] = self.pos[1][0]
            self.pos[0][1] = self.pos[1][1] + cell_size
        elif self.direction == 2:  # Droite
            self.pos[0][1] = self.pos[1][1]
            self.pos[0][0] = self.pos[1][0] + cell_size
        elif self.direction == 4:  # Gauche
            self.pos[0][1] = self.pos[1][1]
            self.pos[0][0] = self.pos[1][0] - cell_size
    def grow(self):
        new_piece = list(self.pos[-1])
        if self.direction == 1:
            new_piece[1] += cell_size
        elif self.direction == 3:
            new_piece[1] -= cell_size
        elif self.direction == 2:
            new_piece[0] -= cell_size
        elif self.direction == 4:
            new_piece[0] += cell_size
        self.pos.append(new_piece)
        self.score += 1
    def check_self_collision(self):
        head_count = 0
        for segment in self.pos:
            if self.pos[0] == segment and head_count > 0:
                return True
            head_count += 1
        return False
    def check_wall_collision(self):
        head = self.pos[0]
        if head[0] < 0 or head[0] >= screen_width or head[1] < 0 or head[1] >= screen_height:
            return True
        return False
    def check_collision_with(self, other_snakes):
        for other in other_snakes:
            if other is self or not other.alive:
                continue
            for segment in other.pos:
                if self.pos[0] == segment:
                    return True
        return False
    def is_colliding(self, other_snakes):
        return self.check_self_collision() or self.check_wall_collision() or self.check_collision_with(other_snakes)
    def draw(self, screen):
        if not self.alive:
            return
        head = True
        for segment in self.pos:
            pygame.draw.rect(screen, self.body_outer, (segment[0], segment[1], cell_size, cell_size))
            if head:
                pygame.draw.rect(screen, self.head_color,
                                 (segment[0] + 1, segment[1] + 1, cell_size - 2, cell_size - 2))
                head = False
            else:
                pygame.draw.rect(screen, self.body_inner,
                                 (segment[0] + 1, segment[1] + 1, cell_size - 2, cell_size - 2))
    def reset(self, start_pos, start_direction):
        self.pos = start_pos.copy()
        self.direction = start_direction
        self.score = 0
        self.alive = True
class AISnake(Snake):
    def __init__(self, name, start_pos, start_direction, body_outer, body_inner, head_color, score_color):
        super().__init__(name, start_pos, start_direction, body_outer, body_inner, head_color, score_color, is_ai=True)
    def make_decision(self, food, all_snakes):
        head = self.pos[0]
        possible_directions = []
        directions = [
            (1, [head[0], head[1] - cell_size]),  # Haut
            (2, [head[0] + cell_size, head[1]]),  # Droite
            (3, [head[0], head[1] + cell_size]),  # Bas
            (4, [head[0] - cell_size, head[1]])  # Gauche
        ]
        for dir_num, new_pos in directions:
            if (dir_num == 1 and self.direction == 3) or \
                    (dir_num == 3 and self.direction == 1) or \
                    (dir_num == 2 and self.direction == 4) or \
                    (dir_num == 4 and self.direction == 2):
                continue
            if not self._is_dangerous_position(new_pos, all_snakes):
                distance = abs(new_pos[0] - food[0]) + abs(new_pos[1] - food[1])
                possible_directions.append((dir_num, distance))
        if possible_directions:
            possible_directions.sort(key=lambda x: x[1])
            self.direction = possible_directions[0][0]
    def _is_dangerous_position(self, pos, all_snakes):
        # Vérifier les murs
        if pos[0] < 0 or pos[0] >= screen_width or pos[1] < 0 or pos[1] >= screen_height:
            return True
        for segment in self.pos:
            if pos == segment:
                return True
        for other in all_snakes:
            if other is self or not other.alive:
                continue
            for segment in other.pos:
                if pos == segment:
                    return True
        return False
class Game:
    def __init__(self):
        self.snakes = []
        self.food = [0, 0]
        self.new_food = True
        self.update_counter = 0
        self.game_over = False
        self.clicked = False
        self.again_rect = Rect(screen_width // 2 - 80, screen_height // 2, 160, 50)
        self._initialize_snakes()
    def _initialize_snakes(self):
        player = Snake(
            "Joueur",
            [[300, 300], [300, 310], [300, 320], [300, 330]],
            1,
            (100, 100, 200),
            (50, 175, 25),
            (255, 0, 0),
            (0, 0, 255),
            is_ai=False
        )
        self.snakes.append(player)
        ai1 = AISnake(
            "IA 1",
            [[100, 100], [100, 110], [100, 120], [100, 130]],
            3,
            (0, 150, 0),
            (50, 200, 50),
            (255, 255, 0),
            (0, 150, 0)
        )
        self.snakes.append(ai1)
        ai2 = AISnake(
            "IA 2",
            [[500, 100], [500, 110], [500, 120], [500, 130]],
            3,
            (150, 0, 150),
            (200, 50, 200),
            (255, 150, 0),
            (150, 0, 150)
        )
        self.snakes.append(ai2)
        ai3 = AISnake(
            "IA 3",
            [[100, 500], [100, 510], [100, 520], [100, 530]],
            1,
            (150, 75, 0),
            (200, 150, 50),
            (0, 255, 255),
            (150, 75, 0)
        )
        self.snakes.append(ai3)
    def spawn_food(self):
        self.food[0] = cell_size * random.randint(0, int((screen_width / cell_size) - 1))
        self.food[1] = cell_size * random.randint(0, int((screen_height / cell_size) - 1))
        self.new_food = False
    def update(self):
        if self.game_over:
            return
        for snake in self.snakes:
            if isinstance(snake, AISnake) and snake.alive:
                snake.make_decision(self.food, self.snakes)
        if self.update_counter > 99:
            self.update_counter = 0
            for snake in self.snakes:
                if snake.alive:
                    snake.move()
            for snake in self.snakes:
                if snake.alive and snake.is_colliding(self.snakes):
                    snake.alive = False
            alive_count = sum(1 for s in self.snakes if s.alive)
            if alive_count <= 1:
                self.game_over = True
        self.update_counter += 1
    def check_food_eaten(self):
        for snake in self.snakes:
            if snake.alive and snake.pos[0] == self.food:
                snake.grow()
                self.new_food = True
                break
    def draw(self, screen):
        screen.fill(bg)
        y_offset = 10
        for snake in self.snakes:
            if snake.alive:
                score_txt = f"{snake.name}: {snake.score}"
                score_img = small_font.render(score_txt, True, snake.score_color)
                screen.blit(score_img, (10, y_offset))
                y_offset += 25
        pygame.draw.rect(screen, food_col, (self.food[0], self.food[1], cell_size, cell_size))
        for snake in self.snakes:
            snake.draw(screen)
        if self.game_over:
            self._draw_game_over(screen)
    def _draw_game_over(self, screen):
        alive_snakes = [s for s in self.snakes if s.alive]
        if alive_snakes:
            winner = max(alive_snakes, key=lambda s: s.score)
            over_text = f"{winner.name} Gagne!"
            color = winner.score_color
        else:
            over_text = "Égalité!"
            color = (255, 0, 0)
        over_img = font.render(over_text, True, color)
        pygame.draw.rect(screen, (255, 0, 0), (screen_width // 2 - 120, screen_height // 2 - 60, 240, 50))
        screen.blit(over_img, (screen_width // 2 - 120, screen_height // 2 - 50))
        again_text = 'Rejouer?'
        again_img = font.render(again_text, True, (0, 0, 255))
        pygame.draw.rect(screen, (255, 0, 0), self.again_rect)
        screen.blit(again_img, (screen_width // 2 - 80, screen_height // 2 + 10))
    def reset(self):
        self.game_over = False
        self.update_counter = 0
        self.food = [0, 0]
        self.new_food = True
        initial_data = [
            ([[300, 300], [300, 310], [300, 320], [300, 330]], 1),
            ([[100, 100], [100, 110], [100, 120], [100, 130]], 3),
            ([[500, 100], [500, 110], [500, 120], [500, 130]], 3),
            ([[100, 500], [100, 510], [100, 520], [100, 530]], 1)
        ]
        for i, snake in enumerate(self.snakes):
            snake.reset(initial_data[i][0], initial_data[i][1])
    def handle_player_input(self, event):
        if event.type == pygame.KEYDOWN and not self.game_over:
            player = self.snakes[0]
            if event.key == pygame.K_UP and player.direction != 3:
                player.direction = 1
            elif event.key == pygame.K_RIGHT and player.direction != 4:
                player.direction = 2
            elif event.key == pygame.K_DOWN and player.direction != 1:
                player.direction = 3
            elif event.key == pygame.K_LEFT and player.direction != 2:
                player.direction = 4
game = Game()
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        game.handle_player_input(event)
        if game.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN and not game.clicked:
                game.clicked = True
            elif event.type == pygame.MOUSEBUTTONUP and game.clicked:
                game.clicked = False
                game.reset()
    if game.new_food:
        game.spawn_food()
    game.check_food_eaten()
    game.update()
    game.draw(screen)
    pygame.display.update()
pygame.quit()