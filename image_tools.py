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
import sys
import git_info
import subprocess
import disk_tools as disk

WAIT_TIME = 1

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

def scale(target,factor):
    imgFile = Image.open(target)
    width, height = imgFile.size
    new_width = int(factor*width)
    new_height = int(factor*height)
    img = imgFile.resize((new_width,new_height), Image.ANTIALIAS)
    img.save(target,"PNG")
    imgFile.close()
    img.close()
    return target


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
        filename = target[:-4] + '_sep_%04d' % i + '.png'
        region.save(filename, "PNG")
        filenames.append(filename)

        upper_left_y += new_height
        lower_right_y += new_height
    imgFile.close()
    return filenames

def make_even(target):      
    imgFile = Image.open(target)
    width, height = imgFile.size
        
    new_height = height - height % 2
    new_width = width - width % 2

    upper_left_x = 0
    upper_left_y = 0
    lower_right_x = new_width
    lower_right_y = new_height

    sub_box = (upper_left_x,upper_left_y,lower_right_x,lower_right_y)
    region = imgFile.crop(sub_box)
    region.save(target, "PNG")
    imgFile.close()
    return target

def pile(targets):
    image = None
    max_width = 0
    total_height = 0
    for target in targets:
        if target != '':
            image = Image.open(target)
            width,height = image.size
            image.close()
            if width > max_width:
                max_width = width    
            total_height += height
            
    total_width = max_width
    piled = Image.new("RGBA", (total_width, total_height))
    x_offset = 0
    for target in targets:
        if target != '':
            image = Image.open(target)
            width,height = image.size
            box = (0,x_offset,width,x_offset + height)
            piled.paste(image, box)
            image.close()
            x_offset += height
    filename = targets[0][:-4]+ '_piled.png'
    piled.save(filename, "PNG")
    return filename

def couple(targets):
    total_width = 0
    for target in targets:
        image = Image.open(target)
        width,height = image.size
        total_width += width
        image.close()
    total_height = height    
    combined = Image.new("RGBA", (total_width, total_height),background)
    for i, target in enumerate(targets):
        image = Image.open(target)
        width,height = image.size
        box = (i*width,0,(i+1)*width,height)
        combined.paste(image, box)
        image.close()
    filename = targets[0][:-4]+ '_coupled.png'
    combined.save(filename, "PNG")
    combined.close()
    return filename

def connect(targets):
    max_width = 0
    max_height = 0
    for target in targets:
        image = Image.open(target)
        width,height = image.size
        if width > max_width:
            max_width = width
        if height > max_height:
            max_height = height
        image.close()
            
    total_width = len(targets)*max_width
    total_height = max_height
    combined = Image.new("RGBA", (total_width, total_height),background)
    for i, target in enumerate(targets):
        image = Image.open(target)
        width,height = image.size
        box = (i*width,0,(i+1)*width,height)
        combined.paste(image, box)
        image.close()
    filename = targets[0][:-4]+ '_connected.png'
    combined.save(filename, "PNG")
    combined.close()
    return filename

def enhance(targets):   
    enhanced = []
    for i, target in enumerate(targets):
        image = Image.open(target)
        enhancer = (ImageEnhance.Color(image))
        image = enhancer.enhance(1.6)
        enhancer = (ImageEnhance.Brightness(image))
        image = enhancer.enhance(2)    
        filename = target[:-4]+ '_enhance_%04d' % i  + str(i) + '.png'
        image.save(filename, "PNG")
        enhanced.append(filename)
        image.close()
    return enhanced

def getCentered(whole,insert_size):
    remainder = whole - insert_size
    return(remainder/2) 

def getLongest(lines):
    longest = 0
    for line in lines:
        if longest < len(line):
            longest = len(line)
    return longest

def overlay(target,text,color,x,y,font_height=40):      
    img = Image.open(target)
    bigHeight = font_height
    bigFont = ImageFont.truetype("Courier Prime Code.ttf", int(bigHeight))
    drawFile = ImageDraw.Draw(img)
    drawFile.text((x, y),text,color,font=bigFont) # 1/10 from upper left corner
    output_file_name = target[:-4] + '_overlay.png'
    img.save(output_file_name, "PNG")
    img.close()
    return output_file_name

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
    bigFont = ImageFont.truetype("Courier Prime Code.ttf", int(bigHeight))
    drawFile = ImageDraw.Draw(img)
    LINE_OFFSET = bigHeight
    offset = 0
    for i,line in enumerate(lines):
        drawFile.text((x, y + offset),line,line_colors[i],font=bigFont) # 1/10 from upper left corner
        offset += LINE_OFFSET
    output_file_name = target[:-4] + '_overlay_lines.png'
    img.save(output_file_name, "PNG")
    img.close()
    return output_file_name    

def blur(image,x1,y1,x2,y2):
    box = (int(x1), int(y1), int(x2), int(y2))
    region = image.crop(box)
    region = region.filter(ImageFilter.BLUR)

    enhancer = ImageEnhance.Brightness(region)
    region = enhancer.enhance(.5)
    image.paste(region, box)
    return image

if __name__ == '__main__':
    target = "example.png"
    results = separate(target)
    for result in results:
        disk.open(result)
    time.sleep(WAIT_TIME)
    disk.cleanUp(results)

    text = []
    line_colors = []
    text.append('Line 1')
    line_colors.append(colors[0])
    text.append('Line 2')
    line_colors.append(colors[1])
    text.append('Line 3')
    line_colors.append(colors[2])
    output_file_name_1 = overlayLines(target,text,line_colors)
    disk.open(output_file_name_1)    
    time.sleep(WAIT_TIME)
    disk.cleanUp(output_file_name_1)

    output_file_name_2 = overlay(target,text[0],line_colors[0],100,10)
    disk.open(output_file_name_2)   
    time.sleep(WAIT_TIME)
    disk.cleanUp(output_file_name_2)

    enhanced = enhance([target])
    for image in enhanced:
        disk.open(image)    
        
    coupled = couple([target,enhanced[0]])
    disk.open(coupled)    

    piled = pile([target,enhanced[0]])
    disk.open(piled)   

    connected = connect([target,enhanced[0]])
    disk.open(connected)   
    
    time.sleep(WAIT_TIME)
    disk.cleanUp(enhanced)
    disk.cleanUp(coupled)
    disk.cleanUp(piled)
    disk.cleanUp(connected)
    
