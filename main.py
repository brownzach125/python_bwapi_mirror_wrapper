from javalang.parse import parse
from javalang.tree import ClassDeclaration, MethodDeclaration

from os import walk, mkdir
from os.path import join, isdir

files = []
for (dirpath, dirnames, filenames) in walk(".\\api"):
    if filenames:
        for filename in filenames:
            files.append((dirpath, filename))


def add_line(indent_level, line):
    return '    ' * indent_level + line + '\n'

file = ""

python_packages = {
}

class_locations = {
    'bwapi': {},
    'bwta': {}
}
known_classes = {}

wrapped_path = join('bwapi_mirror_wrapper')

parsed_filenames = [
        'UnitType.java',
        'Game.java',
        'Mirror.java',
        'Player.java',
]

class_declerations = []

# Find All Packages
for dirname, filename in files:
    #if filename not in parsed_filenames:
    #    continue

    file_path = join(dirname, filename)
    with open(file_path, 'r') as stream:
        java_str = stream.read()

        tree = parse(java_str)

        package_name = tree.package.name

        package_path = join(wrapped_path, package_name)

        if package_name not in python_packages:
            python_packages[package_name] = {}
        python_package = python_packages[package_name]

        if not isdir(package_path):
            mkdir(package_path)
            open(join(package_path, '__init__.py'), 'w+')

        class_decs = tree.filter(ClassDeclaration)
        for path, class_dec in class_decs:
            class_dec.package_name = package_name
            class_dec.package_path = package_path
            class_dec.imports = tree.imports
            class_declerations.append(class_dec)
            class_name = class_dec.name
            python_package[class_name] = class_name
            class_locations[package_name][class_name] = f'bwapi_mirror_wrapper.{package_name}.{class_name}'
            known_classes[class_name] = True

# Wrap Classes
for package, classes in class_locations.items():
    lines = []
    for python_file in classes.keys():
        if python_file != 'JarResources':
            lines.append(f'from . import {python_file}\n')
    with open(join('bwapi_mirror_wrapper', package, '__init__.py'), 'w') as output:
        output.writelines(lines)


for class_dec in class_declerations:
    imports = {}

    file_str = ''
    indent_level = 0

    class_name = class_dec.name
    if class_name == 'JarResources':
        continue

    indent_level += 1
    file_str += add_line(indent_level, f'class {class_name}(object):\n')
    if any('public' in x.modifiers for x in class_dec.constructors) or not class_dec.constructors:
        file_str += add_line(indent_level + 1, f'def __init__(self, *args, **kwargs):')
        file_str += add_line(indent_level + 2, f'self._base = Java_{class_dec.name}(*args, **kwargs)')
        file_str += '\n'
        file_str += add_line(indent_level + 1, f'def __getattribute__(self, attr):')
        file_str += add_line(indent_level + 2, f'return getattr(object.__getattribute__(self, "_base"), attr)')
        file_str += '\n'
    else:
        file_str += add_line(indent_level + 1, f'def __init__(self, field):')
        file_str += add_line(indent_level + 2, f'self._field = field')
        file_str += '\n'

        file_str += add_line(indent_level + 1, f'def __getattribute__(self, attr):')
        file_str += add_line(indent_level + 2, f'field_name = object.__getattribute__(self, "_field")')
        file_str += add_line(indent_level + 2, f'unit_type = getattr(Java_{class_name}, field_name)')
        file_str += add_line(indent_level + 2, f'return getattr(unit_type, attr)')
        file_str += '\n'

    for method in class_dec.methods:
        if 'private' in method.modifiers:
            continue

        method_name = method.name
        if method.return_type:
            return_type = method.return_type.name

        indent_level += 1

        first_line = f'def {method_name}(self, '
        for parameter in method.parameters:
            first_line += parameter.name + ", "

        first_line += '):'

        file_str += add_line(indent_level, first_line)

        if method.return_type and return_type in known_classes:
            if return_type not in imports and return_type != class_name:
                #location = class_locations[return_type]
                #imports[return_type] = f'import {location} as {return_type}'
                #imports[return_type] = f'from AI.src.wrapped.{location} import {return_type}'
                #imports[return_type] = f'import {location}'
                for java_import in class_dec.imports:
                    if return_type in java_import.path or (java_import.wildcard and java_import.path in class_locations and return_type in class_locations[java_import.path]):
                        if java_import.wildcard:
                            return_type_full_value = class_locations[java_import.path][return_type]
                        else:
                            return_type_full_value = class_locations[java_import.path.split('.')[0]][return_type]
                        break
                if not return_type_full_value:
                    return_type_full_value = class_locations[class_dec.package_name][return_type]

                imports[return_type] = f'import {return_type_full_value} as {return_type}'

            file_str += add_line(indent_level + 1, f'return {return_type}.{return_type}()')
        else:
            file_str += add_line(indent_level + 1, f'pass')
        file_str += add_line(indent_level, '')

        indent_level -= 1

    for field in class_dec.fields:
        if 'private' in field.modifiers:
            continue
        indent_level += 1

        if 'public' in field.modifiers and \
           'static' in field.modifiers and \
           'final' in field.modifiers and \
            field.type.name == class_name:
            # This is a instance of the class not a

            field_name = field.declarators[0].name
            if field_name == 'None':
                indent_level -= 1
                continue

            file_str += add_line(indent_level, '')
            file_str += add_line(indent_level, f'{field_name} = {class_name}("{field_name}")')

        indent_level -= 1

    for import_line in imports.values():
        file_str = add_line(indent_level, import_line) + file_str

    indent_level -= 1
    file_str = add_line(indent_level, 'if False:') + file_str
    file_str = f'from {class_dec.package_name} import {class_dec.name} as Java_{class_dec.name}\n\n' + file_str
    file_str += add_line(indent_level, f'else:')
    file_str += add_line(indent_level + 1, f'{class_name} = Java_{class_name}')

    #file_str = '\n' + file_str

    path = join(class_dec.package_path, class_name + '.py')

    with open(path, 'w') as output:
        output.write(file_str)


# TODO temp

#print(python_packages)
