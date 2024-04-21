import math
import threading
from collections import deque
import pygame
import random

# 颜色常量
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
GRASS_GREEN = (170, 204, 102)
ORANGE = (255, 165, 0)
BLUE = (106, 148, 204)

# 方向常量
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 定义背景颜色、速度和背景音乐
background_color = {"WHITE": BLACK, "SNAKE": GRASS_GREEN, "DRAGON": BLUE}
speed = {"WHITE": 2, "SNAKE": 4, "DRAGON": 6}
bgm = {"WHITE": "Assets/bgm1.mp3", "SNAKE": "Assets/bgm2.mp3", "DRAGON": "Assets/bgm3.mp3"}

# 游戏变量
GAME_STATE = "WHITE"
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 1200
CELL_SIZE = 30
ACTIVE_AREA_SIZE = 3
BACKGROUND_COLOR = background_color[GAME_STATE]
SPEED = speed[GAME_STATE]
BGM = bgm[GAME_STATE]
RADIUS = CELL_SIZE // 2  # 蛇的半径


# 定义蛇类
class Snake:
    def __init__(self):
        self.body = deque(
            [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + CELL_SIZE)])
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.grow = False
        self.state = "WHITE"
        self.active_area = (
            SCREEN_WIDTH // 2 - ACTIVE_AREA_SIZE * CELL_SIZE,
            SCREEN_HEIGHT // 2 - ACTIVE_AREA_SIZE * CELL_SIZE,
            ACTIVE_AREA_SIZE * 2 * CELL_SIZE,
            ACTIVE_AREA_SIZE * 2 * CELL_SIZE
        )

    def move(self):
        x, y = self.body[0]
        dx, dy = self.direction
        new_head = ((x + dx * CELL_SIZE), (y + dy * CELL_SIZE))
        self.body.appendleft(new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        self.judge_fail()

    def grow_snake(self):
        self.grow = True
        if food_count % 2 == 0 and food_count < 26:
            self.active_area = (
                snake.active_area[0] - CELL_SIZE,
                snake.active_area[1] - CELL_SIZE,
                snake.active_area[2] + 2 * CELL_SIZE,
                snake.active_area[3] + 2 * CELL_SIZE
            )

    def judge_fail(self):
        global food_count, running, GAME_STATE
        if food_count >= 30:
            return
        if (
                self.body[0] in list(self.body)[1:]
                or self.body[0][0] < self.active_area[0]
                or self.body[0][0] >= self.active_area[0] + self.active_area[2]
                or self.body[0][1] < self.active_area[1]
                or self.body[0][1] >= self.active_area[1] + self.active_area[3]
        ):
            GAME_STATE = "LOSE"
            running = False

    def draw(self, screen):
        for i, segment in enumerate(self.body):
            if self.state == "WHITE":
                pygame.draw.rect(screen, WHITE, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
            elif self.state == "SNAKE":
                segment = (segment[0] + RADIUS, segment[1] + RADIUS)
                pygame.draw.circle(screen, LIGHT_GREEN, segment, RADIUS)
                if i == 0:
                    # 定义不同方向下的偏移量
                    offsets = {
                        UP: [(5, -4), (-5, -4)],
                        DOWN: [(5, 4), (-5, 4)],
                        LEFT: [(-4, 5), (-4, -5)],
                        RIGHT: [(4, 5), (4, -5)]
                    }
                    # 获取当前方向的偏移量
                    eye_offsets = offsets[self.direction]

                    # 根据偏移量绘制眼睛
                    for offset in eye_offsets:
                        pygame.draw.circle(screen, DARK_GREEN, (segment[0] + offset[0], segment[1] + offset[1]), 4)
                else:
                    # 绘制身体
                    pygame.draw.circle(screen, DARK_GREEN, segment, RADIUS / 2)
            elif self.state == "DRAGON":
                if i == 0:
                    # 加载龙头素材
                    if self.direction == UP:
                        head = pygame.image.load("Assets/dragon_head_up.png")
                    elif self.direction == DOWN:
                        head = pygame.image.load("Assets/dragon_head_down.png")
                    elif self.direction == LEFT:
                        head = pygame.image.load("Assets/dragon_head_left.png")
                    else:
                        head = pygame.image.load("Assets/dragon_head_right.png")

                    # 龙头
                    head = pygame.transform.scale(head, (int(1.5 * CELL_SIZE), int(1.5 * CELL_SIZE)))
                    # 根据方向调整龙头的位置
                    head_x, head_y = self.body[0]
                    head_x, head_y = head_x + (CELL_SIZE - head.get_rect().size[0]) / 2, head_y + (
                            CELL_SIZE - head.get_rect().size[1]) / 2
                    # 绘制龙头
                    screen.blit(head, (head_x, head_y))
                else:
                    # 绘制身体
                    segment = (segment[0] + RADIUS, segment[1] + RADIUS)
                    pygame.draw.circle(screen, ORANGE, segment, RADIUS)
                    pygame.draw.circle(screen, RED, segment, RADIUS / 2)
        # 绘制网格
        for x in range(self.active_area[0], self.active_area[0] + self.active_area[2], CELL_SIZE):
            pygame.draw.line(screen, WHITE, (x, self.active_area[1]), (x, self.active_area[1] + self.active_area[3]))
        for y in range(self.active_area[1], self.active_area[1] + self.active_area[3], CELL_SIZE):
            pygame.draw.line(screen, WHITE, (self.active_area[0], y), (self.active_area[0] + self.active_area[2], y))


# 定义食物类
class Food:
    def __init__(self, active_area):
        center_area = (
            active_area[0] + CELL_SIZE,
            active_area[1] + CELL_SIZE,
            active_area[2] - 2 * CELL_SIZE,
            active_area[3] - 2 * CELL_SIZE
        )
        self.position = (
            random.randint(center_area[0] // CELL_SIZE,
                           (center_area[0] + center_area[2] - CELL_SIZE) // CELL_SIZE) * CELL_SIZE,
            random.randint(center_area[1] // CELL_SIZE,
                           (center_area[1] + center_area[3] - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        )

    def draw(self, screen):
        global food_count
        if food_count < 10:
            pygame.draw.rect(screen, RED, (self.position[0], self.position[1], CELL_SIZE, CELL_SIZE))
        else:
            # 苹果
            apple = pygame.image.load("Assets/apple.png")
            apple = pygame.transform.scale(apple, (CELL_SIZE, CELL_SIZE))
            screen.blit(apple, self.position)


# 改变游戏状态
def game_state(state):
    global snake, GAME_STATE, BACKGROUND_COLOR, CELL_SIZE, SPEED, RADIUS, BGM
    snake.state = state
    GAME_STATE = state
    BACKGROUND_COLOR = background_color[state]
    SPEED = speed[state]
    BGM = bgm[state]
    # 换bgm
    pygame.mixer.music.load(BGM)
    pygame.mixer.music.play(-1)
    RADIUS = CELL_SIZE // 2


# 文字绘制函数
def draw_word(word, color, position, size):
    global screen
    font = pygame.font.Font("Assets/YaHei.ttf", size)
    text = font.render(word, True, color)
    text_rect = text.get_rect()
    text_rect.midtop = position
    screen.blit(text, text_rect)


# 显示文字线程
def run_show_word():
    while running:
        show_word()
        pygame.time.delay(10)


# 显示文字
def show_word():
    global screen, food_count, snake, running, GAME_STATE
    # 显示分数
    draw_word("Food Count: " + str(food_count), WHITE, (100, 100), 24)

    messages = [
        ("As you know, don't touch the border!", 5),
        ("It's boring, but keep going.", 10),
        ("You are a snake now.", 13),
        ("Become a dragon!", 20),
        ("Life is long,", 23),
        ("there will always be new first times waiting for us ahead,", 25),
        ("I always look forward to the next adventure.", 28),
        ("I mean life is so good!", 30),
        ("You want it, then go get it!", 114514)
    ]

    for message, threshold in messages:
        if food_count < threshold:
            draw_word(message, ORANGE, (SCREEN_WIDTH // 2, snake.active_area[1] - 50), 28)
            break

    # 绘制logo
    if food_count >= 30:
        draw_logo()


# 绘制logo
def draw_logo():
    global screen, snake, running, GAME_STATE
    # 画出logo.png，位置为active_area边界的右边一个CELL_SIZE
    logo = pygame.image.load("Assets/logo.png")
    logo = pygame.transform.scale(logo, (2 * CELL_SIZE, 2 * CELL_SIZE))
    logo_position = (
        snake.active_area[0] + snake.active_area[2] + 5 * CELL_SIZE,
        snake.active_area[1] + snake.active_area[3] // 2)
    screen.blit(logo, logo_position)
    # 判断是否吃到logo
    if math.hypot(snake.body[0][0] - logo_position[0], snake.body[0][1] - logo_position[1]) <= CELL_SIZE:
        GAME_STATE = "WIN"
        running = False


# 初始化游戏
pygame.init()

# 初始化屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("贪吃蛇")

# 初始化游戏对象
snake = Snake()
food = Food(snake.active_area)
# 定义计数器来跟踪吃到的食物数量
food_count = 0

# 加载背景音乐
pygame.mixer.music.load(BGM)
pygame.mixer.music.play(-1)

# 游戏循环
clock = pygame.time.Clock()
running = True
show_word_thread = threading.Thread(target=run_show_word)
show_word_thread.daemon = True  # 将线程设置为守护线程，以确保在主线程退出时自动关闭
show_word_thread.start()
while running:
    screen.fill(BACKGROUND_COLOR)

    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != DOWN:
                snake.direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.direction = RIGHT

    # 移动蛇
    snake.move()

    # 检测是否吃到食物（距离小于一个单元格）
    if math.hypot(snake.body[0][0] - food.position[0], snake.body[0][1] - food.position[1]) < CELL_SIZE:
        food_count += 1
        snake.grow_snake()
        food = Food(snake.active_area)
        if food_count == 20:
            game_state("DRAGON")
        elif food_count == 10:
            game_state("SNAKE")

    # 绘制蛇和食物
    snake.draw(screen)
    food.draw(screen)
    # 绘制蛇的活动范围
    pygame.draw.rect(screen, ORANGE, snake.active_area, 5)
    # 绘制文字
    show_word()

    # 更新屏幕
    pygame.display.flip()

    # 控制游戏帧率
    clock.tick(SPEED)

# 清空屏幕
screen.fill(BLUE)
while True:
    # 放dragon.png在屏幕中央
    dragon = pygame.image.load("Assets/dragon.png")
    dragon = pygame.transform.scale(dragon, (dragon.get_width(), dragon.get_height()))
    dragon_position = (SCREEN_WIDTH // 2 - dragon.get_width() // 2, SCREEN_HEIGHT // 2 - dragon.get_height() // 2)
    screen.blit(dragon, dragon_position)
    if GAME_STATE == "WIN":
        draw_word("You are the Dragon!", ORANGE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200), 48)
    else:
        draw_word("You got Lost, Thanks for playing!", ORANGE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200), 48)
    pygame.display.flip()
