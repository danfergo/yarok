class Injector:

    def __init__(self, platform, component_ref=None, config=None, providers=None):
        self.providers = providers if providers is not None else []
        self.platform = platform
        self.component_ref = component_ref
        self.config = config if config is not None else self.component_ref[
            'config'] if self.component_ref is not None else None

    def get(self, name_or_cls=None, cls=None):
        name = name_or_cls if isinstance(name_or_cls, str) else None
        injectable_cls = name_or_cls if not isinstance(name_or_cls, str) else cls

        if injectable_cls is None and self.component_ref and self.component_ref['name_path'] == '/' and name == 'world':
            return self.component_ref['instance']
        elif injectable_cls is None and self.component_ref:
            return self.platform.manager.get_by_name(self.component_ref, name)['instance']
        else:
            if isinstance(self.platform, injectable_cls):
                return self.platform
            elif isinstance(self, injectable_cls):
                return self
            elif isinstance(self.config, injectable_cls):
                return self.config
            elif name is not None and self.component_ref:
                return self.platform.manager.get_by_name(self.component_ref, name)['instance']

        for provider in self.providers:
            if 'match_type' in provider and provider['match_type'] == injectable_cls:
                return provider['value']

        return None

    def get_all(self, args):
        if type(args) is dict:
            return {a: self.get(a, args[a]) for a in args}
