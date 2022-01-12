import inspect
import os
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring

from mujoco_py import load_model_from_xml, MjSim


class ComponentsManager:
    """
        Handles loading components templates (.xml) & controllers (.py),
        Builds world model/components tree
    """

    def __init__(self, **kwargs):
        self.id_counter = 0
        root_component_factory = kwargs['root']
        root_component_factories = root_component_factory.__data__['components']

        self.root = {
            'factory': root_component_factory,
            'name': '',
            'id': self.gen_name(),
            'children': []
        }

        self.xml_tree = self.load_tree(self.root, components_factories=root_component_factories)

        self.components = {}

        # build components map and init interfaces
        def walk_components(component):
            for child in component['children']:
                walk_components(child)

            self.components[component['id']] = component

        walk_components(self.root)

        # root['instance'].init()

        # def init(self, sim):
        #     self.init_interfaces(self.root_component, self.model, sim)
        #     self.init_components(root_component)

    def get(self, n):
        return self.components[n]

    def data(self, n):
        return self.components[n]['factory'].__data__

    # def step(self):
    # def step_components(component):
    #     for child in component['children']:
    #         step_components(child)
    #
    #     if 'interface_instance' in component['factory'].__data__ \
    #             and hasattr(component['factory'].__data__['interface_instance'], 'step'):
    #         component['interface_instance'].step()
    #
    # step_components(self.root)

    # if self.viewer is not None:
    #     self.viewer.step()

    def load_tree(self, comp, sub_trees=None, components_factories=None):
        sub_trees = [] if sub_trees is None else sub_trees
        xml_path = comp['factory'].__data__['template_path']
        name = comp['name']
        id = comp['id']

        tree = ET.parse(xml_path).getroot()

        wb = tree.find('worldbody')

        # nesting all descendant content
        for sub_tree in sub_trees:
            if 'parent' in sub_tree.attrib:
                parentName = sub_tree.attrib['parent']
                parent = wb.find(".//body[@name='" + parentName + "']")
                if parent is None:
                    raise KeyError('Failed to inject ' +
                                   tostring(sub_tree, encoding="unicode").replace('\n', '').strip() +
                                   ' body[name=' +
                                   parentName +
                                   '] not being found at ' + xml_path)
                sub_tree.attrib.pop('parent')
                parent.append(sub_tree)
            else:
                wb.append(sub_tree)

        # renaming "foreign keys" to from xxx to id:xxx
        rename_attrs = ['name', 'joint', 'actuator', 'body1', 'body2', 'material', 'mesh', 'texture']

        def rename_fk(els):
            for el in els:
                if el.tag not in components_factories:
                    for attr in rename_attrs:
                        if attr in el.attrib:
                            el.attrib[attr] = id + ':' + el.attrib[attr]
                    rename_fk(list(el))

        rename_fk(list(tree))

        # repathing all local file refs to be relative to the .xml file
        dir_path = str(pathlib.Path(xml_path).parent.resolve())
        for el in tree.iter():
            if 'file' in el.attrib and not el.attrib['file'].startswith('/'):
                el.attrib['file'] = dir_path + '/' + el.attrib['file']

        blocks_names = ['asset', 'sensor', 'actuator', 'equality']
        blocks = {block_name: tree.find(block_name) for block_name in blocks_names}

        parent_map = {c: p for p in tree.iter() for c in p if c.tag in components_factories}

        rename_attrs = ['name', 'joint', 'actuator', 'body1', 'body2', 'material', 'mesh']

        # walking current file .xml tree and looking for components and instantiating them
        def walk_tree(component_trees):
            for component_tree in component_trees:
                tag = component_tree.tag
                if tag in components_factories:

                    component_type = tag  # component.attrib['type']
                    component_name = component_tree.attrib['name']
                    if component_name == '':
                        raise KeyError(
                            'No component should be named ""!, ' + component_type + '[name=root] at' + comp['name'])

                    # creates new sub component data wrapper
                    sub_component = {
                        'id': self.gen_name(component_name),
                        'name': component_name,
                        'factory': components_factories[component_type],
                        'children': []
                    }

                    # appends the newly found sub component to the previous/parent component
                    comp['children'].append(sub_component)

                    # load the new subcomponent tree
                    sub_component_tree = self.load_tree(
                        sub_component,
                        sub_trees=list(component_tree),
                        components_factories=components_factories
                    )

                    # merge all blocks actuators, sensors, etc to with the current component tree
                    for block_name in blocks_names:
                        block = sub_component_tree.find(block_name)
                        if block is not None:
                            if blocks[block_name] is not None:
                                blocks[block_name].extend(block)
                            else:
                                tree.append(block)

                    # merge the new subcomponent tree/body with the current tree
                    # and remove the "component" tag from the current tree
                    comp_wb = sub_component_tree.find('worldbody')
                    parent_map[component_tree].extend(comp_wb)
                    parent_map[component_tree].remove(component_tree)

                else:
                    walk_tree(list(component_tree))

        walk_tree(list(tree))

        return tree

    def gen_name(self, name=''):
        self.id_counter += 1
        return '__c__' + str(self.id_counter) + '-' + name

    def init_components(self, interfaces):

        # sub_components = []
        # for child in comp['children']:
        #     sub_components.extend(self.init_components(child))

        for n, comp in self.components.items():

            # sub_components = list(chain.from_iterable(sub_components))
            # sub_components_map = {t[0]: t[1] for t in sub_components}
            c_data = comp['factory'].__data__
            print(comp['name'], c_data['annotations'], self.components.keys())
            kwargs = {n: self.components[n] for n in c_data['annotations']}

            try:
                c = comp['factory'](**kwargs)
                comp['instance'] = c

                if n in interfaces:
                    # interface_factory = c_data['interfaces'][self.env]
                    # interface = interface_factory(comp['interface_instance_mjc'])
                    c_data['interface_instance'] = interfaces[n]

                    methods = [i for i in dir(interfaces[n].__class__) if i[0:2] != '__']
                    # print(methods, getattr(interface, 'on'))
                    [setattr(c, m, getattr(interfaces[n], m)) for m in methods if hasattr(c, m)]
                    # print(methods)
                    # print()

                # sub_components.append((comp['factory'], c))
            except TypeError as e:
                raise TypeError(str(e) + ', while initiating ' + str(comp['factory']) + (
                    '/' + comp['name'] if comp['name'] is not None else ''))

        # return sub_components

    # def init_interfaces(self, root_component, sim, model):
    #
    #     components = {}
    #
    #     # build components map and init interfaces
    #     def walk_components(component):
    #         component['interface_instance_mjc'] = InterfaceMJC(component['name'], sim, model)
    #         components[component['name']] = component
    #
    #         for child in component['children']:
    #             walk_components(child)
    #
    #     walk_components(root_component)
    #
    #     items = ['sensor', 'actuator', 'camera']
    #     for item in items:
    #         for idx in range(len(getattr(model, item + '_names'))):
    #             # print(model.camera_id2name(0), idx)
    #             abs_name = getattr(model, item + '_id2name')(idx)
    #             col_idx = abs_name.index(':')
    #             component_name = abs_name[:col_idx]
    #             item_name = abs_name[col_idx + 1:]
    #
    #             mjc_interface = components[component_name]['interface_instance_mjc']
    #             getattr(mjc_interface, item + '_name2id')[item_name] = idx
    #             getattr(mjc_interface, item + 's').append(item_name)
    #             mjc_interface.component_name = component_name


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

            interfaces = {k[10:]: kwargs[k] for k in kwargs if k.startswith('interface_')}

            # components = kwargs['components'] if 'components' in kwargs else []
            components = kwargs['components'] if 'components' in kwargs else []
            components = {c.__data__['name']: c for c in components}

            setattr(c, '__data__', {
                'name': class_name,
                'class_file_path': class_file_path,
                'class_dir_path': class_dir_path,
                'template_path': class_dir_path + '/' + class_name + '.xml',
                'components': components,
                'annotations': init_annotations,
                'interfaces': interfaces
            })
        return c

    return _


def on(**kwargs):
    def _(m):
        return m

    return _
