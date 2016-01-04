import sys
import vtk
import os

testReader = vtk.vtkDICOMImageReader()
fullPath = os.path.realpath(__file__)
projectPath= os.path.dirname(os.path.dirname(fullPath))
testReader.SetFileName(projectPath + "/res/3.dcm")
testReader.Update()

viewer = vtk.vtkImageViewer()
viewer.SetInputConnection(testReader.GetOutputPort())
viewer.Render()
viewer.GetRenderer().ResetCamera()
viewer.Render()


b = raw_input("Im Weroniczka and I know it: ")