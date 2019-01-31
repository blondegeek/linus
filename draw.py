import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
from matplotlib.collections import PatchCollection
from calcLattice import *

global tiles, positions_list, orientations_list, types_list, gluing_mapping

def addTripod(coord, orientation, type):
  posX, posY = coord

  height = 0.35
  pos0 = (0.02886, -height/2.)
  length = 0.95 - pos0[0]
  r1 = patches.Rectangle(pos0, length, height, alpha = 0.10)
  r2 = patches.Rectangle(pos0, length, height, alpha = 0.10)
  r3 = patches.Rectangle(pos0, length, height, alpha = 0.10)

  rot1 = mpl.transforms.Affine2D(). \
        rotate_deg(0 + orientation).translate(posX,posY)
  rot2 = mpl.transforms.Affine2D(). \
        rotate_deg(120 + orientation).translate(posX,posY)
  rot3 = mpl.transforms.Affine2D(). \
        rotate_deg(240 + orientation).translate(posX,posY)

  r1.set_transform(rot1)
  r2.set_transform(rot2)
  r3.set_transform(rot3)

  colors = np.array([0.+0.1*type, 0.3+0.1*type, 0.6+0.1*type])
  allPatches = [r1] + [r2] + [r3]

  return (colors, allPatches)

def make_figure():
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111)

    allPositions = positions_list

    allOrientations = orientations_list #in rad
    allTypes = types_list

    normi = mpl.colors.Normalize(vmin=0, vmax=1)
    colorArray = np.empty((0,3))
    patchesList = []

    for pos, ort, types in zip(allPositions, allOrientations, allTypes):
        newTripod = addTripod(pos, math.degrees(ort), types)
        colorArray = np.append(colorArray, [newTripod[0]], axis=0)
        patchesList += newTripod[1]

    collection = PatchCollection(
        patchesList, cmap=mpl.cm.Paired,
        norm=normi, alpha=0.8)
    collection.set_array(colorArray.flatten())
    ax.add_collection(collection)

    plt.axis('scaled')
    return fig
