import pygame
import os
import time
import random
pygame.font.init()

#Setup display screen
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) #Captions variable for constant variables
pygame.display.set_caption("Space Shooter Tutorial")

#Load images
Red_Spaceship = pygame.transform.scale(pygame.image.load(os.path.join("assets","morty.png")), (120,70)) #from the pygame module use image.load to load image from assets folder and name of image.
Green_Spaceship = pygame.transform.scale(pygame.image.load(os.path.join("assets","floating_head.png")), (100,100))
Blue_Spaceship = pygame.transform.rotozoom(pygame.image.load(os.path.join("assets","mr_meeseeks.png")), -35, 0.2)
#Player ship
Yellow_Spaceship = pygame.transform.scale(pygame.image.load(os.path.join("assets","dick_butt.png")), (95, 124))  #("assets","pixel_ship_yellow.png")
#Lasers
Red_laser = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
Green_laser = pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
Blue_laser = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
Yellow_laser = pygame.transform.scale(pygame.image.load(os.path.join("assets","poop.png")), (50,50))
# Background
BG=pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")), (WIDTH, HEIGHT))

class Laser: #laser is an object on its own
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask =  pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height): #To determine if the laser is off screen
        return not (self.y <= height and self.y >= 0) #If laser is on screen return true, if laser is off screen return false

    def collision(self,obj):
        return collide(self, obj)

class Ship: #Creating attributes to players, each player will store their own values
    COOLDOWN = 10

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.player_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0 #To prevent user to keep shooting lasers so we assign a cool down

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        #pygame.draw.rect(window, (255,0,0), (self.x, self.y, 50,50)) #use pygame module and draw rectangle on window at location (self.x, self.y) with size of 50 by 50 and filled (,0)
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+40, self.y+65, self.laser_img) #adjust the start position of laser with respect to player or enemy mask.
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship): #Player class inherit the attribute from ship
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health) #run player class with extension
        self.ship_img = Yellow_Spaceship
        self.laser_img = Yellow_laser
        self.mask = pygame.mask.from_surface(self.ship_img) #using pygame.mask take the surface of player image and make a mask that tells the locations.
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self,window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self,window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width()*(self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP =  {
                 "red": (Red_Spaceship, Red_laser),
                 "blue": (Blue_Spaceship, Blue_laser),
                 "green": (Green_Spaceship, Green_laser)
                 }
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color] #if we pass the color "red", "blue" or "green" then it will return the corresponding image
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel): #enemy ship will keep going down by vel
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            if self.COLOR_MAP["blue"]:
                laser = Laser(self.x+15, self.y+50, self.laser_img)
                self.lasers.append(laser)
                self.cool_down_counter = 1
            else:
                laser = Laser(self.x, self.y, self.laser_img)
                self.lasers.append(laser)
                self.cool_down_counter = 1

def collide(obj1, obj2): #To determine if laser collide with the player --> if mask of both objects overlap
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) #To determine if object1 overlaps object2 by the amount of offset_x and y --> return none if no overlaps, if overlaps, the coordinate of overlap will be returned


#function of the game
def main():
    run = True
    FPS = 40 #check if the character is moved or collided 60 times every 1 seconds
    level = 0 #stage of the game
    lives = 5
    player_vel = 10
    player_laser_vel = 8
    enemy_laser_vel = -2
    main_font = pygame.font.SysFont("comicsansms", 50) #size of the font = 50
    lost_font = pygame.font.SysFont("comicsansms", 50) #size of the font = 50

    enemies = [] #define enemies as array of arbitrary data types
    wave_length = 5
    enemy_vel = -1

    player = Player(300, 0) #start the player at lower part of screen

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window(): #Function for drawing any images/display in the game
        # Takes the background image and treat it as a surface and draw on it. (0,0) starts from top left-hand corner of display screen.
        WIN.blit(BG, (0,0))

        #Display the lives and level on screen by drawing over BG
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255)) #render and print level in comicsan font and in red(255,0,0) colour
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255)) #render and print level in comicsan font and in red(255,0,0) colour

        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH-level_label.get_width()-10,10))

        for enemy in enemies: #draw enemy on screen, Nothing is draw in the first run of while loop
            enemy.draw(WIN)

        player.draw(WIN)

        if lost: #If lost == True then run the condition
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 -lost_label.get_width()/2,350)) #Write lost_label on screen and centre it.

        pygame.display.update() #refresh/redraw the image on display screen 60imes per sec


    while run: #while run is true
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0: #Stop the game if the lives are less than 0 or the health of player has reached below 0
            lost = True
            lost_count += 1

        if lost: #If lost == True then run the condition
            if lost_count > FPS*3: #if time elapsed more than 3 seconds then terminate the run else continue
                run = False
            else:
                continue #Goes back to the codes before the line continue, in other words, the program will not proceed to generate the enemies and deduce lives.

        if len(enemies) == 0: # For the first run of the while loop, the number of elements in enemies is zero so condition is true.
            level += 1 #when the number of enemies on screen is equal to 0 then the level will go up by 1
            wave_length += 5 #once level goes up by 1 the number of enemies spawned increase by 5
            for i in range(wave_length): #Spawn different enemies randomly off the screen at random location at the top
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(700, 1000), random.choice(["red","blue","green"])) #enemy starts at random x range of 50 to width - 100
                enemies.append(enemy)

        for event in pygame.event.get(): #sense for any occurence of event such as user input
            if event.type == pygame.QUIT: #if we quit/exit the game, we stop the run and run = false
                run = False
        keys = pygame.key.get_pressed() #use pygame.key and get input of all keys pressed 60times per sec and move in that direciton
        if keys[pygame.K_a] and player.x - player_vel > 0: # move left
            player.x -= player_vel #minus pixel size from location index
        elif keys[pygame.K_LEFT] and player.x - player_vel > 0: # move left but not beyond the screen
            player.x -= player_vel #minus pixel size from location index
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #move right but not beyond the screen
            player.x += player_vel
        elif keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: #move right but not beyond the screen
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: #move up but not beyond the screen
            player.y -= player_vel
        elif keys[pygame.K_UP] and player.y - player_vel > 0: #move up but not beyond the screen
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height()+15 < HEIGHT: #move down but not beyond the screen
            player.y += player_vel
        elif keys[pygame.K_DOWN] and player.y + player_vel + player.get_height()+15 < HEIGHT: #move down but not beyond the screen
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]: #make enemies list a copy
            enemy.move(enemy_vel*level)
            enemy.move_lasers(enemy_laser_vel*level, player)

            if random.randrange(0,round(4*FPS/level)) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            if enemy.y + enemy.get_height() < 0: #check the location of the enemies, if they are off screen then lives of player minus by 1 and remove the enemy object from the list and if the list reaches 0, enemies respawn
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(player_laser_vel, enemies)

def main_menu():
    title_font1 = pygame.font.SysFont("comicsansms", 50)
    title_font2 = pygame.font.SysFont("comicsansms", 50)
    title_font3 = pygame.font.SysFont("comicsansms", 40)
    run = True
    while run: #while run is true
        WIN.blit(BG,(0,0))
        title_label = title_font1.render("THE PEW PEW GAME OF", 1, (0,255,0))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        title_label = title_font2.render("PICKLED DICK-BUTT RICK", 1, (0,255,0))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 400))
        title_label = title_font3.render("Created by KIM RUI", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 470))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
