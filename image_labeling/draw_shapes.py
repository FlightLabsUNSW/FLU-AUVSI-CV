
import cv2 as cv
import numpy as np
import os

colour_defs = {
    'white':(255,255,255),
    'black':(0,0,0),
    'gray':(256/2,256/2,256/2),
    'red':(0,0,255),
    'blue':(255,0,0),
    'green':(0,255,0),
    'yellow':(0,245,245),
    'purple':(125,0,125),
    'brown':(0,0,0),
    'orange':(0,0,0)
    }

possible_chars = [
    'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
    '0','1','2','3','4','5','6','7','8','9'
    ]


def draw_circle(bg_img, colour):
    centre = (int(bg_img.shape[0]/2), int(bg_img.shape[1]/2))
    radius = min(centre)
    cv.circle(bg_img, centre, radius, colour, cv.FILLED)

def draw_semicircle(bg_img, colour):
    centre = (int(bg_img.shape[0]/2), int(3*bg_img.shape[1]/4))
    radius = min(int(bg_img.shape[0]/2), int(bg_img.shape[1]/2))
    cv.circle(bg_img, centre, radius, colour, cv.FILLED)
    cv.rectangle(bg_img, (0,centre[1]), bg_img.shape[:2], (255,255,255,255), cv.FILLED)

def draw_quarter_circle(bg_img, colour):
    centre = (0, bg_img.shape[1])
    radius = min(bg_img.shape[:2])
    cv.circle(bg_img, centre, radius, colour, cv.FILLED)

def draw_triangle(bg_img, colour):
    pass

def draw_square(bg_img, colour):
    centre = (int(bg_img.shape[0]/2), int(bg_img.shape[1]/2))
    cv.rectangle(bg_img, (0,0), bg_img.shape[:2], colour, cv.FILLED)

def draw_rectangle(bg_img, colour):
    centre = (int(bg_img.shape[0]/2), int(bg_img.shape[1]/2))
    top_left = (0, int(bg_img.shape[1]/4))
    bottom_right = (bg_img.shape[0], int(3*bg_img.shape[1]/4))
    cv.rectangle(bg_img, top_left, bottom_right, colour, cv.FILLED)

def draw_trapezoid(bg_img, colour):
    pass

def draw_pentagon(bg_img, colour):
    pass

def draw_hexagon(bg_img, colour):
    pass

def draw_heptagon(bg_img, colour):
    pass

def draw_octagon(bg_img, colour):
    pass

def draw_star(bg_img, colour):
    pass

def draw_cross(bg_img, colour):
    pass

possible_shapes = [
    draw_circle,
    draw_semicircle,
    draw_quarter_circle,
    draw_triangle,
    draw_square,
    draw_rectangle,
    draw_trapezoid,
    draw_pentagon,
    draw_hexagon,
    draw_heptagon,
    draw_octagon,
    draw_star,
    draw_cross
    ]


shape_img = np.ones((450,450,4), np.uint8)*255
draw_quarter_circle(shape_img, (0,0,0))
print(shape_img.shape)
print(shape_img[225,225])
cv.imshow('img', shape_img)
cv.waitKey(0)
cv.destroyAllWindows()

