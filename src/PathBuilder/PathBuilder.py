
class PathBuilder(object):
    @staticmethod
    def resourcePath():
        raise NotImplementedError

    @staticmethod
    def testsPath():
        raise NotImplementedError

    @staticmethod
    def confPath():
        raise NotImplementedError

    @staticmethod
    def unitPath():
        raise NotImplementedError

    @staticmethod
    def srcPath():
        raise NotImplementedError

    @staticmethod
    def pathPath():
        raise NotImplementedError
    
    @staticmethod
    def guiPath():
        raise NotImplementedError

    @staticmethod
    def appendPath(path="/", toAppend=""):
        raise NotImplementedError