from elementalcms.extensions import ElementalController


class ElementalExtension:

    __controllers: [ElementalController] = []

    def __init__(self, controllers: [ElementalController]):
        self.__controllers = controllers

    def get_controllers(self) -> [ElementalController]:
        return self.__controllers
