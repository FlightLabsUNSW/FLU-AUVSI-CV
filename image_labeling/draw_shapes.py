
import cv2 as cv
import numpy as np
import os
import json

colour_defs = {
    'white':(255,255,255),
    'black':(0,0,0),
    'gray':(256/2,256/2,256/2),
    'red':(0,0,255),
    'blue':(255,0,0),
    'green':(0,255,0),
    'yellow':(0,245,245),
    'purple':(125,0,125),
    'brown':(165,42,42),
    'orange':(255,165,0)
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
    radius = int(6*450/7)
    centre = (int(bg_img.shape[0]/2 - 4/(3*np.pi)*radius), int(bg_img.shape[1]/2 + 4/(3*np.pi)*radius))
    cv.circle(bg_img, centre, radius, colour, cv.FILLED)
    p1 = (0,0)
    p2 = (centre[0], bg_img.shape[1])
    cv.rectangle(bg_img, p1, p2, (255,255,255,255), cv.FILLED)
    p1 = (0,centre[1])
    p2 = (bg_img.shape[0],bg_img.shape[1])
    cv.rectangle(bg_img, p1, p2, (255,255,255,255), cv.FILLED)

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

def coord_dist(x1,y1,x2,y2):
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)

def draw_star(bg_img, colour):
    numberOfPoints = 5
    rotationAngle = -np.pi/2
    xCenter = bg_img.shape[0]/2
    yCenter = bg_img.shape[1]/2

    start = 0.0
    stop = (numberOfPoints-1)*np.pi
    step = (numberOfPoints-1)/numberOfPoints*np.pi
    # Determine the angles that the arm tips are at
    theta = np.arange(start, stop, step) + rotationAngle;
    # Define distance from the arm tip to the center of star.
    amplitude = min(bg_img.shape[0]/2, bg_img.shape[1]/2)
    # Get x and y coordinates of the arm tips.
    x = np.multiply(amplitude , np.cos(theta)) + xCenter
    y = np.multiply(amplitude , np.sin(theta)) + yCenter
    star_pts = np.array([[(int(x[i]), int(y[i])) for i in range(min(len(x),len(y)))]], dtype=np.int32)
    pts_in = []
    star_pts = star_pts.tolist()[0]
    #print(star_pts)
    for index,val in enumerate(star_pts):
        i1 = index
        i2 = (index+1)%5
        i3 = (index+4)%5
        #print(pts_in)
        p1 = val
        p2 = star_pts[i2]
        p3 = (int(bg_img.shape[0]/2), int(bg_img.shape[1]/2))
        p4 = star_pts[i3]
        #p2 = [0,0]
        #dist = coord_dist(*val, *star_pts[i2])
        #print(*val, *star_pts[i3], dist)
        #dist = 0
        #ang = 180-54+theta[index]
        #p2[0] = star_pts[i2][0] + np.cos(ang*(180/np.pi))*dist
        #p2[1] = star_pts[i2][1] + np.sin(ang*(180/np.pi))*dist

        #p3 = [0,0]
        #dist = coord_dist(*val, *star_pts[i3])
        #print(*val, *star_pts[i3], dist)
        #dist = 0
        #ang = 54+theta[index]
        #p3[0] = star_pts[i3][0] + np.cos(ang*(180/np.pi))*dist
        #p3[1] = star_pts[i3][1] + np.sin(ang*(180/np.pi))*dist
        rot_triangle = np.array([[p1, p2, p3, p4]], dtype=np.int32)
        cv.polylines(bg_img, pts=rot_triangle, isClosed=False, color=colour)
        cv.fillPoly(bg_img, pts=rot_triangle, color=colour)

        pts_in.append(rot_triangle)
        
    pts_in = np.array(pts_in)
    #print(pts_in)
    #cv.polylines(bg_img, pts=pts_in, isClosed=False, color=colour)
    #cv.fillPoly(bg_img, pts=pts_in, color=colour)

def draw_cross(bg_img, colour):
    vert_top_left = (int(bg_img.shape[0]/4), 0)
    vert_bottom_right = (int(3*bg_img.shape[0]/4), bg_img.shape[1])
    cv.rectangle(bg_img, vert_top_left, vert_bottom_right, colour, cv.FILLED)
    hori_top_left = (0, int(bg_img.shape[1]/4))
    hori_bottom_right = (bg_img.shape[0], int(3*bg_img.shape[1]/4))
    cv.rectangle(bg_img, hori_top_left, hori_bottom_right, colour, cv.FILLED)

def draw_alphanum(bg_img, colour, letter):
    font = cv.FONT_HERSHEY_DUPLEX
    thickness = 10
    pixel_size = (int(bg_img.shape[0]/4), int(bg_img.shape[1]/4))
    try:
        font_scale = cv.getFontScaleFromHeight(font, pixel_size[1], thickness)
    except AttributeError as err:
        font_scale = 5.071428571428571

    font_size, ret = cv.getTextSize(letter, font, font_scale, thickness)
    textX = int((bg_img.shape[1] - font_size[0]) / 2)
    textY = int((bg_img.shape[0] + font_size[1]) / 2)
    
    cv.putText(bg_img, letter, (textX, textY), font, font_scale, colour, thickness)
    bottom_left = (textX, textY)
    top_right = (textX+font_size[0], textY-font_size[1])
    return (*bottom_left, *top_right)

possible_shapes = {
    'circle':draw_circle,
    'semicircle':draw_semicircle,
    'quarter_circle':draw_quarter_circle,
    'triangle':draw_triangle,
    'square':draw_square,
    'rectangle':draw_rectangle,
    'trapezoid':draw_trapezoid,
    'pentagon':draw_pentagon,
    'hexagon':draw_hexagon,
    'heptagon':draw_heptagon,
    'octagon':draw_octagon,
    'star':draw_star,
    'cross':draw_cross
    }


for alpha_i, alphanum in enumerate(possible_chars):
    with open('flu_oldcs.names', 'a') as classfile:
        classfile.write(alphanum+'\n')

#out_dir = 'flu_odlcs'
#out_path = os.path.join(os.getcwd(), out_dir)
#img_num = 0
#for shape, func in possible_shapes.items():
#    for alpha_i, alphanum in enumerate(possible_chars):
#        for colour_name1, shape_colour in colour_defs.items():
#            for colour_name2, letter_colour in colour_defs.items():
#                if colour_name1 != colour_name2:
#                    shape_img = np.ones((450,450,4), np.uint8)*255
#                    func(shape_img, shape_colour)
#                    alpha_pos = draw_alphanum(shape_img,letter_colour, alphanum)
#                    meta_dict = {
#                            'alpha_num':alphanum,
#                            'class_id':alpha_i,
#                            'alpha_colour':colour_name2,
#                            'shape':shape,
#                            'shape_colour':colour_name1,
#                            'icdar_text':{
#                                'xy1':(alpha_pos[0],alpha_pos[3]),
#                                'xy2':(alpha_pos[2],alpha_pos[3]),
#                                'xy3':(alpha_pos[0],alpha_pos[1]),
#                                'xy4':(alpha_pos[2],alpha_pos[1])
#                                },
#                            'yolo_spot':{
#                                'x_center':shape_img.shape[0]/2,
#                                'y_center':shape_img.shape[1]/2,
#                                'width':shape_img.shape[0],
#                                'height':shape_img.shape[1]
#                                }
#                            }
#                    #for key,val in meta_dict['icdar_text'].items():
#                    #    cv.drawMarker(shape_img, val, colour_defs['white'])
#                    #cv.imshow('img', shape_img)
#                    #cv.waitKey(0)
#                    #invert alpha channel
#                    shape_img[:,:,-1] = -shape_img[:,:,-1]+255
#                    cv.imwrite(os.path.join(out_path, str(img_num)+'.png'), shape_img)
#                    file_path = os.path.join(out_path, str(img_num)+'.txt')
#                    with open(file_path, 'w') as meta_file:
#                        json.dump(meta_dict, meta_file)
#                    img_num += 1
#cv.destroyAllWindows()

