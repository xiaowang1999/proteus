"""
Basic setup for NCLS tests following Alistair's template
"""
#selling out
from proteus import iproteus
from proteus.iproteus import *
from proteus import default_p as p
from proteus import default_n as n
from proteus import default_s,default_so
from proteus.mprans import NCLS
import numpy as np
import proteus as pr
reload(p)
reload(n)

import os,sys
sys.path.insert(0,os.pardir)

import vortex2D as vort2D

"""
p file
"""
p.name=vort2D.soname+"_ncls"
p.nd = 2
p.L = [1.0,1.0]
p.domain = Domain.RectangularDomain(L=p.L,
                                    x=(0.0,0.0),
                                    name="box");

p.T = vort2D.T
p.LevelModelType = NCLS.LevelModel

p.coefficients = vort2D.MyCoefficients(epsFact=vort2D.epsFactHeaviside,checkMass=vort2D.checkMass,useMetrics=vort2D.useMetrics,ME_model=0,
                                      EDGE_VISCOSITY=vort2D.EDGE_VISCOSITY, 
                                      ENTROPY_VISCOSITY=vort2D.ENTROPY_VISCOSITY,
                                      POWER_SMOOTHNESS_INDICATOR=vort2D.POWER_SMOOTHNESS_INDICATOR,
                                      FCT=vort2D.FCT)

from proteus.ctransportCoefficients import smoothedHeaviside
class init_cond:
    def __init__(self,center=[0.5,0.75,0.5],radius=0.15):
        self.radius  = radius
        self.center  = center
    def uOfX(self,X):
        dx = X[0]-self.center[0]; dy = X[1]-self.center[1];
        dBubble = self.radius - np.sqrt(dx**2 + dy**2)
        return smoothedHeaviside(vort2D.epsFactHeaviside*he,dBubble)
    def uOfXT(self,X,t):
        return self.uOfX(X)

p.analyticalSolutions = None

def getDBC(x,flag):
    #return lambda x,t: 1.0
    pass

p.dirichletConditions = {0:getDBC}
p.initialConditions  = {0:init_cond(center=[0.5,0.75],radius=0.15)}
p.fluxBoundaryConditions = {0:'outFlow'}

#cek made no flux since v.n = 0 for this v
def getAFBC(x,flag):
   return lambda x,t: 0.0

p.advectiveFluxBoundaryConditions =  {0:getAFBC}
p.diffusiveFluxBoundaryConditions = {0:{}}


"""
n file
"""
n.multilevelNonlinearSolver  = NonlinearSolvers.NLNI
n.levelNonlinearSolver = NonlinearSolvers.Newton
n.fullNewtonFlag = vort2D.fullNewton
n.updateJacobian = False


n.nDTout = vort2D.nDTout
n.DT = p.T/float(n.nDTout)
n.timeIntegration = NCLS.RKEV
n.stepController = StepControl.Min_dt_RKcontroller
if vort2D.timeIntegration_ncls == "SSP33":
    n.timeOrder = 3
    n.nStagesTime = 3
else:
    n.timeOrder = 1
    n.nStagesTime = 1
 
n.runCFL = vort2D.runCFL
n.rtol_u = vort2D.rtol_u
n.atol_u = vort2D.atol_u
n.rtol_res = vort2D.rtol_res
n.atol_res = vort2D.atol_res

#spatial mesh
lRefinement=3
#tag simulation name to level of refinement
n.nn=n.nnx=n.nny=(2**lRefinement)*10+1
n.nnz=1
he=1.0/(n.nnx-1.0)

if vort2D.pDegree_ncls==2:
    n.femSpaces = {0:FemTools.C0_AffineQuadraticOnSimplexWithNodalBasis}
else:
    n.femSpaces = {0:FemTools.C0_AffineLinearOnSimplexWithNodalBasis}

n.subgridError = None #Advection_ASGS(coefficients,nd,lag=False)
n.shockCapturing = NCLS.ShockCapturing(p.coefficients,p.nd,shockCapturingFactor=vort2D.shockCapturingFactor_ncls,
                                       lag=vort2D.lag_shockCapturing_ncls)

if vort2D.parallel or p.LevelModelType == NCLS.LevelModel:
    #n.numericalFluxType = NumericalFlux.Advection_DiagonalUpwind_IIPG_exterior
    n.numericalFluxType = n.DoNothing
    
n.elementQuadrature = Quadrature.SimplexGaussQuadrature(p.nd,vort2D.vortex_quad_order)
n.elementBoundaryQuadrature = Quadrature.SimplexGaussQuadrature(p.nd-1,vort2D.vortex_quad_order)

#parallel partitioning info
n.partitioningType = MeshTools.MeshParallelPartitioningTypes.node

n.tolFac = 0.0
n.linTolFac = n.tolFac
n.linearSolverConvergenceTest = 'r-true'

n.nl_atol_res = 100*vort2D.atolLevelSet
n.l_atol_res = vort2D.atolLevelSet

n.maxNonlinearIts = 20
n.maxLineSearches = 0

n.matrix = LinearAlgebraTools.SparseMatrix

if vort2D.parallel:
    n.multilevelLinearSolver = LinearSolvers.KSP_petsc4py#PETSc
    n.levelLinearSolver = LinearSolvers.KSP_petsc4py#PETSc
    n.linear_solver_options_prefix = 'ncls_'
    n.linearSolverConvergenceTest = 'r-true'
else:
    n.multilevelLinearSolver = LinearSolvers.LU
    n.levelLinearSolver = LinearSolvers.LU

n.conservativeFlux = {}

n.auxiliaryVariables = [AuxiliaryVariables.MassOverRegion()]

so = default_so
so.name = vort2D.soname
so.sList=[default_s]
so.systemStepExact = True

so.needEBQ_GLOBAL  = False
so.needEBQ = False
so.systemStepControllerType = SplitOperator.Sequential_MinAdaptiveModelStep
so.archiveFlag = Archiver.ArchiveFlags.EVERY_USER_STEP
so.DT = n.DT
so.tnList = [i*n.DT for i  in range(n.nDTout+1)]
so.useOneArchive = True

"""

"""
opts = None
#ns = NumericalSolution.NS_base(so,[p],[n],so.sList,iproteus.opts)
