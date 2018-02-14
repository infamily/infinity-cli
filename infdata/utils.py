import inspect
import itertools
from importlib import import_module
from pkgutil import iter_modules

import six
from boltons.iterutils import remap
from functools import reduce
import operator

def dictget(d, mapList):
    '''
    Given:
    >>> d = {'a': [{'b': 'c'}, {'e': 'f'}, {'g': 'h'}]}

    Returns:
    >>> dictget(d, ['a', 2, 'b'])
    >>> 'c'
    '''
    return reduce(operator.getitem, mapList, d)

def metapath(path):
    '''
    Given:
    >>> p = [1, 'a', 2, 'b', 3]

    Returns:
    >>> metapath(p)
    >>> [0, 'a', 0, 'b', 0]
    '''
    metapath = []
    for item in path:
        if isinstance(item, int):
            metapath.append(0)
        else:
            metapath.append(item)
    return metapath


def convert(key, value, meta):
    '''
    Given:
    >>> key = 'something'
    >>> value = '1,234'
    >>> meta = {'': [('int', lambda _: _.replace(',')), ['https://www.wikidata.org/wiki/Q82799']]}

    Returns:
    >>> key = 'Q82799'
    >>> value = 1234
    '''

    schema, types = list(meta.keys()) + list(meta.values())


    if schema:

        for index, operation in enumerate(schema):
            if index == 0:
                continue
            elif index == 1:
                value = eval(operation)(value)

        try:
            value = eval(schema[0])(value)
        except:
            pass

    if types:

        for index, typeurl in enumerate(types):
            if index == 0:
                key = typeurl.rsplit('/',1)[-1]

    return key, value

def standardize(metadata, data, if_schema_value_type=tuple):
    '''
    Combine data with schema and types in metadata by zipping tree.

    Given:
    >>> data = [{'address': {'number': 14, 'street': 'Leonardo str.'},
  'children': [{'age': 1, 'name': 'Mike'}, {'age': 15, 'name': 'Tom'}],
  'name': 'Max'},
 {'address': {'number': 12, 'street': 'Mao str.'},
  'children': [{'age': 10, 'name': 'Sonnie'}],
  'name': 'Lin'},
 {'address': {'number': 1, 'street': 'Nexus str.'},
  'children': [{'age': 1, 'name': 'Deli'}, {'age': 7, 'name': 'Miki'}],
  'name': 'Dim'}]

    >>> metadata = [{'': [['obj'], ['https://www.wikidata.org/wiki/Q7565']],
  'address': {'': [['obj'], ['https://www.wikidata.org/wiki/Q319608']],
   'number': {'': [['int', 'lambda _: int(_)'], ['https://www.wikidata.org/wiki/Q1413235']]},
   'street': {'': [['str'], ['https://www.wikidata.org/wiki/Q24574749']]}},
  'children': [{'': [['obj'], ['https://www.wikidata.org/wiki/Q7569']],
    'age': {'': [['int', 'lambda _: float(_)'], ['https://www.wikidata.org/wiki/Q185836']]},
    'name': {'': [['str'], ['https://www.wikidata.org/wiki/Q82799']]}}],
  'name': {'': [['str'], ['https://www.wikidata.org/wiki/Q82799']]}}]

    Returns:
    >>> standardize(data, metadata)
    [{'Q319608': {'Q1413235': 14, 'Q24574749': 'Leonardo str.'},
  'Q7569': [{'Q185836': 1, 'Q82799': 'Mike'},
   {'Q185836': 15, 'Q82799': 'Tom'}],
  'Q82799': 'Max'},
 {'Q319608': {'Q1413235': 12, 'Q24574749': 'Mao str.'},
  'Q7569': [{'Q185836': 10, 'Q82799': 'Sonnie'}],
  'Q82799': 'Lin'},
 {'Q319608': {'Q1413235': 1, 'Q24574749': 'Nexus str.'},
  'Q7569': [{'Q185836': 1, 'Q82799': 'Deli'},
   {'Q185836': 7, 'Q82799': 'Miki'}],
  'Q82799': 'Dim'}]
    '''

    def visit(path, key, value):
        try:
            meta = dictget(metadata, metapath(path))[key if not isinstance(key, int) else 0]
        except:
            return key, value

        if not any([isinstance(value, t) for t in [dict, list, tuple]]):

            k, v = list(meta.values())[0]
            metamap = {tuple(k): v}

            return convert(key, value, metamap)
        else:
            if isinstance(key, str):
                try:
                    k, v = list(meta)[0]['']
                except:
                    try:
                        k, v = meta['']
                    except:
                        pass

                try:
                    metamap = {tuple(k): v}

                    key, _ = convert(key, value, metamap)
                except:
                    pass

                return key, value

            return key, value


    remapped = remap(data, visit=visit)
    return remapped


def take(data):
    return data[0:1], data[1:]

def normalize(data):
    return standardize(*take(data))

def has_metadata(data):
    try:
        dummy = normalize(data[:2])
        del dummy
        return True
    except:
        return False


def schematize(obj):
    '''
    Get schema of nested JSON, assuming first item in lists.
    '''
    if isinstance(obj, dict):
        return {k: schematize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [schematize(elem) for elem in obj][:1]
    else:
        return obj

def generate_metadata_template(header):
    """
    Generates metadata template based on first record in data.
    """
    schematized = schematize(header)

    def visit(path, key, value):
        if not any([isinstance(value, t) for t in [dict, list, tuple]]):
            return key, {'': [[type(value).__name__],[]]}
        else:
            return key, value

    remapped = remap(schematized, visit=visit)
    remapped[0][''] = [['example.com/people', 'crawler=1.0.0'],['https://www.wikidata.org/wiki/Q35120']]
    return remapped


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def walk_modules(path):
    """Loads a module and all its submodules from the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.

    For example: walk_modules('inf.utils')
    """

    mods = []
    mod = import_module(path)
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, subpath, ispkg in iter_modules(mod.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                mods += walk_modules(fullpath)
            else:
                submod = import_module(fullpath)
                mods.append(submod)
    return mods


def iter_tasks(tasks_module):
    for module in walk_modules(tasks_module):
        for obj in six.itervalues(vars(module)):
            if inspect.isclass(obj) and \
                    obj.__module__ == module.__name__ and \
                    getattr(obj, 'name', None):
                yield obj