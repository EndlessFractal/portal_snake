import pygame
import random

# Initialize pygame and set screen size
pygame.init()
width = 500
height = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pygame Snake")

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Set colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)

# Set snake block size and initial position
block_size = 10
x1 = width // 2
y1 = height // 2

# Set initial direction
direction = "right"

# Set snake's body as a list of blocks
snake_body = []
snake_length = 3

# Set the speed of the snake
snake_speed = 15

# Set initial score
score = 0

# Set font for displaying score
font_style = pygame.font.SysFont(None, 50)


def generate_food():
    global foodx, foody, foodx2, foody2
    foodx = round(random.randrange(0, width - block_size) / block_size) * block_size
    foody = round(random.randrange(0, height - block_size) / block_size) * block_size
    foodx2 = round(random.randrange(0, width - block_size) / block_size) * block_size
    foody2 = round(random.randrange(0, height - block_size) / block_size) * block_size


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

last_direction = direction

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
    if direction == "right":
        x1 += block_size
    elif direction == "left":
        x1 -= block_size
    elif direction == "up":
        y1 -= block_size
    elif direction == "down":
        y1 += block_size

    if x1 > width:
        x1 = 0
    elif x1 < 0:
        x1 = width
    elif y1 > height:
        y1 = 0
    elif y1 < 0:
        y1 = height

    last_direction = direction

    screen.fill(black)

    snake_head = []
    snake_head.append(x1)
    snake_head.append(y1)
    snake_body.append(snake_head)
    if len(snake_body) > snake_length:
        del snake_body[0]

    # Draw snake and food
    for x, y in snake_body:
        pygame.draw.rect(screen, green, [x, y, block_size, block_size])
    pygame.draw.rect(screen, red, [foodx, foody, block_size, block_size])
    pygame.draw.rect(screen, red, [foodx2, foody2, block_size, block_size])

    # Check if snake has eaten food
    if (x1 == foodx and y1 == foody) or (x1 == foodx2 and y1 == foody2):
        generate_food()
        snake_length += 1
        score += 1

    # Update score on screen
    show_score(score)

    # Check for collision with snake body
    for block in snake_body[:-1]:
        if block[0] == x1 and block[1] == y1:
            game_over()

    # Update screen
    pygame.display.update()
    clock.tick(snake_speed)