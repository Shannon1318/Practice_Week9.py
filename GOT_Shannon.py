import random, sys, time, math, pygame
from pygame.locals import *

FPS = 30
WINWIDTH = 640 # width of the program's window, in pixels
WINHEIGHT = 480 # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

SKYCOLOR = (135, 206, 235)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

CAMERASLACK = 90     # how far from the center the dragon moves before moving the camera
MOVERATE = 9         # how fast the player moves
BOUNCERATE = 6       # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 30    # how high the player bounces
STARTSIZE = 35       # how big the player starts off
WINSIZE = 300        # how big the player needs to be to win
INVULNTIME = 2       # how long the player is invulnerable after being hit in seconds
GAMEOVERTIME = 4     # how long the "game over" text stays on the screen in seconds
eggLives = 2        # how many lives the player starts with

numClouds = 80        # number of cloud objects in the active area
numIceDragons = 30    # number of dragons in the active area
dragonMinSpeed = 3 # slowest speed
dragonMaxSpeed = 7 # fastest speed
DIRCHANGEFREQ = 2    # % chance of direction change per frame
LEFT = 'left'
RIGHT = 'right'

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, goodDragon, iceDragon, cloudImages, Khaleesi

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('goodDragon.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Game of Thrones: Fire and Ice')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    # load the image files
    goodDragon = pygame.image.load('goodDragon.png')
    iceDragon = pygame.image.load('iceDragon.png')
    Khaleesi = pygame.image.load('Khaleesi.png')
    cloudImages = []
    for i in range(1, 5):
        x=cloudImages.append(pygame.image.load('clouds.png'))

    while True:
        runGame()

def runGame():
    # set up variables for the start of a new game
    gameOverMode = False      # if the player has lost
    gameOverStartTime = 0     # time the player lost
    winMode = False           # if the player has won

    # create the surfaces to hold game text
    gameOverSurf = BASICFONT.render('Game Over', True, WHITE)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf = BASICFONT.render('You found Khaleesi!', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = BASICFONT.render('(Press "r" to restart.)', True, WHITE)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    # camerax and cameray are the top left of where the camera view is
    camerax = 0
    cameray = 0

    cloudObjs = []    # stores all the clouds
    evilDragons = [] # stores all the bad dragons
    # stores the player object:
    playerObj = {'surface': pygame.transform.scale(goodDragon, (STARTSIZE, STARTSIZE)),
                 'facing': LEFT,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'bounce':0,
                 'lives': eggLives}

    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False

    # start off with some clouds in sky
    for i in range(10):
        cloudObjs.append(makeNewCloud(camerax, cameray))
        cloudObjs[i]['x'] = random.randint(0, WINWIDTH)
        cloudObjs[i]['y'] = random.randint(0, WINHEIGHT)

    while True: # main game loop
        # move all the dragons
        for each in evilDragons:
            # move the squirrel, and adjust for their bounce
            each['x'] += each['movex']
            each['y'] += each['movey']
            each['bounce'] += 1
            if each['bounce'] > each['bouncerate']:
                each['bounce'] = 0 # reset bounce amount

            # random chance they change direction
            if random.randint(0, 99) < DIRCHANGEFREQ:
                each['movex'] = getRandomVelocity()
                each['movey'] = getRandomVelocity()

        # go through all the objects and see if any need to be deleted.
        for i in range(len(cloudObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, cloudObjs[i]):
                del cloudObjs[i]
        for i in range(len(evilDragons) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, evilDragons[i]):
                del evilDragons[i]

        # add more clouds & evil dragons
        while len(cloudObjs) < numClouds:
            cloudObjs.append(makeNewCloud(camerax, cameray))
        while len(evilDragons) < numIceDragons:
            evilDragons.append(makeNewIceDragon(camerax, cameray))

        # adjust camerax and cameray if beyond the "camera slack"
        playerCenterx = playerObj['x'] + int(playerObj['size'] / 2)
        playerCentery = playerObj['y'] + int(playerObj['size'] / 2)
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMERASLACK:
            camerax = playerCenterx + CAMERASLACK - HALF_WINWIDTH
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMERASLACK:
            camerax = playerCenterx - CAMERASLACK - HALF_WINWIDTH
        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMERASLACK:
            cameray = playerCentery + CAMERASLACK - HALF_WINHEIGHT
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = playerCentery - CAMERASLACK - HALF_WINHEIGHT

        # draw the sky background
        DISPLAYSURF.fill(SKYCOLOR)

        # draw all the cloud objects on the screen
        for gObj in cloudObjs:
            gRect = pygame.Rect( (gObj['x'] - camerax,
                                  gObj['y'] - cameray,
                                  gObj['width'],
                                  gObj['height']) )
            DISPLAYSURF.blit(cloudImages[gObj['cloudImage']], gRect)


        # draw the evil dragons
        for drObj in evilDragons:
            drObj['rect'] = pygame.Rect( (drObj['x'] - camerax,
                                         drObj['y'] - cameray - getBounceAmount(drObj['bounce'], drObj['bouncerate'], drObj['bounceheight']),
                                         drObj['width'],
                                         drObj['height']) )
            DISPLAYSURF.blit(drObj['surface'], drObj['rect'])


        # draw the good dragon
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not flashIsOn:
            playerObj['rect'] = pygame.Rect( (playerObj['x'] - camerax,
                                              playerObj['y'] - cameray - getBounceAmount(playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT),
                                              playerObj['size'],
                                              playerObj['size']) )
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])


        # draw the eggs representing lives
        drawEggs(playerObj['lives'])

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
                elif winMode and event.key == K_r:
                    return

            elif event.type == KEYUP:
                # stop moving the player's squirrel
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False

                elif event.key == K_ESCAPE:
                    terminate()

        if not gameOverMode:
            # actually move the player
            if moveLeft:
                playerObj['x'] -= MOVERATE
            if moveRight:
                playerObj['x'] += MOVERATE
            if moveUp:
                playerObj['y'] -= MOVERATE
            if moveDown:
                playerObj['y'] += MOVERATE

            if (moveLeft or moveRight or moveUp or moveDown) or playerObj['bounce'] != 0:
                playerObj['bounce'] += 1

            if playerObj['bounce'] > BOUNCERATE:
                playerObj['bounce'] = 0 # reset bounce amount

            # check if the player has collided with any ice dragons
            for i in range(len(evilDragons)-1, -1, -1):
                evilDr = evilDragons[i]
                if 'rect' in evilDr and playerObj['rect'].colliderect(evilDr['rect']):
                    #a good dragon/ice dragon collision has occurred
                    playerObj['lives'] -= 1
                    if playerObj['lives'] == 0:
                        gameOverMode = True # turn on "game over mode"
                        gameOverStartTime = time.time()
        else:
            # game is over, show "game over" text
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStartTime > GAMEOVERTIME:
                return # end the current game

        # check if the player has won.
        if winMode:
            DISPLAYSURF.blit(winSurf, winRect)
            DISPLAYSURF.blit(winSurf2, winRect2)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawEggs(lives):
    index = 0
    for i in range(lives): # draw eggs
        egg = pygame.image.load("Egg.png")
        DISPLAYSURF.blit(egg, (10, 20 + index))
        index += 40

def terminate():
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    # Returns the number of pixels to offset based on the bounce.
    # Larger bounceRate means a slower bounce.
    # Larger bounceHeight means a higher bounce.
    # currentBounce will always be less than bounceRate
    return int(math.sin( (math.pi / float(bounceRate)) * currentBounce ) * bounceHeight)

def getRandomVelocity():
    speed = random.randint(dragonMinSpeed, dragonMaxSpeed)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    # create a Rect of the camera view
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        # create a Rect object with the random coordinates and use colliderect()
        # to make sure the right edge isn't in the camera view.
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y


def makeNewIceDragon(camerax, cameray):
    dr = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    dr['width']  = (generalSize + random.randint(0, 10)) * multiplier
    dr['height'] = (generalSize + random.randint(0, 10)) * multiplier
    dr['x'], dr['y'] = getRandomOffCameraPos(camerax, cameray, dr['width'], dr['height'])
    dr['movex'] = getRandomVelocity()
    dr['movey'] = getRandomVelocity()
    dr['surface'] = pygame.transform.scale(iceDragon, (dr['width'], dr['height']))
    dr['bounce'] = 0
    dr['bouncerate'] = random.randint(10, 18)
    dr['bounceheight'] = random.randint(10, 50)
    return dr


def makeNewCloud(camerax, cameray):
    cl = {}
    cl['cloudImage'] = random.randint(0, len(cloudImages) - 1)
    cl['width']  = cloudImages[0].get_width()
    cl['height'] = cloudImages[0].get_height()
    cl['x'], cl['y'] = getRandomOffCameraPos(camerax, cameray, cl['width'], cl['height'])
    cl['rect'] = pygame.Rect( (cl['x'], cl['y'], cl['width'], cl['height']) )
    return cl


def isOutsideActiveArea(camerax, cameray, obj):
    # Return False if camerax and cameray are more than
    # a half-window length beyond the edge of the window.
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)


if __name__ == '__main__':
    main()