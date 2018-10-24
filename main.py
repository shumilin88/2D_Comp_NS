# -*- coding: utf-8 -*-
"""
2D Compressible Navier-Stokes solver

Boundary condition options:
    -'wall' for bc_type will imply no-slip, dp and drho of 0; T must be specified
    -'zero_grad' will impose 0 normal gradient of that variable
    
Features to include (across all classes):
    -CoolProp library for material properties (track down needed functions)
    -speed of sound calculation (SolverClasses?)
    -Fix biasing meshing tools (this script and GeomClasses)
        ->Figure out biasing wrt dx and dy array sizes and mesh griding those (GeomClasses)
    -File reader for settings
    -

@author: Joseph
"""

##########################################################################
# ----------------------------------Libraries and classes
##########################################################################
#import numpy
from matplotlib import pyplot, cm
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
import os
import CoolProp.CoolProp as CP

#from GeomClasses import OneDimLine as OneDimLine
from GeomClasses import TwoDimPlanar as TwoDimPlanar
#import MatClasses as Mat
import SolverClasses as Solvers
import FileClasses

##########################################################################
# ------------------------------ Geometry, Domain and BCs Setup
#    Reference directions:
#    left-smallest x coordinate
#    right-largest x value
#    north-largest y coordinate
#    south-smallest y coordinate
##########################################################################
settings={} # Dictionary of problem settings
BCs={} # Dictionary of boundary conditions
# Geometry details
settings['Length']                  = 3*10**(-3)
settings['Width']                   = 6*10**(-3)
settings['Nodes_x']                 = 301
settings['Nodes_y']                 = 601
settings['Fluid']                   = 'Air'
settings['k']                       = CP.PropsSI('L','T', 300, 'P', 101325, settings['Fluid']) # If using constant value
settings['gamma']                   = CP.PropsSI('Cpmass','T',300,'P',101325,settings['Fluid'])/CP.PropsSI('Cvmass','T',300,'P',101325,settings['Fluid'])
settings['R']                       = CP.PropsSI('gas_constant','Air')/CP.PropsSI('M',settings['Fluid']) # Specific to fluid
settings['mu']                      = CP.PropsSI('V','T', 300, 'P', 101325, settings['Fluid'])

# Meshing details
settings['bias_type_x']             = None
settings['bias_size_x']             = 0.003 # Smallest element size (IN PROGRESS)
settings['bias_type_y']             = None
settings['bias_size_y']             = 10**(-6) # Smallest element size (IN PROGRESS)

# Boundary conditions
BCs['bc_type_left']                 = 'inlet'
BCs['bc_left_rho']                  = None
BCs['bc_left_u']                    = None
BCs['bc_left_v']                    = None
BCs['bc_left_p']                    = None
BCs['bc_left_T']                    = None
BCs['bc_type_right']                = 'outlet'
BCs['bc_right_rho']                 = None
BCs['bc_right_u']                   = None
BCs['bc_right_v']                   = None
BCs['bc_right_p']                   = None
BCs['bc_right_T']                   = None
BCs['bc_type_south']                = 'wall'
BCs['bc_south_rho']                 = None
BCs['bc_south_u']                   = None
BCs['bc_south_v']                   = None
BCs['bc_south_p']                   = None
BCs['bc_south_T']                   = 500
BCs['bc_type_north']                = 'wall'
BCs['bc_north_rho']                 = None
BCs['bc_north_u']                   = None
BCs['bc_north_v']                   = None
BCs['bc_north_p']                   = None
BCs['bc_north_T']                   = 500

# Initial conditions ????


# Time advancement
settings['CFL']                     = 0.05
settings['total_time_steps']        = 100


print 'Initializing geometry package...'
#domain=OneDimLine(L,Nx)
domain=TwoDimPlanar(settings)
domain.mesh()

##########################################################################
# -------------------------------------Initialize solver and domain
##########################################################################

print 'Initializing solver package...'
solver=Solvers.TwoDimPlanarSolve(domain, settings, BCs)

print 'Initializing domain...'
domain.rho[1:-1,1:-1]=1.2
domain.u[1:-1,1:-1]=0
domain.v[1:-1,1:-1]=0
domain.T[1:-1,1:-1]=300
#domain.p[:,:]=101325

domain.p[1:-1,1:-1]=domain.rho[1:-1,1:-1]*domain.R*domain.T[1:-1,1:-1]
solver.Apply_BCs()
#domain.T[1:-1,1:-1]=domain.p[1:-1,1:-1]/domain.rho[1:-1,1:-1]/domain.R

domain.rhou[:,:]=domain.rho[:,:]*domain.u[:,:]
domain.rhov[:,:]=domain.rho[:,:]*domain.v[:,:]
domain.rhoE[:,:]=domain.rho[:,:]*(0.5*(domain.u[:,:]**2+domain.v[:,:]**2) \
           +domain.Cv*domain.T[:,:])

##########################################################################
# -------------------------------------File setups
##########################################################################
print 'Initializing files...'
os.chdir('Tests')
datTime=str(datetime.date(datetime.now()))+'_'+'{:%H%M}'.format(datetime.time(datetime.now()))
isBinFile=False

#output_file=FileClasses.FileOut('Output_'+datTime, isBinFile)
input_file=FileClasses.FileOut('Input_'+datTime, isBinFile)

# Write headers to files
input_file.header('INPUT')
#output_file.header('OUTPUT')

# Write input file with settings
input_file.input_writer(settings, BCs)

##########################################################################
# -------------------------------------Solve
##########################################################################
print('######################################################\n')
print('#              2D Navier-Stokes Solver               #\n')
print('#              Created by J. Mark Epps               #\n')
print('#          Part of Masters Thesis at UW 2018-2020    #\n')
print('######################################################\n\n')

print 'Solving:'
for nt in range(settings['total_time_steps']):
    print 'Time step %i of %i'%(nt+1, settings['total_time_steps'])
    solver.Advance_Soln()

##########################################################################
# ------------------------------------Plots
##########################################################################
#fig=pyplot.figure(figsize=(7, 7), dpi=100)
#ax = fig.gca(projection='3d')
#ax.plot_surface(domain2.X, domain2.Y, domain2.T, rstride=1, cstride=1, cmap=cm.viridis,linewidth=0, antialiased=True)
#ax.set_xlim(0,0.001)
#ax.set_ylim(0.005,0.006)
#ax.set_zlim(300, 700)
#ax.set_xlabel('$x$ (m)')
#ax.set_ylabel('$y$ (m)')
#ax.set_zlabel('T (K)')

#fig2=pyplot.figure(figsize=(7,7))
#pyplot.plot(domain.Y[:,1]*1000, domain.T[:,1],marker='x')
#pyplot.xlabel('$y$ (mm)')
#pyplot.ylabel('T (K)')
#pyplot.title('Temperature distribution at 2nd x')
#pyplot.xlim(5,6)

print('Solver has finished its run')