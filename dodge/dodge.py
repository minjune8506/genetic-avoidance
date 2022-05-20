# Referred video https://www.youtube.com/watch?v=-8n91btt5d8

from audioop import mul
import pygame
import sys
import random  # Pythons random library

pygame.init()  # To initialize pygame

# Defining the width and height of the screen
WIDTH = 800  # Global variables
HEIGHT = 600

# 키보드 조작을 더 부드럽게
pygame.key.set_repeat(5,60)

# Defining the color for player and enemy
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0, 255, 0)
BACKGROUND_COLOR = (0, 0, 0)  # Setting the background color, Black

# Defining player position and player block size
PLAYER_SIZE = 15  # Its the size of the block
PLAYER_POS = [WIDTH / 2 - PLAYER_SIZE / 2, HEIGHT / 2 - PLAYER_SIZE / 2]  # Its the x and y-axis position

# Defining an enemy
ENEMY_SIZE = 10
ENEMY_LIST = []  # Defining an enemy list to contain multiple enemies
ENEMY_COUNT = 10
MATRIX = [[False for i in range(WIDTH + 1)] for j in range(HEIGHT + 1)] # Boolean 형태의 map 생성

dx = [0, 1, 1, 1, 0, -1, -1, -1]
dy = [-1, -1, 0, 1, 1, 1, 0, -1] # 8 방향

# Creating a screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # We have a screen of WIDTH 800 and HEIGHT 600
game_over = False
score = 0  # Initializing the score
clock = pygame.time.Clock()  # It defines a clock
myFont = pygame.font.SysFont("monospace", 35)  # Defining the font in pygame (Monospace is font and 35 is in pixels)
endFont = pygame.font.SysFont("comicsansms", 40, True, False)

def set_level(score, ENEMY_COUNT, ENEMY_LIST):
    if score < 20:
        ENEMY_COUNT = 30
    elif score < 50:
        ENEMY_COUNT = 50
    elif score < 100:
        ENEMY_COUNT = 100
    else:
        ENEMY_COUNT = 200

    return ENEMY_COUNT

class Enemy:   
    def draw_enemies(enemy_list):
        for enemy_pos in enemy_list:
            # Drawing the enemy rectangle
            pygame.draw.rect(screen, BLUE, (enemy_pos[0], enemy_pos[1], ENEMY_SIZE, ENEMY_SIZE))

    def drop_enemies(ENEMY_LIST):
        randomValue = random.randint(1, 4)  # It generates a random value betwee 0 and 4
        if len(ENEMY_LIST) < 20:  # When the no. of elements inside the list is less than 10
            if randomValue == 1:
                #남쪽
                x_pos = random.randint(0, WIDTH)  # Assigning the x-coordinate to the new enemy randomly.
                y_pos = HEIGHT
                y_speed = -1
                x_speed = random.randint(-1, 1)
                MATRIX[y_pos][x_pos] = True;
                ENEMY_LIST.append([x_pos, y_pos, x_speed, y_speed])  # It appends new enemy coordinates to the enemy list
            elif randomValue == 2:
                #북쪽
                x_pos = random.randint(0, WIDTH)  # Assigning the x-coordinate to the new enemy randomly.
                y_pos = 0
                y_speed = 1
                x_speed = random.randint(-1, 1)
                MATRIX[y_pos][x_pos] = True;
                ENEMY_LIST.append([x_pos, y_pos, x_speed, y_speed])  # It appends new enemy coordinates to the enemy list
            elif randomValue == 3:
                #서쪽
                x_pos = 0  # Assigning the x-coordinate to the new enemy randomly.
                y_pos = random.randint(0, HEIGHT)
                y_speed = random.randint(-1, 1)
                x_speed = 1
                MATRIX[y_pos][x_pos] = True;
                ENEMY_LIST.append([x_pos, y_pos, x_speed, y_speed])  # It appends new enemy coordinates to the enemy list
            elif randomValue == 4:
                #동쪽
                x_pos = WIDTH  # Assigning the x-coordinate to the new enemy randomly.
                y_pos = random.randint(0, HEIGHT)
                y_speed = random.randint(-1, 1)
                x_speed = -1
                MATRIX[y_pos][x_pos] = True; # 방문처리 추가
                ENEMY_LIST.append([x_pos, y_pos, x_speed, y_speed])  # It appends new enemy coordinates to the enemy list
        
    def get_input() : # 센서를 통해서 장애물 감지
        inputs = [1.0] * 4 # 4 개 짜리 배열 (상, 하, 좌, 우)
        y = int(PLAYER_POS[1])
        x = int(PLAYER_POS[0])
        
        detectRange = 200
        mulNumber = 1 / detectRange

        for i in range((y - detectRange), (y + (detectRange + 1))) : # 주변 위 아래 오른쪽 왼쪽 5칸씩 체크
            for j in range((x - detectRange), (x + (detectRange + 1))) :
                if i == y and x == j :
                    continue

                if i < 0 or i > HEIGHT :
                    break                    

                if j < 0 or j > WIDTH : # 범위를 나간 경우
                    continue # 해당 방향으로는 움직일 수 없음        

                if MATRIX[i][j] : # 장애물이 있는 경우                
                    ny = y - i
                    nx = x - j               

                    if ny > 0: # ny 가 양수인 경우 (위)
                        inputs[0] = min(inputs[0], (mulNumber * abs(ny)))
                    elif ny < 0 : # ny 가 음수인 경우 (아래)
                        inputs[1] = min(inputs[1], (mulNumber * abs(ny)))

                    if nx > 0 : # nx 가 양수인 경우 (왼쪽)
                        inputs[2] = min(inputs[2], (mulNumber * abs(nx)))
                    elif nx < 0 : # nx 가 음수인 경우 (오른쪽)
                        inputs[3] = min(inputs[3], (mulNumber * abs(nx)))
        
        print(inputs) # 출력
        return inputs # 장애물이 해당 방향에 없는 경우는 1, 아니면 센서값
                
    def out_of_range(x, y) : # 계산한 좌표가 범위 밖으로 나가는지를 계산
        if (x < 0 or x > WIDTH) or (y < 0 or y > HEIGHT) :
            return True
        else :
            return False
                
    def update_enemy_positions(ENEMY_LIST, score):
        for idx, ENEMY_POS in enumerate(ENEMY_LIST):  # Using the enumerate function
            # Updating the position of enemy and making the enemy block fall        
            x_move = False
            y_move = False

            if not ((ENEMY_POS[0] < 0 or ENEMY_POS[0] > WIDTH) or (ENEMY_POS[1] < 0 or ENEMY_POS[1] > HEIGHT)) : # 범위를 벗어나지 않는 경우에만
                MATRIX[ENEMY_POS[1]][ENEMY_POS[0]] = False;
            
            if 0 <= ENEMY_POS[1] <= HEIGHT :
                ENEMY_POS[1] += ENEMY_POS[3]  # It increments the value of height
                y_move = True            

            if 0 <= ENEMY_POS[0] <= WIDTH :
                ENEMY_POS[0] += ENEMY_POS[2]
                x_move = True            

            if not x_move or not y_move: # x 혹은 y 좌표로 움직이지 않은 경우는 끝에 도달했다라는 것임
                ENEMY_LIST.pop(idx)  # It pops out the enemy from the enemy_list
                score +=1  # Incrementing the score each time we pass it
            elif not ((ENEMY_POS[0] < 0 or ENEMY_POS[0] > WIDTH) or (ENEMY_POS[1] < 0 or ENEMY_POS[1] > HEIGHT)) :            
                MATRIX[ENEMY_POS[1]][ENEMY_POS[0]] = True; # 변경된 좌표에 다시 방문처리    

        return score  # It returns the score

    def collision_check(enemy_list, player_pos):   # Causes the game to end if it returns True
        for enemy_pos in enemy_list:  # It iterates through each enemy_pos inside enemy_list
            if Enemy.detect_collision(player_pos, enemy_pos):  # returns True if collision is detected for any enemy_pos
                return True
        return False

    def detect_collision(PLAYER_POS, ENEMY_POS):
            p_x = PLAYER_POS[0]
            p_y = PLAYER_POS[1]

            e_x = ENEMY_POS[0]
            e_y = ENEMY_POS[1]

            if (e_x >= p_x and e_x < (p_x + PLAYER_SIZE)) or (p_x >= e_x and p_x < (e_x + ENEMY_SIZE)):  # Checks to see the x-overlap
                if (e_y >= p_y and e_y < (p_y + PLAYER_SIZE)) or (p_y >= e_y and p_y < (e_y + ENEMY_SIZE)):  # Checks to see the y-overlap
                    return True
            return False  # False is returned only when the above if statements do not get run.

def limit(PLAYER_POS):  # Function to restrict the movement of the player
    p_x = PLAYER_POS[0]
    p_y = PLAYER_POS[1]

    if p_x <=0 and p_y <=0:
        p_x = 0
        p_y = 0

    elif p_x >= WIDTH and p_y <=0:
        p_x = WIDTH - PLAYER_SIZE
        p_y = 0

    elif p_x >= WIDTH and p_y >= HEIGHT:
        p_x = WIDTH -PLAYER_SIZE
        p_y = HEIGHT -PLAYER_SIZE

    elif p_x <= 0 and p_y >= HEIGHT:
        p_x = 0
        p_y = HEIGHT -PLAYER_SIZE

    elif p_x >= WIDTH:
        p_x = WIDTH -PLAYER_SIZE

    elif p_x <= 0:
        p_x = 0

    elif p_y >= HEIGHT:
        p_y = HEIGHT -PLAYER_SIZE

    elif p_y <= 0:
        p_y = 0

    PLAYER_POS = [p_x, p_y]

    return PLAYER_POS

while not game_over :  # It keeps running until we hit the game_over condition

    for event in pygame.event.get():  # For loop to get an event
        # print(event)  # It prints the event each time

        if event.type == pygame.QUIT:  # When we click on the close button it exits the program
            sys.exit()

        if event.type == pygame.KEYDOWN:  # (press Ctrl + /) for commenting many lines simultaneously
            x = PLAYER_POS[0]
            y = PLAYER_POS[1]  # Just grabbing the x and y coordinates

            if event.key == pygame.K_LEFT:  # When left key is pressed
                x -= PLAYER_SIZE  # Decrementing the position of x by PLAYER_SIZE (moving it by one whole block)

            elif event.key == pygame.K_RIGHT:  # When right key is pressed
                x += PLAYER_SIZE  # Incrementing the position of x by PLAYER_SIZE (moving it by one whole block)

            elif event.key == pygame.K_UP:
                y -= PLAYER_SIZE

            elif event.key == pygame.K_DOWN:
                y += PLAYER_SIZE

            PLAYER_POS = [x, y]  # We are passing in the new x and y values
            PLAYER_POS = limit(PLAYER_POS)  # Calling the limit function

    screen.fill(BACKGROUND_COLOR)  # It takes in an RGB value and updates the screen

    Enemy.drop_enemies(ENEMY_LIST)   # Calling the drop enemies function
    score = Enemy.update_enemy_positions(ENEMY_LIST, score)  # It updates the enemy position and stores the score value
    Enemy.get_input()
    # print(score)  # Prints score to the console
    ENEMY_COUNT = set_level(score, ENEMY_COUNT, ENEMY_LIST)

    text = "Score:" + str(score)  # Storing our score to "text" variable
    final_score = "Final Score: " + str(score)
    msg = "Better Luck next time!!"
    label1 = myFont.render(text, 1, YELLOW)  #
    screen.blit(label1,  (WIDTH-200, HEIGHT-50))# Attaching our label to screen

    if Enemy.collision_check(ENEMY_LIST, PLAYER_POS):   # It will enter the loop only when the function returns True
        label2 = endFont.render(final_score, 1, RED)  # The font will be printed in "red"
        label3 = endFont.render(msg, 1, (0, 255, 0))
        screen.blit(label2, (250, 250))  # It updates text to the specific part(position) of the screen
        screen.blit(label3, (250, 300))

        game_over = True
        # break  # It breaks out of the loop without showing the overlap

    Enemy.draw_enemies(ENEMY_LIST)   # Calling the draw enemy function

    # Drawing the player rectangle
    pygame.draw.rect(screen, RED, (PLAYER_POS[0], PLAYER_POS[1], PLAYER_SIZE, PLAYER_SIZE))  # rect(Surface, Color, Rect, width=0) Look pygame documentatioN

    clock.tick(30)  # Setting the clock to 30 frames per second

    pygame.display.update()  # It will update the changes on our screen each time

    if game_over:
        pygame.time.wait(3000)  # The wait value is in millisecond hence here the wait is 3 seconds

