def interface(**kwargs):
    def _(c):
        if not hasattr(c, '__data__'):
            defaults = kwargs['defaults'] if 'defaults' in kwargs else {}

            setattr(c, '__data__', {
                'defaults': defaults,  # interface config defaults
            })
        return c

    return _
