import os


class DebugPathBuilder(object):
    basePath = os.path.realpath(__file__)
    projectPath = os.path.dirname(os.path.dirname(os.path.dirname(basePath)))

    @staticmethod
    def resourcePath():
        fullPath = os.path.join(DebugPathBuilder.projectPath, "res")
        return fullPath

    @staticmethod
    def testsPath():
        fullPath = os.path.join(DebugPathBuilder.projectPath, "tests")
        return fullPath

    @staticmethod
    def confPath():
        fullPath = os.path.join(DebugPathBuilder.projectPath, "tests", "conf")
        return fullPath

    @staticmethod
    def unitPath():
        fullPath = os.path.join(DebugPathBuilder.projectPath, "tests", "unit")
        return fullPath

    @staticmethod
    def srcPath():
        fullPath = os.path.join(DebugPathBuilder.projectPath, "src")
        return fullPath

    @staticmethod
    def pathPath():
        fullPath = os.path.join(DebugPathBuilder.projectPath, "src", "PathBuilder")
        return fullPath

    @staticmethod
    def guiPath():
        fullPath = os.path.join(DebugPathBuilder.projectPath, "src", "GUI")
        return fullPath

    @staticmethod
    def appendPath(path="/", toAppend=""):
        return os.path.join(path, toAppend)
