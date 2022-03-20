# 5 March 2022
# Lucas Wirz-Vitiuk
# Code to generate randomised art

# Import libraries
import os
import pygame
import time
from gpiozero import Servo
import RPi.GPIO as GPIO
from gpiozero.pins.pigpio import PiGPIOFactory
import random as rnd

# Initiate factory to trigger the actuator properly
factory = PiGPIOFactory()

# Define function for both endswitches
def endswitch(channel):
    global direction
    print('Switch was pushed')
    actuator.mid()
    time.sleep(0.5)
    if direction == 2:
        direction = 1
    if direction == 3:
        direction = 0
    print('Servo stopped')

# Define conditions to quit (only via keyboard)
def switch_off():
    GPIO.output(backgroundlight, 0)
    actuator.mid()
    time.sleep(0.5)
    print('Servo stopped')
    actuator.value = None
    GPIO.cleanup()
    print('Turn off')

# Define how to create art
def create_art():
    
    # Create empty dictionary for all random points
    dots = {'x': [], 'y': []}

    # Randomly decide how many lines to draw
    lines = rnd.randint(3, 11)

    # Generate random points inside canvas (with defined border) 
    for i in range(lines):
        dots['x'].append(rnd.randint(5, window_x - 5))
        dots['y'].append(rnd.randint(5, window_y - 5))

    # Draw every line individually
    for j in range(lines):

        # Last line connects to the first point
        if j == lines - 1:
            k = 0
        else:
            k = j + 1

        # Draw line (black) and update the canvas
        pygame.draw.line(
            screen,
            0x000000,
            (dots['x'][j], dots['y'][j]),
            (dots['x'][k], dots['y'][k]),
            2
        )
        pygame.display.update()
        time.sleep(1)

    # Wait a little longer before coloring
    time.sleep(1.5)

    # Initiate color
    color = pygame.Color(0, 0, 0)
    # Randomly set HSVA to everything but white (or too bright colors)
    color.hsva = (rnd.randint(0, 360), rnd.randint(50, 100), rnd.randint(50, 100), 100)

    # Draw colored polygon (random color from above)
    pygame.draw.polygon(
        screen,
        color,
        list(zip(dots['x'], dots['y'])),
        0
    )

    # Draw outlines again (black)
    pygame.draw.polygon(
        screen,
        0x000000,
        list(zip(dots['x'], dots['y'])),
        2
    )

    # Update canvas to show final drawing
    pygame.display.update()

# Function to shutdown the Raspberry Pi properly
def shutdown(timer):
    print("Shutting down")
    text = font.render('ART OVER' , True, (255, 0, 0))
    rect = text.get_rect(center=screen.get_rect().center)
    screen.blit(text, rect)
    pygame.display.update()
    switch_off()
    pygame.quit()
    time.sleep(5)
    os.system("sudo shutdown -h now")

# Define pins
servopin = 12
switch = 7
breaker = 13
backgroundlight = 22

# Initiate direction (0 = horizontally, 1 = vertically)
direction = 0

# Set GPIO to use pin numbers
GPIO.setmode(GPIO.BOARD)

# Setup pins for buttons and LEDs
GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(breaker, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(backgroundlight, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)

# Setup events for buttons
GPIO.add_event_detect(switch, GPIO.RISING, callback=endswitch, bouncetime=500)
GPIO.add_event_detect(breaker, GPIO.RISING, callback=shutdown, bouncetime=500)

# Initiate the actuator
actuator = Servo(servopin, pin_factory=factory)
time.sleep(0.5)

# Define the screen resolution and the size of the canvas (considering mat)
resolution_x, resolution_y = 1280, 1024
window_x, window_y = 640, 512

# Center the canvas
pos_x, pos_y = int((resolution_x - window_x)/2), int((resolution_y - window_y)/2)
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{pos_x},{pos_y}"

# Initiate pygame with white canvas
pygame.init()
screen = pygame.display.set_mode((window_x, window_y), pygame.NOFRAME)
font = pygame.font.Font(pygame.font.get_default_font(), 36)
screen.fill((255, 255, 255))
pygame.display.flip()

# Initiate cooldown for turning off the backlight LEDs
cooldown = pygame.time.get_ticks()

# Starting repeating part
print('Go!')
while True:
    
    # Set ticks
    now = pygame.time.get_ticks()

    # Waiting for a button to be pushed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            switch_off()
            exit()
        if event.type == pygame.KEYDOWN:
            
            # Quit the scrypt with escape (only via keyboard)
            if event.key == pygame.K_ESCAPE:
                switch_off()
                pygame.quit()
                exit()

            # Shutdown the Raspberry Pi properly when E is pressed
            if event.key == pygame.K_e:
                print('E')
                shutdown(50)
                exit()

            # Start when Art Button is pushed
            if event.key == pygame.K_SPACE:
                print('Button pushed')

                # Turn on LEDs if they are not running yet
                GPIO.output(backgroundlight, 1)

                # Randomly change the orientation
                change_orientation = rnd.randint(0, 1)
                if change_orientation:
                    
                    # Draw a 3/4 circle for both arrows 
                    pygame.draw.circle(
                        screen,
                        0x000000,
                        [int(window_x/2), int(window_y/2)],
                        75,
                        6
                    )
                    pygame.draw.rect(
                        screen,
                        0xFFFFFF,
                        (int(window_x/2), int(window_y/2), 82, 82)
                    )

                    # Change orientation depending on the orientation before
                    if direction == 0:
                        direction = 2

                        # Draw arrow anti-clockwise and update canvas
                        pygame.draw.line(
                            screen,
                            0x000000,
                            (int(window_x/2), int(75 + (window_y/2) - 3)),
                            (int((window_x/2) - 15), int(75 + (window_y/2) - 15 - 3)),
                            6
                        )
                        pygame.draw.line(
                            screen,
                            0x000000,
                            (int(window_x/2), int(75 + (window_y/2) - 3)),
                            (int((window_x/2) - 15), int(75 + (window_y/2) + 15 - 3)),
                            6
                        )
                        pygame.display.update()

                        # Slowly start actuator to turn anti-clockwise
                        for x in range(1, 51):
                            actuator.value = -1*((x**2)/5000)
                            time.sleep(0.015)
                        print('Turn anti-clockwise')

                    # Other orientation
                    if direction == 1:
                        direction = 3

                        # Draw arrow clockwise and update canvas
                        pygame.draw.line(
                            screen,
                            0x000000,
                            (int(75 + (window_x/2) - 3), int(window_y/2)),
                            (int(75 + (window_x/2) + 15 - 3), int((window_y/2) - 15)),
                            6
                        )
                        pygame.draw.line(
                            screen,
                            0x000000,
                            (int(75 + (window_x/2) - 3), int(window_y/2)),
                            (int(75 + (window_x/2) - 15 - 3), int((window_y/2) - 15)),
                            6
                        )
                        pygame.display.update()

                        # Slowly start actuator to turn clockwise
                        for x in range(1, 51):
                            actuator.value = (x**2)/5000
                            time.sleep(0.015)
                        print('Turn clockwise')

                    # Timer to show the arrows and turn
                    time.sleep(4)

                    # Delete the arrows
                    screen.fill((255, 255, 255))
                    pygame.display.update()

                # Print output to recognise no movement
                else:
                    print('Stay in position')

                # Wait before creating art
                time.sleep(1)
                
                # Start function to create art
                create_art()

                # Timer to show the artwork
                time.sleep(11)

                # Delete the artwork
                screen.fill((255, 255, 255))
                pygame.display.update()
                time.sleep(1)

                # Print a randomised message on the canvas
                adjective = ['TEMPORARY', 'RANDOM', 'ABSTRACT', 'UNIQUE']
                text = font.render('this ART is ' + adjective[rnd.randint(0, 3)], True, (0, 0, 0))
                if direction == 1:
                    text = pygame.transform.rotate(text, 90)
                rect = text.get_rect(center=screen.get_rect().center)
                screen.blit(text, rect)
                pygame.display.update()

                # Timer to read the message
                time.sleep(5)

                # Delete the message
                screen.fill((255, 255, 255))
                pygame.display.update()

                # Reset cooldown
                cooldown = pygame.time.get_ticks()
                
                # Clear cached inputs (to only start again if the button is pushed from now)
                pygame.event.clear()
                print('Go again!')

    # Turn off the background LEDs if there is no input anymore
    if now - cooldown >= 15000:
        print('No input, lights off')
        GPIO.output(backgroundlight, 0)

    # Restrict the requests if there is no input
    time.sleep(0.5)

# End of the ArtScript
