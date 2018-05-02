# ffmpeg -i movie.mov -r 1 fooframes/frames%05d.jpg
# extract 1 frame for every second of the movie...
import os, sys

def combine(folder, target):
    cmd = 'ffmpeg -framerate 4 -i {folder}{target}_%04d.png -c:v libx264 -r 60 -pix_fmt yuv420p {folder}temp.mp4 -y'
    cmd  = cmd.format(folder=folder, target=target)
    print(cmd)
    os.system(cmd)
    
    cmd = 'ffmpeg -i {folder}temp.mp4 -vf reverse {folder}out.mp4 -y'
    cmd = cmd.format(folder=folder)
    print(cmd)
    os.system(cmd)
    
    cmd = 'rm {folder}temp.mp4'
    cmd = cmd.format(folder=folder)
    print(cmd)
    os.system(cmd)

    cmd = 'rm {folder}{target}*.png'
    cmd = cmd.format(folder=folder,target=target)
    print(cmd)
    os.system(cmd)

    return(0)

if __name__ == "__main__":
    combine('output/','birdseye')

