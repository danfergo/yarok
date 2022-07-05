import inspect
import os
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring

from .config import ConfigBlock

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


def stringify(el):
    """ used to construct exception messages """
    """ returns  """
    return tostring(el, encoding="unicode") \
               .replace('\n', '') \
               .strip() \
               .split('>')[0] + '>'


class ComponentsManager:
    """
    Handles loading components templates (.xml) & controllers (.py)
    and Builds xml tree and components i.e.,

    - self.xml_tree   =>
    - self.components => dict ([component.id] => dict(
        class => component factory class,
        name => component name,
        tag => component tag name (to be used in the template)
        class_name => component factory (snake-case) name,
        id => auto generated id,
        children => [dict(...)],
        instance => object ref             # set while instantiating the components
    ))


    """

    def __init__(self, root_component, components_config: ConfigBlock):
        self.id_counter = 0
        # used for direct access to component
        self.components_config = components_config
        self.components = {}

        # used to iterate trough all components, depth first, 
        # leafs-to-root, because of dependencies, etc.
        self.components_tree = {
            'class': root_component,
            'name': '',
            'name_path': '/',
            'id': self.gen_id(),
            'parent': None,
            'children': [],
            'config': components_config['/'] if components_config is not None else {}
        }
        self.xml_tree = self.load_tree(self.components_tree)

        # print( tostring(self.xml_tree, encoding="unicode") )

        # build components map, for direct access
        def walk_components(component):
            for child in component['children']:
                walk_components(child)
            self.components[component['id']] = component

        walk_components(self.components_tree)

    def is_id(self, idx):
        return isinstance(idx, int) or isinstance(idx, str)

    def gen_id(self, name=''):
        self.id_counter += 1
        # '__c__' + str(self.id_counter) + '-' +
        return name + '#' + str(self.id_counter)

    def get(self, n):
        return self.components[n]

    def get_by_name(self, c, name):
        """
            Gets a component by 'name', given its parent 'c' (or its parent id)
        """
        comp = self.components[c] if self.is_id(c) else c
        for child in comp['children']:
            if name == child['name']:
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

    def load_tree(self, comp):
        """
            The method that loads the multiple components and its template (.xml) into
            a single xml/model tree. It also loads the multiple components into a tree
        """

        # inits auxiliar variables from the component metadata
        template = comp['class'].__data__['template']
        xml_path = comp['class'].__data__['template_path']
        id = comp['id']

        # loads xml tree from xml path
        tree = ET.fromstring(template) if template is not None else ET.parse(xml_path).getroot()

        # re-pathing all file refs, that are not absolute refs,
        # to be relative to the .xml file
        dir_path = str(pathlib.Path(xml_path).parent.resolve())
        for e in tree.iter():
            if 'file' in e.attrib and not e.attrib['file'].startswith('/'):
                e.attrib['file'] = dir_path + '/' + e.attrib['file']

        # renaming primary&foreign keys to from xxx to id:xxx
        # !!!! understand the rename_fk in two places. is it simplifiable?
        def rename_fk(els):
            for el in els:
                if el.tag == 'worldbody':
                    continue
                try:
                    self.parse_attributes(el, comp)
                except Exception as e:
                    c_path = comp['name_path']
                    raise Exception('\n\n' + e.args[0]
                                    + ',\nfor ' + c_path
                                    + ',\n\nplease patch yarok config with { components: { ' + c_path + ' : { ' + e.args[
                                        1] + ': <value> }}}  '
                                    )

                for attr in RENAME_KEYS_ATTRS_NAMES:
                    if attr in el.attrib:
                        el.attrib[attr] = id + ':' + el.attrib[attr]
                rename_fk(list(el))

        rename_fk(list(tree))

        # walking current file .xml tree and looking for components and instantiating them
        def walk_tree(elements, parent_component):
            component_components_factories = parent_component['class'].__data__['components']

            for element in elements:
                tag = element.tag

                if tag in EXTENDABLE_BLOCKS_NAMES:
                    continue
                elif tag in component_components_factories:
                    component_tag = tag
                    component_name = element.attrib['name']

                    if component_name == '':
                        raise KeyError(
                            'No component should be named ""!, ' +
                            component_tag +
                            '[name=root] at' +
                            parent_component['name'])

                    # creates new sub component data wrapper
                    sub_component = {
                        'id': self.gen_id(component_name),
                        'name': component_name,
                        'name_path': ('/' + component_name) \
                            if (parent_component['name_path'] == '/') \
                            else (parent_component['name_path'] + '/' + component_name),
                        'tag': component_tag,
                        'class': component_components_factories[component_tag],
                        'parent': parent_component,
                        'children': []
                    }
                    sub_component['config'] = self.components_config[
                        sub_component['name_path']] if self.components_config is not None else {}

                    # appends the newly found sub component to the previous/parent component
                    parent_component['children'].append(sub_component)

                    # load the new subcomponent tree
                    sub_component_tree = self.load_tree(
                        sub_component
                    )

                    self.merge_trees(tree, element, sub_component_tree)

                    # nests all descendant elements specified in the parent xml,
                    # e.g. in the environment.xml <parent><child_to_nest parent='link_name'></child_to_nest></parent>
                    # in this case, the child_to_nest is nested as the last child of the the element @name='link_name'
                    # in the current .xml template.
                    # !!!!! EDIT THIS COMMENT / DOCUMENTATION
                    for nested_element in list(element):
                        if 'parent' in nested_element.attrib:
                            parentName = nested_element.attrib['parent']
                            parent = sub_component_tree.find(
                                ".//body[@name='" + (sub_component['id'] + ':' + parentName) + "']")
                            if parent is None:
                                raise KeyError('Failed to nest ' +
                                               stringify(nested_element) + '>,' +
                                               ' body[name=' +
                                               parentName +
                                               '] not being found in ' + sub_component['tag'] + ' template.')
                            # sub_tree.attrib['__base_component__'] = sub_tree['base_component']
                            nested_element.attrib.pop('parent')
                            parent.append(nested_element)
                        else:
                            sub_component_tree.find('worldbody').append(nested_element)

                        walk_tree([nested_element], comp)

                else:
                    walk_tree(list(element), comp)

                try:
                    self.parse_attributes(element, comp)
                except Exception as e:
                    raise Exception(e.args[0] + ',\nfor ' + str(comp))

                for attr in RENAME_KEYS_ATTRS_NAMES:
                    if attr in element.attrib:
                        element.attrib[attr] = parent_component['id'] + ':' + element.attrib[attr]

        walk_tree(tree, comp)

        return tree

    def parse_attributes(self, elem, comp):
        def set(k, v):
            elem.attrib[k] = v

        try:
            {set(k, self.replace_all(v, comp['config'])) for k, v in elem.attrib.items() if "$" in v}
        except Exception as e:
            raise Exception(e.args[0] + ',\nfor ' + stringify(elem), e.args[1])

    def replace_all(self, attr, config):
        # not very pretty code, but it works
        # replaces all ${key} -> config[key] in the attr.

        wrap = {'txt': attr, 'offset': 0}
        regex = "(\$\{(\w(\w|\\n)*)\})"

        def replace(match, o):
            txt = o['txt']
            offset = o['offset']
            k = match.group(2)
            s = match.span(2)
            if k not in (config or {}):
                raise Exception(
                    'Failed to find config "' + k + '" while parsing "' + attr + '".',
                    k
                )

            o['txt'] = txt[: offset + s[0] - 2] + config[k] + txt[offset + s[1] + 1:]
            # offset is used to compensate the "original" spans
            # for the differences in the string before and after
            o['offset'] += len(config[k]) - (s[1] - s[0]) - 3

        ''
        [replace(x, wrap) for x in re.finditer(regex, attr)]
        return wrap['txt']

    def merge_trees(self, tree, element, sub_component_tree):
        # auxiliary map that maps child->parent element,
        # for component instantiation elements
        parent_map = {
            child_: parent_
            for parent_ in tree.iter()
            for child_ in parent_
            if child_ == element
            # if is_component(child_)
        }
        extendable_blocks = {
            block_name: tree.find(block_name)
            for block_name in EXTENDABLE_BLOCKS_NAMES
        }

        # merge all blocks actuators, sensors, etc
        # with the current component tree
        for block_name in extendable_blocks:
            block = sub_component_tree.find(block_name)
            if block is not None:
                if extendable_blocks[block_name] is not None:
                    extendable_blocks[block_name].extend(block)
                else:
                    tree.append(block)

        # remove the "component" tag from the current tree
        # merge the new subcomponent tree/body with the current tree
        parent_map[element].remove(element)
        comp_wb = sub_component_tree.find('worldbody')
        parent_map[element].extend(comp_wb)

        return parent_map[element]

    def init_components(self, interfaces, config: ConfigBlock):
        """
            Initializes components.
            Called after all the interfaces are instantiated (by the platform manager)

            Iterates through all components,
                - Gets the component class annotations,
                instantiates the component and stores at component['instance']

                - Gets and stores the component interface
        """

        def step_components(comp):
            # build the children, its dependencies, first.
            for child in comp['children']:
                step_components(child)

            c_data = comp['class'].__data__
            try:
                c = comp['class'](**{
                    **{
                        n: self.get_by_name(comp, n)['instance'] for n in c_data['annotations']
                    },
                    # **(
                    #     {config: ConfigBlock(config[parent['name_path']])} if parent['name_path'] in config else {}
                    # )
                })

                comp['instance'] = c

                if comp['id'] in interfaces:
                    interface = c_data['interface_instance'] = interfaces[comp['id']]
                    methods = [i for i in dir(interface.__class__) if i[0:2] != '__']
                    [setattr(c, m, getattr(interface, m)) for m in methods if hasattr(c, m)]

            except TypeError as e:
                raise TypeError(str(e) + ', while initiating ' + str(comp['class']) + (
                    '/' + comp['name'] if comp['name'] is not None else ''))

        step_components(self.components_tree)

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
            components = {c.__data__['tag']: c for c in components}
            probe = kwargs['probe'] if 'probe' in kwargs else None
            template = kwargs['template'] if 'template' in kwargs else None
            tag = kwargs['tag'] if 'tag' in kwargs else None

            setattr(c, '__data__', {
                'tag': tag if tag is not None else class_name,
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
