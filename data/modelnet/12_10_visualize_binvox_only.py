import argparse
import sys
import os
sys.path.insert(1, os.path.realpath(__file__ + '../lib/'))
from blender_utils import *
import common
import json
import h5py
import numpy as np

def read_json(file):
    """
    Read a JSON file.

    :param file: path to file to read
    :type file: str
    :return: parsed JSON as dict
    :rtype: dict
    """

    assert os.path.exists(file), 'file %s not found' % file

    with open(file, 'r') as fp:
        return json.load(fp)

def read_hdf5(file, key = 'tensor'):
    """
    Read a tensor, i.e. numpy array, from HDF5.

    :param file: path to file to read
    :type file: str
    :param key: key to read
    :type key: str
    :return: tensor
    :rtype: numpy.ndarray
    """

    assert os.path.exists(file), 'file %s not found' % file

    h5f = h5py.File(file, 'r')
    tensor = h5f[key][()]
    h5f.close()

    return tensor

if __name__ == '__main__':

    try:
        argv = sys.argv[sys.argv.index("--") + 1:]
    except ValueError:
        log('[Error] "--" not found, call as follows:', LogLevel.ERROR)
        log('[Error] $BLENDER --background --python 12_3_visualize_binvox.py -- 1>/dev/null config_folder', LogLevel.ERROR)
        exit()

    if len(argv) < 1:
        log('[Error] not enough parameters, call as follows:', LogLevel.ERROR)
        log('[Error] $BLENDER --background --python 12_3_visualize_binvox.py -- 1>/dev/null config_folder', LogLevel.ERROR)
        exit()

    config_folder = argv[0] + '/'
    assert os.path.exists(config_folder), 'directory %s does not exist' % config_folder

    config_files = ['test.json']
    for config_file in config_files:
        config = read_json(config_folder + config_file)

        height = config['height']
        width = config['width']
        depth = config['depth']
        scale = 1./max(height, width, depth)

        n_observations = config['n_observations']

        filled = read_hdf5(common.filename(config, 'filled_file'))
        filled = np.repeat(filled, n_observations, axis=0)

        vis_directory = common.dirname(config, 'vis_dir')
        if not os.path.isdir(vis_directory):
            os.makedirs(vis_directory)

        voxel_size = 0.0125
        if height >= 48:
            voxel_size = 0.009
        if height >= 64:
            voxel_size = 0.0065
        log('[Data] voxel size ' + str(voxel_size))

        N = 30
        log('[Data] %d samples' % filled.shape[0])
        for i in range(N):
            n = i * (filled.shape[0] // N)
            camera_target = initialize()
            output_material = make_material('BRC_Material_Mesh', (0.66, 0.45, 0.23), 0.8, True)

            load_volume(filled[n][0], voxel_size, output_material, (0, 0, 0), (width*scale, depth*scale, height*scale), 'zxy')

            rotation = (5, 0, 125)
            distance = 0.5
            png_file = vis_directory + '/%d_bin_only.png' % n
            render(camera_target, png_file, rotation, distance)

            log('[Data] wrote %s' % png_file)