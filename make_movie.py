# ffmpeg -i movie.mov -r 1 fooframes/frames%05d.jpg
# extract 1 frame for every second of the movie...
import os, sys

def combine(target):
    cmd_start = 'ffmpeg -framerate 4 -i '
    cmd_end = '_%04d.png -c:v libx264 -r 60 -pix_fmt yuv420p 1.mp4 -y'
    cmd = cmd_start + target + cmd_end
    print cmd
    os.system(cmd)
    
    cmd = 'ffmpeg -i 1.mp4 -vf reverse out.mp4 -y'
    print cmd
    os.system(cmd)
    
    cmd = 'rm 1.mp4'
    print cmd
    os.system(cmd)

    return(0)

if __name__ == "__main__":
    combine('birdseye')

