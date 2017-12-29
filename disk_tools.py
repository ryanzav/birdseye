'''
Created on Feb 21, 2016

@author: ryanz
'''

import string
import os
import sys
import subprocess

if sys.platform.startswith('darwin'):
    delete_command = 'rm'
    copy_command = 'cp'
    move_command = 'mv'
else:
    delete_command = 'del'
    copy_command = 'copy'
    rename_command = 'ren'

def copy(f,new): 
    cmd = copy_command + " " + f + " " + new
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print cmd
        print e.output
    return new
    
def move(f,new): 
    if sys.platform.startswith('darwin'):
        cmd = move_command + " " + f + " " + new
        try:
            response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        except subprocess.CalledProcessError as e:
            print cmd
            print e.output
        return new
    else:
        copy(f,new)
        cleanUp(f)
            

def open(f): 
    cmd = "open " + f
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print cmd
        print e.output

def cleanUp(files):
    if type(files) != list:
        files = [files]
    for f in files:
        cmd = delete_command + " " + f
        try:
            response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        except subprocess.CalledProcessError as e:
            print cmd
            print e.output

def makeFolder(folder):
    cmd = "mkdir " + folder
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print cmd
        print e.output

def deleteFolder(folder):
    cmd = delete_command + " -r " + folder
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print cmd
        print e.output

if __name__ == '__main__':
    pass
    
