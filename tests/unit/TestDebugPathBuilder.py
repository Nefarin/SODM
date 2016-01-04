import os
import imp
import unittest

path = fullPath = os.path.realpath(__file__)
projectPath= os.path.dirname(os.path.dirname(os.path.dirname(fullPath)))
fullPath = os.path.join(projectPath, "src", "PathBuilder", "DebugPathBuilder.py")
p = imp.load_source("DebugPathBuilder", fullPath)


class TestDebugPathBuilder(unittest.TestCase):
    def test_resourcePath(self):
        self.assertEqual(p.DebugPathBuilder.resourcePath(), "/home/marek/SODM/res")
        try:
            p.DebugPathBuilder.resourcePath()
        except NotImplementedError:
            self.fail("Not implemented error.")

    def test_testsPath(self):
        self.assertEqual(p.DebugPathBuilder.testsPath(), "/home/marek/SODM/tests")
        try:
            p.DebugPathBuilder.testsPath()
        except NotImplementedError:
            self.fail("Not implemented error.")

    def test_confPath(self):
        self.assertEqual(p.DebugPathBuilder.confPath(), "/home/marek/SODM/tests/conf")
        try:
            p.DebugPathBuilder.confPath()
        except NotImplementedError:
            self.fail("Not implemented error.")

    def test_unitPath(self):
        self.assertEqual(p.DebugPathBuilder.unitPath(), "/home/marek/SODM/tests/unit")
        try:
            p.DebugPathBuilder.unitPath()
        except NotImplementedError:
            self.fail("Not implemented error.")

    def test_srcPath(self):
        self.assertEqual(p.DebugPathBuilder.srcPath(), "/home/marek/SODM/src")
        try:
            p.DebugPathBuilder.srcPath()
        except NotImplementedError:
            self.fail("Not implemented error.")

    def test_pathPath(self):
        self.assertEqual(p.DebugPathBuilder.pathPath(), "/home/marek/SODM/src/PathBuilder")
        try:
            p.DebugPathBuilder.pathPath()
        except NotImplementedError:
            self.fail("Not implemented error.")

    def test_guiPath(self):
        self.assertEqual(p.DebugPathBuilder.guiPath(), "/home/marek/SODM/src/GUI")
        try:
            p.DebugPathBuilder.guiPath()
        except NotImplementedError:
            self.fail("Not implemented error.")

    def test_appendPath(self):
        self.assertEqual(p.DebugPathBuilder.appendPath("abc", "bca"), "abc/bca")
        self.assertEqual(p.DebugPathBuilder.appendPath(p.DebugPathBuilder.srcPath(), "abc"), p.DebugPathBuilder.srcPath() + "/abc")
        try:
            p.DebugPathBuilder.pathPath()
        except NotImplementedError:
            self.fail("Not implemented error.")

if __name__ == "__main__":
    unittest.main()