# Python File System Visualizer
A simple python script that visualizes the chosen folder's structure using Pygame.

File/folder size is proportional to the size of the rectangle on the screen, and 
structure is displayed by the "expansion" of the folders.

## Usage
>$ python files_visualizer.py folder_directory

## Controls
Left click: Expand folder

Right click: Close folder

e: Expand folder and its subfolders

c: Close everything but the top level folder

## Blurb
The original concept for this came from a school assignment; however, there 
were several aspects of the original program I did not like. Namely,
- The original appearance of the program is awful
- Information was displayed in a sub-optimal way
- The controls were not optimal, with several unnecessary features

This, combined with the professor specifically stating that none of the 
assignment's starter code could be distributed, lead to me making a new version 
of the program from scratch. The only parts I have kept are the code I wrote
myself for that assignment.