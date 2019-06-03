
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
    pad_y = (1/2-(1/4)*3**(1/2))*bg_img.shape[1]
    p1 = (int(bg_img.shape[0]/2), pad_y)
    p2 = (bg_img.shape[0], bg_img.shape[1]-pad_y)
    p3 = (0, bg_img.shape[1]-pad_y)
    pts_in = np.array([[p1,p2,p3]], dtype=np.int32)
    cv.polylines(bg_img, pts=pts_in, isClosed=False, color=colour)
    cv.fillPoly(bg_img, pts=pts_in, color=colour)

def draw_square(bg_img, colour):
    centre = (int(bg_img.shape[0]/2), int(bg_img.shape[1]/2))
    cv.rectangle(bg_img, (0,0), bg_img.shape[:2], colour, cv.FILLED)

def draw_rectangle(bg_img, colour):
    top_left = (0, int(bg_img.shape[1]/4))
    bottom_right = (bg_img.shape[0], int(3*bg_img.shape[1]/4))
    cv.rectangle(bg_img, top_left, bottom_right, colour, cv.FILLED)

def draw_trapezoid(bg_img, colour):
    top_left = (int(bg_img.shape[0]/4), int(bg_img.shape[1]/4))
    top_right = (int(3*bg_img.shape[0]/4), bg_img.shape[1]/4)
    bottom_right = (bg_img.shape[0], int(3*bg_img.shape[1]/4))
    bottom_left = (0, int(3*bg_img.shape[1]/4))
    pts_in = np.array([[top_left,top_right,bottom_right,bottom_left]], dtype=np.int32)
    cv.polylines(bg_img, pts=pts_in, isClosed=False, color=colour)
    cv.fillPoly(bg_img, pts=pts_in, color=colour)


def draw_pentagon(bg_img, colour):
    p1 = 225,0
    p2 = 11,155
    p3 = 93,407
    p4 = 357,407
    p5 = 439,155
    pts_in = np.array([[p1,p2,p3,p4,p5]], dtype=np.int32)
    cv.polylines(bg_img, pts=pts_in, isClosed=False, color=colour)
    cv.fillPoly(bg_img, pts=pts_in, color=colour)
    

def draw_hexagon(bg_img, colour):
    p1 = 225,0
    p2 = 30,112
    p3 = 30,337
    p4 = 225,450
    p5 = 420,338
    p6 = 420,113
    pts_in = np.array([[p1,p2,p3,p4,p5,p6]], dtype=np.int32)
    cv.polylines(bg_img, pts=pts_in, isClosed=False, color=colour)
    cv.fillPoly(bg_img, pts=pts_in, color=colour)

def draw_heptagon(bg_img, colour):
    p1 = 225,0
    p2 = 49,85
    p3 = 6,275
    p4 = 127,428
    p5 = 323,428
    p6 = 444,275
    p7 = 401,85
    pts_in = np.array([[p1,p2,p3,p4,p5,p6,p7]], dtype=np.int32)
    cv.polylines(bg_img, pts=pts_in, isClosed=False, color=colour)
    cv.fillPoly(bg_img, pts=pts_in, color=colour)

def draw_octagon(bg_img, colour):
    p1 = 225,0
    p2 = 66,66
    p3 = 0,225
    p4 = 66,384
    p5 = 225,450
    p6 = 384,384
    p7 = 450,225
    p8 = 384,66
    pts_in = np.array([[p1,p2,p3,p4,p5,p6,p7,p8]], dtype=np.int32)
    cv.polylines(bg_img, pts=pts_in, isClosed=False, color=colour)
    cv.fillPoly(bg_img, pts=pts_in, color=colour)

def draw_star(bg_img, colour):
    pass

def draw_cross(bg_img, colour):
    vert_top_left = (int(bg_img.shape[0]/4), 0)
    vert_bottom_right = (int(3*bg_img.shape[0]/4), bg_img.shape[1])
    cv.rectangle(bg_img, vert_top_left, vert_bottom_right, colour, cv.FILLED)


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
print(shape_img.shape)
print(shape_img[225,225])
draw_cross(shape_img, (0,0,0))
cv.imshow('img', shape_img)
cv.waitKey(0)
cv.destroyAllWindows()

