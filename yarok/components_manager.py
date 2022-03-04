import inspect
import os
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring

from mujoco_py import load_model_from_xml, MjSim

# attributes that are renamed from 'name' to 'id'
RENAME_KEYS_ATTRS_NAMES = [
    'name',
    'joint',
    'actuator',
    'body1',
    'body2',
    'material',
    'mesh',
    'texture'
]

# names of the blocks to be merged
# except worldbody that follows a special merging process
# i.e. nesting components, etc.
EXTENDABLE_BLOCKS_NAMES = [
    'asset',
    'sensor',
    'actuator',
    'equality'
]


class ComponentsManager:
    """
    Handles loading components templates (.xml) & controllers (.py)
    and Builds xml tree and components i.e.,

    - self.xml_tree   =>
    - self.components => dict ([component.id] => dict(
        class => component factory class,
        name => component name,
        class_name => component factory (snake-case) name,
        id => auto generated id,
        children => [dict(...)],
        instance => object ref             # set while instantiating the components
    ))


    """

    def __init__(self, **kwargs):
        self.id_counter = 0
        self.components = {}

        root = {
            'class': kwargs['root'],
            'name': '',
            'id': self.gen_id(),
            'parent': None,
            'children': []
        }
        self.xml_tree = self.load_tree(root)

        # build components map
        def walk_components(component):
            for child in component['children']:
                walk_components(child)
            self.components[component['id']] = component

        walk_components(root)

    def is_id(self, idx):
        return isinstance(idx, int) or isinstance(idx, str)

    def gen_id(self, name=''):
        self.id_counter += 1
        # '__c__' + str(self.id_counter) + '-' +
        return name

    def get(self, n):
        return self.components[n]

    def get_by_name(self, c, name):
        """
            Gets a component by 'name', given its parent 'c' (or its parent id)
        """
        comp = self.components[c] if self.is_id(c) else c

        for child in comp['children']:
            if name == 'name':
                return child
        return None

    def data(self, c):
        comp = self.components[c] if self.is_id(c) else c
        return comp['class'].__data__

    def step(self):
        print('-->')

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

    def load_tree(self, comp, sub_tree=None):
        """
            The method that loads the multiple components and its template (.xml) into
            a single xml/model tree. It also loads the multiple components into a tree
        """

        # inits auxiliar variables from the component metadata
        template = comp['class'].__data__['template']
        xml_path = comp['class'].__data__['template_path']
        component_components_factories = comp['class'].__data__['components']
        id = comp['id']

        def is_component(el):
            # if el in __components_factories__:
            #     return el.tag
            # print(el in components_factories)
            return el.tag in component_components_factories

        # loads xml tree from xml path
        tree = ET.fromstring(template) if template is not None else ET.parse(xml_path).getroot()

        # re-pathing all file refs, that are not absolute refs, to be relative to the .xml file
        dir_path = str(pathlib.Path(xml_path).parent.resolve())
        for e in tree.iter():
            if 'file' in e.attrib and not e.attrib['file'].startswith('/'):
                e.attrib['file'] = dir_path + '/' + e.attrib['file']

        # nests all descendant elements specified in the parent xml,
        # e.g. in the environment.xml <parent><child_to_nest parent='link_name'></child_to_nest></parent>
        # in this case, the child_to_nest is nested as the last child of the the element @name='link_name'
        # in the current .xml template.
        wb = tree.find('worldbody')
        if sub_tree is not None:
            for sub_tree in list(sub_tree['tree']):
                if 'parent' in sub_tree.attrib:
                    parentName = sub_tree.attrib['parent']
                    parent = wb.find(".//body[@name='" + parentName + "']")
                    if parent is None:
                        raise KeyError('Failed to inject ' +
                                       tostring(sub_tree, encoding="unicode").replace('\n', '').strip() +
                                       ' body[name=' +
                                       parentName +
                                       '] not being found at ' + xml_path)
                    # sub_tree.attrib['__base_component__'] = sub_tree['base_component']
                    sub_tree.attrib.pop('parent')
                    parent.append(sub_tree)
                else:
                    wb.append(sub_tree)

        # renaming primary&foreign keys to from xxx to id:xxx
        def rename_fk(els):
            for el in els:
                if not is_component(el):
                    for attr in RENAME_KEYS_ATTRS_NAMES:
                        if attr in el.attrib:
                            el.attrib[attr] = id + ':' + el.attrib[attr]
                    rename_fk(list(el))

        rename_fk(list(tree))

        extendable_blocks = {block_name: tree.find(block_name) for block_name in EXTENDABLE_BLOCKS_NAMES}

        # auxiliary map that maps child->parent element,
        # for component instantiation elements
        parent_map = {child_: parent_ for parent_ in tree.iter()
                      for child_ in parent_ if is_component(child_)}

        # walking current file .xml tree and looking for components and instantiating them
        def walk_tree(element_tree):
            for element in list(element_tree):
                tag = element.tag
                if is_component(element):

                    component_class_name = tag
                    component_name = element.attrib['name']

                    if component_name == '':
                        raise KeyError(
                            'No component should be named ""!, ' +
                            component_class_name +
                            '[name=root] at' +
                            comp['name'])

                    # creates new sub component data wrapper
                    sub_component = {
                        'id': self.gen_id(component_name),
                        'name': component_name,
                        'class_name': component_class_name,
                        'class': component_components_factories[component_class_name],
                        'parent': comp,
                        'children': []
                    }

                    # appends the newly found sub component to the previous/parent component
                    comp['children'].append(sub_component)

                    # load the new subcomponent tree
                    sub_component_tree = self.load_tree(
                        sub_component,
                        sub_tree={'tree': element, 'base_component': comp}
                    )

                    # if hasattr(component_tree,  '__components_factories__'):
                    #     print(getattr(component_tree, '__components_factories__'))

                    # merge all blocks actuators, sensors, etc
                    # with the current component tree
                    for block_name in extendable_blocks:
                        block = sub_component_tree.find(block_name)
                        if block is not None:
                            if extendable_blocks[block_name] is not None:
                                extendable_blocks[block_name].extend(block)
                            else:
                                tree.append(block)

                    # merge the new subcomponent tree/body with the current tree
                    # and remove the "component" tag from the current tree
                    comp_wb = sub_component_tree.find('worldbody')
                    parent_map[element].extend(comp_wb)
                    parent_map[element].remove(element)

                else:
                    walk_tree(element)

        walk_tree(tree)

        return tree

    def init_components(self, interfaces):
        """
            Initializes components.
            Called after all the interfaces are instantiated (by the platform manager)

            Iterates through all components,
                - Gets the component class annotations,
                instantiates the component and stores at component['instance']

                - Gets and stores the component interface
        """

        for component_id, comp in self.components.items():

            c_data = comp['class'].__data__

            try:
                c = comp['class'](**{n: self.get_by_name(comp, n) for n in c_data['annotations']})
                comp['instance'] = c

                if component_id in interfaces:
                    interface = c_data['interface_instance'] = interfaces[component_id]

                    methods = [i for i in dir(interface.__class__) if i[0:2] != '__']
                    [setattr(c, m, getattr(interface, m)) for m in methods if hasattr(c, m)]

            except TypeError as e:
                raise TypeError(str(e) + ', while initiating ' + str(comp['class']) + (
                    '/' + comp['name'] if comp['name'] is not None else ''))

    # interface_factory = c_data['interfaces'][self.env]
    # interface = interface_factory(comp['interface_instance_mjc'])
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

            components = kwargs['components'] if 'components' in kwargs else []
            components = {c.__data__['class_name']: c for c in components}
            probe = kwargs['probe'] if 'probe' in kwargs else None
            template = kwargs['template'] if 'template' in kwargs else None

            setattr(c, '__data__', {
                'class_name': class_name,  # the name of the factory class, in snake case
                'class_file_path': class_file_path,  # the abs path of the FILE where the class is declared
                'class_dir_path': class_dir_path,  # the abs path of the DIRECTORY where the class is declared
                'template': template,
                'template_path': class_dir_path + '/' + class_name + '.xml',  # the abs path of the .xml template

                # the dict of components' classes indexed by class name
                # e.g.:  {'ur5': <class 'yarok.components.ur5.ur5.UR5'>, ...}
                'components': components,

                # the class constructor annotations
                # format: dict({ comp. name : class }) e.g.
                # e.g.:  {'mani': <class 'yarok.components.ur5.ur5.UR5'>, ...}
                'annotations': init_annotations,

                # interfaces's classes indexed environment "name"
                # e.g.: {'mjc': <class 'yarok.components.ur5.ur5.UR5InterfaceMJC'>}
                'interfaces': interfaces,

                # probe. a fn that returns an object key:value
                # the value is plotted or logged depending on the type.
                'probe': probe
            })
        return c

    return _
