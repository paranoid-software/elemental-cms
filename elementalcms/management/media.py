import click


class Media(click.Group):

    def __init__(self):
        super(Media, self).__init__()
        self.name = 'media'
