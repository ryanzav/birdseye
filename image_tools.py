'''
Created on Feb 21, 2016

@author: ryanz
'''

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL import ImageEnhance

import time
import string
import os
from PIL.FontFile import WIDTH
from __builtin__ import True
import sys
import git_info
import subprocess

colors = [(77,77,255,255), #bluish
        (230,25,75,255), # red
        (60,180,75,255), # green
        (255,225,25,255), # yellow
        (0,130,200,255), # blue
        (245,130,48,255), #orange
        (145,30,180,255), # purple
        (70,240,240,255), # cyan
        (240,50,230,255), # magenta
        (210,245,60,255), # lime
        (250,190,190,255), # pink
        (0,128,128,255), # teal
        (230,190,255,255), # lavender
        (170,110,40,255), # brown
        (255,250,200,255), # beige
        (128,0,0,255), # maroon
        (170,255,195,255), # mint
        (128,128,0,255), # olive
        (255,215,180,255), # coral
        (0,0,128,255) #navy
        ]

width_fraction = 16
height_fraction = 9

def split(target,pieces=0):      
    imgFile = Image.open(target)
    width, height = imgFile.size

    if pieces == 0:
        for i in range(1,100):
            if i*height*width_fraction/height_fraction > width/i:
                break
        pieces = i + i%2
        
    new_width = round(width/pieces)

    upper_left_x = 0
    upper_left_y = 0
    lower_right_x = new_width
    lower_right_y = height

    filenames = []
    for i in range(pieces):
        sub_box = (upper_left_x,upper_left_y,lower_right_x,lower_right_y)
        region = imgFile.crop(sub_box)
        filename = target[:-4]+ '_' + str(i) + '.png'
        region.save(filename, "PNG")
        filenames.append(filename)

        upper_left_x += new_width
        lower_right_x += new_width

    print '\nSplit into pieces.'
    return filenames
    
def stack(targets):
    images = []
    for target in targets:
        images.append( Image.open(target) )

    width, height = images[0].size
    total_height = len(targets)*height
    combined = Image.new("RGBA", (width, total_height))#,background)
    for i, image in enumerate(images):
        box = (0,i*height,width,(i+1)*height)
        combined.paste(image, box)
    filename = targets[0][:-4]+ '_stacked.png'
    combined.save(filename, "PNG")

    print '\nStack.'
    return filename

def split_then_stack(target,pieces=0):
    files = split(target,pieces)
    stacked = stack(files)
    cleanUp(files)
    return stacked

def overlay(target,text,color,x,y,font_height=40):      
    img = Image.open(target)
    width, height = img.size

    bigHeight = font_height
    bigFont = ImageFont.truetype("Courier Prime Code.ttf", bigHeight)
    drawFile = ImageDraw.Draw(img)
    drawFile.text((x, y),text,color,font=bigFont) # 1/10 from upper left corner
    output_file_name = target[:-4] + '_overlay.png'
    img.save(output_file_name, "PNG")

    print '\nOverlaid.'
    return output_file_name

def getCentered(whole,insert_size):
    remainder = whole - insert_size
    return(remainder/2) 

def getLongest(lines):
    longest = 0
    for line in lines:
        if longest < len(line):
            longest = len(line)
    return longest

def overlayLines(target,lines,line_colors,font_height=None,x=None,y=None):      
    insert_fraction = 3
    img = Image.open(target)
    width, height = img.size

    if font_height == None:
        insert_size = height/insert_fraction
        line_count = len(lines)
        font_height_1 = insert_size/line_count            

        insert_size = width/insert_fraction
        char_count = getLongest(lines)            
        font_height_2 = 2*insert_size/char_count # The height is 2x char width.

        if font_height_1 < font_height_2:
            font_height = font_height_1
        else:
            font_height = font_height_2         
    
    if x == None:
        longest = getLongest(lines)
        insert_width = longest * font_height/2
        x = getCentered(width, insert_width)

    if y == None:
        line_count = len(lines)
        insert_height = line_count * font_height
        y = getCentered(height, insert_height)

    bigHeight = font_height
    bigFont = ImageFont.truetype("Courier Prime Code.ttf", bigHeight)
    drawFile = ImageDraw.Draw(img)
    LINE_OFFSET = bigHeight
    offset = 0
    for i,line in enumerate(lines):
        drawFile.text((x, y + offset),line,line_colors[i],font=bigFont) # 1/10 from upper left corner
        offset += LINE_OFFSET
    output_file_name = target[:-4] + '_overlay_lines.png'
    img.save(output_file_name, "PNG")

    print '\nOverlaid.'
    return output_file_name    

def rename(f,new): 
    cmd = "mv " + f + " " + new
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output

def openImage(f): 
    cmd = "open " + f
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output

def cleanUp(files):
    if type(files) != list:
        files = [files]
    for f in files:
        cmd = "rm " + f
        try:
            response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        except subprocess.CalledProcessError as e:
            print e.output

if __name__ == '__main__':
    target = "birdseye-example.png"

    text = []
    line_colors = []
    text.append('Line 1')
    line_colors.append(colors[0])
    text.append('Line 2')
    line_colors.append(colors[1])
    text.append('Line 3')
    line_colors.append(colors[2])
    output_file_name_1 = overlayLines(target,text,line_colors)
    openImage(output_file_name_1)    

    output_file_name_2 = overlay(target,text[0],line_colors[0],100,10)
    openImage(output_file_name_2)   

    stacked = split_then_stack(target,3)
    openImage(stacked)    
    time.sleep(3)
    cleanUp(output_file_name_1)
    cleanUp(output_file_name_2)
    cleanUp(stacked)
    
