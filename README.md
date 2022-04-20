# A-star-Pathfinding-algorithm
A visualization of the A-star-Pathfinding-algorithm

How to use:
1. Choose a Tile for the start and one for the end. 
2. Choose as many tiles as you wish to be barriers (=RED). You can hold down the mouse button to draw the red tiles.
3. Press Space to let the algorithm run. 
4. If there is a solution, a message box will pop up showing you the disatance of the optimal path. Otherwise, you will be told that there is no valid solution

At any point, you may press Backspace to clear all Tiles and to restart. 

Legend:

ORANGE = Start and End of Path 

GREY = not explored tile

GREEN = Explored tile; meaning that all its direct neighbours' distances have been Calculated (= all neighbours are BLUE) 

BLUE = Tile that hasn´t been explored, but the distances to the start and end file have been calculated 

RED = Those tiles are Barriers and their distances to the start and end should not be calculated

