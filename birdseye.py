"""Birdseye
This script does a git-blame on each line of a project's source code and then
generates a color coded image of the source text for the entire project.

The purpose of this script is to help visualize a git repo's history in
various ways.
A movie can be generated with ffmpeg that shows the evolution of a repo.

This requires 'pillow' which is a fork of the Python Image Library (PIL).
"""
import os, os.path, time, calendar, sys, argparse
from io import open
from PIL import Image, ImageFont, ImageDraw
import git_info, image_tools, make_movie
import disk_tools as disk

# Configuration
OPEN_AFTER = True           # Open the resulting image or movie with a local application.
MAX_FILES = 100             # Maximum number of files to process.
MAX_LINES = 10000           # Maximum lines in any file to process.
TERMINAL_WIDTH = 80         # The maximum width of any line.
MAX_MSG_LENGTH = 80         # The maximum git commit info message length.
SHOW_COMMIT_INFO = False    # Display the commit details in the info block.
PROCESS_ALL = False         # Include files without a git history.
SKIP_GIT = False            # Just show the files without any git details.
COLOR_SCHEME = 1            # Color scheme selection.
BIG_CHAR = False            # Use a larger character size.
NO_SCALE = False            # Don't scale the images based on the total number of files.
SAVE_TEMP = False           # Save previous output in temp folder.
NEWEST = 0                  # Number of seconds old for a line to be colored fully bright.
MONTHS = 6                  # Default number of months to use to scale the coloring of lines.
REGENERATE_ALL = True       # Regenerate all files and don't optimize by only updating files shown in diff.
DEFAULT_REVS = 5            # The default number of commits to include in a movie.
FORCE_SIZE = True           # Force all the movie frames to be the same size.
FORCE_EVEN = True           # Force the height and width to be even numbers.
HEIGHT_LIMIT = 4000         # Max file height before file is split.
CORNER_TEXT = False         # Put info in the corner instead of the center.
OVERRIDE_FONT = None        # Force an info font size.
OVERRIDE_X = None           # Force info location.
OVERRIDE_Y = None           # Force info location.

HORIZONTAL_GAP = 200
HOFFSET = 40
ROW_OFFSET = 20
TITLE_HEIGHT = 20
BIG_CHAR_HEIGHT = 18
BIG_CHAR_WIDTH = 6
LIL_CHAR_HEIGHT = 3
LIL_CHAR_WIDTH = 1
if BIG_CHAR:
    CHAR_HEIGHT = BIG_CHAR_HEIGHT
    CHAR_WIDTH = BIG_CHAR_WIDTH
else:
    CHAR_HEIGHT = LIL_CHAR_HEIGHT
    CHAR_WIDTH = LIL_CHAR_WIDTH
MAX_CHARS = 96
MAX_WIDTH = MAX_CHARS * CHAR_WIDTH + HORIZONTAL_GAP
MAX_HEIGHT = MAX_LINES * CHAR_HEIGHT

# Constants
DATE_FORMAT = "%Y-%m-%d"
DAY = 24 * 60 * 60      # Seconds in a day
SOURCE_FOLDER = '.'
TEMP_FOLDER = os.path.join('.', 'temp')
OUTPUT_FOLDER = os.path.join('.', 'output')

paleblue = (128, 153, 230, 255)
greenish = (62, 230, 200, 255)
bluish = (77, 77, 255, 255)
black = (0, 0, 0, 255)
white = (255, 255, 255, 255)
darkblue = (3, 3, 90, 255)
lightblue = (100, 100, 120, 255)
transparent = (0, 0, 0, 0)

deepnavy = (30, 34, 42, 255)     # Background (Deep Navy/Gray)
silver =(171, 178, 191, 255)     # Primary Text (Off-white/Silver)
skyblue = (97, 175, 239, 255)    # Blue (File Names/Identifiers)
colors1 = [
    (224, 200, 200, 255),  # Red 
    (240, 113, 120, 255),  # Rose/Pink 
    (180, 190, 254, 255),  # Lavender 
    (82, 139, 255, 255),   # Deep Blue
    (255, 204, 102, 255),  # Gold 
    (198, 120, 221, 255),  # Purple
    (86, 182, 194, 255),   # Cyan 
    (115, 218, 202, 255),  # Mint/Teal
    (229, 192, 123, 255),  # Yellow
    (209, 154, 102, 255),  # Orange
]

colors2 = [
    (60, 180, 75, 50),     # green
    (0, 130, 200, 50),     # blue
    (230, 190, 255, 50),   # lavender
    (170, 255, 195, 50),   # mint
    (128, 128, 0, 50),     # olive
    (255, 215, 180, 50),   # coral
    (0, 0, 128, 50),       # navy
]

if COLOR_SCHEME == 1:
    background = deepnavy
    info_color = silver
    filename_color = skyblue
    colors = colors1
else:
    background = black
    info_color = greenish
    filename_color = white
    colors = colors2

# Variables
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
        msg = 'New author: ' + author
        printOver(msg)
        print('')
    else:
        author_lines[author] += 1
    return authors[author]


def filterFiles(root, name):
    # Expanded list of common binary file extensions
    binary_extensions = [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff',
        '.zip', '.exe', '.bin', '.dll', '.pdf', '.doc',
        '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.rar',
        '.7z', '.iso', '.tar', '.gz', '.bz2', '.swf',
        '.class', '.apk', '.dmg', '.mp3', '.wav', '.mp4',
        '.avi', '.mov', '.mkv', '.flv', '.webm', '.jar',
        '.icns', '.pyc', '.ttf'
    ]
    
    # Return False for files without an extension (no '.' in the basename).
    if os.path.splitext(name)[1] == '':
        return False
    # Ignore any files inside a .git directory.
    if '.git' in root.split(os.path.sep):
        return False
    # Ignore common binary files
    if os.path.splitext(name)[1].lower() in binary_extensions:
        return False
    return True


def getAllFiles(targets, first):
    allFiles = []
    neededFiles = []
    for target in targets:
        target = os.path.abspath(target)
        # Don't run diff if not doing sequence or if regenerating all images.
        if not first and not REGENERATE_ALL:
            diff = git_info.getDiff(target)
            print(("Diff:" + diff))
        else:
            diff = ""
        for root, dirs, files in os.walk(target, topdown=True):
            dirs.sort()
            files.sort()
            for name in files:  # or name[-2:] == '.h'
                if filterFiles(root, name):
                    if REGENERATE_ALL or first or name in diff:
                        neededFiles.append((os.path.join(root, name)))
                    allFiles.append((os.path.join(root, name)))
                    if len(allFiles) >= MAX_FILES:
                        return allFiles, neededFiles
    return allFiles, neededFiles


def getAge(blame):
    '''Return the normalized age of a line based on the blame info.'''
    # Get the index after the year from the blame line. Good until 2100.
    # TODO: This will break if there are filenames starting with 20.
    i1 = blame.find(' 20') + 1
    date = blame[i1:i1 + 1 + blame[i1+1:].find(' ')]
    try:
        diff = (
            time.time()
            - calendar.timegm(time.strptime(date, DATE_FORMAT))
        )
    except:
        print("Bad date format.")
        diff = NEWEST
    if diff < NEWEST:
        diff = NEWEST
    elif diff > oldest:
        diff = oldest
    # newest commit is 255, oldest is 0
    age = 255 - int(255*(diff-NEWEST)/(oldest-NEWEST))
    return age


def drawText(f, font, titleFont, titleHeight, charHeight):
    '''Generate an image in memory based on the text of the input file.'''
    source = processFile(f)
    if not source:
        return None
    # Limit to maximimum number of lines.
    source = source[:MAX_LINES]

    if SHOW_COMMIT_INFO:
        commitInfo = git_info.getCommitNumber(os.path.split(f)[0])

    if SKIP_GIT:
        blames = len(source)*["a"]
    else:
        blames = git_info.getBlame(f)
        if not blames:
            if PROCESS_ALL:
                blames = len(source)*["a"]
            else:
                return None

    imgHeight = titleHeight*3 + (5 + len(source))*charHeight
    imgWidth = MAX_WIDTH

    imgFile = Image.new("RGBA", (imgWidth, imgHeight), transparent)
    drawFile = ImageDraw.Draw(imgFile)

    # Draw the filename.
    name = str(os.path.split(f)[1])
    vOffset = titleHeight
    drawFile.text((HOFFSET, vOffset), name, filename_color, font=titleFont)
    vOffset += titleHeight * 2

    # Draw each line.
    for y, srcs in enumerate(zip(source, blames)):
        line, blame = srcs
        if len(line.strip()) == 0 or len(blame.strip()) == 0:
            continue
        if y + 1 < len(source):
            # Get the color from the last author of each line.
            author = blame[blame.find('<')+1:blame.find('>')]
            # This will generate a new index each time a new author is passed.
            author_index = getAuthorIndex(author)
            author_index = author_index % len(colors)
            temp_color = colors[author_index]
            # Calculate age for each line.
            if show_age:
                age = getAge(blame)
                # Dark blue. Newer commits are brighter.
                # Older commits approach dark blue.
                aged_color = (age, age, age, 255)
                # Scale all the components of the color by the normalized age.
                age_scale = age/255.  # Newest approach 1.
                author_color = (
                    int(temp_color[0]*age_scale),
                    int(temp_color[1]*age_scale),
                    int(temp_color[2]*age_scale), 255)
            else:
                author_color = temp_color
                if SHOW_COMMIT_INFO:
                    if (blame[:7] == commitInfo):
                        author_color = white
     

            if age_only:
                line_color = aged_color
            else:
                line_color = author_color

            # Draw the line of text with the calculated color.
            drawFile.text((HOFFSET, vOffset + charHeight*y),
                          line, line_color, font=font)

    # The box is a 4-tuple defining the left, upper, right,
    # and lower pixel coordinate. The Python Imaging Library
    # uses a coordinate system with (0, 0) in the upper left corner.
    # Crop the image to the calculated limits.
    box = (0, 0, imgWidth, imgHeight)
    region = imgFile.crop(box)
    imgFile.close()
    del imgFile
    del drawFile
    return region


def printOver(msg):
    spaces = TERMINAL_WIDTH - len(msg)
    if spaces < 0:
        spaces = 0
        msg = msg[-TERMINAL_WIDTH:]
    msg = "\r{}{}".format(str(msg), ' '*spaces)

    sys.stdout.write(msg)
    sys.stdout.flush()

def drawImages(output_file_name, allFiles, scale_div=1):
    '''Generate an image for each target file.'''
    font = ImageFont.truetype("Courier Prime Code.ttf", CHAR_HEIGHT)
    titleFont = ImageFont.truetype("Courier Prime Code.ttf", TITLE_HEIGHT)

    print(('Processing ' + str(len(allFiles)) + ' files...'))
    fileImages = []
    for _, f in enumerate(sorted(allFiles)):
        printOver(str(f))
        # Generate the image in memory.
        region = drawText(f, font, titleFont, TITLE_HEIGHT, CHAR_HEIGHT)
        if not region:
            continue
        # Scale each image if needed.
        if scale_div != 1:
            new_w = int(region.size[0]*scale_div)
            new_h = int(region.size[1]*scale_div)
            region = region.resize((new_w, new_h), Image.Resampling.LANCZOS)
        # Binary alpha
        r, g, b, a = region.split()
        # a = a.point(lambda p: 255 if p > 200 else p+55)
        a = a.point(lambda p: min(p*4,255))
        region = Image.merge('RGBA', (r, g, b, a))

        # Save the image to a file.
        dirname, filename = os.path.split(f)
        fileImage = os.path.join(TEMP_FOLDER, dirname.split(
            os.path.sep)[-1] + '_' + filename + '.png')
        region.save(fileImage, "PNG")
        del region
        fileImages.append(fileImage)

    printOver('File processing complete.')
    print('')
    return fileImages


def drawBlank(output_file_name, imgWidth, imgHeight):
    imgFile = Image.new("RGBA", (imgWidth, imgHeight), transparent)
    imgFile.save(output_file_name, 'PNG')
    return output_file_name


def processFile(filename):
    try:
        f = open(filename, 'r', encoding='utf-8')
        data = f.read()
        f.close()
    except IOError:
        print("Failed to open file " + filename)
        return None
    except UnicodeDecodeError:
        print(f'Failed to decode {filename} as UTF-8! Trying something else!')
        try:
            f = open(filename, 'r', encoding='utf_16_le')
            data = f.read()
            f.close()
        except UnicodeDecodeError:
            print("Retry open failed!")
            return None

    databyline = data.split('\n')
    return databyline


def cornerText(target, working_file_name):
    text = []
    line_colors = []
    line_colors.append(greenish)
    text.append(git_info.getBaseRepoName(target))
    for author in sorted(authors):
        text.append(author + ' ' + str(author_lines[author]))
        author_color = authors[author] % len(colors)
        line_colors.append(colors[author_color])
    x = 100
    y = ROW_OFFSET
    overlaid = image_tools.overlayLines(
        working_file_name, text, line_colors, 40, x, y)
    return overlaid

def centerText(target, working_file_name, extra=False):
    text = []
    line_colors = []
    text.append(git_info.getBaseRepoName(target))
    line_colors.append(info_color)
    text.append(git_info.getLastCommitDate(target))
    line_colors.append(info_color)
    if SHOW_COMMIT_INFO:
        lines = git_info.getLastCommit(target).split('\n')
        for line in lines:
            while len(line) > 0:
                text.append(line[:MAX_MSG_LENGTH])
                line = line[MAX_MSG_LENGTH:]
                line_colors.append(info_color)
    if extra:
        text.append("File count: " + git_info.getFileCount(target))
        line_colors.append(info_color)
        for author in sorted(authors):
            text.append(author + ' ' + str(author_lines[author]))
            author_color = authors[author] % len(colors)
            line_colors.append(colors[author_color])

    overlaid = image_tools.overlayLines(
        working_file_name, text, line_colors,
        OVERRIDE_FONT, OVERRIDE_X, OVERRIDE_Y, 2)
    return overlaid


def limitHeight(fileImages):
    height_limit = HEIGHT_LIMIT
    added = []
    deleted = []
    for image in fileImages:
        whole = Image.open(image)
        if whole.size[1] > height_limit:
            results = image_tools.separate(image, 2)
            fileImages.remove(image)
            deleted.append(image)
            fileImages = results + fileImages
            added += results
            disk.cleanUp(image)
        whole.close()
        del whole
    return fileImages


def createImage(target, first=True, index=0, movie=False,
                info=True, forced_width=0, forced_height=0):
    '''Generates a digital image based on the contents of the target folder.'''
    # Figure out the filenames based on the target name.
    base = git_info.getBaseRepoName(target)
    output_file_name = os.path.join(
        OUTPUT_FOLDER, base + '_%04d' % index + '.png')

    # Generate the list of paths to the target files that will be used
    # to generate the images.
    allFiles, neededFiles = getAllFiles([target], first)

    # Calculate the scale of the output based on the total number of files.
    global scale_div
    if first:
        scale_div = 1 - len(allFiles)/1000.0
        if scale_div < .1:
            scale_div = .1
        if NO_SCALE:
            scale_div = 1
        print(('Scale = ' + str(scale_div)))

    # Generate the list of images that will be created.
    allFileImages = []
    for _, f in enumerate(allFiles):
        dirname, filename = os.path.split(f)
        fileImage = os.path.join(TEMP_FOLDER, dirname.split(
            os.path.sep)[-1] + '_' + filename + '.png')
        allFileImages.append(fileImage)

    # Setup a temp folder for the files during processing.
    disk.makeFolder(TEMP_FOLDER)
    # Setup an output folder for the end result.
    disk.makeFolder(OUTPUT_FOLDER)

    # Generate the images themselves.
    drawImages(output_file_name, neededFiles, scale_div)

    # Get just the images we need,
    # ignoring other temp images that are generated.
    folderImages = os.listdir(TEMP_FOLDER)
    runImages = []
    for image in folderImages:
        for match in allFileImages:
            if os.path.split(match)[1] in image:
                runImages.append(os.path.join(TEMP_FOLDER, image))
    runImages.sort()
    if len(runImages) == 0:
        print("Error: No images found.")
        return None

    # Append all the files together into a long strip.
    pile_file = image_tools.pile(runImages)
    # Split the strip into each segments.
    separated_files = image_tools.separate(pile_file)
    disk.cleanUp(pile_file)
    # Stitch together the segments.
    connected = image_tools.connect(separated_files)
    disk.cleanUp(separated_files)

    # Force the height and width to be even numbers.
    if FORCE_EVEN:
        connected = image_tools.make_even(connected)

    # When making a movie adjust each frame to
    # the same height and width.
    if movie and FORCE_SIZE and not first:
        img = Image.open(connected)
        if img.size[0] < forced_width:
            blank = drawBlank('blank.png', forced_width -
                              img.size[0], img.size[1])
            connected = image_tools.couple([connected, blank])
            disk.cleanUp('blank.png')
        img = Image.open(connected)
        if img.size[1] < forced_height:
            blank = drawBlank(
                'blank.png', img.size[0], forced_height-img.size[1])
            connected = image_tools.pile([connected, blank])
            disk.cleanUp('blank.png')
        img.close()
        del img

    if info:
        if CORNER_TEXT: # Apply text overlay in the corner.
            overlaid2 = cornerText(target, connected)
            disk.cleanUp(connected)     
        else:     # Apply text overlay in the center.
            overlaid2 = centerText(target, connected, extra=True)
            disk.cleanUp(connected)     
    else:
        overlaid2 = connected   

    # Fill background under the image with the selected background color
    overlaid2 = image_tools.composite_over(overlaid2, background)

    disk.move(overlaid2, output_file_name)
    return output_file_name


def gitHistory(target, revisions, info):
    branch = git_info.getBranch(target)
    response = git_info.resetHead(target, branch)
    print(response)

    forced_width = 0
    forced_height = 0
    for i in range(1, revisions):
        print('{i}/{revisions} {percent}%'.format(
            i=i,
            revisions=revisions,
            percent=int(100.0*i/revisions)))
        if i == 1:
            first = True
        else:
            first = False
        movie = True
        center_text = info

        file_name = createImage(target=target, first=first, index=i,
                                movie=movie, info=center_text,
                                forced_width=forced_width,
                                forced_height=forced_height)
        if first:
            img = Image.open(file_name)
            forced_width = img.size[0]
            forced_height = img.size[1]
            img.close()
            del img

        resetAuthors()
        response = git_info.checkoutRevision(target, 1)
        print(response)
        if 'fatal' in response:
            break

    return branch


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--target", help="Target folder path.")
    parser.add_argument("--movie", help="Generate a video of the repo changes over time.", action="store_true")
    parser.add_argument("--revs", help="Number of revisions to use in movie.")
    parser.add_argument(
        "--no_info",
        help="Exclude text overlay of git commit information.",
        action="store_true")
    parser.add_argument(
        "--show_age",
        help="Color code lines according to commit age AND author.",
        action="store_true")
    parser.add_argument(
        "--months",
        help="Number of months to scale the color coding of commits to.")
    parser.add_argument(
        "--age_only", help="Only color code the lines by age, not author.",
        action="store_true")

    args = parser.parse_args()

    if args.months:
        months = int(args.months)
    else:
        months = MONTHS
    # Number of seconds old for a line to be colored black.
    oldest = months * 30 * DAY

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
    else:
        show_age = False

    if args.age_only:
        age_only = True
        show_age = True
    else:
        age_only = False

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
    if movie:
        msg += 'Revs = {revs}\n'.format(revs=str(revs))
    msg += 'Info = {info}\n'.format(info=str(info))
    msg += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
    msg += '                                                      ><> \n'
    print(msg)

    if not SAVE_TEMP:
        disk.deleteFolder(TEMP_FOLDER)

    if movie:
        branch = ''
        try:
            branch = gitHistory(target, revs, info)
            base = git_info.getBaseRepoName(target)
            make_movie.combine(OUTPUT_FOLDER, base)
            if OPEN_AFTER:
                disk.open(os.path.join(OUTPUT_FOLDER, 'out.mp4'))
        finally:
            response = git_info.resetHead(target, branch)
            print(response)
    else:
        output_file_name = createImage(target=target, info=info)
        if OPEN_AFTER:
            disk.open(output_file_name)
