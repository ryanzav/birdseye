'''
Created on Feb 21, 2016

@author: ryanz
'''

import string
import os
import sys
import subprocess
import shutil

copy = shutil.copyfile
move = shutil.move

def open(f):
    if sys.platform == "linux2":
        cmd = "xdg-open " + f
    elif sys.platform == "darwin":
        cmd = "open " + f
    else:
        cmd = f

    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print(cmd)
        print(e.output)

def cleanUp(files):
    if type(files) != list:
        files = [files]
    for f in files:
        os.remove(f)

def makeFolder(folder):
    if not os.path.isdir(folder):
        try:
            os.mkdir(folder)
        except OSError as ex:
            print(ex)

def deleteFolder(folder):
    if os.path.isdir(folder):
        try:
            shutil.rmtree(folder)
        except OSError as ex:
            print(ex)

if __name__ == '__main__':
    pass
    
