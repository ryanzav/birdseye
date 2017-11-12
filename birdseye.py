'''
Created on Feb 21, 2016

@author: ryanz
'''

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL import ImageEnhance

import string
import os
from PIL.FontFile import WIDTH

from __builtin__ import True
import sys
import git_info
import image_tools

SOURCE_FOLDER = "." 
#SOURCE_FOLDER = '/Users/ryanz/Desktop/lib-nilon'
SOURCE_FOLDER = '/Users/ryanz/Desktop/devices-nlight-air-sub-ghz'
MAX_FILES = 30000

MAX_TOTAL_HEIGHT = 10000
HORIZONTAL_GAP = 200
hOffset = 40
ROW_OFFSET = 20
COLUMN_OFFSET = HORIZONTAL_GAP
MAX_FOLDER_FILES = MAX_FILES
MAX_TOTAL_WIDTH =1000000 #65000
MAX_TXT_DIMENSION = 6000

bigHeight = 100
titleHeight = 20
charHeight = 3
charWidth = 1
MAX_CHARS = 96
MAX_WIDTH = MAX_CHARS * charWidth
MAX_LINES = 200#500
MAX_HEIGHT = MAX_LINES * charHeight

ROTATION = 0
SCALE_DIV = 1

greenish = (32,200,170,255)
bluish = (77,77,255,255)
black = (0,0,0,255)
white = (255,255,255,255)
darkblue = (0,0,40,255)
transparent = (0,0,0,0)
background = darkblue


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

authors = {}
author_lines = {}

def getAuthorIndex(author):
    global authors
    global author_lines
    first_last = author.split(',')
    if len(first_last) > 1:
        author = first_last[1] + ' ' + first_last[0]
    author = author.strip()
    if author not in authors:
        index = len(authors)
        authors[author] = index
        author_lines[author] = 1
    else:
        author_lines[author] += 1
    return authors[author]

def filterFiles(root, name):
    if 'mirror' in root:
        return False
    if 'TraceRecorder' in root:
        return False 
    if 'mbedtls' in root:
        return False 
    if 'mock' in root or 'mock' in name:
        return False                
    if (name[-3:] == '.md' or name[-2:] == '.c' or name[-3:] == '.py'):
        return True
    else:
        return False

def getAllFiles(targets):
    allFiles = []
    for target in targets:
        for root, dirs, files in os.walk(target, topdown=True):
            files.sort()
            for name in files[:MAX_FOLDER_FILES]: # or name[-2:] == '.h' 
                if filterFiles(root, name):             
                    allFiles.append((os.path.join(root, name)))
                    if len(allFiles) >= MAX_FILES:
                        break
            if len(allFiles)-1 >= MAX_FILES:
                break
    return allFiles

def getMaxLengthInFiles(allFiles):
    maxLengthInFiles = 0
    maxLinesInFiles = 0
    for f in allFiles:
        source = processFile(f)       
        if len(source) > maxLinesInFiles:
            maxLinesInFiles = len(source)
        
        for y, line in enumerate(source):    
            if len(line) > maxLengthInFiles:
                maxLengthInFiles = len(line)
    return(maxLengthInFiles, maxLinesInFiles)

def main(targets, outputName):      
    allFiles = getAllFiles(targets)
     
    filesCount = len(allFiles)
    if filesCount == 0:
        print 'no files'
        return None

    maxLengthInFiles, maxLinesInFiles = getMaxLengthInFiles(allFiles)      

    print 'Number of files: ' + str(filesCount)
    print 'Max lines: ' + str(maxLinesInFiles)
    print 'Max length: ' + str(maxLengthInFiles)
    
    blanks = 3 + (filesCount + 3)%2
    print 'blanks: ' + str(blanks)

    widest = maxLengthInFiles * charWidth 
    if widest > MAX_WIDTH:
        widest = MAX_WIDTH
        print 'Width too wide.'
    
    tallest = maxLinesInFiles * charHeight
    if tallest > MAX_HEIGHT:
        tallest = MAX_HEIGHT
        print 'Height too tall.'
    
    imgHeight = 2*ROW_OFFSET + (tallest + ROW_OFFSET) 
    if imgHeight > MAX_TOTAL_HEIGHT:
        imgHeight = MAX_TOTAL_HEIGHT
        print 'Height maxed out'
    
    xOffsets = []
    for _ in range(filesCount + blanks):
        xOffsets.append(widest+HORIZONTAL_GAP)
    
    imgWidth = 0
    for offset in xOffsets:
        imgWidth += offset

    img = Image.new("RGBA", (imgWidth, imgHeight),background)
    drawFileImg = ImageDraw.Draw(img)
    font = ImageFont.truetype("Courier Prime Code.ttf", charHeight)
    titleFont = ImageFont.truetype("Courier Prime Code.ttf", titleHeight)
    bigFont = ImageFont.truetype("Courier Prime Code.ttf", bigHeight)
    print 'Image dimensions: ' + str(imgWidth) + ' x ' + str(imgHeight)

    cwidth = imgWidth 
    cheight = imgHeight 
    rowOffset = ROW_OFFSET
    oldDirName = os.path.dirname(allFiles[0])

    j = 0
    columnOffset = 0
    for _ in range( blanks ):
        # box = (0, 0, widest + HORIZONTAL_GAP, tallest)
        # region = imgFile.crop(box)
        # img.paste(region, box)
        columnOffset += xOffsets[j]
        j+=1

    for i,f in enumerate(allFiles):
        x = 0
        imgFile = Image.new("RGBA", (cheight, cwidth),background) 
        drawFile = ImageDraw.Draw(imgFile)    
        sys.stdout.write("\r {0} {1}                         ".format(str(i), str(f)))
        sys.stdout.flush()
        source = processFile(f)       

        name = str(os.path.split(f)[1])
        drawFile.text((hOffset, 0),name,greenish,font=titleFont)
        vOffset = titleHeight * 2

        for y, line in enumerate(source[:MAX_LINES]):  
            if len( line.strip() ) == 0:
                continue          
            if y + 1 < len(source):
                author = git_info.getAuthor(f,y)
                author_index = getAuthorIndex(author)
                author_index = author_index % len(colors)
                author_color = colors[author_index]
                drawFile.text((hOffset+x, vOffset + charHeight*y),line[:MAX_CHARS],author_color,font=font)

        # The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.
        # The Python Imaging Library uses a coordinate system with (0, 0) in the upper left corner.
        box = (0, 0, widest + HORIZONTAL_GAP, tallest)
        region = imgFile.crop(box)
        del imgFile
        del drawFile
        box = (0+columnOffset, 0 + rowOffset, widest + HORIZONTAL_GAP + columnOffset, tallest + rowOffset)
        img.paste(region, box)

        columnOffset += xOffsets[j]           
        j+=1

    width, height = img.size

    width_fraction = 16.
    height_fraction = 9.
    for i in range(1,100):
        if i*height*width_fraction/height_fraction > width/i: 
            break # Find the number of pieces to cut the wide image into such that stacking them give a 16:9 ratio.
    pieces = i

    print 'Pieces: ' + str(pieces)

    if SCALE_DIV > 1:
        img = img.resize((int(round(width/SCALE_DIV)),int(round(height/SCALE_DIV))), Image.ANTIALIAS)
    enhancer = (ImageEnhance.Color(img))
    img = enhancer.enhance(1.6)
    enhancer = (ImageEnhance.Brightness(img))
    img = enhancer.enhance(2)    
    img.save(outputName, "PNG")
    print '\nfin'
    return pieces

def processFile(filename):
    try:
        f = open(filename,'r')
    except IOError:
        return

    data = f.read(8000)
    f.close()
    databyline = string.split(data, '\n')
    return databyline

if __name__ == '__main__':
    targets = []
    target = SOURCE_FOLDER
    folders =  os.listdir(target)   
    images = []
    base = git_info.getBaseRepoName(target)
    output_file_name = base + '.png'

    wide_file_name = 'wide.png'
    pieces = main([target], wide_file_name)
    print authors
    print author_lines
        
    stacked_file_name = image_tools.split_then_stack(wide_file_name,pieces)
    image_tools.cleanUp(wide_file_name)

    text = []
    line_colors = []
    line_colors.append(greenish)
    text.append(git_info.getBaseRepoName(target))
    for author in sorted( authors):
        text.append(author + ' ' + str(author_lines[author]))
        author_color = authors[author] % len(colors)
        line_colors.append(colors[author_color])
    
    x = 100
    y = ROW_OFFSET
    overlay_file_name = image_tools.overlayLines(stacked_file_name, text, line_colors, 40, x, y)
    image_tools.cleanUp(stacked_file_name)
    
    text = []
    line_colors = []
    text.append(git_info.getBaseRepoName(target))
    line_colors.append(white)
    text.append(git_info.getLastCommitDate(target))
    line_colors.append(white)
    text.append("File count: " + git_info.getFileCount(target))
    line_colors.append(white)
    text.append((git_info.getLineCount(target) + " lines").strip())
    line_colors.append(white)

    overlay_file_name = image_tools.overlayLines(overlay_file_name, text, line_colors)        
    image_tools.rename(overlay_file_name,output_file_name)
    image_tools.cleanUp(overlay_file_name)
    image_tools.openImage(output_file_name)

    exit()

    
    
