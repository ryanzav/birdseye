# ffmpeg -i movie.mov -r 1 fooframes/frames%05d.jpg
# extract 1 frame for every second of the movie...
import os, sys

def combine(folder, target):
    temp_file = os.path.join('{folder}','temp.mp4')
    target_files = os.path.join('{folder}','{target}_%04d.png')
    output_file = os.path.join('{folder}','out.mp4')

    cmd = 'ffmpeg -framerate 4 -i ' + target_files + ' -c:v libx264 -r 60 -pix_fmt yuv420p ' + temp_file +  ' -y'
    cmd  = cmd.format(folder=folder, target=target)
    print(cmd)
    os.system(cmd)
    
    cmd = 'ffmpeg -i ' + temp_file + ' -vf reverse ' + output_file + ' -y'
    cmd = cmd.format(folder=folder)
    print(cmd)
    os.system(cmd)
    
    os.remove(os.path.join(folder,'temp.mp4'))

    # cmd = 'rm {folder}/{target}*.png'
    # cmd = cmd.format(folder=folder,target=target)
    # print(cmd)
    # os.system(cmd)

    return(0)

if __name__ == "__main__":
    combine('output','birdseye')

