#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Grace Li (li85)
Date: 8/10/2021

Contour plots to kinetic and total energy perturbations
of single Fourier mode in the x-y plane.

To avoid over crowding the plot with high frequency modes, we normalize the
x and y axis to only plot a couple periods. By setting the axis variables to 
Ny * x and Ny * y (or Nx*x and Nx*y in the Ny = 0 case), the scaling represents
how many periods in y (or in x for the Ny=0 case) we're at.

With this choice of axis, the density perturbation exponent depends on the ratio kx/ky.
The sonic/vortex and entropy exponents have no dependence on kx or ky alone
just on the ratio, which is present from the omega term contributing the kx.

The density, pressure, and velocity values and amplitude have no ky dependence,
only dependence on the ratio kx/ky.

However, the shock amplitude delta_xs has ky or kx only dependence instead of 
dependence on the ratio. This comes from the form of Eqn 32 and 35.
The magnitude also depends on epsilon_k, which just scales everything else as a multiple

"""

import numpy as np
from numpy import pi as pi
import matplotlib as mpl
import matplotlib.pyplot as plt
import math

import sys 
sys.path.append('..') #go up a directory to the GraceGrains parent directory
from LinearAnalysis.SingleMode import SingleModeSolution

# %% Visualize the energy perturbations in x-y space
# for fixed t to give the shock front xs just exiting (right edge) of the plot
 
fontsizes = {'XL': 20, 'L': 17, 'M': 12, 'S':11}

#Colormap
cmap = plt.get_cmap('Spectral')
nbins = 40 #number of levels to use in plot

# Define fixed parameters
Ny = 20
epsilon_k = 0.1 #epsilon_k scales all values, so we leave it fixed at 1
gamma = (5/3)
gamma_str = '5/3' #for labeling the plot

# Define parameters to try. Ratio = kx/ky, M1 = Mach number
ratios = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
Nxs = np.array(ratios) * Ny
M1s = [1.75, 2.25, 2.75]

# Nxs = [20]
# Nxs = [0.2*Ny]
# M1s = [1.75]

# Loop through parameters and generate plot
# for Nx in [1,5,10,20]:
for Nx in Nxs:
    for M1 in M1s:
        
        # Define simulation class
        sim = SingleModeSolution(Nx, Ny, M1, epsilon_k=epsilon_k, gamma=gamma)

        # Generate 2 2D grids for the x & y bounds
        # Normalize by Ny or Nx to only plot a couple periods and not be too crowded
        # Normalize by Nx if ky = 0
        if Ny == 0:
            x0, x1 = 0, 2*sim.Lx / Nx #initial and final x values
            y0, y1 = 0, 2*sim.Ly / Nx #initial and final y values
        # Otherwise normalize by Ny
        else:
            x0, x1 = 0, 2*sim.Lx / Ny #initial and final x values
            y0, y1 = 0, 2*sim.Ly / Ny #initial and final y values
        dx, dy = (x1-x0)/50, (y1-y0)/50 # make these smaller to increase the resolution
        x, y = np.mgrid[slice(x0, x1 + 2*dx, dx), slice(y0, y1 + 2*dy, dy)]

        #Calculate a t value that would just push the shock completely out of the plot box
        if sim.longwavelength: 
            if sim.Nx == 0:
                max_delta_xs = sim.epsilon_k * sim.R * sim.M2**2 / (sim.ky * math.sqrt(1-sim.M2**2))
            else:
                max_delta_xs = np.abs(np.real(sim.delta_xs(sim.phi / sim.omega)))
        else:
            max_delta_xs = np.abs(np.real(sim.delta_xs((pi / 2) * sim.omega)))
        t = (x1 + max_delta_xs) / (sim.M2 * sim.a2) 

        # Get z values to visualize: kinetic and total energy perturbation. 
        # Plot the preshock density perturbation in dimensionless x coordinates for comparison
        # x and t are bounds, so z should be the value *inside* those bounds.
        # Therefore, remove the last value from the z array.
        titles = [r"Kinetic Energy Perturbation", 
                  r"Total Energy Perturbation",
                  r"Preshock Density Perturbation"]
        zs = [sim.delta_KE(t, x, y), 
                  sim.delta_TE(t, x, y), 
                  sim.rho1*np.real(sim.delta_rho_rho1(t, x, y))]
        for i in range(len(zs)):
            zs[i] = zs[i][:-1, :-1]    
        
        #Plot the perturbation contour plots
        n_cols = 3
        fig, axs = plt.subplots(1, n_cols, figsize=(15,5.2))

        for index in range(n_cols):
            
            ax = axs[index] #specify axis
            z = zs[index] #specify z value
    
            # pick sensible levels, and define a normalization
            # instance which takes data values and translates those into levels.
            levels = mpl.ticker.MaxNLocator(nbins=nbins).tick_values(z.min(), z.max())
            norm = mpl.colors.BoundaryNorm(levels, ncolors=cmap.N, clip=True)
    
            # Plot contour plot
            if Ny == 0:
                cf = ax.contourf(Nx * x[:-1, :-1] + dx/2.,
                                 Nx * y[:-1, :-1] + dy/2., 
                                 z, levels=levels, cmap=cmap)
            else:
                cf = ax.contourf(Ny * x[:-1, :-1] + dx/2.,
                                 Ny * y[:-1, :-1] + dy/2., 
                                 z, levels=levels, cmap=cmap)
            
            #Formatting - colorbar
            fmt = mpl.ticker.ScalarFormatter(useMathText=True)
            fmt.set_powerlimits((0, 0))
            cbar = fig.colorbar(cf, ax=ax, format=fmt)
            cbar.ax.yaxis.get_offset_text().set_fontsize(fontsizes['S'])
            cbar.ax.tick_params(labelsize=fontsizes['M'])
            cbar.ax.yaxis.set_offset_position('left')                         
            cbar.update_ticks()
            
            #Formatting - title/axes/labels
            ax.set_title(titles[index], fontsize=fontsizes['L'])
            ax.tick_params(axis='x', labelsize=fontsizes['M'])
            ax.tick_params(axis='y', labelsize=fontsizes['M'])
            if sim.Ny == 0:
                ax.set_xlim(Nx*x0, Nx*x1)
                ax.set_ylim(Nx*y0, Nx*y1)
                ax.set_xlabel(r"$N_x \ x$")
                ax.set_ylabel(r"$N_x \ y$")
            else:
                ax.set_xlim(Ny*x0, Ny*x1)
                ax.set_ylim(Ny*y0, Ny*y1)
                ax.set_xlabel(r"$N_y \ x$")
                ax.set_ylabel(r"$N_y \ y$")
        
        if sim.Ny == 0:
            suptitle = r"$N_x=$"+ str(Nx) + r", $M_1=$" + str(M1) + r", $N_y=$" +str(Ny)
            savename = 'plots/energy/Ny-0--Nx-' + str(Nx) + '--M1-' + str(M1) + '.png'
        else:
            suptitle = r"$k_x/k_y=$"+ "{0:.2g}".format(Nx/Ny) + r", $M_1=$" + str(M1) + r", $N_y=$" +str(Ny)
            savename = 'plots/energy/ratio-'+ "{0:.2g}".format(Nx/Ny) + '--M1-' + str(M1) + '.png'
            
        suptitle = suptitle + r", $\epsilon_k=$" + str(epsilon_k) + r", $\gamma=$" + gamma_str
        fig.suptitle(suptitle, fontsize = fontsizes['XL'])
        
        fig.tight_layout(rect=[0, 0.03, 1, 0.94])
        
        plt.savefig(savename, facecolor='white', bbox_inches='tight')
        
        plt.close()
