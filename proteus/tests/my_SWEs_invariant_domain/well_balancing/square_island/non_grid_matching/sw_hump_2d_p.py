from proteus import *
from proteus.default_p import *
from proteus.mprans import SW2D
from proteus.mprans import SW2DCV
from proteus.Domain import RectangularDomain
nd=2

T=1.0
L=(1.0,1.0)
g = 9.81
island=0.2
wl=0.1
xl=0.25
xr=0.75
yl=0.25
yr=0.75
domain = RectangularDomain(L=L)

#This is relevant just when use_second_order_NonFlatB_with_EV_stabilization=True
cE=1
LUMPED_MASS_MATRIX=0
USE_EV_BASED_ON_GALERKIN=0

bt = domain.boundaryTags
bt['front'] = bt['bottom']
bt['back'] = bt['top']
domain.writePoly("tank2d")

##############################
##### INITIAL CONDITIONS #####
##############################
class water_height:
    def __init__(self,wl=0.1,xl=0.25,xr=0.75,yl=0.25,yr=0.75,island=0.05):
        self.wl=wl
    def uOfXT(self,X,t):
        x = X[0]
        y = X[1]
        if (xl <= x and x <= xr and yl <= y and y <= yr):
            if (island >= wl):
                h = 0.
            else:
                h = wl-island
        else:
            h = wl
        return h

class Zero:
    def uOfXT(self,x,t):
        return 0.0

class Const:
    def uOfXT(self,x,t):
        return 0.0

initialConditions = {0:water_height(wl,xl,xr,yl,yr,island),
                     1:Zero(),
                     2:Zero()}

analyticalSolution = {0:Const(),
                       1:Const(), 
                       2:Const()}
######################
##### BATHYMETRY #####
######################
def bathymetry_function(X):
    x = X[0]
    y = X[1]
    return island*(xl <= x)*(x <= xr)*(yl <= y)*(y <= yr)

###################################
##### FOR BOUNDARY CONDITIONS #####
###################################
def getDBC_h(x,flag):
    return None

#note, these are the same for hu and hv so we can cheat and use  this p-file for SW2DCV and SW2D
def getDBC_u(x,flag):
   if (x[0] in [0.0,L[0]]) or flag in [bt['left'],bt['right']]:
       return lambda x,t: 0.0
   else:
       return None

def getDBC_v(x,flag):
   if x[1] in [0.0,L[1]] or flag in [bt['front'],bt['back']]:
       return lambda x,t: 0.0
   else:
       return None

dirichletConditions = {0:getDBC_h,
                       1:getDBC_u,
                       2:getDBC_v}

fluxBoundaryConditions = {0:'outFlow',
                          1:'outFlow',
                          2:'outFlow'}

def getAFBC_h(x,flag):
    return lambda x,t: 0.0

def getAFBC_u(x,flag):
    if flag == 0:
        return lambda x,t: 0.0
    else:
        return None
def getAFBC_v(x,flag):
    if flag == 0:
        return lambda x,t: 0.0
    else:
        return None

advectiveFluxBoundaryConditions =  {0:getAFBC_h,
                                    1:getAFBC_u,
                                    2:getAFBC_v}

def getDFBC_u(x,flag):
    if flag == 0:
        return lambda x,t: 0.0
    else:
        return None

def getDFBC_v(x,flag):
    if flag == 0:
        return lambda x,t: 0.0
    else:
        return None

diffusiveFluxBoundaryConditions = {0:{},
                                   1:{1:getDFBC_u},
                                   2:{2:getDFBC_v}}

#########################################
##### CREATE MODEL AND COEFFICIENTS #####
#########################################
bathymetry={0:bathymetry_function}
LevelModelType = SW2DCV.LevelModel
coefficients = SW2DCV.Coefficients(g=g,bathymetry=bathymetry)
coefficients = SW2DCV.Coefficients(g=g,bathymetry=bathymetry,cE=cE,LUMPED_MASS_MATRIX=LUMPED_MASS_MATRIX,USE_EV_BASED_ON_GALERKIN=USE_EV_BASED_ON_GALERKIN)
