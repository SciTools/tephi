# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.


import os
import sys
import re
import inspect


document_dict = {
                     # Use autoclass for classes
                     'class': '''
%(object_docstring)s

..

    .. autoclass:: %(object_name)s
        :members:
        :undoc-members:

''',
                     'function': '''
.. autofunction:: %(object_name)s

''',
                     # For everything else, let automodule do some magic...
                     None: '''

.. autodata:: %(object_name)s

'''}


def lookup_object_type(obj):
        if inspect.isclass(obj):
            return 'class'
        elif inspect.isfunction(obj):
            return 'function'
        else:
            return None


def auto_doc_module(file_path, import_name, root_package, package_toc=None, title=None):
    r = __import__(import_name)
    r = sys.modules[import_name]
    elems = dir(r)

    if '__all__' in elems:
        document_these = r.__all__
        document_these = [[obj, r.__getattribute__(obj)] for obj in document_these]
    else:
        document_these = [[obj, r.__getattribute__(obj)] for obj in elems if not obj.startswith('_') and not inspect.ismodule(r.__getattribute__(obj))]
        is_from_this_module = lambda x, this_module=r.__name__: hasattr(x[1], '__module__') and x[1].__module__ == r.__name__
    
        document_these = filter(is_from_this_module, document_these)
        sort_order = {'class': 2, 'function':1, None:0}
        # sort them according to sort_order dict
        document_these = sorted(document_these, key=lambda x: sort_order.get(lookup_object_type(x[1]),0))
        
    tmp = ''
    for element, obj in document_these:
        tmp += '----------\n' + document_dict[lookup_object_type(obj)] % {'object_name': import_name + '.' + element,
                                                         'object_name_header_line':'+' * len(import_name + '.' + element),
                                                         'object_docstring': inspect.getdoc(obj),
                                                         }
            

    module_elements = '\n'.join([' * :py:obj:`%s`' % (element) for element, obj in document_these])
    
    tmp = r'''.. _%(import_name)s:

%(title_underline)s
%(title)s
%(title_underline)s

%(sidebar)s
   
.. currentmodule:: %(root_package)s

.. automodule:: %(import_name)s

In this module:

%(module_elements)s


''' + tmp
    if package_toc:
       sidebar = """
.. sidebar:: Modules in this package

%(package_toc_tree)s

    """ % {'package_toc_tree': package_toc}
    else:
       sidebar = ''
 
    return tmp % {'title': title or import_name, 'title_underline': '=' * len(title or import_name), 'import_name': import_name, 'root_package':root_package, 'sidebar':sidebar, 'module_elements': module_elements}


def auto_doc_package(file_path, import_name, root_package, sub_packages):
    package_toc = '\n      '.join(sub_packages)
    package_toc = '''
   .. toctree::
      :maxdepth: 2
      :titlesonly:
      
      %s

   
''' % package_toc
    
    if '.' in import_name:
        title = None
    else:
        title = import_name.capitalize() + ' reference documentation'

    return auto_doc_module(file_path, import_name, root_package, package_toc=package_toc, title=title)


def auto_package_build(app):

    root_package = app.config.autopackage_name
    if root_package is None:
        raise ValueError('set the autopackage_name variable in the conf.py file')

    if not isinstance(root_package, list):
        raise ValueError("autopackage was expecting a list of packages to document e.g. ['itertools']")

    for package in root_package:
        do_package(package)


def do_package(package_name):

#    out_dir = package_name + os.path.sep
    out_dir = os.path.join('source', package_name) + os.path.sep

    # import the root package. If this fails then an import error will be raised.
    module = __import__(package_name)
    root_package = package_name
    rootdir = os.path.dirname(module.__file__)


    package_folder = []
    module_folders = {}
    for root, subFolders, files in os.walk(rootdir):
        for fname in files:
            name, ext = os.path.splitext(fname)
            
            # skip some non-relevant files
            if ( fname.startswith('.') or fname.startswith('#') or re.search("^_[^_]", fname) or 
                 fname.find('.svn')>=0 or not (ext in ['.py', '.so']) ):
                continue
            
            rel_path = root_package + os.path.join(root, fname).split(rootdir)[-1]
            mod_folder = root_package + os.path.join(root).split(rootdir)[-1].replace('/','.')

            # only add to package folder list if it contains an __init__ script
            if name == '__init__':
                package_folder.append([mod_folder, rel_path])
            else:
                import_name = mod_folder + '.' + name
                module_folders.setdefault(mod_folder, []).append([import_name, rel_path])
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    for package, package_path in package_folder:
        if '._' in package or 'test' in package:
            continue

        sub_packages = (spackage for spackage, spackage_path in package_folder if spackage != package and spackage.startswith(package))
        paths = [os.path.join(*spackage.rsplit('.', 2)[-2:None])+'.rst' for spackage in sub_packages]
        paths.extend([os.path.join(os.path.basename(os.path.dirname(path)), os.path.splitext(os.path.basename(path))[0]) for imp_name, path in module_folders.get(package, [])])
        paths.sort()
        doc = auto_doc_package(package_path, package, root_package, paths)

        package_dir = out_dir + package.replace('.', os.path.sep)
        if not os.path.exists(package_dir):
            os.makedirs(out_dir + package.replace('.', os.path.sep))
           
        out_path = package_dir + '.rst'
        if not os.path.exists(out_path) or doc != ''.join(open(out_path, 'r').readlines()):
            print(f'creating out of date/non-existant document {out_path}')
            with open(out_path, 'w') as fo:
                fo.write(doc)

        for import_name, module_path in module_folders.get(package, []):
            doc = auto_doc_module(module_path, import_name, root_package)
            out_path = out_dir + import_name.replace('.', os.path.sep) + '.rst'
            if not os.path.exists(out_path) or doc != ''.join(open(out_path, 'r').readlines()):
                print(f'creating out of date/non-existant document {out_path}')
                with open(out_path, 'w') as fo:
                    fo.write(doc)


def setup(app):
    app.connect('builder-inited', auto_package_build)
    app.add_config_value('autopackage_name', None, 'env')
