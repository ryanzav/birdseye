'''
Created on Feb 21, 2016

@author: ryanz
'''

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageEnhance

import os
import time
import calendar
from PIL.FontFile import WIDTH

import sys
import git_info
import image_tools
import disk_tools as disk
import argparse
import math
import os.path
from io import open

import make_movie

show_age = False
age_only = False
DATE_FORMAT = "%Y-%m-%d"
day = 24 * 60 * 60 # Seconds in a day
newest = 0 # Number of seconds old for a line to be colored fully bright.
months = 6 # Default number of months to use to scale the coloring of lines.

scale_div = 1

OPEN_AFTER = True
REALLY_BIG = 5000

DEFAULT_REVS = 5
TOTAL_HEIGHT = 5000

FORCE_WIDTH = True

FORCE_EVEN = True

SOURCE_FOLDER = '.'
TEMP_FOLDER = os.path.join('.', 'temp')
OUTPUT_FOLDER = os.path.join('.', 'output')

MAX_FILES = 100000
MAX_LINES = 100000
HEIGHT_LIMIT = 4000 # Max file height before file is split.

CORNER_TEXT = False
CENTER_TEXT = False

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

TERMINAL_WIDTH = 80

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
        msg = 'New author: ' + author
        printOver(msg)
        print('')
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
    if (name[-3:] == '.md' or name[-3:] == '.py' or name[-2:] == '.c') and 'network.c' not in name:
        return True
    else:
        return False

def getAllFiles(targets, first):
    allFiles = []
    neededFiles = []
    for target in targets:
        target = os.path.abspath(target)
        diff = git_info.getDiff(target)
        print(("Diff:" + diff))
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
    blames = git_info.getBlame(f)

    source = processFile(f)
    if not source:
        return None

    while len(blames) < len(source):
        blames.append("<not.committed.yet>")

    imgHeight = titleHeight*3 + (5 +len(source))*charHeight #Override
    imgWidth = MAX_WIDTH

    imgFile = Image.new("RGBA", (imgWidth, imgHeight),background)
    drawFile = ImageDraw.Draw(imgFile)

    name = str(os.path.split(f)[1])
    vOffset = titleHeight
    drawFile.text((hOffset, vOffset),name,greenish,font=titleFont)
    vOffset += titleHeight * 2

    for y, srcs in enumerate(zip(source[:MAX_LINES],blames)):
        line, blame = srcs
        if len( line.strip() ) == 0 or len(blame.strip()) == 0:
            continue
        if y + 1 < len(source):
            if show_age:
                i1 = blame.find(' 201') + 1
                date = blame[i1:i1 + 1 + blame[i1+1:].find(' ')]
                try:
                    diff = time.time() - calendar.timegm(time.strptime(date, DATE_FORMAT))
                except:
                    print("Bad date format.")
                    diff = newest
                if diff < newest:
                    diff = newest
                elif diff > oldest:
                    diff = oldest
                age = 255 - int(255*(diff-newest)/(oldest-newest))   # newest commit is 255, oldest is 0
                aged_color = (age,age,age,255) # Dark blue. Newer commits are brighter. Older commits approach dark blue.

            author = blame[blame.find('<')+1:blame.find('>')]
            author_index = getAuthorIndex(author)
            author_index = author_index % len(colors)
            temp_color = colors[author_index]

            if show_age:
                age_scale = age/255. # Newest approach 1.
                author_color = (int(temp_color[0]*age_scale), int(temp_color[1]*age_scale), int(temp_color[2]*age_scale), 255)
            else:
                author_color = temp_color

            if age_only:
                line_color = aged_color
            else:
                line_color = author_color

            drawFile.text((hOffset, vOffset + charHeight*y),line,line_color,font=font)

    # The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate.
    # The Python Imaging Library uses a coordinate system with (0, 0) in the upper left corner.
    height = vOffset + ( len(source) + 5 )*charHeight
    box = (0, 0, imgWidth, imgHeight)
    region = imgFile.crop(box)
    del imgFile
    del drawFile
    return region

def printOver(msg):
    spaces = TERMINAL_WIDTH - len(msg)
    if spaces < 0:
        spaces = 0
    msg = "\r{}{}".format(str(msg),' '*spaces)
    msg = msg[:TERMINAL_WIDTH]
    sys.stdout.write(msg)
    sys.stdout.flush()

def drawImages(output_file_name, allFiles, scale_div=1):
    font = ImageFont.truetype("Courier Prime Code.ttf", charHeight)
    titleFont = ImageFont.truetype("Courier Prime Code.ttf", titleHeight)
    bigFont = ImageFont.truetype("Courier Prime Code.ttf", bigHeight)

    print(('Processing ' + str(len(allFiles)) + ' files...'))
    fileImages = []
    for i,f in enumerate(sorted(allFiles)):
        printOver(str(f))
        region = drawText(f,font,titleFont,titleHeight,charHeight)
        if not region:
            continue

        new_w = int(region.size[0]*scale_div)
        new_h = int(region.size[1]*scale_div)
        region = region.resize((new_w,new_h), Image.ANTIALIAS)

        dirname, filename = os.path.split(f)
        fileImage = os.path.join(TEMP_FOLDER, dirname.split(os.path.sep)[-1] + '_' + filename + '.png')
        region.save(fileImage, "PNG")
        del region
        fileImages.append(fileImage)
    printOver('File processing complete.')
    print('')
    return fileImages

def drawBlank(output_file_name, imgWidth, imgHeight):
    imgFile = Image.new("RGBA", (imgWidth, imgHeight),background)
    imgFile.save(output_file_name,'PNG')
    return output_file_name

def processFile(filename):
    try:
        f = open(filename,'r')
        data = f.read()
        try:
            text = data.decode('utf-8')
        except AttributeError:
            text = data
        f.close()
    except IOError:
        print("Failed to open file!")
        return None
    except UnicodeDecodeError:
        print("Failed to decode file!")
        return None
    
    databyline = text.split('\n')
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

def centerText(target, working_file_name, extra = False):
    text = []
    line_colors = []
    text.append(git_info.getBaseRepoName(target))
    line_colors.append(white)
    text.append(git_info.getLastCommitDate(target))
    line_colors.append(white)
    if extra:
        text.append("File count: " + git_info.getFileCount(target))
        line_colors.append(white)
        for author in sorted( authors):
            text.append(author + ' ' + str(author_lines[author]))
            author_color = authors[author] % len(colors)
            line_colors.append(colors[author_color])
    overlaid = image_tools.overlayLines(working_file_name, text, line_colors, OVERRIDE_FONT, OVERRIDE_X, OVERRIDE_Y,2)
    return overlaid

def limitHeight(fileImages):
    height_limit = HEIGHT_LIMIT
    added = []
    deleted = []
    for image in fileImages:
        whole = Image.open(image)
        if whole.size[1] > height_limit:
            results = image_tools.separate(image,2)
            fileImages.remove(image)
            deleted.append(image)
            fileImages = results + fileImages
            added += results
            disk.cleanUp(image)
        del whole
    return fileImages

def createImage(target,first=True,index=0,movie=False, info = True, alphabetical_sort = False, forced_width = 0, forced_height = 0):
    global scale_div
    base = git_info.getBaseRepoName(target)
    commit = git_info.getCommitNumber(target)
    output_file_name = os.path.join(OUTPUT_FOLDER, base + '_%04d' % index + '.png')

    allFiles, neededFiles = getAllFiles([target],first)

    if first:
        scale_div = 1 - len(allFiles)/1000.0
        if scale_div < .1:
            scale_div = .1
        print(('Scale = ' + str(scale_div)))

    allFileImages = []
    for i,f in enumerate(allFiles):
        dirname, filename = os.path.split(f)
        fileImage = os.path.join(TEMP_FOLDER, dirname.split(os.path.sep)[-1] + '_' + filename + '.png')
        allFileImages.append(fileImage)

    disk.makeFolder(TEMP_FOLDER)
    disk.makeFolder(OUTPUT_FOLDER)

    newFileImages = drawImages(output_file_name, neededFiles,scale_div)

    #newFileImages = limitHeight(newFileImages) # @TODO: Need modify allFiles to include filename changes from chopping files.

    folderImages = os.listdir(TEMP_FOLDER)

    runImages = []
    for image in folderImages:
        for match in allFileImages:
            if os.path.split(match)[1] in image:
                runImages.append(os.path.join(TEMP_FOLDER, image))
    runImages.sort()
    if len(runImages) == 0:
        return

    if alphabetical_sort:
        total_height = 0
        batch = []
        separated_files = []
        letters = 'abcdefghijklmnopqrstuvwxyz'
        index = 0
        for i,f in enumerate(runImages):
            img = Image.open(f)
            name = os.path.split(f)[1]
            letter = name[0].lower()
            print((letters[index]))
            if letter not in letters or letter != letters[index]:
                while letter != letters[index] and index < 25:
                    index+=1
                if TOTAL_HEIGHT - total_height > 0:
                    batch.append(drawBlank('blank.png',MAX_WIDTH,TOTAL_HEIGHT-total_height))
                pile_file = image_tools.pile(batch)
                batch = []
                batch.append(f)
                separated_files.append(pile_file)
                total_height = img.size[1]
            else:
                batch.append(f)
                total_height += img.size[1]
        if len(batch) > 0:
            if TOTAL_HEIGHT - total_height > 0:
                batch.append(drawBlank('blank.png',MAX_WIDTH,TOTAL_HEIGHT-total_height))
            pile_file = image_tools.pile(batch)
            batch = []
            separated_files.append(pile_file)
    else:
        pile_file = image_tools.pile(runImages)
        separated_files = image_tools.separate(pile_file)
        disk.cleanUp(pile_file)

    connected = image_tools.connect(separated_files)
    disk.cleanUp(separated_files)

    if FORCE_EVEN:
        connected = image_tools.make_even(connected)

    if movie and FORCE_WIDTH and not first:
        img = Image.open(connected)
        if img.size[0] < forced_width:
            blank = drawBlank('blank.png',forced_width-img.size[0],img.size[1])
            connected = image_tools.couple([connected,blank])
            disk.cleanUp('blank.png')
        img = Image.open(connected)
        if img.size[1] < forced_height:
            blank = drawBlank('blank.png',img.size[0],forced_height-img.size[1])
            connected = image_tools.pile([connected,blank])
            disk.cleanUp('blank.png')

    enhanced = image_tools.enhance([connected])
    disk.cleanUp(connected)

    if CORNER_TEXT:
        overlaid = cornerText(target, enhanced[0])
        disk.cleanUp(enhanced)
    else:
        overlaid = enhanced[0]

    if info:
        overlaid2 = centerText(target, overlaid, extra = True)
        disk.cleanUp(overlaid)
    else:
        overlaid2 = overlaid

    # img = Image.open(overlaid2)
    # if img.size[0] > REALLY_BIG:
    #     image_tools.scale(overlaid2,.5)

    disk.move(overlaid2, output_file_name)
    return output_file_name

def gitHistory(target,revisions,info):
    branch = git_info.getBranch(target)
    response = git_info.resetHead(target,branch)
    print(response)

    forced_width = 0
    forced_height = 0
    for i in range(1,revisions):
        print(( '{i}/{revisions} {percent}%'.format( i=i,revisions=revisions,percent=int(100.0*i/revisions) ) ))
        if i == 1:
            first = True
        else:
            first = False
        movie = True
        center_text = info

        file_name = createImage(target=target,first=first,index=i,movie=movie,info=center_text,forced_width=forced_width,forced_height=forced_height)
        if first:
            img = Image.open(file_name)
            forced_width = img.size[0]
            forced_height = img.size[1]

        resetAuthors()
        response = git_info.checkoutRevision(target, 1)
        print(response)
        if 'fatal' in response:
            break

    return branch


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--target", help="Target folder path.")
    parser.add_argument("--movie", help="Movie demo.", action="store_true")
    parser.add_argument("--revs", help="Number of revisions to use in movie.")
    parser.add_argument("--no_info", help="Exlude text overlay of git commit information.", action="store_true")
    parser.add_argument("--show_age", help="Color code lines according to commit age AND author.", action="store_true")
    parser.add_argument("--months", help="Number of months to scale the color coding of commits to.")
    parser.add_argument("--age_only", help="Only color code the lines by age, not author.", action="store_true")

    args = parser.parse_args()

    if args.months:
        months = int(args.months)
    oldest = months * 30 * day # Number of seconds old for a line to be colored black.

    if args.movie:
        movie = True
    else:
        movie = False

    if args.no_info:
        info = False
    else:
        info = True

    if args.show_age:
        show_age = True

    if args.age_only:
        age_only = True

    if args.target is None:
        target = SOURCE_FOLDER
    else:
        target = args.target

    if args.revs is None:
        revs = DEFAULT_REVS
    else:
        revs = int(args.revs)

    msg = '\n                                           ~~(OvO)~~     \n'
    msg += '\nCreating a bird\'s eye view...\n'
    msg += 'Folder = {target}\n'.format(target=target)
    msg += 'Movie = {movie}\n'.format(movie=str(movie))
    msg += 'Info = {info}\n'.format(info=str(info))
    msg += 'Revs = {revs}\n'.format(revs=str(revs))
    msg += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
    msg += '                                                      ><> \n'
    print(msg)

    disk.deleteFolder(TEMP_FOLDER)
    if movie:
        branch = ''
        try:
            branch = gitHistory(target,revs,info)
            base = git_info.getBaseRepoName(target)
            make_movie.combine(OUTPUT_FOLDER,base)
            if OPEN_AFTER:
                disk.open(os.path.join(OUTPUT_FOLDER, 'out.mp4'))
        finally:
            response = git_info.resetHead(target,branch)
            print(response)
    else:
        output_file_name = createImage(target=target,info=info)
        if OPEN_AFTER:
            disk.open(output_file_name)

    disk.deleteFolder(TEMP_FOLDER)
