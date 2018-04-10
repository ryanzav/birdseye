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
    cmd = "xdg-open " + f
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print cmd
        print e.output

def cleanUp(files):
    if type(files) != list:
        files = [files]
    for f in files:
        os.remove(f)

def makeFolder(folder):
    try:
        os.mkdir(folder)
    except OSError as ex:
        print ex

def deleteFolder(folder):
    try:
        shutil.rmtree(folder)
    except OSError as ex:
        print ex

if __name__ == '__main__':
    pass
    
