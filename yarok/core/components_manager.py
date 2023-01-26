import copy
import pathlib
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring

from yarok.core.config_block import ConfigBlock

# attributes that are renamed from 'name' to 'id'
RENAME_KEYS_ATTRS_NAMES = [
    'name',
    'joint',
    'actuator',
    'body1',
    'body2',
    'joint1',
    'joint2',
    'material',
    'mesh',
    'texture',
    'tendon'
]

# names of the blocks to be merged
# except worldbody that follows a special merging process
# i.e. nesting components, etc.
EXTENDABLE_BLOCKS_NAMES = [
    'default',
    'asset',
    'tendon',
    'sensor',
    'actuator',
    'equality',
    'contact'
]


def stringify(el):
    return tostring(el, encoding="unicode")


def stringify_header(el):
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

        # used to iterate through all components, depth first,
        # leafs-to-root, because of dependencies, etc.
        config = components_config['/'] if '/' in components_config else ConfigBlock({})
        config.defaults(root_component.__data__['defaults'])
        self.components_tree = {
            'class': root_component,
            'name': '',
            'name_path': '/',
            'id': self.gen_id(),
            'parent': None,
            'children': [],
            'config': config
        }
        self.xml_tree = self.load_tree(self.components_tree)

        if True:
            f = open("scene.xml", "w")
            f.write(tostring(self.xml_tree, encoding='unicode'))
            f.close()

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

    def get(self, comp_id):
        return self.components[comp_id]

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

    def config(self, c):
        comp = self.components[c] if self.is_id(c) else c
        return comp['config']

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

        # handling lean trees
        # if tree.tag != 'mujoco':
        #     mujocoRoot = ET.Element("mujoco")
        #     mujocoRoot.append(tree)
        #     tree = mujocoRoot

        # if not any([e.tag =='worldbody' for e in tree.getChildren()]):
        #     worldbodyRoot = ET.Element("worldbody")
        #     worldbodyRoot.append(tree)

        extends = comp['class'].__data__['extends']
        if extends is not None:
            cls = comp['class']
            comp['class'] = extends
            ext_tree = self.load_tree(comp)
            # element = ET.Element("ext-wrapper")
            # wb = ext_tree.find('worldbody')
            self.merge_nonbody_blocks(ext_tree, tree)
            ext_tree.find('worldbody').extend(tree.find('worldbody'))

            comp['class'] = cls
            tree = ext_tree

        # re-pathing all file refs, that are not absolute refs,
        # to be relative to the .xml file
        dir_path = str(pathlib.Path(xml_path).parent.resolve())
        for e in tree.iter():
            if 'file' in e.attrib and not e.attrib['file'].startswith('/'):
                e.attrib['file'] = dir_path + '/' + e.attrib['file']

        # renaming primary&foreign keys to from xxx to id:xxx
        # !!!! understand the rename_fk in two places. is it simplifiable?
        def rename_fk_recur(els):
            for el in els:
                if el.tag == 'worldbody':
                    continue
                try:
                    self.parse_attributes(el, comp['config'])
                except Exception as e:
                    c_path = comp['name_path']
                    raise Exception('\n\n' + e.args[0]
                                    + ',\nfor ' + c_path
                                    + ',\n\nplease patch yarok config with { components: { ' + c_path + ' : { ' +
                                    e.args[
                                        1] + ': <value> }}}  '
                                    )

                for attr in RENAME_KEYS_ATTRS_NAMES:
                    if attr in el.attrib:
                        el.attrib[attr] = id + ':' + el.attrib[attr]
                rename_fk_recur(list(el))

        rename_fk_recur(list(tree))

        # walking current file .xml tree and looking for components and instantiating them
        def walk_tree_recur(parent, elements, parent_component, config=None):
            c_data = parent_component['class'].__data__

            for element in elements:
                tag = element.tag

                try:
                    self.parse_attributes(element, config or comp['config'])
                except Exception as e:
                    raise Exception(e.args[0] + ',\nfor ' + str(comp))

                has_if = 'if' in element.attrib
                if has_if:
                    condition_str = element.attrib['if']
                    element.attrib.pop('if')
                    condition = eval(condition_str, None, config or parent_component['config'])
                    if not condition:
                        parent.remove(element)
                        continue

                if tag in EXTENDABLE_BLOCKS_NAMES:
                    continue

                elif tag == 'for':
                    condition_str = element.attrib['each']
                    var_name = element.attrib['as'] if 'as' in element.attrib else None
                    # print('--> ', parent_component['config'],  globals()['range'])
                    conf = config or parent_component['config']
                    elems = eval(condition_str, None, conf)
                    parent.remove(element)

                    for e in elems:
                        new_config = None if var_name is None else ConfigBlock({
                            var_name: e
                        })
                        new_config.defaults(config or comp['config'])
                        new_element = copy.deepcopy(element)
                        parent.extend(new_element)
                        walk_tree_recur(parent, list(new_element), comp, config=new_config)

                elif tag == 'if':
                    condition_str = element.attrib['the']
                    condition = eval(condition_str)
                    parent.remove(element)

                    if condition:
                        parent.extend(element)
                        walk_tree_recur(parent, list(element), comp)

                elif tag in c_data['components']:
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
                        'class': c_data['components'][component_tag],
                        'parent': parent_component,
                        'children': []
                    }
                    config = self.components_config[sub_component['name_path']] \
                        if sub_component['name_path'] in self.components_config \
                        else ConfigBlock({})
                    config.defaults(sub_component['class'].__data__['defaults'])
                    sub_component['config'] = config

                    # appends the newly found sub component to the previous/parent component
                    parent_component['children'].append(sub_component)

                    # load the new subcomponent tree
                    sub_component_tree = self.load_tree(sub_component)
                    # if tag == 'digit':
                    #     print('DIGIT !!')
                    #     print(tostring(sub_component_tree, encoding='unicode'))
                    self.merge_nonbody_blocks(tree, sub_component_tree)

                    # nest in place the "body" of the declared component
                    parent.remove(element)
                    comp_wb = sub_component_tree.find('worldbody')
                    parent.extend(comp_wb)

                    # further, nests the declared content, in the declared component,
                    # ==> as last child if no "parent" is specified.
                    # ==> (or) inside the body with name @parent
                    #
                    # e.g. <parent><child_to_nest parent='link_name'></child_to_nest></parent>
                    # the child_to_nest is nested as the last child of the element @name='link_name'
                    component_content_elements = list(element)
                    for nested_element in component_content_elements:
                        if 'parent' in nested_element.attrib:
                            # print('PARENT', nested_element.attrib)
                            parentName = nested_element.attrib['parent']
                            new_parent = parent.find(
                                ".//body[@name='" + (sub_component['id'] + ':' + parentName) + "']")
                            if new_parent is None:
                                raise KeyError('Failed to nest ' +
                                               stringify_header(nested_element) + '>,' +
                                               ' body[name=' +
                                               parentName +
                                               '] not being found in ' + sub_component['tag'] + ' template.')
                            # sub_tree.attrib['__base_component__'] = sub_tree['base_component']
                            nested_element.attrib.pop('parent')
                            new_parent.append(nested_element)
                            walk_tree_recur(new_parent, [nested_element], comp, config)
                        else:
                            new_parent = parent  # sub_component_tree.find('worldbody')
                            new_parent.append(nested_element)
                            walk_tree_recur(new_parent, [nested_element], comp, config)

                else:
                    walk_tree_recur(element, list(element), comp, config)

                for attr in RENAME_KEYS_ATTRS_NAMES:
                    if attr in element.attrib:
                        element.attrib[attr] = parent_component['id'] + ':' + element.attrib[attr]

        walk_tree_recur(tree, [tree.find('worldbody')], comp)

        return tree

    def parse_attributes(self, elem, config):
        def set(k, v):
            elem.attrib[k] = v

        try:
            {set(k, self.replace_all(v, config)) for k, v in elem.attrib.items() if "$" in v}
        except Exception as e:
            raise Exception(e.args[0] + ',\nfor ' + stringify_header(elem), e.args[1])

    def replace_all(self, attr, config):
        # not very pretty code, but it works
        # replaces all {expression} -> eval(expressio, None, config) in the attr.

        wrap = {'txt': attr, 'offset': 0}
        # todo improve this regex to pass python code
        regex = "(\$\{(\w(\w|\+|\.|\*|\ |\\n|\'|[|]|=|/|%)*)\})"

        def replace(match, o):
            txt = o['txt']
            offset = o['offset']
            k = match.group(2)
            s = match.span(2)

            v = str(eval(k, None, config))
            # if k not in (config or {}):
            #     raise Exception(
            #         'Failed to find config "' + k + '" while parsing "' + attr + '".',
            #         k
            #     )

            o['txt'] = txt[: offset + s[0] - 2] + v + txt[offset + s[1] + 1:]
            # offset is used to compensate the "original" spans
            # for the differences in the string before and after
            o['offset'] += len(v) - (s[1] - s[0]) - 3

        [replace(x, wrap) for x in re.finditer(regex, attr)]
        return wrap['txt']

    def merge_nonbody_blocks(self, tree, sub_component_tree):
        # auxiliary map that maps child->parent element,
        # for component instantiation elements
        # parent_map = {
        #     child_: parent_
        #     for parent_ in tree.iter()
        #     for child_ in parent_
        #     if child_ == element
        #     # if is_component(child_)
        # }

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
                    if block_name == 'default' or block_name == 'asset':
                        tree.insert(0, block)
                    else:
                        tree.append(block)

        # remove the "component" tag from the current tree
        # merge the new subcomponent tree/body with the current tree
        # print('>> ', element, parent, parent_map[element], parent == parent_map[element])
        # parent_map[element]
        # parent.remove(element)
        # comp_wb = sub_component_tree.find('worldbody')
        # parent.extend(comp_wb)

        # return parent_map[element]
