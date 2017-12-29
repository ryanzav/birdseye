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
import disk_tools as disk
import argparse
import math

import make_movie

if sys.platform.startswith('darwin'):
    slash = '/'
else:
    slash = '\\'    


SOURCE_FOLDER = '.'
SOURCE_FOLDER = '../lib-nilon'
#SOURCE_FOLDER = '../devices-nlight-air-sub-ghz'
TEMP_FOLDER = '.' + slash + 'temp' + slash

MAX_FILES = 50000
MAX_LINES = 100000
HEIGHT_LIMIT = 4000 # Max file height before file is split.

OPEN_IMAGE = False
CORNER_TEXT = False
CENTER_TEXT = True

OVERRIDE_FONT = None
OVERRIDE_X = None
OVERRIDE_Y = None

HORIZONTAL_GAP = 200
hOffset = 40
ROW_OFFSET = 20

bigHeight = 100
titleHeight = 20
charHeight = 3
charWidth = 1
MAX_CHARS = 96
MAX_WIDTH = MAX_CHARS * charWidth + HORIZONTAL_GAP

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

authors = {}
author_lines = {}

def resetAuthors():
    global author_lines
    for author in author_lines:
        author_lines[author] = 0

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

def getAllFiles(targets, first):
    allFiles = []
    neededFiles = []
    for target in targets:
        target = os.path.abspath(target)
        diff = git_info.getDiff(target)
        print "Diff:" + diff
        for root, dirs, files in os.walk(target, topdown=True):
            dirs.sort()
            files.sort()
            for name in files: # or name[-2:] == '.h' 
                if filterFiles(root, name):                     
                    if first or name in diff:            
                        neededFiles.append((os.path.join(root, name)))
                    allFiles.append((os.path.join(root, name)))    
                    if len(allFiles) >= MAX_FILES:
                        return allFiles,neededFiles
    return allFiles,neededFiles
    
def drawText(f,font,titleFont,titleHeight,charHeight):

    sys.stdout.write("\r{0}                         ".format(str(f)))
    sys.stdout.flush()

    source = processFile(f)       

    imgHeight = titleHeight*3 + (5 +len(source))*charHeight #Override
    imgWidth = MAX_WIDTH

    imgFile = Image.new("RGBA", (imgWidth, imgHeight),background) 
    drawFile = ImageDraw.Draw(imgFile)    

    name = str(os.path.split(f)[1])
    vOffset = titleHeight 
    drawFile.text((hOffset, vOffset),name,greenish,font=titleFont)
    vOffset += titleHeight * 2
    
    for y, line in enumerate(source[:MAX_LINES]):
        if len( line.strip() ) == 0:
            continue          
        if y + 1 < len(source):
            author = git_info.getAuthor(f,y)
            author_index = getAuthorIndex(author)
            author_index = author_index % len(colors)
            author_color = colors[author_index]
            drawFile.text((hOffset, vOffset + charHeight*y),line,author_color,font=font)

    # The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.
    # The Python Imaging Library uses a coordinate system with (0, 0) in the upper left corner.
    height = vOffset + ( len(source) + 5 )*charHeight
    box = (0, 0, imgWidth, imgHeight)
    region = imgFile.crop(box)
    del imgFile
    del drawFile
    return region

def drawImages(output_file_name, allFiles):

    font = ImageFont.truetype("Courier Prime Code.ttf", charHeight)
    titleFont = ImageFont.truetype("Courier Prime Code.ttf", titleHeight)
    bigFont = ImageFont.truetype("Courier Prime Code.ttf", bigHeight)

    print 'Processing ' + str(len(allFiles)) + ' files...'
    fileImages = []
    for i,f in enumerate(sorted(allFiles)):        
        region = drawText(f,font,titleFont,titleHeight,charHeight)

        new_w = int(region.size[0]*SCALE_DIV)
        new_h = int(region.size[1]*SCALE_DIV)
        region = region.resize((new_w,new_h), Image.ANTIALIAS)

        fileImage = TEMP_FOLDER + os.path.split(f)[0].split(slash)[-1] + '_' +  os.path.split(f)[1] + '.png'
        region.save(fileImage, "PNG")
        del region
        fileImages.append(fileImage)
    
    return fileImages


def processFile(filename):
    try:
        f = open(filename,'r')
    except IOError:
        print("Failed to open file!")
        return ["Failed to open file!"]

    data = f.read()
    f.close()
    databyline = string.split(data, '\n')
    return databyline

def cornerText(target, working_file_name):
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
    overlaid = image_tools.overlayLines(working_file_name, text, line_colors, 40, x, y)
    return overlaid
    
def centerText(target, working_file_name):
    text = []
    line_colors = []
    text.append(git_info.getBaseRepoName(target))
    line_colors.append(white)
    text.append(git_info.getLastCommitDate(target))
    line_colors.append(white)
    #text.append("File count: " + git_info.getFileCount(target))
    #line_colors.append(white)
    # text.append((git_info.getLineCount(target) + " lines").strip())
    # # line_colors.append(white)
    # for author in sorted( authors):
    #     text.append(author + ' ' + str(author_lines[author]))
    #     author_color = authors[author] % len(colors)
    #     line_colors.append(colors[author_color])        
    overlaid = image_tools.overlayLines(working_file_name, text, line_colors, OVERRIDE_FONT, OVERRIDE_X, OVERRIDE_Y,2)        
    return overlaid

def limitHeight(fileImages):
    height_limit = HEIGHT_LIMIT
    for image in fileImages:
        whole = Image.open(image)
        if whole.size[1] > height_limit:
            print(image)
            results = image_tools.separate(image,2)
            fileImages.remove(image)    
            fileImages = results + fileImages
        del whole    
    return fileImages

def createImage(target,first,index):
    base = git_info.getBaseRepoName(target)
    commit = git_info.getCommitNumber(target)
    output_file_name = base + '_%04d' % index + '.png'
    
    allFiles, neededFiles = getAllFiles([target],first)    
    # if len(allFiles) == 0:
    #     return()

    disk.makeFolder(TEMP_FOLDER)

    newFileImages = drawImages(output_file_name, neededFiles)

    newFileImages = limitHeight(newFileImages)
    
    # fileImages = []
    # for root, dirs, files in os.walk(TEMP_FOLDER, topdown=True):
    #     for f in files:
    #         fileImages.append((os.path.join(root, f)))

    allFileImages = []
    for i,f in enumerate(allFiles):
        fileImage = TEMP_FOLDER + os.path.split(f)[0].split(slash)[-1] + '_' + os.path.split(f)[1] + '.png'
        allFileImages.append(fileImage)

    pile_file = image_tools.pile(allFileImages)
    
    separated_files = image_tools.separate(pile_file)
    disk.cleanUp(pile_file)

    connected = image_tools.connect(separated_files)
    disk.cleanUp(separated_files)   

    enhanced = image_tools.enhance([connected])
    disk.cleanUp(connected)    

    if CORNER_TEXT:
        overlaid = cornerText(target, enhanced[0])
        disk.cleanUp(enhanced)        
    else:
        overlaid = enhanced[0]

    if CENTER_TEXT: 
        overlaid2 = centerText(target, overlaid)
        disk.cleanUp(overlaid) 
    else:
        overlaid2 = overlaid
    
    disk.move(overlaid2, output_file_name)   

    #disk.deleteFolder(TEMP_FOLDER)

    if OPEN_IMAGE:
        disk.open(output_file_name)
        
def gitHistory(target,revisions):
    response = git_info.resetHead(target)
    print(response)

    for i in range(1,revisions):
        if i == 1:
            first = True
        else:
            first = False
        createImage(SOURCE_FOLDER,first,i)
        resetAuthors()
        response = git_info.checkoutRevision(target, 1)
        print(response)

    response = git_info.resetHead(target)
    print(response)

if __name__ == '__main__':  
    gitHistory(SOURCE_FOLDER,50)
    make_movie.combine()
    exit()

    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--target", help="Target folder location.")
    args = parser.parse_args()
    if args.target is None:
        createImage(SOURCE_FOLDER)
    else:
        createImage(args.target)


    

 
    
