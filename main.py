# -*- coding: utf-8 -*-
"""
2D Compressible Navier-Stokes solver

Boundary condition options:
    -'wall' for bc_type will imply no-slip, dp of 0; T must be specified
    -'zero_grad' will impose 0 normal gradient of that variable
    
Features to include (across all classes):
    -CoolProp library for material properties (track down needed functions)
    -Fix biasing meshing tools (this script and GeomClasses)
        ->Figure out biasing wrt dx and dy array sizes and mesh griding those (GeomClasses)
    -File reader for settings
    -periodic boundary conditions (SolverClasses)
    -recode Calculate_Stress() in SolverClasses to use compute_Flux() function; make way for WENO scheme
    -total pressure for inlet calculations

ME765 project setup:
BCs['bc_type_left']                 = 'periodic'
BCs['bc_left_rho']                  = None
BCs['bc_left_u']                    = None
BCs['bc_left_v']                    = None
BCs['bc_left_p']                    = None
BCs['bc_left_T']                    = None
# numpy.linspace(400, 900, settings['Nodes_y'])
BCs['bc_type_right']                = 'periodic'
BCs['bc_right_rho']                 = None
BCs['bc_right_u']                   = None
BCs['bc_right_v']                   = None
BCs['bc_right_p']                   = None
BCs['bc_right_T']                   = None
# numpy.linspace(400, 900, settings['Nodes_y'])
BCs['bc_type_south']                = 'wall'
BCs['bc_south_rho']                 = None
BCs['bc_south_u']                   = None
BCs['bc_south_v']                   = None
BCs['bc_south_p']                   = None
BCs['bc_south_T']                   = 600
# numpy.linspace(400, 900, settings['Nodes_x'])
BCs['bc_type_north']                = 'wall'
BCs['bc_north_rho']                 = None
BCs['bc_north_u']                   = None
BCs['bc_north_v']                   = None
BCs['bc_north_p']                   = None
BCs['bc_north_T']                   = 300
# numpy.linspace(400, 900, settings['Nodes_x'])

Inlet/outlet
BCs['bc_type_left']                 = 'inlet'
BCs['bc_left_rho']                  = None
BCs['bc_left_u']                    = 5.0
BCs['bc_left_v']                    = 0
BCs['bc_left_p']                    = 2*101325
BCs['bc_left_T']                    = 300
# numpy.linspace(400, 900, settings['Nodes_y'])
BCs['bc_type_right']                = 'outlet'
BCs['bc_right_rho']                 = None
BCs['bc_right_u']                   = None
BCs['bc_right_v']                   = None
BCs['bc_right_p']                   = 101325
BCs['bc_right_T']                   = None
# numpy.linspace(400, 900, settings['Nodes_y'])
BCs['bc_type_south']                = 'wall'
BCs['bc_south_rho']                 = None
BCs['bc_south_u']                   = None
BCs['bc_south_v']                   = None
BCs['bc_south_p']                   = None
BCs['bc_south_T']                   = 600
# numpy.linspace(400, 900, settings['Nodes_x'])
BCs['bc_type_north']                = 'wall'
BCs['bc_north_rho']                 = None
BCs['bc_north_u']                   = None
BCs['bc_north_v']                   = None
BCs['bc_north_p']                   = None
BCs['bc_north_T']                   = 600
# numpy.linspace(400, 900, settings['Nodes_x'])

BCs['bc_type_left']                 = 'wall'
BCs['bc_left_rho']                  = None
BCs['bc_left_u']                    = None
BCs['bc_left_v']                    = None
BCs['bc_left_p']                    = None
BCs['bc_left_T']                    = 300
# numpy.linspace(400, 900, settings['Nodes_y'])
BCs['bc_type_right']                = 'wall'
BCs['bc_right_rho']                 = None
BCs['bc_right_u']                   = None
BCs['bc_right_v']                   = None
BCs['bc_right_p']                   = None
BCs['bc_right_T']                   = 300
# numpy.linspace(400, 900, settings['Nodes_y'])
BCs['bc_type_south']                = 'wall'
BCs['bc_south_rho']                 = None
BCs['bc_south_u']                   = None
BCs['bc_south_v']                   = None
BCs['bc_south_p']                   = None
BCs['bc_south_T']                   = 300
# numpy.linspace(400, 900, settings['Nodes_x'])
BCs['bc_type_north']                = 'wall'
BCs['bc_north_rho']                 = None
BCs['bc_north_u']                   = None
BCs['bc_north_v']                   = None
BCs['bc_north_p']                   = None
BCs['bc_north_T']                   = 300
# numpy.linspace(400, 900, settings['Nodes_x'])
@author: Joseph
"""
# Parabolic velocity profile creator
# Assumption of equally spaced y coordinates
#def parabolic_Vel(u_max, u_min, y):
#    u=numpy.zeros_like(y)
#    u[0]=u_min
#    u[-1]=u_min
#    smallest=self.xbias[1]
#    u[:int(len(y)/2)]=numpy.linspace(2*self.L/(self.Nx-1)-smallest,smallest,(self.Nx-1)/2)
#    u[int(len(y)/2):-1]=numpy.linspace(smallest,2*self.L/(self.Nx-1)-smallest,(self.Nx-1)/2)
#    
#    return u


##########################################################################
# ----------------------------------Libraries and classes
##########################################################################
import numpy
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
settings['Length']                  = 3.0
settings['Width']                   = 3.0
settings['Nodes_x']                 = 60
settings['Nodes_y']                 = 60
settings['Fluid']                   = 'Air'
#CP.PropsSI('L','T', 300, 'P', 101325, settings['Fluid'])
settings['k']                       = CP.PropsSI('L','T', 300, 'P', 101325, settings['Fluid']) # If using constant value
settings['gamma']                   = CP.PropsSI('Cpmass','T',300,'P',101325,settings['Fluid'])/CP.PropsSI('Cvmass','T',300,'P',101325,settings['Fluid'])
settings['R']                       = CP.PropsSI('gas_constant','Air')/CP.PropsSI('M',settings['Fluid']) # Specific to fluid
settings['mu']                      = CP.PropsSI('V','T', 300, 'P', 101325, settings['Fluid'])#0.02
settings['Gravity_x']               = 0
settings['Gravity_y']               = -9.81

# Meshing details
"""
Biasing options:
    -'OneWayUp'   for linearly increasing element sizes with increasing x/y
    -'OneWayDown' for linearly decreasing element sizes with increasing x/y
    -'TwoWayEnd'  for linearly increasing sizes till middle, then decrease again
    -'TwoWayMid'  for linearly decreasing sizes till middle, then increase again
    -size         is the smallest element size based on above selection
"""
settings['bias_type_x']             = None
settings['bias_size_x']             = 0.005 # Smallest element size
settings['bias_type_y']             = None
settings['bias_size_y']             = 0.0005 # Smallest element size

# Boundary conditions
"""
Options:
    -'periodic': no properties need to be specified; implied on opposite face too
    -'periodic': [IN PROGRESS] specify pressure, is poiseuille flow
    -'wall': specify T, ('grad',[value]) or 'zero_grad'; no slip and dp=0 enforced implicitly
    -'slip_wall': specify T as value or ('grad', [value]); rest is enforced implicitly
    -'outlet': specify pressure; rest is calculated from interior points
    -'inlet': [IN PROGRESS] specify velocities, temperature and pressure
Profiles possible; must be same size as number of nodes on that boundary
'zero_grad' assumes 0 gradient of that variable (temperature so far)
('grad',[value]) enforces a gradient normal to boundary (temperature on walls)
"""
BCs['bc_type_left']                 = 'outlet'
BCs['bc_left_u']                    = None
BCs['bc_left_v']                    = None
BCs['bc_left_p']                    = 101325
BCs['bc_left_T']                    = None
# numpy.linspace(400, 900, settings['Nodes_y'])
BCs['bc_type_right']                = 'outlet'
BCs['bc_right_u']                   = None
BCs['bc_right_v']                   = None
BCs['bc_right_p']                   = 101325
BCs['bc_right_T']                   = None
# numpy.linspace(400, 900, settings['Nodes_y'])
BCs['bc_type_south']                = 'slip_wall'
BCs['bc_south_u']                   = None
BCs['bc_south_v']                   = None
BCs['bc_south_p']                   = None
BCs['bc_south_T']                   = 600
# numpy.linspace(400, 900, settings['Nodes_x'])
BCs['bc_type_north']                = 'slip_wall'
BCs['bc_north_u']                   = None
BCs['bc_north_v']                   = None
BCs['bc_north_p']                   = None
BCs['bc_north_T']                   = 300
# numpy.linspace(400, 900, settings['Nodes_x'])

# Time advancement
settings['CFL']                     = 0.9
settings['total_time_steps']        = 1
settings['total_time']              = 3.0
settings['Time_Scheme']             = 'RK4'

##########################################################################
# -------------------------------------Read input file
##########################################################################
del settings, BCs
settings={}
BCs={}
fin=FileClasses.FileIn('Input_File', 0)
fin.Read_Input(settings, BCs)

# Initial conditions from previous run/already in memory
Use_inital_values                   = False

print('######################################################')
print('#              2D Navier-Stokes Solver               #')
print('#              Created by J. Mark Epps               #')
print('#          Part of Masters Thesis at UW 2018-2020    #')
print('######################################################\n')
print 'Initializing geometry package...'
#domain=OneDimLine(L,Nx)
domain=TwoDimPlanar(settings)
domain.mesh()
print '################################'

##########################################################################
# -------------------------------------Initialize solver and domain
##########################################################################

print 'Initializing solver package...'
solver=Solvers.TwoDimPlanarSolve(domain, settings, BCs)
print '################################'
print 'Initializing domain...'
if not Use_inital_values:
    T=numpy.zeros((domain.Ny,domain.Nx))
    u=numpy.zeros((domain.Ny,domain.Nx))
    v=numpy.zeros((domain.Ny,domain.Nx))
    p=numpy.zeros((domain.Ny,domain.Nx))
    
    u[:,:]=0
    v[:,:]=0
    
    #domain.rho[:,:]=CP.PropsSI('D','T',300,'P',101325,settings['Fluid'])
    T[:,:]=300
    p[:,:]=101325
#    p[:,:int(settings['Nodes_x']/2)]=101325
#    p[:,int(settings['Nodes_x']/2):]=3*101325
    #p=domain.rho*domain.R*T
    domain.rho=p/(domain.R*T)
else:
    domain.rho=rho.copy()
domain.rhou=domain.rho*u
domain.rhov=domain.rho*v
domain.rhoE=domain.rho*(0.5*(u**2+v**2)+domain.Cv*T)

solver.Apply_BCs(domain.rho, domain.rhou, domain.rhov, domain.rhoE, \
                 u, v, p, T, solver.dx, solver.dy)
#domain.rho[:,0]=p[:,0]/(domain.R*T[:,0])
# Experiment-rectangular solid inside domain, border on south face
#u[25:35,25:35]=0
#v[25:35,25:35]=0
#T[25:35,25:35]=600
#p[25:35,25]=p[25:35,24]
#p[25:35,35]=p[25:35,36]
#p[35,25:35]=p[36,25:35]
#p[25,25:35]=p[24,25:35]
##p[1:9,21:29]=101325
##
#domain.rho[25:35,25:35]=p[25:35,25:35]/domain.R/T[25:35,25:35]
#domain.rhou[25:35,25:35]=domain.rho[25:35,25:35]*u[25:35,25:35]
#domain.rhov[25:35,25:35]=domain.rho[25:35,25:35]*v[25:35,25:35]
#domain.rhoE[25:35,25:35]=domain.rho[25:35,25:35]*0.5*(u[25:35,25:35]**2+v[25:35,25:35]**2+2*domain.Cv*T[25:35,25:35])
    
print '################################'
##########################################################################
# -------------------------------------File setups
##########################################################################
print 'Initializing files...'
os.chdir('Tests')
datTime=str(datetime.date(datetime.now()))+'_'+'{:%H%M}'.format(datetime.time(datetime.now()))
isBinFile=False

#output_file=FileClasses.FileOut('Output_'+datTime, isBinFile)

# Write headers to files
#output_file.header('OUTPUT')

print '################################'

##########################################################################
# -------------------------------------Solve
##########################################################################
print 'Solving:'
t,nt=0,0
if settings['total_time_steps']==None:
    settings['total_time_steps']=settings['total_time']*10**9
if settings['total_time']==None:
    settings['total_time']=settings['total_time_steps']

while nt<settings['total_time_steps'] and t<settings['total_time']:
#for nt in range(settings['total_time_steps']):
    print 'Time step %i, Time elapsed=%f'%(nt+1,t)
    err,dt=solver.Advance_Soln()
    if err==1:
        print '#################### Solver aborted #######################'
        break
    t+=dt
    nt+=1
    
#output_file.close()

##########################################################################
# ------------------------------------Post-processing
##########################################################################
u,v,p,T=domain.primitiveFromConserv(domain.rho, domain.rhou, domain.rhov, domain.rhoE)
rho=domain.rho
X,Y=domain.X,domain.Y
# 2D plot
#fig=pyplot.figure(figsize=(7, 7))
#ax = fig.gca(projection='3d')
#ax.plot_surface(domain.X, domain.Y, T, rstride=1, cstride=1, cmap=cm.viridis,linewidth=0, antialiased=True)
##ax.set_xlim(0,0.001)
##ax.set_ylim(0.005,0.006)
#ax.set_zlim(300, BCs['bc_south_T'])
#ax.set_xlabel('$x$ (m)')
#ax.set_ylabel('$y$ (m)')
#ax.set_zlabel('T (K)');
#fig.savefig('Plot1.png',dpi=300)

# 1D Plot-Temperature distribution in y
#fig2=pyplot.figure(figsize=(7,7))
#pyplot.plot(domain.Y[:,int(settings['Nodes_x']/2)], T[:,int(settings['Nodes_x']/2)],marker='x')
#pyplot.xlabel('$y$ (m)')
#pyplot.ylabel('T (K)')
#pyplot.title('Temperature distribution')
#pyplot.xlim(0,3);
#fig2.savefig('Plot2.png',dpi=300)

# 1D Plot-Pressure distribution in y
#fig3=pyplot.figure(figsize=(7,7))
#pyplot.plot(domain.Y[:,int(settings['Nodes_x']/2)], p[:,int(settings['Nodes_x']/2)]-101325,marker='x')
#pyplot.xlabel('$y$ (m)')
#pyplot.ylabel('P (Pa gage)')
#pyplot.title('Pressure distribution')
#pyplot.xlim(0,3);
#fig3.savefig('Plot2.png',dpi=300)

# Velocity Quiver plot and pressure contour
pl=5
fig4=pyplot.figure(figsize=(7, 7))
pyplot.quiver(X[::pl, ::pl], Y[::pl, ::pl], \
              u[::pl, ::pl], v[::pl, ::pl]) 
pyplot.contourf(X, Y, p-101325, alpha=0.5, cmap=cm.viridis)  
pyplot.colorbar()
pyplot.xlabel('$x$ (m)')
pyplot.ylabel('$y$ (m)')
pyplot.title('Velocity plot and Gage Pressure contours');
#fig4.savefig(datTime+'_Vel_Press.png',dpi=300)

# Temperature contour
fig5=pyplot.figure(figsize=(7, 7))
pyplot.contourf(X, Y, T, alpha=0.5, cmap=cm.viridis)  
pyplot.colorbar()
pyplot.xlabel('$x$ (m)')
pyplot.ylabel('$y$ (m)')
pyplot.title('Temperature distribution');
#fig5.savefig(datTime+'_Temp.png',dpi=300)

# Density contour
#fig6=pyplot.figure(figsize=(7, 7))
#pyplot.contourf(X, Y, rho, alpha=0.5, cmap=cm.viridis)  
#pyplot.colorbar()
#pyplot.xlabel('$x$ (m)')
#pyplot.ylabel('$y$ (m)')
#pyplot.title('Density distribution');
#fig6.savefig(datTime+'_Temp.png',dpi=300)

print('Solver has finished its run')