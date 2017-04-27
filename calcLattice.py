import math
import numpy as np

####################################
# User-defined input
angles = ((0, 2*math.pi/3, 4*math.pi/3),
          (0, 2*math.pi/3, 4*math.pi/3),
          (0, 2*math.pi/3, 4*math.pi/3))
lengths = ((1, 1, 1),(1, 1, 1),(1,1,1))
IDs = ((1,2,3),(4,5,6),(7,8,9))

# gluing_mapping = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0} #dimer
# gluing_mapping = {1:1, 2:0, 3:0, 4:0, 5:0, 6:0} #dimer
# gluing_mapping = {1:2, 2:1, 3:0, 4:2, 5:1, 6:0} #hexamer
#
# gluing_mapping = {1:4, 2:3, 3:2, 4:1, 5:0, 6:0} #snow flake
# gluing_mapping = {1:4, 2:3, 3:2, 4:1, 5:0, 6:6} #chiral L
# gluing_mapping = {1:4, 2:3, 3:2, 4:1, 5:5, 6:0} #chiral R

# gluing_mapping = {1:1, 2:2, 3:3, 4:1, 5:5, 6:6} #lattice without holes

# gluing_mapping = {1:4, 2:3, 3:2, 4:1, 5:0, 6:7, 7:6, 8:0, 9:0} #chiral snowflake
# gluing_mapping = {1:4, 2:3, 3:2, 4:1, 5:0, 6:7, 7:6, 8:8, 9:0} # big holes
gluing_mapping = {1:1, 2:4, 3:0, 4:2, 5:0, 6:8, 7:9, 8:6, 9:7} #triangular holes

max_iterations = 300
####################################

class Tile:
    """
    Array with attributes for each tile.
    Orientation is referent to global origin
    """
    def __init__(self):
        self.position       = []
        self.orientation    = []
        self.type           = []
        self.arms           = []

    def add_position(self, position):
        self.position.append(position)
    def add_orientation(self, orientation):
        self.orientation.append(orientation)
    def add_type(self, type):
        self.type.append(type)
    def add_arms(self, arm):
        self.arms.append(arm)

class Arm:
    """
    Array with attributes for each arm.
    Angle is referent to the particle
    """
    def __init__(self):
        self.length         = []
        self.angle          = []
        self.ID             = []

    def add_length(self, length):
        self.length.append(length)
    def add_angle(self, angle):
        self.angle.append(angle)
    def add_ID(self, ID):
        self.ID.append(ID)

def populate_arms(tile):
    tileType = tile.type[0]
    for angle, length, ID in zip(angles[tileType],
                                 lengths[tileType],
                                 IDs[tileType]):
        new_arm = Arm()
        new_arm.add_length(length)
        new_arm.add_angle(angle)
        new_arm.add_ID(ID)
        tile.add_arms(new_arm)
    return tile

def make_tile(position, orientation, type):
    new_tile = Tile()
    new_tile.add_position(position)
    new_tile.add_orientation(orientation)
    new_tile.add_type(type)
    new_tile = populate_arms(new_tile)
    return new_tile

def find_complement_particle_type(arm_ID):
    complement_arm_ID = gluing_mapping[arm_ID]
    not_in = []
    for index, ID in enumerate(IDs, start = 0):
        if complement_arm_ID in ID:
            particle_type = index
    return particle_type

def find_complement_particle_orientation(original_particle,
                                         original_arm_index,
                                         complement_particle_type,
                                         complement_arm_index
                                         ):
    original_arm_angle = original_particle.arms[original_arm_index].angle[0]
    original_particle_orientation = original_particle.orientation[0]
    # rotate original arm according to the global particle orientation
    original_arm_direction = original_arm_angle + original_particle_orientation
    complement_arm_angle = angles[complement_particle_type][complement_arm_index]
    #rotate it so they face each other
    complement_particle_orientation = math.pi + original_arm_direction - complement_arm_angle
    return(complement_particle_orientation)

def find_complement_particle_position(original_particle,
                                      original_arm_index,
                                      complement_particle_type,
                                      complement_arm_index
                                      ):
    original_arm_angle = original_particle.arms[original_arm_index].angle[0]
    original_particle_orientation = original_particle.orientation[0]
    original_particle_position = original_particle.position[0]
    # rotate original arm according to the global particle orientation
    original_arm_direction = original_arm_angle + original_particle_orientation
    original_arm_direction_vector = (math.cos(original_arm_direction),
                                     math.sin(original_arm_direction))

    original_arm_length = original_particle.arms[original_arm_index].length[0]

    complement_particle_position = (original_particle_position[0] \
                                   + 2.0 * original_arm_direction_vector[0],
                                   original_particle_position[1] \
                                   + 2.0 * original_arm_direction_vector[1])
    #will break in python 3: do list(map(round, complement_particle_position))
    complement_particle_position = [ round(x, 3) for x in complement_particle_position ]
    return(complement_particle_position)

tiles = []
positions_list = [(0.,0.)]
orientations_list = [0.]
types_list = [0]

def make_lattice():
    first_tile = make_tile((0.,0.),0.,0)
    tiles.append(first_tile)

    for tile in tiles:
        if (len(tiles) > max_iterations):
            break
        for arm_index, arm in enumerate(tile.arms, start = 0):
            arm_ID = arm.ID[0]
            complement_arm_ID = gluing_mapping[arm_ID]
            if (gluing_mapping[arm_ID] != 0):
                complement_particle_type = find_complement_particle_type(arm_ID)
                complement_arm_index = IDs[complement_particle_type].index(complement_arm_ID)
                complement_particle_orientation = \
                  find_complement_particle_orientation(tile, arm_index,
                                                       complement_particle_type,
                                                       complement_arm_index)
                complement_particle_position = \
                  find_complement_particle_position(tile, arm_index,
                                                    complement_particle_type,
                                                    complement_arm_index)
                complement_particle_position = (complement_particle_position[0],
                                                complement_particle_position[1])
                if complement_particle_position not in positions_list:
                    positions_list.append(complement_particle_position)
                    orientations_list.append(complement_particle_orientation)
                    types_list.append(complement_particle_type)
                    new_tile = make_tile(complement_particle_position,
                                         complement_particle_orientation,
                                         complement_particle_type)
                    tiles.append(new_tile)
    pass

make_lattice()
