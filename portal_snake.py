import os
import random
import sys
from collections import deque

import pygame


def resource_path(*paths):
    base_path = getattr(sys, '_MEIPASS', os.getcwd())
    return os.path.join(base_path, *paths)


def game():
    # Initialize pygame and set screen size
    pygame.init()
    width, height = 500, 500
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Portal Snake")

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Set colors
    white = (255, 255, 255)
    red = (255, 0, 0)
    blue = (0, 255, 255)

    # Set snake block size and initial position
    block_size = 10
    snake_rect = pygame.Rect(width // 2, height // 2, block_size, block_size)

    def create_tiled_background(image_path, block_size, screen_width, screen_height):
        # Load the image and convert it to the same format as the screen
        background_image = pygame.image.load(image_path).convert()

        # Create a new surface to hold the tiled background
        tiled_background = pygame.Surface((screen_width, screen_height))

        # Loop to blit the subsurface repeatedly
        for x in range(0, screen_width, block_size):
            for y in range(0, screen_height, block_size):
                subsurface_rect = pygame.Rect((x, y), (block_size, block_size))
                tiled_background.blit(background_image, subsurface_rect)

        return tiled_background

    def draw_tiled_background(screen, background_surface):
        screen.blit(background_surface, (0, 0))

    background_path = resource_path('resources', 'background.png')
    background_surface = create_tiled_background(background_path, block_size, width, height)

    # Load music and sfx paths
    audio_path = resource_path('resources', 'music.mp3')
    sound_path = resource_path('resources', 'eat.mp3')

    # Play music continuously
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(loops=-1)

    # Load eat sfx
    sfx = pygame.mixer.Sound(sound_path)
    sfx.set_volume(1.0)

    # Set initial direction
    direction = "right"
    last_direction = direction

    # Set snake's body as a deque of rects
    snake_body = deque()
    snake_length = 3
    for _ in range(snake_length):
        snake_body.appendleft(snake_rect.copy())

    # Set the speed of the snake
    snake_speed = 15

    # Set initial score
    score = 0

    # Set font for displaying score
    font_style = pygame.font.SysFont("Arial", 30)

    # Create a list to store food rects
    food_rects = []

    # Function to generate food at random locations
    def generate_food():
        if len(food_rects) == 0:
            snake_positions = set((rect.x, rect.y) for rect in snake_body)
            existing_food_positions = set((food.x, food.y) for food in food_rects)
            new_food_rects = []
            while len(new_food_rects) < 5:
                food_rect = pygame.Rect(
                    round(random.randrange(0, width - block_size) / block_size) * block_size,
                    round(random.randrange(0, height - block_size) / block_size) * block_size,
                    block_size,
                    block_size,
                )
                if (food_rect.x, food_rect.y) not in snake_positions and (food_rect.x, food_rect.y) not in existing_food_positions:
                    new_food_rects.append(food_rect)
                    existing_food_positions.add((food_rect.x, food_rect.y))
            food_rects.extend(new_food_rects)

    # Function to display score on screen
    def show_score(score):
        score_text = font_style.render(str(score), True, white)
        score_text_rect = score_text.get_rect(center=(width // 2, 20))
        screen.blit(score_text, score_text_rect)

    # Game over function
    def game_over():
        message = font_style.render("Game Over", True, red)
        text_rect = message.get_rect(center=(width / 2, height / 2))
        screen.blit(message, text_rect)
        pygame.display.update()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

    key_queue = []

    # Flag to indicate if AI is in control
    ai_control = False

    # BFS AI function to find the shortest path to food
    def bfs_ai(snake_rect, food_rects, snake_body):
        distance_map = {}  # Dictionary to store shortest distances to positions
        queue = deque([(snake_rect.x, snake_rect.y, 0, [])])  # Initialize the queue with snake's current position and distance

        snake_body_positions = set((rect.x, rect.y) for rect in snake_body)  # Set to store snake's body positions

        while queue:
            x, y, distance, path = queue.popleft()  # Dequeue the next position from the queue

            if (x, y) in distance_map and distance >= distance_map[(x, y)]:  # Skip if a shorter path has already been found
                continue

            distance_map[(x, y)] = distance  # Update the shortest distance for the position

            if any(x == food.x and y == food.y for food in food_rects):  # Check if position contains food
                return path  # Return the path to food

            # Calculate the Manhattan distance between the current position and all adjacent positions
            adjacent_positions = [
                ((x + block_size) % width, y, distance + 1, path + ['right']),
                ((x - block_size) % width, y, distance + 1, path + ['left']),
                (x, (y + block_size) % height, distance + 1, path + ['down']),
                (x, (y - block_size) % height, distance + 1, path + ['up'])
            ]

            # Sort adjacent positions based on their Manhattan distance to the food
            adjacent_positions.sort(key=lambda pos: manhattan_distance(pos[:2], get_closest_food(food_rects, pos[:2])))

            for pos in adjacent_positions:
                if pos[:2] not in snake_body_positions:  # Skip positions that are part of snake's body
                    queue.append(pos)  # Enqueue the valid position

        return []  # Return empty path if no valid path is found

    def manhattan_distance(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_closest_food(food_rects, position):
        return min(food_rects, key=lambda food: manhattan_distance(position, (food.x, food.y)))

    # Run the game loop
    generate_food()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    ai_control = not ai_control  # Toggle AI control
                elif not ai_control:
                    key_queue.append(event.key)

        if ai_control:
            # AI Control
            if not key_queue:
                path = bfs_ai(snake_rect, food_rects, snake_body)

                if path:
                    next_move = path[0]

                    if next_move == 'right' and last_direction != "left":
                        direction = "right"
                    elif next_move == 'left' and last_direction != "right":
                        direction = "left"
                    elif next_move == 'up' and last_direction != "down":
                        direction = "up"
                    elif next_move == 'down' and last_direction != "up":
                        direction = "down"

        while key_queue:
            key = key_queue.pop(0)
            if key == pygame.K_LEFT and last_direction != "right":
                direction = "left"
            elif key == pygame.K_RIGHT and last_direction != "left":
                direction = "right"
            elif key == pygame.K_UP and last_direction != "down":
                direction = "up"
            elif key == pygame.K_DOWN and last_direction != "up":
                direction = "down"

        # Move snake and wrap around screen with boundary checks
        if direction == "right":
            snake_rect.x += block_size
            if snake_rect.x >= width:
                snake_rect.x = 0
        elif direction == "left":
            snake_rect.x -= block_size
            if snake_rect.x < 0:
                snake_rect.x = width - block_size
        elif direction == "up":
            snake_rect.y -= block_size
            if snake_rect.y < 0:
                snake_rect.y = height - block_size
        elif direction == "down":
            snake_rect.y += block_size
            if snake_rect.y >= height:
                snake_rect.y = 0

        last_direction = direction

        draw_tiled_background(screen, background_surface)

        # Check for collision with food
        for food in food_rects.copy():
            if snake_rect.colliderect(food):
                sfx.play()
                score += 1
                food_rects.remove(food)
                snake_length += 1
                snake_body.appendleft(snake_rect.copy())
                generate_food()
                break

        # Check for collision with body
        if any(snake_rect.colliderect(snake_block) for snake_block in list(snake_body)[1:]):
            game_over()

        # Move the snake body
        snake_body.appendleft(snake_rect.copy())
        snake_body.pop()
        # Draw the snake body
        for snake_block in snake_body:
            pygame.draw.rect(screen, white, snake_block)

        # Draw food
        for food in food_rects:
            pygame.draw.rect(screen, blue, food)

        # Display score
        show_score(score)

        pygame.display.update()
        clock.tick(snake_speed)


if __name__ == "__main__":
    game()
