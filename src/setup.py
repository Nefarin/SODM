import sys
sys.path.append("/home/marek/SODM/src/PathBuilder")

from DebugPathBuilder import DebugPathBuilder

sys.path.append(DebugPathBuilder.guiPath())
sys.path.append(DebugPathBuilder.resourcePath())
sys.path.append(DebugPathBuilder.confPath())
sys.path.append(DebugPathBuilder.unitPath())
sys.path.append(DebugPathBuilder.pathPath())
sys.path.append(DebugPathBuilder.testsPath())
sys.path.append(DebugPathBuilder.srcPath())