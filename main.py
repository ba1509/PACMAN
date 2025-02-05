# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 17:20:10 2025

@author: AB 1509
"""
import copy
import math
import pygame
from boards import boards  # Make sure boards.py exists (see below)

pygame.init()
pygame.display.set_caption("Pac-Man")

# Screen dimensions and setup
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 950
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

#screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
clock = pygame.time.Clock()

# Game constants
FPS = 60
FONT = pygame.font.Font('freesansbold.ttf', 20)
PI = math.pi

# Level data and colors
level_data = copy.deepcopy(boards)
wall_color = 'blue'

# Load player frames (expects images assets/player_images/1.png ... 4.png)
player_frames = [
    pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (45, 45))
    for i in range(1, 2)
]



# Load ghost images (make sure these files exist in assets/ghost_images/)
ghost_imgs = {
    'blinky': pygame.transform.scale(pygame.image.load('assets/ghost_images/red.png'), (45, 45)),
    'pinky': pygame.transform.scale(pygame.image.load('assets/ghost_images/pink.png'), (45, 45)),
    'inky': pygame.transform.scale(pygame.image.load('assets/ghost_images/blue.png'), (45, 45)),
    'clyde': pygame.transform.scale(pygame.image.load('assets/ghost_images/orange.png'), (45, 45)),
    'spooked': pygame.transform.scale(pygame.image.load('assets/ghost_images/powerup.png'), (45, 45)),
    'dead': pygame.transform.scale(pygame.image.load('assets/ghost_images/dead.png'), (45, 45))
}

# --------------------------
# Global Game State Variables
# --------------------------

# Player state
player_x, player_y = 450, 663
player_direction = 0  # 0=right, 1=left, 2=up, 3=down
player_speed = 2
player_moves = False
direction_command = 0

# Ghost initial positions and states
blinky_x, blinky_y, blinky_dir = 56, 58, 0
inky_x, inky_y, inky_dir = 440, 388, 2
pinky_x, pinky_y, pinky_dir = 440, 438, 2
clyde_x, clyde_y, clyde_dir = 440, 438, 2

# Each ghost has a “target” (updated each frame) and a state dictionary.
ghost_targets = [(player_x, player_y)] * 4
ghost_states = {
    'blinky': {'dead': False, 'in_box': False, 'eaten': False},
    'inky':   {'dead': False, 'in_box': False, 'eaten': False},
    'pinky':  {'dead': False, 'in_box': False, 'eaten': False},
    'clyde':  {'dead': False, 'in_box': False, 'eaten': False}
}
ghost_speeds = [2, 2, 2, 2]

# Animation/timing counters and gameplay variables
frame_counter = 0
flicker_state = False
startup_counter = 0
score = 0
lives = 3
powerup_active = False
powerup_timer = 0
game_over = False
game_won = False
allowed_turns = [False, False, False, False]  # For the player

# --------------------------
# Ghost Class
# --------------------------

class Ghost:
    """
    A class representing a ghost.
    Direction indices: 0=right, 1=left, 2=up, 3=down.
    (Movement is simplified for this example.)
    """
    def __init__(self, x, y, target, speed, img, direction, dead, in_box, ghost_id):
        self.x_pos = x
        self.y_pos = y
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direction
        self.dead = dead
        self.in_box = in_box
        self.id = ghost_id
        self.turns, self.in_box = self.evaluate_turns()
        self.rect = self.draw()

    @property
    def center_x(self):
        return self.x_pos + 22

    @property
    def center_y(self):
        return self.y_pos + 22

    def draw(self):
        # Decide which ghost image to draw based on state and powerup
        idx = self.id
        eaten_list = [ghost_states['blinky']['eaten'],
                      ghost_states['inky']['eaten'],
                      ghost_states['pinky']['eaten'],
                      ghost_states['clyde']['eaten']]
        if (not powerup_active and not self.dead) or (powerup_active and eaten_list[idx] and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup_active and not self.dead and not eaten_list[idx]:
            screen.blit(ghost_imgs['spooked'], (self.x_pos, self.y_pos))
        else:
            screen.blit(ghost_imgs['dead'], (self.x_pos, self.y_pos))
        return pygame.Rect(self.center_x - 18, self.center_y - 18, 36, 36)

    def evaluate_turns(self):
        """
        Check which directions are available based on the maze layout.
        """
        num1 = (SCREEN_HEIGHT - 50) // 32
        num2 = SCREEN_WIDTH // 30
        num3 = 15
        turns = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:
            # Right
            if level_data[self.center_y // num1][(self.center_x + num3) // num2] < 3 or \
               (level_data[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (self.in_box or self.dead)):
                turns[0] = True
            # Left
            if level_data[self.center_y // num1][(self.center_x - num3) // num2] < 3 or \
               (level_data[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (self.in_box or self.dead)):
                turns[1] = True
            # Up
            if level_data[(self.center_y - num3) // num1][self.center_x // num2] < 3 or \
               (level_data[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                turns[2] = True
            # Down
            if level_data[(self.center_y + num3) // num1][self.center_x // num2] < 3 or \
               (level_data[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                turns[3] = True
        else:
            # Tunnel wrapping
            turns[0] = True
            turns[1] = True

        # Determine if inside ghost box
        in_box = (350 < self.x_pos < 550 and 370 < self.y_pos < 480)
        return turns, in_box

    def fallback_move(self):
        """If no preferred move is available, take any allowed turn."""
        for idx, possible in enumerate(self.turns):
            if possible:
                self.direction = idx
                if idx == 0:
                    self.x_pos += self.speed
                elif idx == 1:
                    self.x_pos -= self.speed
                elif idx == 2:
                    self.y_pos -= self.speed
                elif idx == 3:
                    self.y_pos += self.speed
                return

    def generic_ghost_move(self, vertical_bias=False, horizontal_bias=False):
        """
        A simplified ghost movement: try to move toward the target.
        You can adjust the bias flags to make some ghosts prefer vertical or horizontal movement.
        """
        tx, ty = self.target
        diff_x = tx - self.x_pos
        diff_y = ty - self.y_pos
        moved = False

        if horizontal_bias:
            if diff_x > 0 and self.turns[0]:
                self.x_pos += self.speed
                self.direction = 0
                moved = True
            elif diff_x < 0 and self.turns[1]:
                self.x_pos -= self.speed
                self.direction = 1
                moved = True
            if not moved:
                if diff_y > 0 and self.turns[3]:
                    self.y_pos += self.speed
                    self.direction = 3
                    moved = True
                elif diff_y < 0 and self.turns[2]:
                    self.y_pos -= self.speed
                    self.direction = 2
                    moved = True
        elif vertical_bias:
            if diff_y > 0 and self.turns[3]:
                self.y_pos += self.speed
                self.direction = 3
                moved = True
            elif diff_y < 0 and self.turns[2]:
                self.y_pos -= self.speed
                self.direction = 2
                moved = True
            if not moved:
                if diff_x > 0 and self.turns[0]:
                    self.x_pos += self.speed
                    self.direction = 0
                    moved = True
                elif diff_x < 0 and self.turns[1]:
                    self.x_pos -= self.speed
                    self.direction = 1
                    moved = True
        else:
            if abs(diff_x) >= abs(diff_y):
                if diff_x > 0 and self.turns[0]:
                    self.x_pos += self.speed
                    self.direction = 0
                    moved = True
                elif diff_x < 0 and self.turns[1]:
                    self.x_pos -= self.speed
                    self.direction = 1
                    moved = True
            if not moved:
                if diff_y > 0 and self.turns[3]:
                    self.y_pos += self.speed
                    self.direction = 3
                    moved = True
                elif diff_y < 0 and self.turns[2]:
                    self.y_pos -= self.speed
                    self.direction = 2
                    moved = True
        if not moved:
            self.fallback_move()

        # Wrap horizontally
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30

        return self.x_pos, self.y_pos, self.direction

    def move_blinky(self):
        return self.generic_ghost_move()

    def move_inky(self):
        return self.generic_ghost_move(vertical_bias=True)

    def move_pinky(self):
        return self.generic_ghost_move(horizontal_bias=True)

    def move_clyde(self):
        # Clyde “scatters” when far from the player, else chases.
        distance = abs(player_x - self.x_pos) + abs(player_y - self.y_pos)
        if distance > 150:
            self.target = (50, SCREEN_HEIGHT - 50)  # Scatter target
        else:
            self.target = (player_x, player_y)
        return self.generic_ghost_move()

# --------------------------
# Utility Functions
# --------------------------

def draw_ui():
    """Draw the score, lives, and game over / win messages."""
    score_text = FONT.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    if powerup_active:
        pygame.draw.circle(screen, 'blue', (140, 930), 15)
    for i in range(lives):
        life_img = pygame.transform.scale(player_frames[0], (30, 30))
        screen.blit(life_img, (650 + i * 40, 915))
    if game_over or game_won:
        color = 'red' if game_over else 'green'
        msg = 'Game over! Press SPACE to restart!' if game_over else 'Victory! Press SPACE to restart!'
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        message = FONT.render(msg, True, color)
        screen.blit(message, (100, 300))


def handle_player_collisions(score, powerup, p_timer, eaten):
    """
    Check if the player has collided with a pellet (1) or power pellet (2)
    and update score/powerup state accordingly.
    """
    num1 = (SCREEN_HEIGHT - 50) // 32
    num2 = SCREEN_WIDTH // 30
    cx = player_x + 23
    cy = player_y + 24
    if 0 < player_x < 870:
        cell_value = level_data[cy // num1][cx // num2]
        if cell_value == 1:
            level_data[cy // num1][cx // num2] = 0
            score += 10
        elif cell_value == 2:
            level_data[cy // num1][cx // num2] = 0
            score += 50
            powerup = True
            p_timer = 0
            eaten = [False, False, False, False]
    return score, powerup, p_timer, eaten


def draw_level():
    """Render the maze, pellets, and walls."""
    num1 = (SCREEN_HEIGHT - 50) // 32
    num2 = SCREEN_WIDTH // 30
    for i, row in enumerate(level_data):
        for j, val in enumerate(row):
            x_center = j * num2 + (0.5 * num2)
            y_center = i * num1 + (0.5 * num1)
            if val == 1:
                pygame.draw.circle(screen, 'white', (int(x_center), int(y_center)), 4)
            elif val == 2 and not flicker_state:
                pygame.draw.circle(screen, 'white', (int(x_center), int(y_center)), 10)
            elif val == 3:
                pygame.draw.line(screen, wall_color, (int(x_center), i * num1), (int(x_center), i * num1 + num1), 3)
            elif val == 4:
                pygame.draw.line(screen, wall_color, (j * num2, int(y_center)), (j * num2 + num2, int(y_center)), 3)
            elif val == 5:
                pygame.draw.arc(screen, wall_color, [(j * num2 - (num2 * 0.4)) - 2, int(y_center), num2, num1], 0, PI / 2, 3)
            elif val == 6:
                pygame.draw.arc(screen, wall_color, [(j * num2 + (num2 * 0.5)), int(y_center), num2, num1], PI/2, PI, 3)
            elif val == 7:
                pygame.draw.arc(screen, wall_color, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], PI, 3*PI/2, 3)
            elif val == 8:
                pygame.draw.arc(screen, wall_color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1], 3*PI/2, 2*PI, 3)
            elif val == 9:
                pygame.draw.line(screen, 'white', (j * num2, int(y_center)), (j * num2 + num2, int(y_center)), 3)


def draw_player():
    """Draw the player sprite according to the current direction and animation frame."""
    frame_idx = (frame_counter // 5) % len(player_frames)
    if player_direction == 0:
        screen.blit(player_frames[frame_idx], (player_x, player_y))
    elif player_direction == 1:
        screen.blit(pygame.transform.flip(player_frames[frame_idx], True, False), (player_x, player_y))
    elif player_direction == 2:
        screen.blit(pygame.transform.rotate(player_frames[frame_idx], 90), (player_x, player_y))
    elif player_direction == 3:
        screen.blit(pygame.transform.rotate(player_frames[frame_idx], 270), (player_x, player_y))


def check_turns(cx, cy):
    """
    Determine which directions the player can move based on current position.
    """
    turns = [False, False, False, False]
    num1 = (SCREEN_HEIGHT - 50) // 32
    num2 = SCREEN_WIDTH // 30
    num3 = 15
    if cx // 30 < 29:
        if player_direction == 0:
            if level_data[cy // num1][(cx + num3) // num2] < 3:
                turns[0] = True
        elif player_direction == 1:
            if level_data[cy // num1][(cx - num3) // num2] < 3:
                turns[1] = True
        elif player_direction == 2:
            if level_data[(cy - num3) // num1][cx // num2] < 3:
                turns[2] = True
        elif player_direction == 3:
            if level_data[(cy + num3) // num1][cx // num2] < 3:
                turns[3] = True
        if 12 <= cx % num2 <= 18:
            if level_data[(cy - num3) // num1][cx // num2] < 3:
                turns[2] = True
            if level_data[(cy + num3) // num1][cx // num2] < 3:
                turns[3] = True
        if 12 <= cy % num1 <= 18:
            if level_data[cy // num1][(cx - num3) // num2] < 3:
                turns[1] = True
            if level_data[cy // num1][(cx + num3) // num2] < 3:
                turns[0] = True
    else:
        turns[0] = True
        turns[1] = True
    return turns


def move_player(px, py):
    """Move the player if the next cell in the current direction is allowed."""
    if player_direction == 0 and allowed_turns[0]:
        px += player_speed
    elif player_direction == 1 and allowed_turns[1]:
        px -= player_speed
    elif player_direction == 2 and allowed_turns[2]:
        py -= player_speed
    elif player_direction == 3 and allowed_turns[3]:
        py += player_speed
    return px, py


def determine_ghost_targets(blx, bly, inx, iny, pix, piy, clx, cly):
    """
    Compute each ghost’s target based on the powerup state and their status.
    """
    return_base = (380, 400)
    if player_x < 450:
        runaway_x = 900
    else:
        runaway_x = 0
    if player_y < 450:
        runaway_y = 900
    else:
        runaway_y = 0

    def ghost_target_logic(gname, gx, gy, eaten):
        if powerup_active:
            if not ghost_states[gname]['dead'] and not eaten:
                if gname == 'blinky':
                    return (runaway_x, runaway_y)
                elif gname == 'inky':
                    return (runaway_x, player_y)
                elif gname == 'pinky':
                    return (player_x, runaway_y)
                elif gname == 'clyde':
                    return (450, 450)
            if not ghost_states[gname]['dead'] and eaten:
                if 340 < gx < 560 and 340 < gy < 500:
                    return (400, 100)
                else:
                    return (player_x, player_y)
            if ghost_states[gname]['dead']:
                return return_base
        else:
            if not ghost_states[gname]['dead']:
                if 340 < gx < 560 and 340 < gy < 500:
                    return (400, 100)
                else:
                    return (player_x, player_y)
            else:
                return return_base

    eaten_list = [ghost_states['blinky']['eaten'],
                  ghost_states['inky']['eaten'],
                  ghost_states['pinky']['eaten'],
                  ghost_states['clyde']['eaten']]
    blink_target = ghost_target_logic('blinky', blx, bly, eaten_list[0])
    inky_target = ghost_target_logic('inky', inx, iny, eaten_list[1])
    pinky_target = ghost_target_logic('pinky', pix, piy, eaten_list[2])
    clyde_target = ghost_target_logic('clyde', clx, cly, eaten_list[3])
    return [blink_target, inky_target, pinky_target, clyde_target]


def reset_game_state():
    """Reset positions and states after the player loses a life."""
    global player_x, player_y, player_direction, direction_command
    global blinky_x, blinky_y, blinky_dir
    global inky_x, inky_y, inky_dir
    global pinky_x, pinky_y, pinky_dir
    global clyde_x, clyde_y, clyde_dir
    global powerup_active, powerup_timer, startup_counter, ghost_states
    startup_counter = 0
    powerup_active = False
    powerup_timer = 0
    player_x, player_y = 450, 663
    player_direction = 0
    direction_command = 0
    blinky_x, blinky_y, blinky_dir = 56, 58, 0
    inky_x, inky_y, inky_dir = 440, 388, 2
    pinky_x, pinky_y, pinky_dir = 440, 438, 2
    clyde_x, clyde_y, clyde_dir = 440, 438, 2
    for gname in ghost_states:
        ghost_states[gname]['eaten'] = False
        ghost_states[gname]['dead'] = False
        ghost_states[gname]['in_box'] = False

# --------------------------
# Main Game Loop
# --------------------------

running = True
while running:
    clock.tick(FPS)
    
    # Animate player and flicker (used for power-pellet flashing)
    if frame_counter < 19:
        frame_counter += 1
        if frame_counter > 3:
            flicker_state = False
    else:
        frame_counter = 0
        flicker_state = True

    # Powerup timer logic
    if powerup_active and powerup_timer < 600:
        powerup_timer += 1
    elif powerup_active and powerup_timer >= 600:
        powerup_active = False
        powerup_timer = 0
        for gname in ghost_states:
            ghost_states[gname]['eaten'] = False

    # Startup delay before movement begins
    if startup_counter < 180 and not game_over and not game_won:
        player_moves = False
        startup_counter += 1
    else:
        player_moves = True

    screen.fill('black')
    draw_level()
    center_x = player_x + 23
    center_y = player_y + 24

    # Adjust ghost speeds based on state
    if powerup_active:
        ghost_speeds = [1, 1, 1, 1]
    else:
        ghost_speeds = [2, 2, 2, 2]
    if ghost_states['blinky']['eaten']:
        ghost_speeds[0] = 2
    if ghost_states['inky']['eaten']:
        ghost_speeds[1] = 2
    if ghost_states['pinky']['eaten']:
        ghost_speeds[2] = 2
    if ghost_states['clyde']['eaten']:
        ghost_speeds[3] = 2
    if ghost_states['blinky']['dead']:
        ghost_speeds[0] = 4
    if ghost_states['inky']['dead']:
        ghost_speeds[1] = 4
    if ghost_states['pinky']['dead']:
        ghost_speeds[2] = 4
    if ghost_states['clyde']['dead']:
        ghost_speeds[3] = 4

    # Check win condition (all pellets eaten)
    game_won = True
    for row in level_data:
        if 1 in row or 2 in row:
            game_won = False
            break

    # Draw player hitbox (for collision detection) and player sprite
    player_hitbox = pygame.draw.circle(screen, 'black', (center_x, center_y), 20, 2)
    draw_player()

    # Instantiate ghosts with current positions, speeds, etc.
    blinky = Ghost(blinky_x, blinky_y, ghost_targets[0], ghost_speeds[0], ghost_imgs['blinky'], blinky_dir,
                   ghost_states['blinky']['dead'], ghost_states['blinky']['in_box'], 0)
    inky = Ghost(inky_x, inky_y, ghost_targets[1], ghost_speeds[1], ghost_imgs['inky'], inky_dir,
                 ghost_states['inky']['dead'], ghost_states['inky']['in_box'], 1)
    pinky = Ghost(pinky_x, pinky_y, ghost_targets[2], ghost_speeds[2], ghost_imgs['pinky'], pinky_dir,
                  ghost_states['pinky']['dead'], ghost_states['pinky']['in_box'], 2)
    clyde = Ghost(clyde_x, clyde_y, ghost_targets[3], ghost_speeds[3], ghost_imgs['clyde'], clyde_dir,
                  ghost_states['clyde']['dead'], ghost_states['clyde']['in_box'], 3)
    draw_ui()

    # Update ghost targets based on positions and player location
    ghost_targets = determine_ghost_targets(blinky_x, blinky_y, inky_x, inky_y, pinky_x, pinky_y, clyde_x, clyde_y)
    allowed_turns = check_turns(center_x, center_y)

    # If movement is allowed, update positions
    if player_moves:
        player_x, player_y = move_player(player_x, player_y)
        # Ghost movements:
        if not ghost_states['blinky']['dead'] and not blinky.in_box:
            blinky_x, blinky_y, blinky_dir = blinky.move_blinky()
        else:
            blinky_x, blinky_y, blinky_dir = blinky.move_clyde()
        if not ghost_states['pinky']['dead'] and not pinky.in_box:
            pinky_x, pinky_y, pinky_dir = pinky.move_pinky()
        else:
            pinky_x, pinky_y, pinky_dir = pinky.move_clyde()
        if not ghost_states['inky']['dead'] and not inky.in_box:
            inky_x, inky_y, inky_dir = inky.move_inky()
        else:
            inky_x, inky_y, inky_dir = inky.move_clyde()
        clyde_x, clyde_y, clyde_dir = clyde.move_clyde()

    # Check player collisions with pellets/power pellets
    eaten_list = [ghost_states['blinky']['eaten'],
                  ghost_states['inky']['eaten'],
                  ghost_states['pinky']['eaten'],
                  ghost_states['clyde']['eaten']]
    score, powerup_active, powerup_timer, eaten_list = handle_player_collisions(score, powerup_active,
                                                                                powerup_timer, eaten_list)
    ghost_states['blinky']['eaten'] = eaten_list[0]
    ghost_states['inky']['eaten'] = eaten_list[1]
    ghost_states['pinky']['eaten'] = eaten_list[2]
    ghost_states['clyde']['eaten'] = eaten_list[3]

    # Check collisions between the player and ghosts (when not powered up)
    if not powerup_active:
        if (player_hitbox.colliderect(blinky.rect) and not ghost_states['blinky']['dead']) or \
           (player_hitbox.colliderect(inky.rect) and not ghost_states['inky']['dead']) or \
           (player_hitbox.colliderect(pinky.rect) and not ghost_states['pinky']['dead']) or \
           (player_hitbox.colliderect(clyde.rect) and not ghost_states['clyde']['dead']):
            if lives > 0:
                lives -= 1
                reset_game_state()
            else:
                game_over = True
                player_moves = False
                startup_counter = 0

    # If powerup is active, check if the player “eats” a ghost
    def handle_powerup_eat(ghost_name, ghost_obj):
        if powerup_active and player_hitbox.colliderect(ghost_obj.rect) and not ghost_states[ghost_name]['dead']:
            if not ghost_states[ghost_name]['eaten']:
                ghost_states[ghost_name]['dead'] = True
                ghost_states[ghost_name]['eaten'] = True
                eaten_count = sum(ghost_states[g]['eaten'] for g in ghost_states)
                score_gain = (2 ** eaten_count) * 100
                return score_gain
        return 0

    score += handle_powerup_eat('blinky', blinky)
    score += handle_powerup_eat('inky', inky)
    score += handle_powerup_eat('pinky', pinky)
    score += handle_powerup_eat('clyde', clyde)

    # If a dead ghost returns to its box, revive it
    if blinky.in_box and ghost_states['blinky']['dead']:
        ghost_states['blinky']['dead'] = False
    if inky.in_box and ghost_states['inky']['dead']:
        ghost_states['inky']['dead'] = False
    if pinky.in_box and ghost_states['pinky']['dead']:
        ghost_states['pinky']['dead'] = False
    if clyde.in_box and ghost_states['clyde']['dead']:
        ghost_states['clyde']['dead'] = False

    # Wrap player around tunnels
    if player_x > 900:
        player_x = -47
    elif player_x < -50:
        player_x = 897

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction_command = 0
            elif event.key == pygame.K_LEFT:
                direction_command = 1
            elif event.key == pygame.K_UP:
                direction_command = 2
            elif event.key == pygame.K_DOWN:
                direction_command = 3
            elif event.key == pygame.K_SPACE and (game_over or game_won):
                # Restart game
                powerup_active = False
                powerup_timer = 0
                lives = 3
                score = 0
                startup_counter = 0
                game_over = False
                game_won = False
                level_data = copy.deepcopy(boards)
                reset_game_state()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_command == 0:
                direction_command = player_direction
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = player_direction
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = player_direction
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = player_direction

    # Change player direction if allowed
    if direction_command == 0 and allowed_turns[0]:
        player_direction = 0
    elif direction_command == 1 and allowed_turns[1]:
        player_direction = 1
    elif direction_command == 2 and allowed_turns[2]:
        player_direction = 2
    elif direction_command == 3 and allowed_turns[3]:
        player_direction = 3

    pygame.display.flip()

pygame.quit()

