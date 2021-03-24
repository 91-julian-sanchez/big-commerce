import yaml
import os
import ntpath
import logging

# logging.basicConfig(
#     filename=f'../../../.log/{ntpath.basename(os.path.basename(__file__)).replace(".py", "")}.log',
#     format='%(levelname)s: %(message)s',
#     level=logging.INFO
# )

__config = None

def config(config_path='../../..'):
    global __config
    if not __config:
        with open(f'{config_path}/config.yaml', mode='r') as f:
            __config = yaml.load(f, Loader=yaml.FullLoader)

    return __config