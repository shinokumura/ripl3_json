import os
import shutil
import time
import json


def slices(s, *args):
    position = 0
    for length in args:
        yield s[position : position + length]
        position += length


def flatten(xs):
    from collections.abc import Iterable

    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


def flatten_list(list):
    return [item for sublist in list for item in sublist]


def check_list(init_list):
    print(init_list)
    # print(any(isinstance(i, list) for i in init_list))

    def _is_list_instance(init_list):
        print(isinstance(init_list, list))

        sub_list = flatten_list(init_list)
        _is_list_instance(sub_list)

        return isinstance(init_list, list)


def dict_merge(dicts_list):
    d = {**dicts_list[0]}
    for entry in dicts_list[1:]:
        # print("entry:", entry)
        for k, v in entry.items():
            d[k] = (
                [d[k], v]
                if k in d and type(d[k]) != list
                else [*d[k] + v]
                if k in d
                else v
            )
    return d



def combine_dict(d1, d2):
    return {
        k: list(d[k] for d in (d1, d2) if k in d)
        for k in set(d1.keys()) | set(d2.keys())
    }



def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None


def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def del_file(fname):
    os.remove(fname)



def del_outputs(name, outpath):

    path = os.path.join(outpath, name)

    if os.path.exists(path):
        shutil.rmtree(path)

    os.mkdir(path)


def process_time(func):
    """
    for debugging purpose, delete @decorator
    """

    def inner(*args):
        start_time = time.time()
        func(*args)
        print(str(func), "--- %s seconds ---" % (time.time() - start_time))

    return inner


def print_time(start_time=None):
    if start_time:
        str = "--- %s seconds ---" % (time.time() - start_time)
        return str

    else:
        return time.time()


