import sys
import os
builderPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "PathBuilder")
sys.path.append(builderPath)

from DebugPathBuilder import DebugPathBuilder

sys.path.append(DebugPathBuilder.guiPath())
sys.path.append(DebugPathBuilder.resourcePath())
sys.path.append(DebugPathBuilder.confPath())
sys.path.append(DebugPathBuilder.unitPath())
sys.path.append(DebugPathBuilder.pathPath())
sys.path.append(DebugPathBuilder.testsPath())
sys.path.append(DebugPathBuilder.srcPath())