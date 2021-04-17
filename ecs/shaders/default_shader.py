

class Shader():

    def __init__(self, name="Default Shader"):
        self._name = name

    @property
    def name(self):
        return self._name

    def getVertex(self):
        raise RuntimeError("Shader::getVertex() has not been implemented yet")
    def getGeometry(self):
        raise RuntimeError("Shader::getGeometry() has not been implemented yet")
    def getFragment(self):
        raise RuntimeError("Shader::getFragment() has not been implemented yet")


