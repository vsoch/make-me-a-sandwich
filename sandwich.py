import copy
import random
import pygame

# Game options
pygame.init()
running = True

# Number of rows and columns of sandwiches on the board.
num_rows = 10
num_cols = 10

# A list of sandwich layer colors.
colors = [(0, 0, 255), (0, 255, 0), (0, 0, 100), (0, 100, 0)]

# Which layer indices are compatible.
compatible_types = set([frozenset([0, 2]), frozenset([1, 3])])

# Size of each sandwich.
square_x = 60
square_y = 60

# Boundary between multiple sandwich layers.
boundary_size = 4

screen = pygame.display.set_mode([num_rows * square_x, num_cols * square_y])


class GridElement:
    def __init__(self, x_low, y_low, x_high, y_high, type_index=None):
        self._prev_clicking = False
        self.selected = False
        self.x_low = x_low
        self.x_high = x_high
        self.y_low = y_low
        self.y_high = y_high
        if type_index is None:
            self.type_indices = []
        else:
            self.type_indices = [type_index]

    def check_clicked(self):
        """Check if the element has been clicked (and click is released)."""
        clicking = pygame.mouse.get_pressed()[0]
        x, y = pygame.mouse.get_pos()

        if clicking and self.x_low < x < self.x_high and self.y_low < y < self.y_high:
            clicking = True
        else:
            clicking = False

        if not clicking and self._prev_clicking:
            clicked = True
        else:
            clicked = False

        self._prev_clicking = clicking
        return clicked

    def toggle_selected(self):
        self.selected = not self.selected

    def draw(self):
        """Draw the sandwich, including multiple layers and a boundary if selected."""
        for i, type_index in enumerate(self.type_indices):
            # Draw the layers.
            height = (self.y_high - self.y_low) // len(self.type_indices)
            pygame.draw.rect(
                screen, colors[type_index],
                (self.x_low, self.y_low + height * i, self.x_high - self.x_low, height))
            # Draw a line between layers.
            if i > 0:
                pygame.draw.line(screen, (0, 0, 0),
                (self.x_low, self.y_low + height * i), (self.x_high, self.y_low + height * i), 6)
        # draw boundary if selected.
        if self.selected:
            pygame.draw.rect(
            	screen, (255, 255, 0),
                             (self.x_low,
                              self.y_low,
                              self.x_high - self.x_low - boundary_size / 2,
                              self.y_high - self.y_low - boundary_size / 2), boundary_size)

def get_neighbors(i, j):
    neighbors = []
    if i > 0:
        neighbors.append((i-1, j))
    if j > 0:
        neighbors.append((i, j-1))
    if i < num_rows - 1:
        neighbors.append((i+1, j))
    if j < num_cols - 1:
        neighbors.append((i, j+1))
    return neighbors

# The grid stores all the sandwiches.
grid = {}
for i in range(num_rows):
    for j in range(num_cols):
        grid[(i, j)] = GridElement(
            i * square_x,
            j * square_y,
            i * square_x + square_x,
            j * square_y + square_y,
            type_index=random.randrange(len(colors)))

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    # Keep track of all elements to delete.
    all_deleted = set()

    # Iterate through all elements in the grid.
    for loc, el in grid.items():
        # Exit early if not clicked.
        if not el.check_clicked():
            continue
        # If clicked, toggle selected.
        el.toggle_selected()

        # Get neighbors to check for action.
        neighbor_locs = set(get_neighbors(*loc))
        # Only add to selected element if it contains a single type.
        if len(el.type_indices) != 1:
            continue

        # Iterate until no element is deleted.
        # If multiple neighbors are selected it's possible to make a sandwich with more than 2 layers.
        while True:
            deleted = set()
            # Iterate through neighbors.
            for loc in neighbor_locs:
                # Only use selected elements.
                if not grid[loc].selected:
                    continue
                neighbor_el = grid[loc]
                # Only allow adding an element if it has a single type.
                if len(neighbor_el.type_indices) != 1:
                    continue
                neighbor_type = neighbor_el.type_indices[0]
                # Check if the neighbor layer can be added from either the top or bottom.
                # Delete the neighbor if combined.
                if frozenset([el.type_indices[0], neighbor_type]) in compatible_types:
                    el.type_indices.insert(0, neighbor_type)
                    deleted.add(loc)
                elif frozenset([el.type_indices[-1], neighbor_type]) in compatible_types:
                    el.type_indices.append(neighbor_type)
                    deleted.add(loc)
            # Update the neighbors. New layers may be added after adding some of the neighbors.
            neighbor_locs = neighbor_locs - deleted
            # Update all deleted elements.
            all_deleted.update(deleted)
            if not deleted:
                break

    # Delete elements.
    for del_i, del_j in all_deleted:
        # Make a new element at the top of the column
        new_el = GridElement(
                del_i * square_x,
                -square_y,
                del_i * square_x + square_x,
                0,
                type_index=random.randrange(len(colors)))
        # Add the new element to the grid.
        grid[del_i, -1] = new_el
        # Specify elements to be moved (there could be an animation).
        moving_column = {loc: el for loc, el in grid.items() if loc[0] == del_i and loc[1] < del_j}
        # Move the column down.
        for loc in moving_column:
            el = grid[loc]
            el.y_low += square_y
            el.y_high += square_y
            el.selected = False
        # Update the location on the grid.
        for loc, el in moving_column.items():
            grid[(loc[0], loc[1] + 1)] = el

    # Draw the elements.
    for el in grid.values():
        el.draw()
    pygame.display.flip()

pygame.quit()
