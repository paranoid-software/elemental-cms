from elementalcms.extends import Controller


class Applet:

    name: str
    __controllers: [Controller] = []

    def __init__(self, name, controllers: [Controller]):
        self.name = name
        self.__controllers = controllers

    def get_controllers(self) -> [Controller]:
        return self.__controllers
