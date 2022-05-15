import pygame, math, random, sys, time
from pygame.locals import *

#This is a simple game based on Game of thrones.
#Press spacebar to fire flames at the enemy dragons
#Use arrows to move up, down, right, and left
#If you touch Khaleesi you win
#If you touch an ice dragon you lose a life - each egg represents a life

class Dragon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velx = 10
        self.vely = 10
        self.lives = 5
        self.alive = True
        self.drag = pygame.image.load("goodDragon.png")
        self.rect = self.drag.get_rect()

    def drawLives(self, screen):
        index = 0
        x = self.lives
        while x > 0:  # draw eggs
            egg = pygame.image.load("Egg.png")
            screen.blit(egg, (10, 20 + index))
            x -= 1
            index += 40

    def move_dragon(self, userInput, screen):
        drag = pygame.image.load("goodDragon.png")
        if userInput[pygame.K_LEFT] and self.x >= 10:
            self.x -= self.velx
        elif userInput[pygame.K_RIGHT] and self.x < 480:
            self.x += self.velx
        if userInput[pygame.K_UP] and self.y > 0:
            self.y -= self.vely
        elif userInput[pygame.K_DOWN] and self.y < 480:
            self.y += self.vely
        screen.blit(drag, (self.x, self.y))

def main():
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    pygame.display.set_icon(pygame.image.load('goodDragon.png'))
    pygame.display.set_caption('Khaleesi\'s Dragons')

    #Sound
    pygame.mixer.music.load("GOT.mp3")
    pygame.mixer.music.set_volume(.5)
    pygame.mixer.music.play(-1)

    WHITE = (255, 255, 255)
    SKYCOLOR = (135, 206, 235)

    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)
    player = Dragon(100, 40)

    # If game is over
    gameOverSurf = BASICFONT.render('Game Over!', True, WHITE)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (250, 250)

    #If you find Khaleesi
    winSurf = BASICFONT.render('You found Khaleesi!', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (250, 250)

    #If you lose a life
    winSurf2 = BASICFONT.render('(You lost a life)', True, WHITE)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (250, 280)

    # Set up evil dragons aka Ice Dragons
    num_iceDragons = 4
    iceDImg = []
    iceDx = []
    iceDy = []
    iceDx_change = []
    iceDy_change = []
    for i in range(num_iceDragons):
        iceDImg.append(pygame.image.load('iceDragon.png'))
        iceDx.append(random.randint(0, 500))
        iceDy.append(random.randint(50, 500))
        iceDx_change.append(4)
        iceDy_change.append(10)

    # flames from dragon breath
    flame = pygame.image.load("flame.png")
    flameX = player.x
    flameY = player.y
    flameY_change = 20
    flame_ready = True

    # Main Loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

        screen.fill((SKYCOLOR))

        #Draw Clouds
        cloud = pygame.image.load("clouds.png")
        for y in range(30,480, 100):
            for x in range(30,450, 100):
                screen.blit(cloud,(x, y))

        # Draw Lives left
        player.drawLives(screen)
        # Draw Khaleesi
        Khaleesi = pygame.image.load("Khaleesi.png")
        rectK = Khaleesi.get_rect(center=(300, 300))
        screen.blit(Khaleesi, (rectK))

        for i in range(num_iceDragons):
            iceDx[i] += iceDx_change[i]
            iceDy[i] += iceDy_change[i]
            if iceDx[i] <= 0:
                iceDx_change[i] = 5
                iceDy[i] += iceDy_change[i]
            elif iceDx[i] >= 480:
                iceDx_change[i] = -10
                iceDy[i] += iceDy_change[i]
            if iceDy[i] <= 0:
                iceDy_change[i] = 5
            elif iceDy[i] >= 400:
                iceDy_change[i] = -20
            screen.blit(iceDImg[i], (iceDx[i], iceDy[i]))

        if player.alive == False:
            if player.lives < 0:
                screen.blit(gameOverSurf, gameOverRect)
            else:
                screen.blit(winSurf2, winRect2)
                #player.lives -= 1

        # input
        userInput = pygame.key.get_pressed()
        #Player Movement
        player.move_dragon(userInput, screen)

         # flame firing
        if userInput[pygame.K_SPACE]:
            if flame_ready == True:
                #flame coordinates to breathe fire from
                flameX = player.x
                flameY = player.y
                fireFlame(flame, flameX, flameY, screen)
                flame_ready = False

        #Move flames
        if flame_ready == False:
            flameY -= flameY_change
            screen.blit(flame, (flameX, flameY))
            if flameY <= 0:
                flameY = 480
                flame_ready = True

        #Check if flame hits ice dragon - then ice dragon disappears/reappears
        collisionEnemy = isCollision(iceDx[i], iceDy[i], flameX, flameY)
        if collisionEnemy:
                flameY = 480
                flame_ready = True
                iceDx[i] = random.randint(0, 500)
                iceDy[i] = random.randint(0, 100)

            # Ice Dragon hits player and takes a life
        collisionDeath = isCollision(iceDx[i], iceDy[i], player.x, player.y)
        if collisionDeath:
            player.alive = False
            screen.blit(winSurf2, winRect2)
            hatchSound = pygame.mixer.Sound("EggHatch.mp3")
            hatchSound.play(maxtime=400)
            player.lives -=1
            player.drawLives(screen)

        #Check if player touches Khaleesi
        collisionWin = isCollision(player.x, player.y, rectK.x, rectK.y)
        if collisionWin:  # If dragon collides with Khaleesi
            screen.blit(winSurf, winRect)

        pygame.time.delay(30)
        pygame.display.update()

def fireFlame(flame, flameX, flameY, screen):
    screen.blit(flame, (flameX, flameY - 15))
    flameSound = pygame.mixer.Sound("Dragon_Sound.mp3")
    flameSound.play(maxtime=500)

def isCollision(iceDx,iceDy,flameX,flameY):
    distance = math.sqrt((math.pow(iceDx - flameX, 2)) + (math.pow(iceDy - flameY, 2)))
    if distance <= 100:
        return True
    else:
        return False

def terminate():
            pygame.quit()
            sys.exit()

main()

