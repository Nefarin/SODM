import os
import imp
import unittest

path = fullPath = os.path.realpath(__file__)
projectPath= os.path.dirname(os.path.dirname(os.path.dirname(fullPath)))
fullPath = os.path.join(projectPath, "src", "PathBuilder", "PathBuilder.py")
p = imp.load_source("PathBuilder", fullPath)


class TestPathBuilder(unittest.TestCase):
    def test_resourcePath(self):
        with self.assertRaises(NotImplementedError):
            p.PathBuilder.resourcePath()

    def test_testsPath(self):
        with self.assertRaises(NotImplementedError):
            p.PathBuilder.testsPath()

    def test_confPath(self):
        with self.assertRaises(NotImplementedError):
            p.PathBuilder.confPath()

    def test_unitPath(self):
        with self.assertRaises(NotImplementedError):
            p.PathBuilder.confPath()

    def test_srcPath(self):
        with self.assertRaises(NotImplementedError):
            p.PathBuilder.srcPath()

    def test_srcPath(self):
        with self.assertRaises(NotImplementedError):
            p.PathBuilder.guiPath()

    def test_pathPath(self):
        with self.assertRaises(NotImplementedError):
            p.PathBuilder.pathPath()
    def test_appendPath(self):
        with self.assertRaises(NotImplementedError):
            p.PathBuilder.appendPath()

if __name__ == "__main__":
    unittest.main()