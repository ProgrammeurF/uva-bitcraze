import time
import math

def motionless_flight(distance:int=0, height:int=0.0, speed:int=0.0):
    time.sleep(5)


def static_flight(pc, distance:int= 1.5, height:int=0.5, speed:int=0.2):
    """
    Static flight for 30 seconds at height metres
    """
    pc.go_to(0.0, 0.0, height) 
    time.sleep(30)


def linearx_flight(pc, distance:int= 1.5, height:int=1.0, speed:int=0.2):
    """
    Dynamic flight: rise, fly backward, fly forward, land.
    """
    # RISE
    pc.go_to(0.0, 0.0, height) 
    time.sleep(0.5)

    # GO BACK
    pc.go_to(-distance, 0.0, height) 

    # GO FORWARD
    pc.go_to(distance, 0.0, height) 

    # RETURN
    time.sleep(0.5)
    pc.go_to(0.0, 0.0, height) 

    
def lineary_flight(pc, distance:int= 1.5, height:int=1.0, speed:int=0.2):
    """
    Dynamic flight: rise, fly left, fly right, land.
    """
    # RISE
    pc.go_to(0.0, 0.0, height) 
    time.sleep(0.5)

    # GO FORWARD
    pc.go_to(0.0, distance, height) 

    # GO BACK
    pc.go_to(0.0, -distance, height) 

    # RETURN
    time.sleep(0.5)
    pc.go_to(0.0, 0.0, height) 


def linearxy_flight(pc, distance:int= 1.5, height:int=1.0, speed:int=0.2):
    """
    Dynamic flight: rise, fly topleft fly bottomright, land.
    """
    # RISE
    pc.go_to(0.0, 0.0, height) 
    time.sleep(0.5)

    # GO FORWARD
    pc.go_to(distance, distance, height) 

    # GO BACK
    pc.go_to(-distance, -distance, height) 

    # RETURN
    time.sleep(0.5)
    pc.go_to(0.0, 0.0, height) 


def square_flight(pc, distance:int=1.5, height:int=1.0, speed:int=0.2):
    """
    Square flight: make a square
    """
    # rise up
    pc.go_to(distance, 0.0, height) 
    time.sleep(0.5)

    # go to top right corner
    pc.go_to(distance, -distance, height) 

    # go to bottom right corner
    pc.go_to(-distance, -distance, height) 

    # go to bottom left corner
    pc.go_to(-distance, distance, height) 

    # go to top left corner
    pc.go_to(distance, distance, height) 

    # go to original position
    pc.go_to(distance, 0.0, height) 

    # RETURN
    time.sleep(0.5)
    pc.go_to(0.0, 0.0, height) 
    

def circle_flight(pc, distance: float = 1.5, height: float = 0.5, speed: float = 0.2):
    """
    Circle flight around (0,0) at a constant height.
    """
    rad = distance 
    steps = 40
    
    # calculate needed time for circle for speed
    circumference = 2 * math.pi * rad
    total_time = circumference / speed
    time_per_step = total_time / steps

    pc.go_to(rad, 0.0, height)
    time.sleep(1.5)
    
    # move step for circle
    for i in range(steps + 1):
        angle = (2 * math.pi / steps) * i
        x = rad * math.cos(angle)
        y = rad * math.sin(angle) 
        pc._cf.high_level_commander.go_to(x, y, height, 0, time_per_step, relative=False)
        time.sleep(time_per_step)

    pc.go_to(0.0, 0.0, height)
    time.sleep(1)


def helix_flight(pc, distance:float=1.5, height:float=0.5, speed:float=0.2):
    """
    Helix flight around (0,0). 
    Enforces the exact YAML speed by utilizing the high_level_commander with calculated step durations.
    """
    rad = distance
    steps = 40

    # calculates time steps
    circumference = 2 * math.pi * rad
    total_time = circumference / speed
    time_step = total_time / steps

    # calculates height steps
    max_height = 2.0
    h_steps = (max_height - height) / (steps // 2)
    
    h = height
    pc.go_to(rad, 0.0, h)
    time.sleep(1)
    
    for i in range(steps + 1):
        # computes new z
        if i < (steps//2):
            h += h_steps
        elif i > (steps//2) and h > height:
            h -= h_steps
            
        # changes new x, y
        angle = (2 * math.pi / steps) * i
        x = rad * math.cos(angle)
        y = rad * math.sin(angle) 
        
        pc._cf.high_level_commander.go_to(x, y, h, 0, time_step, relative=False)
        
        time.sleep(time_step)

    pc.go_to(0.0, 0.0, height)
    time.sleep(1)


def staircasex_flight(pc, distance:int= 1.5, height:int=0.5, speed:int=0.2):
    max_height = 2.0
    max_distance = distance * 2
    staircase_steps = 4

    # computes stepsize
    h_steps = (max_height - height) / staircase_steps
    d_steps = max_distance / staircase_steps
    
    pc.go_to(0.0, 0.0, height) 
    time.sleep(0.5)

    # start staircase
    d = -distance
    pc.go_to(d, 0.0, height) 

    d += d_steps
    pc.go_to(d, 0.0, height) 

    height += h_steps
    pc.go_to(d, 0.0, height) 

    d += d_steps
    pc.go_to(d, 0.0, height) 

    height += h_steps
    pc.go_to(d, 0.0, height) 

    d += d_steps
    pc.go_to(d, 0.0, height) 

    height += h_steps
    pc.go_to(d, 0.0, height) 

    time.sleep(0.5)

    # return
    pc.go_to(0, 0) 



def turn_flight(pc, distance:int= 1.5, height:int=0.5, speed:int=0.2):
    pc._cf.high_level_commander.go_to(0.0, 0.0, height, 0, 2.0, relative=False)
    time.sleep(2)
    pc._cf.high_level_commander.go_to(0.0, 0.0, height, 180, 2.0, relative=False)
    time.sleep(2)
    pc._cf.high_level_commander.go_to(0.0, 0.0, height, 0, 2.0, relative=False)
    # time.sleep(2)
    # pc._cf.high_level_commander.go_to(0.0, 0.0, height, 270, 2.0, relative=False)
    # time.sleep(2)
    # pc._cf.high_level_commander.go_to(0.0, 0.0, height, 360, 2.0, relative=False)
    time.sleep(2)


def up_flight(pc, distance:int= 1.5, height:int=0.5, speed:int=0.2):
    start_height = 0.3

    h = start_height
    while h <= 2.5:
        pc.go_to(0.5, 0.5, h) 
        h += 0.1
        time.sleep(0.3)


