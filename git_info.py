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

def getDiff(folder):
    cmd = 'git diff --name-status HEAD@{1}'
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output
        reponse = ''        
    os.chdir(cwd)    
    return response



def checkoutRevision(folder, prev):
    cmd = 'git checkout HEAD~' + str(int(prev)) 
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output
        reponse = ''        
    os.chdir(cwd)    
    return response

def resetHead(folder):
    cmd = 'git checkout develop'
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output
        reponse = ''        
    os.chdir(cwd)    
    return response

def getFileCount(folder):
    cmd = 'git ls-files | wc -l'
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output
        reponse = ''        
    os.chdir(cwd)    
    return string.strip(response)

def getLineCount(folder):
    cmd = 'git ls-files | xargs wc -l'
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output
        reponse = ''        
    os.chdir(cwd)    
    response = response[:-1].split('\n')
    return response[-1]

def getLastCommit(folder):
    cmd = 'git log -1 --date=local'
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    except subprocess.CalledProcessError as e:
        print e.output
        reponse = ''        
    os.chdir(cwd)    
    return response

def getLastCommitDate(folder):
    msg = getLastCommit(folder)
    lines = msg.split('\n')
    for line in lines:
        if 'Date:' in line:
            return line[5:].strip()
    return 'Date not found.'

def getCommitNumber(folder):
    msg = getLastCommit(folder)
    lines = msg.split('\n')
    return lines[0][7:14]

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
    f = "/Users/ryanz/Desktop/lib-nilon/nlight.py"
    folder = os.path.split(f)[0]
    line = 20
    print getAuthor(f,line)

    print resetHead(folder)
    print checkoutRevision(folder,10)

    print 'lines: ' + getLineCount(folder)

    file_count = getFileCount(folder)
    print file_count

    last_commit = getLastCommit(folder)
    print last_commit

    last_commit_date = getLastCommitDate(folder)
    print last_commit_date

    commit_number = getCommitNumber(folder)
    print commit_number

    repo = getRepo(folder)
    print repo
    

    base = parseRepo(repo)
    print base
    print getBaseRepoName(folder)