import calcLattice
from calcLattice import make_lattice, reset
import draw
from draw import addTripod, make_figure
import matplotlib as mpl
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
from calcLattice import tiles, positions_list, orientations_list, types_list
from calcLattice import gluing_mapping
from sklearn.cluster import KMeans
from sph_projection_utils import *
import matplotlib.cm as cm
import itertools

global tiles, positions_list, orientations_list, types_list, gluing_mapping

# TODO: Add ability to do radial shells
def ylms_within_r_cutoff(coords, r_cutoff, L_max=5):
    phi, theta = xyz_to_phi_theta(coords)
    r = np.linalg.norm(coords, axis=-1)
    r_shape = r.shape  # [N...]
    r.reshape(1, *r_shape) # [1, N...]
    r_cutoff = [r_cutoff] if type(r_cutoff) == float or type(r_cutoff) == int else r_cutoff
    sort_indices = np.argsort(r, axis=-1)
    ylms = get_Ylm_coeffs(phi, theta, sum=False, L_max=L_max)  # [R, N...]
    output = []
    for r_cut in r_cutoff:
        ylms_cutoff = np.where((r > 0.) & (r <= r_cut), ylms, np.zeros(ylms.shape))
        output.append(ylms_cutoff)
    return output

def norm_sph(array):
    N, L_sum = array.shape
    L_max = int(np.sqrt(L_sum - 1))
    output = np.zeros((N, L_max + 1))
    for L in range(L_max + 1):
        output[:, L] = np.linalg.norm(array[:, L ** 2: (L + 1) ** 2], axis=-1)
    return output

def get_sph_and_norm_clusters(coords, r_cutoff, n_clusters_sph=20, n_clusters_norm=10, round_sph=None, round_norm=None):
    ylms_cutoff = np.sum(ylms_within_r_cutoff(coords, r_cutoff)[0], axis=-1)
    local_cutoff_norms = norm_sph(ylms_cutoff.T)

    if round_sph:
        ylms_cutoff = np.round(ylms_cutoff, round_sph)
    if round_norm:
        local_cutoff_norms = np.round(local_cutoff_norms, round_norm)
    
    kmeans_norm = KMeans(n_clusters=10, random_state=0).fit(local_cutoff_norms)
    kmeans_sph = KMeans(n_clusters=20, random_state=0).fit(ylms_cutoff.T)

    norms_colors = kmeans_norm.fit_predict(local_cutoff_norms)
    sph_colors = kmeans_sph.fit_predict(ylms_cutoff.T)

    return  (kmeans_sph, sph_colors), (kmeans_norm, norms_colors)

def make_cluster_dict(labels, pos, classes=None):
    classes = np.max(colors) + 1 if classes is None else classes
    clusters_dict = {k: [] for k in range(classes)}
    for k,v in zip(labels, pos):
        clusters_dict[k].append(v)

def get_cluster_function(clusters, function):
    cluster_function_dict = {cluster: [] for cluster in clusters}
    pairs_dict = {cluster: [] for cluster in clusters}
    for cluster in clusters:
       points = clusters[cluster]
       if len(points) > 2:
           for pair in itertools.combinations(range(len(points)), 2):
               one, two = pair
               cluster_function_dict[cluster].append(
                   function(points[one], points[two]))
               pairs_dict[cluster].append((one, two))
    return cluster_function_dict, pairs_dict
