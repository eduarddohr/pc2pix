'''Render point clouds from test dataset using pc2pix

'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from keras import backend as K
import tensorflow as tf

import numpy as np
import argparse

import sys
sys.path.append("..")
from ptcloud_stacked_ae import PtCloudStackedAE
from general_utils import plot_3d_point_cloud, plot_image, plot_images
from shapenet import get_split
from in_out import load_ply
from loader import read_view_angle
from general_utils import plot_3d_point_cloud, plot_image, plot_images

import os
import datetime
from PIL import Image
import scipy.misc
#sys.path.append("evaluation")
from utils import get_ply


def norm_angle(angle):
    angle *= 0.5
    angle += 0.5
    return angle

def norm_pc(pc):
    pc = pc / 0.5
    return pc

def render_by_pc2pix(ptcloud_ae, pc2pix, pc, elev_code, azim_code, filename):
    pc_code = ptcloud_ae.encoder.predict(pc)
    noise = np.random.uniform(-1.0, 1.0, size=[1, 128])
    fake_image = pc2pix.generator.predict([noise, pc_code, elev_code, azim_code])
    fake_image *= 0.5
    fake_image += 0.5
    fake_image = fake_image[0]
    scipy.misc.toimage(fake_image, cmin=0.0, cmax=1.0).save(filename)

    # print(fake_image.shape)
    # fake_image = Image.fromarray(fake_image)
    # fake_image.save(filename)
    # plot_image(fake_image, color=True, filename=filename)

PLY_PATH = "../data/shape_net_core_uniform_samples_2048"
PC_CODES_PATH = "pc_codes"
PLOTS_PATH = "plots3d"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    help_ = "Load h5 ptcloud_ae model trained ae weights"
    parser.add_argument("-w", "--ptcloud_ae_weights", help=help_)
    help_ = "Shapnet category or class (chair, airplane, etc)"
    parser.add_argument("-a", "--category", default='chair', help=help_)
    help_ = "Split file"
    parser.add_argument("-s", "--split_file", default='data/chair_exp.json', help=help_)
    help_ = "PLY files folder"
    parser.add_argument("--ply", default=PLY_PATH, help=help_)
    help_ = "pc codes folder"
    parser.add_argument("--pc_codes", default=PC_CODES_PATH, help=help_)
    help_ = "Point cloud code dim"
    parser.add_argument("-p", "--pc_code_dim", default=32, type=int, help=help_)
    help_ = "Kernel size"
    parser.add_argument("-k", "--kernel_size", default=1, type=int, help=help_)
    args = parser.parse_args()

    batch_size = 32
    pc_code_dim = args.pc_code_dim
    category = args.category

    ptcloud_ae = PtCloudStackedAE(latent_dim=pc_code_dim,
                                  kernel_size=args.kernel_size,
                                  category=category,
                                  evaluate=True)
    ptcloud_ae.stop_sources()

    if args.ptcloud_ae_weights:
        print("Loading point cloud ae weights: ", args.ptcloud_ae_weights)
        ptcloud_ae.use_emd = False
        ptcloud_ae.ae.load_weights(args.ptcloud_ae_weights)
    else:
        print("Trained point cloud ae required to pc2pix")
        exit(0)

    js = get_ply(args.split_file)

    datasets = ('test')
    start_time = datetime.datetime.now()
    os.makedirs(PLOTS_PATH, exist_ok=True)
    n = 0
    for key in js.keys():
        # key eg 03001627
        data = js[key]
        tags = data['test']
        ply_path_main = os.path.join(args.ply, key)
        tagslen = len(tags)
        n_interpolate = 10
        for i in range(tagslen - 1):
            tag = tags[i]
            ply_file = os.path.join(ply_path_main, tag + ".ply")
            pc = load_ply(ply_file)
            target_path = os.path.join(PLOTS_PATH, tag + "_" + str(n) + ".png")
            n += 1
            fig = plot_3d_point_cloud(pc[:, 0],
                                      pc[:, 1],
                                      pc[:, 2],
                                      show=False,
                                      colorize='rainbow',
                                      filename=target_path)
            pc = norm_pc(pc)
            shape = pc.shape
            pc = np.reshape(pc, [-1, shape[0], shape[1]])
            pc_code1 = ptcloud_ae.encoder.predict(pc)

            tag = tags[i+1]
            ply_file = os.path.join(ply_path_main, tag + ".ply")
            pc = load_ply(ply_file)
            target_path = os.path.join(PLOTS_PATH, tag + "_" + str(n_interpolate + 1) + ".png")
            fig = plot_3d_point_cloud(pc[:, 0],
                                      pc[:, 1],
                                      pc[:, 2],
                                      show=False,
                                      colorize='rainbow',
                                      filename=target_path)

            pc = norm_pc(pc)
            shape = pc.shape
            pc = np.reshape(pc, [-1, shape[0], shape[1]])
            pc_code2 = ptcloud_ae.encoder.predict(pc)

            pc_codes = []
            shape = pc_code1.shape
            for i in range(n_interpolate):
                #pc_code = []
                delta = (pc_code2 - pc_code1)/(n_interpolate + 1)
                delta *= (i + 1)
                pc_code = pc_code1 + delta

                pc = ptcloud_ae.decoder.predict(pc_code)
                pc *= 0.5
                target_path = os.path.join(PLOTS_PATH, tag + "_" + str(n) + ".png")
                n += 1
                fig = plot_3d_point_cloud(pc[0][:, 0],
                                          pc[0][:, 1],
                                          pc[0][:, 2],
                                          show=False,
                                          colorize='rainbow',
                                          filename=target_path)
                print("pc_code shape:", pc_code.shape)
                print(pc_code)

            exit(0)
