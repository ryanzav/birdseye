'''
Created on Feb 21, 2016

@author: ryanz
'''

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL import ImageEnhance
from PIL import ImageFilter

import time
import string
import os
from PIL.FontFile import WIDTH
from __builtin__ import True
import sys
import git_info
import subprocess

colors = [
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

darkblue = (0,0,40,255)
transparent = (0,0,0,0)
background = darkblue

width_fraction = 16
height_fraction = 9

def separate(target,pieces=0):      
    imgFile = Image.open(target)
    width, height = imgFile.size

    if pieces == 0:
        for i in range(1,100):
            if i*width*height_fraction/width_fraction > height/i:
                break
        pieces = i + i%2
        
    new_height = round(height/pieces)

    upper_left_x = 0
    upper_left_y = 0
    lower_right_x = width
    lower_right_y = new_height

    filenames = []
    for i in range(pieces):
        sub_box = (upper_left_x,upper_left_y,lower_right_x,lower_right_y)
        region = imgFile.crop(sub_box)
        filename = target[:-4]+ '_' + str(i) + '.png'
        region.save(filename, "PNG")
        filenames.append(filename)

        upper_left_y += new_height
        lower_right_y += new_height
    return filenames

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
    return filename

def pile(targets):
    images = []
    for target in targets:
        if target != '':
            images.append( Image.open(target) )
    
    max_width = 0
    total_height = 0
    for image in images:
        width,height = image.size
        if width > max_width:
            max_width = width    
        total_height += height
            
    total_width = max_width
    piled = Image.new("RGBA", (total_width, total_height))
    x_offset = 0
    for i, image in enumerate(images):
        width,height = image.size
        box = (0,x_offset,width,x_offset + height)
        piled.paste(image, box)
        x_offset += height
    filename = targets[0][:-4]+ '_piled.png'
    piled.save(filename, "PNG")
    return filename


def connect(targets):
    images = []
    for target in targets:
        images.append( Image.open(target) )
    
    max_width = 0
    max_height = 0
    for image in images:
        width,height = image.size
        if width > max_width:
            max_width = width
        if height > max_height:
            max_height = height
            
    total_width = len(targets)*max_width
    total_height = max_height
    combined = Image.new("RGBA", (total_width, total_height),background)
    for i, image in enumerate(images):
        width,height = image.size
        box = (i*width,0,(i+1)*width,height)
        combined.paste(image, box)
    filename = targets[0][:-4]+ '_connected.png'
    combined.save(filename, "PNG")
    return filename

def enhance(targets):
    images = []
    for target in targets:
        images.append( Image.open(target) )
    
    for i, image in enumerate(images):
        enhancer = (ImageEnhance.Color(image))
        image = enhancer.enhance(1.6)
        enhancer = (ImageEnhance.Brightness(image))
        image = enhancer.enhance(2)    
        image.save(target, "PNG")
    return targets

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
    #output_file_name = target[:-4] + '_overlay.png'
    img.save(target, "PNG")
    return target

def getCentered(whole,insert_size):
    remainder = whole - insert_size
    return(remainder/2) 

def getLongest(lines):
    longest = 0
    for line in lines:
        if longest < len(line):
            longest = len(line)
    return longest

def overlayLines(target,lines,line_colors,font_height=None,x=None,y=None, fraction=3):      
    insert_fraction = fraction
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
    
  
    longest = getLongest(lines)
    insert_width = longest * font_height*2/3
    if x == None:
        x = getCentered(width, insert_width)

    line_count = len(lines)
    insert_height = line_count * font_height
    if y == None: 
        y = getCentered(height, insert_height)

    blur(img,x-10,y-10,x+insert_width+10,y+insert_height+10 )

    bigHeight = font_height
    bigFont = ImageFont.truetype("Courier Prime Code.ttf", bigHeight)
    drawFile = ImageDraw.Draw(img)
    LINE_OFFSET = bigHeight
    offset = 0
    for i,line in enumerate(lines):
        drawFile.text((x, y + offset),line,line_colors[i],font=bigFont) # 1/10 from upper left corner
        offset += LINE_OFFSET
    #output_file_name = target[:-4] + '_overlay_lines.png'
    img.save(target, "PNG")
    return target    


def copy(f,new): 
    cmd = "cp " + f + " " + new
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output
    return new

def rename(f,new): 
    cmd = "mv " + f + " " + new
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output
    return new

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

def makeFolder(folder):
    cmd = "mkdir " + folder
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output

def deleteFolder(folder):
    cmd = "rm -r " + folder
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output

def blur(image,x1,y1,x2,y2):
    box = (x1, y1, x2, y2)
    region = image.crop(box)
    region = region.filter(ImageFilter.BLUR)

    enhancer = ImageEnhance.Brightness(region)
    region = enhancer.enhance(.5)
    image.paste(region, box)
    return image

if __name__ == '__main__':
    target = '2.png'
    results = separate(target)
    for result in results:
        openImage(result)
    exit()
    target = "birdseye-example.png"
    target = copy(target,"output.png")
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
    cleanUp(stacked)
    
