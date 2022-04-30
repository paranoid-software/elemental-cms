from elementalcms.extends import Controller


class Applet:

    __controllers: [Controller] = []

    def __init__(self, controllers: [Controller]):
        self.__controllers = controllers

    def get_controllers(self) -> [Controller]:
        return self.__controllers
