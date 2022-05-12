from elementalcms.extends import Controller


class Applet:

    _name: str
    __controllers: [Controller] = []

    def __init__(self, name, controllers: [Controller]):
        self._name = name
        self.__controllers = controllers

    def get_controllers(self) -> [Controller]:
        return self.__controllers
