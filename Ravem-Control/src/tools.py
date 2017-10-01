from sys import platform
import config
import json


def port_return():
    if platform.startswith('linux'):
        return config.PORT_NAME_LINUX
    elif platform.startswith('win') or platform.startswith('cygwin'):
        return config.PORT_NAME_WINDOWS
    elif platform.startswith('darwin'):
        return config.PORT_NAME_OSX


def find_methods(obj):
        return [method for method in dir(obj) if callable(getattr(obj, method)) and not method.startswith('_')]


def make_config(save=True):
    config_list = []
    for var in dir(config):
        if not var.startswith('_'):
            value = eval("config.{}".format(var))
            type_local = type(value).__name__
            if type_local == "int" or type_local == "float":
                type_local = "number"
            if type_local == "str":
                type_local = "string"
            obj = {'name': var, 'value': value, 'type': type_local}
            config_list.append(obj)
    if save:
        with open('./storage/config.json', 'wb') as outfile:
            json.dump(config_list, outfile, sort_keys=True, indent=4, separators=(',', ': '))
    return config_list


def change_config_legacy(data, worker):
    for key, var in enumerate(data):
        var["value"] = str(var["value"])
        counter = var["value"].count('.')
        if counter == 0 and var["value"].isdigit():
            data[key]["value"] = int(var["value"])
        elif counter == 1:
            if var["value"].lstrip('-').replace('.','',1).isdigit():
                data[key]["value"] = float(var["value"])
        elif var["value"].lower() == "true":
            data[key]["value"] = True
        elif var["value"].lower() == "false":
            data[key]["value"] = False
    with open('./storage/config.json', 'wb') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))
    load_config(worker)


def change_config(data, worker):
    with open('./storage/config.json', 'wb') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))
    load_config(worker)


def load_config(worker=None):
    with open('./storage/config.json') as data_file:
        data = json.load(data_file)
        for var in data:
            if not isinstance(var["value"], basestring):
                exec 'config.{} = {}'.format(var["name"], var["value"])
            else:
                exec 'config.{} = "{}"'.format(var["name"], var["value"])
            if worker != None and worker.success:
                if var["name"].startswith('SET_'):
                    exec 'worker.{}({})'.format(var["name"].lower(), var["value"])


def config_settable_init(worker):
    if worker.success:
        with open('./storage/config.json') as data_file:
            data = json.load(data_file)
            for var in data:
                if var["name"].startswith('SET_'):
                    exec 'worker.{}({})'.format(var["name"].lower(), var["value"])


def calculate_battery(voltage):
    max_dif = 4.2 * config.BATTERY_CELL_COUNT - 3 * config.BATTERY_CELL_COUNT
    dif = voltage - (3 * config.BATTERY_CELL_COUNT)
    level = int(dif/max_dif * 100)
    return level