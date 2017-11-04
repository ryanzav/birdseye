import subprocess
import os   
import string

def getAuthor(f,line):
    author = 'Not found'
    line += 1 # no line zero.
    folder = os.path.split(f)[0]
    cwd = os.getcwd()
    os.chdir(folder)
    cmd = "git blame -p -L " + str(line) + ',' + str(line) + ' ' + f
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output
        response = ''        
    os.chdir(cwd)

    data_by_line = string.split(response, '\n')

    for row in data_by_line:
        if row[:7] == 'author ':
            author = row[7:]
            break
    return author

def getRepo(folder):
    cmd = 'git config --get remote.origin.url'
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output
        reponse = ''        
    os.chdir(cwd)    
    return response

def parseRepo(url):
    splat = string.split(url,'/')
    splat = string.split(splat[-1],'.')
    splat = string.split(splat[0],'\n')
    return splat[0]

def getBaseRepoName(folder):
    repo = getRepo(folder)    
    base = parseRepo(repo)
    return base

if __name__ == '__main__':
   # f = "/Users/ryanz/Desktop/devices-nlight-air-sub-ghz/common/BLE-ctrl/BLE-task.c"
    f = "/Users/ryanz/Desktop/lib-nilon/nilon_log.py"
    folder = os.path.split(f)[0]
    line = 20
    print getAuthor(f,line)
    repo = getRepo(folder)
    print repo
    base = parseRepo(repo)
    print base
    print getBaseRepoName(folder)