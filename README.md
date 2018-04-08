# birdseye
Create a bird's eye view of a project's source code. 


[example]: example.png "example"

![alt text][example]

This does a git-blame on each line of a project's source code and then generates a color coded image of the source text for the entire project.

Usage: 

Generate an image of the latest birsdeye git repo itself:
    python birdseye.py

Generate a movie of the last 20 git commits of the birdseye repo:
    python birdseye.py --movie --revs 20

Generate an image of another git repo:
    python birdseye.py --target ../other_repo
 
