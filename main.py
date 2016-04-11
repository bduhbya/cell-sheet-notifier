#! /usr/bin/python
from find_panini import checkForPaniniUpdates

updateFuncs = [checkForPaniniUpdates]

def main():
    for update in updateFuncs:
        update()

if __name__ == "__main__":
    main()
