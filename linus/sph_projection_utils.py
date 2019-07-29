from lie_learn.representations.SO3.spherical_harmonics import rsh
import numpy as np
import plotly
import plotly.plotly as py
from plotly.graph_objs import *
from plotly.graph_objs.layout.scene import *
import os
import matplotlib.pyplot as plt

#plotly.tools.set_credentials_file(username=os.environ['plotly_user'], api_key=os.environ['plotly_key'])

DEFAULT_AXIS = dict(showbackground=True,
                    backgroundcolor="rgb(230, 230,230)",
                    gridcolor="rgb(255, 255, 255)",
                    zerolinecolor="rgb(255, 255, 255)",
                    )

DEFAULT_LAYOUT = Layout(showlegend=False,
                        width=500,
                        height=500)

def get_random_coords(rnd, num_coords):
    coords = rnd.randn(num_coords,3)
    coords /= np.linalg.norm(coords, axis=-1, keepdims=True)
#   No origin for now
#     coords = np.concatenate((coords, [[0., 0., 0.]]), axis=0)
    return coords

def xyz_to_phi_theta(x):
    phi = np.arccos(x[...,2] / np.linalg.norm(x, axis=-1))
    theta = np.arctan2(x[..., 0], x[..., 1])
    return phi, theta

def get_Ylm_coeffs(phi, theta, L_max=5, sum=True):
    Ls = np.array([l for l in range(0, L_max + 1, 1) for m in range(-l, l+1)])
    Ls = Ls.reshape(*[-1, *np.ones(len(phi.shape), dtype=int)])
    Ms = np.array([m for l in range(0, L_max + 1, 1) for m in range(-l, l+1)])
    Ms = Ms.reshape(*[-1, *np.ones(len(phi.shape), dtype=int)])
    ylms = rsh(Ls, Ms, np.expand_dims(phi, axis=0), np.expand_dims(theta, axis=0))
    if sum:
        return np.sum(ylms, axis=-1)
    else:
        return ylms

def spherical_plotly_trace(coeff, L_max, num_angular_points=200):
    phi = np.expand_dims(np.linspace(0, np.pi, num_angular_points), axis=0)
    theta = np.expand_dims(np.linspace(0, 2 * np.pi, num_angular_points), axis=-1)
    
    # Phi is 0 to pi and theta 0 to 2 pi
    x = np.sin(phi) * np.sin(theta)
    y = np.sin(phi) * np.cos(theta)
    z = np.cos(phi) * np.ones(theta.shape)
    
    Ls = np.expand_dims(np.expand_dims(
        np.array([l for l in range(0, L_max + 1, 1) for m in range(-l, l+1)]), axis=-1), axis=-1)
    Ms = np.expand_dims(np.expand_dims(
        np.array([m for l in range(0, L_max + 1, 1) for m in range(-l, l+1)]), axis=-1), axis=-1)
    coeff = np.expand_dims(np.expand_dims(coeff, axis=-1), axis=-1)
    Ys = np.sum(coeff * rsh(Ls, Ms, np.expand_dims(phi, axis=0), np.expand_dims(theta, axis=0)), axis=0)
    return x, y, z, Ys

def visualize_spharm_and_coords(real_coords, pred_coord, L_max=8, num_angular_points=200):

    angles = xyz_to_phi_theta(real_coords)
    coeffs = get_Ylm_coeffs(*angles, L_max=L_max)
    print(coeffs.shape)
    x, y, z, Y_signal = spherical_plotly_trace(coeffs, L_max=L_max, num_angular_points=num_angular_points)
    
    x2, y2, z2 = real_coords[:, 0], real_coords[:, 1], real_coords[:, 2]
    x3, y3, z3 = pred_coord[:, 0], pred_coord[:, 1], pred_coord[:, 2]
    
    trace = Surface(x=x,
                y=y,
                z=z,
                showscale=True, 
                surfacecolor=Y_signal,
                opacity=0.75)
    
    trace2 = Scatter3d(x=x2,
                       y=y2,
                       z=z2, mode='markers')

    trace3 = Scatter3d(x=x3,
                       y=y3,
                       z=z3, mode='markers')
    
    data = [trace, trace2, trace3]
    fig = Figure(data=data, layout=DEFAULT_LAYOUT)
    return fig

def visualize_coeff_series(coeffs, L_max=8, num_angular_points=200, cmin=None, cmax=None): 
    make_trace = lambda x: spherical_plotly_trace(x, L_max=L_max, num_angular_points=num_angular_points)
    data = data = [Surface(x=x, y=y, z=z, visible=False, name = 'x= '+str(step),
                           showscale=True, surfacecolor=Y_signal, cmin=cmin, cmax=cmax) 
        for step, (x, y, z, Y_signal) in zip(range(len(coeffs)), map(make_trace, coeffs))] 

    data[0]['visible'] = True
    
    steps = []
    for i in range(len(data)):
        step = dict(
            method = 'restyle',  
            args = ['visible', [False] * len(data)],
        )
        step['args'][1][i] = True # Toggle i'th trace to "visible"
        steps.append(step)
        
    sliders = [dict(
        active = 0,
        currentvalue = {"prefix": "x: "},
        pad = {"t": 50},
        steps = steps
    )]
    
    layout = dict(sliders=sliders)
    fig = dict(data=data, layout=layout)
    return fig 
