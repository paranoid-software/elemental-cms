import click


class Static(click.Group):

    def __init__(self):
        super(Static, self).__init__()
        self.name = 'static'
