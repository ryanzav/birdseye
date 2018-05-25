# birdseye
Create a bird's eye view of a project's source code.


[example]: example.png "example"

![alt text][example]

This does a git-blame on each line of a project's source code and then generates a color coded image of the source text for the entire project.

### Usage

```
usage: birdseye.py [-h] [--target TARGET] [--movie] [--revs REVS] [--no_info]
                   [--show_age] [--months MONTHS] [--age_only]

optional arguments:
  -h, --help       show this help message and exit
  --target TARGET  Target folder path.
  --movie          Movie demo.
  --revs REVS      Number of revisions to use in movie.
  --no_info        Exlude text overlay of git commit information.
  --show_age       Color code lines according to commit age AND author.
  --months MONTHS  Number of months to scale the color coding of commits to.
  --age_only       Only color code the lines by age, not author.
```

**Example Uses**

Display the module argument options:

    $ python birdseye.py --help

Generate an image of the latest birsdeye git repo itself:

    $ python birdseye.py

Generate an image of another git repo:

    $ python birdseye.py --target ../other_repo

Generate an image with the colors coded darker depending on the age of the commit, and scaled to the number of months argument.

    $ python birdseye.py --show_age --months 12 --no_info

Generate the same image but with the age color coded instead of the author and suppress the author info.

    $ python birdseye.py --show_age --age_only --no_info

Generate a movie of the last 20 git commits to the birdseye repo:

    $ python birdseye.py --movie --revs 20


