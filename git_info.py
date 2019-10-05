import subprocess
import os   

def getBlame(f):
    folder = os.path.split(f)[0]
    cwd = os.getcwd()
    os.chdir(folder)
    cmd = "git blame --abbrev=0 -e '" + f + "'"
    try:        
        sub = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        response, err = sub.communicate()     
        response = response.decode() 
        err = err.decode()         
    except subprocess.CalledProcessError as e:
        print("Error: " + e.output)
        response = ''        
    except UnicodeDecodeError as e:
        print("Error: UnicodeDecodeError")
        response = '' 
    if len(err) > 0:
        if "no such path" in err:
            response = ''  # Ignore new file.
        else:
            print("Error: " + err)
            response = ''           
    if response == '':
        data_by_line = None
    else:
        data_by_line = response.split('\n')
    os.chdir(cwd)
    return data_by_line

def getAuthor(f,line):
    author = 'Not found'
    line += 1 # no line zero.
    folder = os.path.split(f)[0]
    cwd = os.getcwd()
    os.chdir(folder)
    cmd = "git blame -p -L " + str(line) + "," + str(line) + " '" + f + "'" 
    try:        
        sub = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        response, err = sub.communicate()    
        response = response.decode()    
        err = err.decode()
    except subprocess.CalledProcessError as e:
        print(e.output)
        response = ''        
    os.chdir(cwd)

    if 'fatal' in err:
        return author
        
    data_by_line = response.split('\n')

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
        response = response.decode()        
    except subprocess.CalledProcessError as e:
        print(e.output)
        response = ''        
    os.chdir(cwd)    
    return response

def getBranch(folder):
    cmd = 'git branch | grep \'*\''
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        response = response.decode()        
    except subprocess.CalledProcessError as e:
        print(e.output)
        response = ''        
    os.chdir(cwd)    
    return response[2:]

def getDiff(folder):
    cmd = 'git diff --name-status HEAD@{1}'
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        response = response.decode()
    except subprocess.CalledProcessError as e:
        print(e.output)
        response = ''        
    os.chdir(cwd)    
    return response

def checkoutRevision(folder, prev):
    cmd = 'git checkout HEAD~' + str(int(prev)) 
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        sub = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, err = sub.communicate()
        err  = err.decode()
    except subprocess.CalledProcessError as e:
        print('exception')
        print(e.output)      
    os.chdir(cwd)    
    return err

def resetHead(folder, branch): 
    cmd = 'git checkout ' + branch
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        response = response.decode()        
    except subprocess.CalledProcessError as e:
        print(e.output)
        response = ''        
    os.chdir(cwd)    
    return response

def getFileCount(folder):
    cmd = 'git ls-files | wc -l'
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        response = response.decode()
    except subprocess.CalledProcessError as e:
        print(e.output)
        response = ''        
    os.chdir(cwd)    
    return response.strip()

def getLineCount(folder):
    cmd = 'git ls-files | xargs wc -l'
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        response = response.decode()        
    except subprocess.CalledProcessError as e:
        print(e.output)
        response = ''        
    os.chdir(cwd)    
    response = response[:-1].split('\n')
    return response[-1]

def getLastCommit(folder):
    cmd = 'git log -1 --date=local'
    cwd = os.getcwd()
    os.chdir(folder)    
    try:
        response = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        response = response.decode()        
    except subprocess.CalledProcessError as e:
        print(e.output)
        response = ''        
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
    #url = url.decode()
    splat = url.split('/')
    splat = splat[-1].split('.')
    splat = splat[0].split('\n')
    return splat[0]

def getBaseRepoName(folder):
    repo = getRepo(folder)    
    base = parseRepo(repo)
    return base

if __name__ == '__main__':
    cwd = os.getcwd()
    f = cwd + '/birdseye.py'
    folder = os.path.split(f)[0]
    line = 20
    print()
    print("Get author: ")
    print(getAuthor(f,line))
    
    #branch = getBranch(folder)
    #print(resetHead(folder,branch))
    #print(checkoutRevision(folder,10))
    print()
    print("Line count: " + getLineCount(folder))

    file_count = getFileCount(folder)
    print()    
    print("File count: " + file_count)

    last_commit = getLastCommit(folder)
    print()    
    print("Last commit: ")
    print(last_commit)

    last_commit_date = getLastCommitDate(folder)
    print()
    print("Last commit date: ")
    print(last_commit_date)

    commit_number = getCommitNumber(folder)
    print()
    print("Last commit number: ")
    print(commit_number)

    repo = getRepo(folder)
    print()    
    print("Repo: " + repo)

    base = parseRepo(repo)
    print()
    print("Base: " + base)
    print("Base repo name: " + getBaseRepoName(folder))

    print()
    #print(resetHead(folder,branch))