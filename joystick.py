"""
Mecanum wheel control by joystick
Using MODBUS-ASCII protocol
python 3.8
winxos 20191231
"""
import pygame
import socket
import binascii


ADDR = ("192.168.0.106", 10001)  # your esp32 ip address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp socket


def create_cmd(reg, x1):
    """
    Modbus Ascii protocol frame builder
    :param reg: Modbus Register address
    :param x1: value
    :return: Modbus Ascii frame
    """
    c = bytearray([1, 6, 0, reg, 0, 0])
    #  Modbus value have 2 bytes, i use the first byte as positive and the second byte as negative
    if x1 > 0:
        c[4] = x1
    else:
        c[5] = -x1
    x = sum(c) % 256
    #  x is LRC check
    if x == 0:
        c.append(0)
    else:
        c.append(256 - x)
    return f":{binascii.b2a_hex(c).decode()}\r\n"


# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputting the
# information.
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def print(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


pygame.init()

# Set the width and height of the screen [width,height]
size = [400, 200]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("My Game")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()

# Get ready to print
textPrint = TextPrint()

# -------- Main Program Loop -----------
while done == False:
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        if event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")
    screen.fill(WHITE)
    textPrint.reset()

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()
    if joystick_count > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        name = joystick.get_name()
        textPrint.print(screen, "Joystick name: {}".format(name))
        axes = joystick.get_numaxes()
        textPrint.print(screen, "Number of axes: {}".format(axes))
        textPrint.indent()
        for i in range(axes):
            axis = joystick.get_axis(i)
            textPrint.print(screen, "Axis {} value: {:>6.3f}".format(i, axis))
        textPrint.unindent()

        vx = joystick.get_axis(0)
        vy = joystick.get_axis(1)
        vz = joystick.get_axis(4)
        if abs(vx) > 0.2 or abs(vy) > 0.2 or abs(vz) > 0.2:
            if abs(vx) < 0.2:
                vx = 0
            if abs(vy) < 0.2:
                vy = 0
            # spd is your 4 motor's speed, the +- sign depends on your wheel install type and motor direct,
            # you may need to read some article about Mecanum wheel to handler it.
            spd = [vx + vy + vz, vx - vy - vz, vx + vy - vz, vx - vy + vz]
            print(f"{vx:.2f} {vy:.2f} {vz:.2f}")
            for j in range(4):
                t = int(spd[j] * 250)
                if t > 255:
                    t = 255
                if t < -255:
                    t = -255
                #  constrict the speed to range [-255,255]
                s.sendto(create_cmd(j, t).encode(), ADDR)
    pygame.display.flip()
    clock.tick(20)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
