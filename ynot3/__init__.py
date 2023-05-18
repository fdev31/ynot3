#!/bin/env python
import os
import sys


def run():
    try:
        image = sys.argv[1]
    except IndexError:
        print("Usage: python %s <image>" % sys.argv[0])
    else:
        os.environ["SDL_VIDEODRIVER"] = "x11"
        from .gui import main

        main(image)


if __name__ == "__main__":
    run()
