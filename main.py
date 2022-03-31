from itertools import count
from mimetypes import init
import pygame
from pygame import mixer
import random
import os
import ctypes
from sys import exit
import time 
import threading

pygame.init()
mixer.init()

user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# Real screen width and height
width=screensize[0]
height=screensize[1]

#Hard coded screen dimensions for testing purposes
# width=1000
# height=700

gameWindow=pygame.display.set_mode((width, height), vsync=1)
pygame.display.set_caption("Snakespeare")

#colors
white=(255,255,255)
black=(0,0,0)
red=(255,0,0)
brown=(160,82,45)
welcome_screen=(138, 58, 58)
end_screen=(46, 42, 156)
cyan=(50, 88, 168)

font=pygame.font.SysFont(None, 36)
clock=pygame.time.Clock()
time_limit=5 #change this to change the display time of special food
offset=3 #Change this to adjust the thickness of the border
prev_score_cap=0

food_type=0 #Determins the type of food, normal food=0, special food=1
food_determination_counter=0
c=time_limit
is_threading=False

def countdown():
    global c, time_limit
    
    for x in range(time_limit):
        c=c-1
        time.sleep(1)

def draw_borders(gameWindow):
    pygame.draw.rect(gameWindow, brown, [0,42,width,offset]) #Top border
    pygame.draw.rect(gameWindow, brown, [0,42,offset,height]) #Left border
    pygame.draw.rect(gameWindow, brown, [0,height-offset,width,offset]) #bottom border
    pygame.draw.rect(gameWindow, brown, [width-offset,42,offset,height]) #right border

def draw_snake(gameWindow, color, snake_list, size):
    for x,y in snake_list:
        pygame.draw.rect(gameWindow, color, [x, y, size, size])

def generate_food(gameWindow, x, y):
    global food_type, food_determination_counter,c, is_threading, time_limit
    if food_determination_counter==5:
        if is_threading==False:
            c=time_limit
            countdown_thread=threading.Thread(target=countdown)
            countdown_thread.start()

        # Time bar
        pygame.draw.rect(gameWindow, black, [500,10,time_limit*20,20])
        pygame.draw.rect(gameWindow, red, [500,10,c*20,20])

        food=pygame.image.load("assets/images/food_spc.png")
        gameWindow.blit(food, [x,y])
        food_type=1
        is_threading=True
        if (c==0):
            food_determination_counter=(food_determination_counter+1)%6

    elif food_determination_counter!=5:
        food=pygame.image.load("assets/images/food.png")
        gameWindow.blit(food, [x, y])
        food_type=0
        is_threading=False


def show_score(text, font, color, highscore):
    text_source=font.render(text, True, color)
    gameWindow.blit(text_source, [5,10])

    text_source=font.render(highscore, True, color)
    gameWindow.blit(text_source, [200, 10])



def welcome():
    global food_determination_counter, food_type
    food_type=0
    food_determination_counter=0
    mixer.music.load("assets/music/intro.mp3")
    mixer.music.play()

    exit_game=False
    bgImg=pygame.image.load("assets/images/bg1.png")
    bgImg=pygame.transform.scale(bgImg, (width, height))
    gameWindow.blit(bgImg, [0,0])

    source=font.render("Welcome to Snakespeare", True, white)
    source_rect=source.get_rect(center=(width/2, height/4))
    gameWindow.blit(source, source_rect)

    pygame.draw.rect(gameWindow, cyan, [width/16, height/2, width/4,100]) #Kid mode box
    pygame.draw.rect(gameWindow, white, [(width/16)+5, (height/2)+5, (width/4)-10,90])

    pygame.draw.rect(gameWindow, cyan, [(3*width)/8, height/2, width/4,100]) #Gamer mode box
    pygame.draw.rect(gameWindow, white, [((3*width)/8)+5, (height/2)+5, (width/4)-10,90])

    pygame.draw.rect(gameWindow, cyan, [(11*width)/16, height/2, width/4,100]) #Quit box
    pygame.draw.rect(gameWindow, white, [((11*width)/16)+5, (height/2)+5, (width/4)-10,90])

    source=font.render("Kid mode", True, black)
    source_rect=source.get_rect(center=((3*width)/16, (height/2)+50))
    gameWindow.blit(source, source_rect)

    source=font.render("Gamer mode", True, black)
    source_rect=source.get_rect(center=(width/2, (height/2)+50))
    gameWindow.blit(source, source_rect)

    source=font.render("Quit", True, black)
    source_rect=source.get_rect(center=((13*width)/16, (height/2)+50))
    gameWindow.blit(source, source_rect)

    while not exit_game:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                exit_game=True                
            if event.type==pygame.MOUSEBUTTONDOWN:
                mouse_x,mouse_y=pygame.mouse.get_pos()
                if event.button==1:
                    if mouse_x>width/16 and mouse_x<(width/16+width/4) and mouse_y>height/2 and mouse_y<(height/2+100):
                        mode=0
                        mixer.music.stop()
                        runGame(mode)
                    if mouse_x>(3*width/8) and mouse_x<((3*width/8)+width/4) and mouse_y>height/2 and mouse_y<(height/2+100):
                        mode=1
                        mixer.music.stop()
                        runGame(mode)
                    if mouse_x>(11*width/16) and mouse_x<((11*width/16)+width/4) and mouse_y>height/2 and mouse_y<(height/2+100):
                        exit_game=True
                    
        pygame.display.update()
    
    pygame.quit()
    exit()
            


def runGame(mode):
    bgImg=pygame.image.load("assets/images/bg2.png").convert_alpha()
    bgImg=pygame.transform.scale(bgImg, (width, height)).convert_alpha()

    #Game Highscore is defined here
    if (not os.path.exists("highscore.txt")):
        with open("highscore.txt", "w") as f:
            f.write("0");
    with open("highscore.txt", "r") as f:
        highscore=int(f.read())


    #Game Specific Variables
    exit_game=False
    game_over=False
    start=False
    newHighScore=False
    snake_x=random.randint(10,width/2)
    snake_y=random.randint(42,height/2)
    food_x=random.randint(20, width-60)
    food_y=random.randint(42, height-50)
    food_size=5
    size= 10
    init_velocity=5 #Change this to change the speed of the snake
    vx=0
    vy=0
    fps=60
    sensitivity=size+20 #Change this to adjust the proximity of food and snake
    snake_list=[]
    snake_length=3 #Change this to adjust the length of snake when it grows
    score=0
    direction_y=None #True means +ve direction, False means negative
    direction_x=None #True means +ve direction, False means negative    


    #Game Loop
    while not exit_game:
        if game_over:
            bgImg=pygame.image.load("assets/images/bg3.png")
            bgImg=pygame.transform.scale(bgImg, (width, height)).convert_alpha()
            gameWindow.blit(bgImg, [0,0])

            if newHighScore:
                text="!NEW HIGHSCORE!"
                source=font.render(text, True, white)
                source_rect=source.get_rect(center=(width/2, height/3.5))
                gameWindow.blit(source, source_rect)
                with open("highscore.txt", "w") as f:
                    f.write(str(highscore))
            else:
                source=font.render("Oops! You crashed X(", True, white)
                source_rect=source.get_rect(center=(width/2, height/3.5))
                gameWindow.blit(source, source_rect)

            source=font.render("Your Score: "+str(score), True, white)
            source_rect=source.get_rect(center=(width/2, height/2.5))
            gameWindow.blit(source, source_rect)

            
            
            pygame.draw.rect(gameWindow, red, [(3*width)/8, height/2, width/4,100])
            pygame.draw.rect(gameWindow, white, [((3*width)/8)+5, (height/2)+5, (width/4)-10,90])

            source=font.render("Back", True, black)
            source_rect=source.get_rect(center=(width/2, (height/2)+50))
            gameWindow.blit(source, source_rect)
            
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    exit_game=True
                if event.type==pygame.MOUSEBUTTONDOWN:
                    mouse_x,mouse_y=pygame.mouse.get_pos()
                    if event.button==1:
                        if mouse_x>(3*width/8) and mouse_x<((3*width/8)+width/4) and mouse_y>height/2 and mouse_y<(height/2+100):
                            welcome()

            pygame.display.update()


        else:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    exit_game=True
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:
                        exit_game=True
                if mode==1:
                    if event.type==pygame.MOUSEMOTION:
                        start=True
                        if event.rel[0]>0 and direction_x!=False:
                            vx=init_velocity
                            vy=0
                            direction_x=True
                            direction_y=None

                        if event.rel[0]<0 and direction_x!=True:
                            vx=-init_velocity
                            vy=0
                            direction_x=False
                            direction_y=None

                        if event.rel[1]<0 and direction_y!=True:
                            vy=-init_velocity
                            vx=0
                            direction_x=None
                            direction_y=False

                        if event.rel[1]>0 and direction_y!=False:
                            vy=init_velocity
                            vx=0
                            direction_x=None
                            direction_y=True

                if mode==0:
                    if event.type==pygame.KEYDOWN:
                        start=True
                        if event.key==pygame.K_DOWN and direction_y!=True:
                            vy=init_velocity
                            vx=0
                            direction_x=None
                            direction_y=False
                        

                        if event.key==pygame.K_UP and direction_y!=False:
                            vy=-init_velocity
                            vx=0
                            direction_x=None
                            direction_y=True
                    

                        if event.key==pygame.K_RIGHT and direction_x!=False:
                            vx=init_velocity
                            vy=0
                            direction_x=True
                            direction_y=None
                                    
                        if event.key==pygame.K_LEFT and direction_x!=True: 
                            vx=-init_velocity
                            vy=0
                            direction_x=False
                            direction_y=None
                
                        


            if abs(snake_x-food_x)<sensitivity and abs(snake_y-food_y)<sensitivity:
                mixer.music.load("assets/music/eat.mp3")
                mixer.music.play()
                food_x=random.randint(20, width-20)
                food_y=random.randint(42, height-42)
                snake_length +=4
                if (food_type==0):
                    score=score+1
                elif(food_type==1):
                    score=score+5
                
                #increse velocity logic
                global prev_score_cap
                if (score//3>prev_score_cap):
                    if init_velocity<10:
                        init_velocity +=1
                        prev_score_cap=score//3
                    
                global food_determination_counter
                food_determination_counter=(food_determination_counter+1)%6
            
            
            if score>highscore:
                newHighScore=True
                highscore=score


            gameWindow.blit(bgImg, [0,0])

            draw_snake(gameWindow, black, snake_list, size)
            draw_borders(gameWindow)        

            show_score("Score: "+str(score), font, black, "Highscore: "+str(highscore))
            generate_food(gameWindow, food_x, food_y)
            

            snake_x += vx
            snake_y += vy

            head=[]
            head.append(snake_x)
            head.append(snake_y)
            snake_list.append(head)
            if(len(snake_list)>snake_length):
                del snake_list[0]

            
            #Game Over conditions
            if head in snake_list[:-1] and start:
                game_over=True
                mixer.music.load("assets/music/game_over.mp3")
                mixer.music.play()
                pygame.time.delay(500)
            if(snake_x<0 or snake_x>width-offset or snake_y<42 or snake_y>height-offset):
                game_over=True
                mixer.music.load("assets/music/game_over.mp3")
                mixer.music.play()
                pygame.time.delay(500)
            

            
            clock.tick(fps)
            pygame.display.update()


    pygame.quit()
    exit()
    
welcome()
