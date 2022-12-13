class Injector:

    def __init__(self, platform, component_ref, config=None):
        self.platform = platform
        self.component_ref = component_ref
        self.config = self.component_ref['config'] if config is None else config

    def get(self, name_or_cls=None, cls=None):
        name = name_or_cls if isinstance(name_or_cls, str) else None
        injectable_cls = name_or_cls if not isinstance(name_or_cls, str) else cls

        if injectable_cls is None:
            return self.platform.manager.get_by_name(self.component_ref, name)['instance']
        else:
            if isinstance(self.platform, injectable_cls):
                return self.platform
            elif isinstance(self, injectable_cls):
                return self
            elif isinstance(self.component_ref['config'], injectable_cls):
                return self.config
            elif self.component_ref['name_path'] == '/' and name == 'world':
                return self.component_ref['instance']
            elif name is not None:
                return self.platform.manager.get_by_name(self.component_ref, name)['instance']

        return None

    def get_all(self, args):
        if type(args) is dict:
            return {a: self.get(a, args[a]) for a in args}
