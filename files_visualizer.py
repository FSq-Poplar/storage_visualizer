from __future__ import annotations
import os
import math
import pygame
import sys
from random import randint
from typing import List, Tuple, Optional

DIMENSIONS = (854, 480)


class FileSystemTree:
    """ A tree which represents the data of a file structure.
     rect, _expanded and _colour: used for the visualization
     data_size and _name: data about the file/folder
     _subtrees and _parent_tree: simply part of its tree structure"""
    rect: Tuple[int, int, int, int] = (0, 0, 0, 0)
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[FileSystemTree]
    _parent_tree: Optional[FileSystemTree] = None
    _expanded: bool = False

    def __init__(self, directory: str) -> None:
        """ Creates a FileSystemTree representing the folder """
        self._name = os.path.basename(directory)
        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))
        self._init_subtrees(directory)
        self._init_data_size(directory)

    def _init_subtrees(self, directory: str) -> None:
        """ init helper which creates and sets up subtrees """
        self._subtrees = []
        if os.path.isdir(directory):
            for filename in os.listdir(directory):
                subitem = FileSystemTree(os.path.join(directory, filename))
                self._subtrees.append(subitem)

        for subtree in self._subtrees:
            subtree._parent_tree = self

    def _init_data_size(self, directory: str) -> None:
        """ init helper which computes the size of the tree's directory """
        if len(self._subtrees) == 0:
            if os.path.isdir(directory):
                self.data_size = 1
            else:
                self.data_size = os.path.getsize(directory)
        elif self._name is not None:
            total_size = 0
            for tree in self._subtrees:
                total_size += tree.data_size
            self.data_size = total_size

    def construct_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """ Makes and assigns the rectangles for a directory """
        self.rect = rect
        x, y, width, height = rect
        total_area = width * height

        if len(self._subtrees) == 0 or height == 0 or width == 0:
            self.rect = rect
        elif height >= width:
            self._construct_horizontal_recs(rect, total_area)
        elif height < width:
            self._construct_vertical_recs(rect, total_area)

    def _construct_horizontal_recs(self, rect: Tuple[int, int, int, int],
                                   total_area: int) -> None:
        """ Case if rectangles should be horizontal """
        counter = 1
        x, y, width, height = rect
        for subtree in self._subtrees:
            if self.data_size != 0:
                target_ratio = subtree.data_size / self.data_size
            else:
                target_ratio = 0
            target_area = target_ratio * total_area

            if counter == len(self._subtrees):
                subtree.rect = (x, y, width, height)
                subtree.construct_rectangles((x, y, width, height))
            else:
                y_change = math.floor(target_area / width)
                height -= y_change
                subtree.construct_rectangles((x, y, width, y_change))
                y += y_change
                counter += 1

    def _construct_vertical_recs(self, rect: Tuple[int, int, int, int],
                                 total_area: int):
        """ Case if rectangles should be vertical """
        counter = 1
        x, y, width, height = rect
        for subtree in self._subtrees:
            if self.data_size != 0:
                target_ratio = subtree.data_size / self.data_size
            else:
                target_ratio = 0
            target_area = target_ratio * total_area

            if counter == len(self._subtrees):
                subtree.rect = (x, y, width, height)
                subtree.construct_rectangles((x, y, width, height))
            else:
                x_change = math.floor(target_area / height)
                width -= x_change
                subtree.construct_rectangles((x, y, x_change, height))
                x += x_change
                counter += 1

    def get_visible_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                                   Tuple[int, int, int]]]:
        """ Returns a list of the recs of expanded rectangles """
        if self._expanded is False:
            return [(self.rect, self._colour)]
        else:
            ret = []
            for subtree in self._subtrees:
                ret.extend(subtree.get_visible_rectangles())
            return ret

    def expand(self, expand_all: bool) -> None:
        """ Expands the rectangle. Also expands all subtrees if expand_all """
        if len(self._subtrees) != 0:
            self._expanded = True
        if expand_all:
            for subtree in self._subtrees:
                subtree.expand(True)
            return None

    def collapse(self, collapse_all: bool) -> None:
        """ Collapses a tree into its parent, all trees if collapse_all """
        traverse_tree = self
        if collapse_all:
            while traverse_tree._parent_tree is not None:
                traverse_tree = traverse_tree._parent_tree
        else:
            traverse_tree = traverse_tree._parent_tree
        traverse_tree._collapse_helper()

    def _collapse_helper(self) -> None:
        """ Collapses the tree and its subtrees """
        self._expanded = False
        for subtree in self._subtrees:
            subtree._collapse_helper()

    def get_tree_at_position(self, pos: Tuple[int, int]) -> \
            Optional[FileSystemTree]:
        """ Returns the tree at a given position """
        visible_recs = []
        for rect_and_color in self.get_visible_rectangles():
            visible_recs.append(rect_and_color[0])  # Removing color tuples

        possible_rects = []
        for rect in visible_recs:
            if rect[0] <= pos[0] <= rect[0] + rect[2] \
                    and rect[1] <= pos[1] <= rect[1] + rect[3]:
                possible_rects.append(rect)

        return self._find_tree_by_rect(
            self._conflict_resolver(possible_rects, pos))

    def _find_tree_by_rect(self, rect: Tuple) -> Optional[FileSystemTree]:
        """ Returns the tree which is represented by a given rectangle """
        if self.rect is rect:
            return self
        else:
            for subtree in self._subtrees:
                if subtree._find_tree_by_rect(rect) is not None:
                    return subtree._find_tree_by_rect(rect)
        return None

    @staticmethod
    def _conflict_resolver(possible_rects: List, pos: Tuple) \
            -> Optional[Tuple[int, int, int, int]]:
        """ Picks a single rectangle if pos lies on the edge of several """
        x_conflict = 0
        y_conflict = 0

        for rec in possible_rects:
            if rec[0] == pos[0]:
                x_conflict += 0.5
            if rec[0] + rec[2] == pos[0]:
                x_conflict += 0.5
            if rec[1] == pos[1]:
                y_conflict += 0.5
            if rec[1] + rec[3] == pos[1]:
                y_conflict += 0.5

        for rect in possible_rects:
            if x_conflict >= 1 and rect[0] == pos[0]:
                possible_rects.remove(rect)
            elif y_conflict >= 1 and rect[1] == pos[1]:
                possible_rects.remove(rect)

        if len(possible_rects) == 0:
            return None
        else:
            return possible_rects[0]

    def get_directory(self) -> str:
        """ Returns the file or folder's directory """
        if self._parent_tree is None:
            return self._name
        else:
            return self._parent_tree.get_directory() + os.sep + self._name


def visualize(tree: FileSystemTree) -> None:
    """ Draws the initial state of the visualization using pygame """
    pygame.init()
    screen = pygame.display.set_mode(DIMENSIONS)
    pygame.display.set_caption("Simple Python File System Visualizer")
    _render(screen, tree, None)
    tree.construct_rectangles((0, 0, DIMENSIONS[0], DIMENSIONS[1] - 25))
    tree.expand(True)
    _input_loop(screen, tree)


def _render(surface: pygame.Surface, tree: Optional[FileSystemTree],
            selected_item: Optional[FileSystemTree]) -> None:
    """ Updates the visual when any changes are made """
    _clear_screen(surface)
    subscreen = surface.subsurface((0, 0, DIMENSIONS[0], DIMENSIONS[1] - 25))
    for rect in tree.get_visible_rectangles():
        pygame.draw.rect(subscreen, rect[1], rect[0])
    if selected_item is not None:
        pygame.draw.rect(subscreen, (255, 255, 255), selected_item.rect, 2)
    _render_text(surface, _get_display_text(selected_item))
    pygame.display.flip()


def _clear_screen(surface: pygame.Surface) -> None:
    """ Resets the screen so text is not messed up """
    pygame.draw.rect(surface, pygame.color.THECOLORS['black'],
                     (0, 0, DIMENSIONS[0], DIMENSIONS[1]))


def _render_text(screen: pygame.Surface, text: str) -> None:
    """ Shows the information pertinent to the selected directory """
    font = pygame.font.SysFont("Segoe UI", 25 - 8)
    text_surface = font.render(text, 1, pygame.color.THECOLORS['white'])
    text_pos = (5, DIMENSIONS[1] - 25)
    screen.blit(text_surface, text_pos)


def _input_loop(screen: pygame.Surface, tree: FileSystemTree) -> None:
    """ Infinite loop that changes the visuals based on a user input """
    while True:
        event = pygame.event.poll()
        selected = tree.get_tree_at_position(pygame.mouse.get_pos())

        if event.type == pygame.QUIT:
            return None
        elif event.type == pygame.MOUSEBUTTONUP:
            _handle_click(event.button, selected)
        elif event.type == pygame.KEYUP and selected is not None:
            if event.key == pygame.K_e:
                selected.expand(True)
            elif event.key == pygame.K_c:
                selected.collapse(True)

        _render(screen, tree, selected)


def _handle_click(mouse_act: int, selected: Optional[FileSystemTree]) -> None:
    """ Expands selected if left click, collapses otherwise """
    if selected is None:
        pass
    elif mouse_act == 1:
        selected.expand(False)
    elif mouse_act == 3:
        selected.collapse(False)


def _get_display_text(selected: Optional[FileSystemTree]) -> str:
    """ Returns a string giving data for the selected directory """
    if selected is None:
        return "No file or folder selected."
    else:
        return selected.get_directory() + \
               " (Size: {})".format(_get_size_text(selected))


def _get_size_text(selected: Optional[FileSystemTree]) -> str:
    """ Converts the size to something more readable """
    size_bits = selected.data_size
    unit = " Bytes"
    if size_bits > 1024:
        size_bits = round(size_bits / 1024, 2)
        unit = " KB"
    elif size_bits > 1048576:
        size_bits = round(size_bits / 1048576, 2)
        unit = " MB"
    elif size_bits > 1073741824:
        size_bits = round(size_bits / 1073741824, 2)
        unit = " GB"
    return str(size_bits) + unit


""" Block which is actually run """
file_tree = FileSystemTree(sys.argv[1])
visualize(file_tree)
