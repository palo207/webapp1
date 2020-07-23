# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 20:21:25 2020

@author: pavol
"""

import os
import cv2

x=250
y=150
color=(255,0,0)
thickness=-1
radius = 20
filename="layout1.jpg"

directory_path = os.path.dirname(__file__)
file_path = os.path.join(directory_path, "static/layout.jpg")
new_filepath = os.path.join(directory_path, "static/layout1.jpg")
img=cv2.imread(file_path)
img1=cv2.circle(img,(x,y),radius,color,thickness)
cv2.imwrite(new_filepath, img1)
