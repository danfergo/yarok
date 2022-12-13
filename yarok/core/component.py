import re
import os
import sys
import pathlib
import inspect

# CamelCase to snake_case
# https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
r1 = re.compile(r'(.)([A-Z][a-z]+)')
r2 = re.compile(r'__([A-Z])')
r3 = re.compile(r'([a-z0-9])([A-Z])')


def to_snake_case(name):
    name = r1.sub(r'\1_\2', name)
    name = r2.sub(r'_\1', name)
    name = r3.sub(r'\1_\2', name)
    return name.lower()


def component(**kwargs):
    def _(c):
        if not hasattr(c, '__data__'):
            class_name = to_snake_case(c.__name__)
            class_file_path = os.path.abspath((sys.modules[c.__module__].__file__))
            class_dir_path = str(pathlib.Path(class_file_path).parent.resolve())

            class_members = {t[0]: t[1] for t in inspect.getmembers(c)}
            init_members = {t[0]: t[1] for t in inspect.getmembers(class_members['__init__'])}
            init_annotations = init_members['__annotations__'] if '__annotations__' in init_members else {}

            extends = kwargs['extends'] if 'extends' in kwargs else None
            rel_template_path = kwargs['template_path'] if 'template_path' in kwargs else class_name + '.xml'
            template_path = os.path.join(class_dir_path, rel_template_path)
            components = kwargs['components'] if 'components' in kwargs else []
            components = {c.__data__['tag']: c for c in components}
            template = kwargs['template'] if 'template' in kwargs else None
            tag = kwargs['tag'] if 'tag' in kwargs else None
            defaults = kwargs['defaults'] if 'defaults' in kwargs else {}

            interfaces = {k[10:]: kwargs[k] for k in kwargs if k.startswith('interface_')}
            if len(interfaces) > 0:
                print("[deprecated] in "
                      + class_name
                      + ", interface_mjc and interface_hw should be "
                        "replace with defaults={'interface_mjc':xxx, 'interface_hw':xx}")
                defaults = {**{k: interfaces[k[10:]] for k in kwargs if k.startswith('interface_')}, **defaults}

            probe = kwargs['probe'] if 'probe' in kwargs else None
            if probe is not None:
                print("[deprecated] in "
                      + class_name
                      + ", interface_mjc and interface_hw should be "
                        "replace with defaults={'probe':xxx'}")
                defaults = {**{'probe': probe}, **defaults}

            setattr(c, '__data__', {
                'tag': tag if tag is not None else class_name,
                'class_name': class_name,  # the name of the factory class, in snake case
                'class_file_path': class_file_path,  # the abs path of the FILE where the class is declared
                'class_dir_path': class_dir_path,  # the abs path of the DIRECTORY where the class is declared
                'template': template,
                'template_path': template_path,  # the abs path of the .xml template
                'defaults': defaults,  # component config defaults
                # the dict of components' classes indexed by class name
                # e.g.:  {'ur5': <class 'yarok.components.ur5.ur5.UR5'>, ...}
                'components': components,
                'extends': extends,
                # the class constructor annotations
                # format: dict({ comp. name : class }) e.g.
                # e.g.:  {'mani': <class 'yarok.components.ur5.ur5.UR5'>, ...}
                'annotations': init_annotations,

                # interfaces's classes indexed environment "name"
                # e.g.: {'mjc': <class 'yarok.components.ur5.ur5.UR5InterfaceMJC'>}
                # 'interfaces': interfaces,

                # probe. a fn that returns an object key:value
                # the value is plotted or logged depending on the type.
                # 'probe': probe
            })
        return c

    return _
