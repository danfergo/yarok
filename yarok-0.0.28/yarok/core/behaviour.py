def behaviour(**kwargs):
    def _(c):
        if not hasattr(c, '__data__'):
            defaults = kwargs['defaults'] if 'defaults' in kwargs else {}

            setattr(c, '__data__', {
                'defaults': defaults,  # behaviour config defaults
            })
        return c

    return _
