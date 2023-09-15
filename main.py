# i want to give credit to Lemaster Tech for using his ideas relating to the background of this game and for the joystick implementation


import pygame
from board import boards
import math

pygame.init()
width = 600  # width of screen
height = 650  # height of screen
screen = pygame.display.set_mode([width, height])
timer = pygame.time.Clock()  # speed at which game runs
fps = 60 #frame per second
font = pygame.font.Font("freesansbold.ttf", 20)
level = boards  # board is the list for background
color = "blue"
PI = math.pi
players_image = pygame.transform.scale(pygame.image.load(f'pacman-png-25195.png'), (28, 28)) #player image of pacman
live_images = pygame.transform.scale(pygame.image.load(f'pacman-png-25195.png'), (14, 14)) # image of pacman for lives
redghost_image = pygame.transform.scale(pygame.image.load(f'redghost.png'), (28,28)) # image of ghost red one
direction = 0  # initial direction of pacman which is to the right
player_x = 285  # initial x position of pacman
player_y = 425  # initial y position of pacman

redghost_x = 275  # initial x position of red ghost
redghost_y = 275   # initial y position of red ghost

count = 0
flicker = False
allowed_turns = [False, False, False, False]
player_speed = 1  # speed of pacman when it moves
direction_command = 0
score = 0
power_up_time = 0
power_up = False
lives = 5 # number of lives pacman has


def draw_board():  # method to draw board uses a list
    num1 = ((height - 50) // 32)
    num2 = (width // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:   # 1 is the small dots
                pygame.draw.circle(screen, "white", (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2 and not flicker: # 2 is the big dots
                pygame.draw.circle(screen, "white", (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 8)

            if level[i][j] == 3: # 3 is vertical blue lines
                pygame.draw.line(screen, color, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4: # 4 is the horizontal b;ue lines
                pygame.draw.line(screen, color, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5: # is for the arc add
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], 0,
                                PI / 2, 3)
            if level[i][j] == 6: # is for the arc sugar
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1],
                                PI / 2, PI, 3)

            if level[i][j] == 7: # is for the arc To
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.5 * num1)), num2, num1], PI,
                                3 * PI / 2, 3)

            if level[i][j] == 8: # is for the arc Coffee
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.5)), (i * num1 - (0.5 * num1)), num2, num1],
                                3 * PI / 2, 2 * PI, 3)


def draw_pacman(): # draw pacman and the image is rotated depending on the direction
    if direction == 0:
        screen.blit(players_image, (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(players_image, True, False), (player_x, player_y))

    elif direction == 2:
        screen.blit(pygame.transform.rotate(players_image, 90), (player_x, player_y))

    elif direction == 3:
        screen.blit(pygame.transform.rotate(players_image, 270), (player_x, player_y))

def draw_redghost(): # draw redghost onto the screen
    screen.blit(redghost_image,(redghost_x, redghost_y) )
def check_position(centerx, centery): # determines when can pacman can turn or not
    turns = [False, False, False, False]
    num1 = (height - 50) // 32  # y direction
    num2 = (width // 30)  # x direction
    num3 = 6  # fudge factor // checks ahead
    num4 = 15 # correction for fudeg when turning left and up
    # check collisions based on center x and center y of player +/- fudge number
    # 1,2 represents dots, big dots or path where pacman can move
    if centerx // 30 < 29: # if pacman position is within the 29 squares horizontally
        if direction == 0:
            if level[centery // num1][(centerx - num4) // num2] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num4) // num1][centerx // num2] < 3:
                turns[3] = True
                # print('m') needs to be erased used for testing only
        if direction == 3:
            if level[(centery - num4) // num1][centerx // num2] < 3:
                turns[2] = True
                # print('n') needs to be erased used for testing only
        if direction == 2 or direction == 3:
            # if direction is either up or down and pacman is in the middle of a square
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num4) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num4) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num4) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True

    return turns



def drawscore(): # methods that displays the score
    score_display = font.render(f'Score is: {score}', True, 'white')
    screen.blit(score_display,(10,height -20))


def moveplayer(pcenter_x, pcenter_y):
    if direction == 0 and allowed_turns[0]:  # r
        pcenter_x += player_speed

    elif direction == 1 and allowed_turns[1]:  # l
        pcenter_x -= player_speed

    if direction == 2 and allowed_turns[2]:  # u
        pcenter_y -= player_speed
    elif direction == 3 and allowed_turns[3]:  # d
        pcenter_y += player_speed

    return pcenter_x, pcenter_y


def powerup_display(power_up_time, lives): # methods that displays how much time power_up is available and displays the lives left
    powerup_display = font.render(f'Power_up_time is: {power_up_time}', True, 'white')
    screen.blit(powerup_display, (390, height - 20))
    for i in range(lives):
        screen.blit(players_image, ((380+(i*30)),  (height - 60)))


def check_collision(score, power_up_time, power_up): # whenever pacman goes through a bullet it eats it and the score increases
    num1 = (height-50)// 32
    num2 = width//30
    if 0 < player_x < (width - 30):
        if level[center_y//num1][center_x// num2] == 1:
            level[center_y//num1][center_x// num2] = 0
            score += 10

        if level[center_y//num1][center_x// num2] == 2:
            level[center_y//num1][center_x// num2] = 0
            score += 50
            power_up_time += 1
            power_up = True
    return score, power_up_time,power_up





run = True
while run:    # for large points to flicker
    timer.tick(fps)
    if count <= 10:
        count += 1
        if count > 3:
            flicker = False
    else:
        count = 0
        flicker = True
    if power_up and power_up_time <= 300:
        power_up_time += 1
    elif power_up and power_up_time > 300:
        power_up = False
        power_up_time = 0

    screen.fill("black")
    draw_board()
    draw_pacman()
    draw_redghost()
    drawscore()

    center_x = player_x + 23 # x position of pacman

    center_y = player_y + 24 # y position of pacman
    allowed_turns = check_position(center_x, center_y)
    player_x, player_y = moveplayer(player_x, player_y)
    score, power_up_time, power_up = check_collision(score, power_up_time, power_up)
    # print(players_image)
    powerup_display(power_up_time, lives)
    for event in pygame.event.get():  # everything pygame can get is in .get()
        if event.type == pygame.QUIT:  # if close button press then loops break
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction_command = 0
            if event.key == pygame.K_LEFT:
                direction_command = 1
            if event.key == pygame.K_UP:
                direction_command = 2
            if event.key == pygame.K_DOWN:
                direction_command = 3

        if event.type == pygame.KEYUP: # if key is not pressed pacman still moves in the direction sets when the key was pressed
                                      # joystick function
            if event.key == pygame.K_RIGHT and direction_command == 3:
                direction_command = direction
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = direction
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = direction
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = direction

    if direction_command == 0 and allowed_turns[0]:
        direction = 0
    if direction_command == 1 and allowed_turns[1]:
        direction = 1
    if direction_command == 2 and allowed_turns[2]:
       direction = 2
    if direction_command == 3 and allowed_turns[3]:
        direction = 3
    if direction_command == 4 and allowed_turns[4]:
        direction = 4
   # print(allowed_turns)

    if player_x > 900:
        player_x = -40
    elif player_x < -50:
        player_x = 900

    pygame.display.flip()  #
pygame.quit()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
