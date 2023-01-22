from collections import deque
import pygame
import random

# Initialize pygame and set screen size
pygame.init()
width = 500
height = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Portal Snake")

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Set colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)

# Set snake block size and initial position
block_size = 10
snake_rect = pygame.Rect(width // 2, height // 2, block_size, block_size)

# Set initial direction
direction = "right"
last_direction = direction

# Set snake's body as a deque of rects
snake_body = deque()
snake_length = 3
for i in range(snake_length):
    snake_body.appendleft(snake_rect.copy())

# Set the speed of the snake
snake_speed = 15

# Set initial score
score = 0

# Set font for displaying score
font_style = pygame.font.SysFont(None, 50)

# Create a list to store food rects
food_rects = []


# Function to generate food at random locations
def generate_food():
    global food_rects
    if len(food_rects) == 0:
        for i in range(5):
            food_rect = pygame.Rect(
                round(random.randrange(0, width - block_size) / block_size) * block_size,
                round(random.randrange(0, height - block_size) / block_size) * block_size,
                block_size,
                block_size,
            )
            food_collision = False
            # Check if food is going to be generated inside snake
            for snake_block in snake_body:
                if snake_block.colliderect(food_rect):
                    food_collision = True
                    break
            if not food_collision:
                food_rects.append(food_rect)
            else:
                i -= 1


# Function to display score on screen
def show_score(score):
    score_text = font_style.render("Score: " + str(score), True, white)
    screen.blit(score_text, [0, 0])


# Game over function
def game_over():
    message = font_style.render("Game Over", True, red)
    text_rect = message.get_rect(center=(width / 2, height / 2))
    screen.blit(message, text_rect)
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()
    quit()


key_queue = []

# Run the game loop
generate_food()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            key_queue.append(event.key)

    while len(key_queue) > 0:
        key = key_queue.pop(0)
        if key == pygame.K_LEFT and last_direction != "right":
            direction = "left"
        elif key == pygame.K_RIGHT and last_direction != "left":
            direction = "right"
        elif key == pygame.K_UP and last_direction != "down":
            direction = "up"
        elif key == pygame.K_DOWN and last_direction != "up":
            direction = "down"

    # Move snake and wrap around screen
    if direction == "right":
        snake_rect.x += block_size
    elif direction == "left":
        snake_rect.x -= block_size
    elif direction == "up":
        snake_rect.y -= block_size
    elif direction == "down":
        snake_rect.y += block_size

    if snake_rect.x > width:
        snake_rect.x = 0
    elif snake_rect.x < 0:
        snake_rect.x = width
    elif snake_rect.y > height:
        snake_rect.y = 0
    elif snake_rect.y < 0:
        snake_rect.y = height

    last_direction = direction

    screen.fill(black)

    # Check for collision with food
    for food in food_rects:
        if snake_rect.colliderect(food):
            score += 1
            food_rects.remove(food)
            snake_length += 1
            snake_body.appendleft(snake_rect.copy())
            generate_food()
            break

    # Check for collision with body
    for i in range(len(snake_body) - 1):
        if snake_rect.colliderect(snake_body[i + 1]):
            game_over()

    # Move the body
    pygame.display.update()
    clock.tick(snake_speed)
