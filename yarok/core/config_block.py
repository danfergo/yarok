class ConfigBlock:

    def __init__(self, config):
        self.config = config
        self._defaults = {}

    def defaults(self, defaults):
        self._defaults = defaults

    def __contains__(self, item):
        return item in self.config or item in self._defaults
    
    def __getitem__(self, item):

        def as_config_block(cfg, defaults=None):
            if type(cfg) == dict:
                block = ConfigBlock(cfg)
                if defaults is not None:
                    block.defaults(defaults)
                return block
            return cfg

        if item in self.config:
            return as_config_block(self.config[item],
                                   self._defaults[item] if item in self._defaults else {})
        if item in self._defaults:
            return as_config_block(self._defaults[item])

        raise KeyError()
        return None

    def is_config_block(self, key):
        return isinstance(self[key], ConfigBlock)
