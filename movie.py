from PIL import Image, ImageFont, ImageDraw
from subprocess import Popen, PIPE, STDOUT
import io
import time
import random
import os

def make(dst, fps):
    base = os.getcwd()
    files = os.listdir(base)
    files.sort()   
    
    width = 3840
    height = 2160
    
    cmd = ['ffmpeg', '-loglevel', 'info', '-y', '-threads', 'auto', '-f', 'image2pipe', '-vcodec', 'ppm', '-s', '%sx%s' % (width, height), '-r', str(fps), '-i', '-', '-vcodec', 'libx264', dst]

    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    
    bg_image = Image.new('RGB', (width, height))        
    output = io.StringIO()     
    for file in files:
        if '.png' not in file:
            continue
        if 'lib-nilon' not in file:
            continue                        
        print(file)
        image = Image.open(file).convert('RGBA')
        #image = image.crop((0,0,width,height))
        image = image.resize((width, height), Image.ANTIALIAS)        
        for _ in range(5):                       
            result = bg_image.copy()            
            result.paste(image)            
            result.save(output, 'ppm')            

    print('done')
    p.stdin.write(output.getvalue())
    out, err = p.communicate()

if __name__=='__main__':
    make('test.mp4',25)
