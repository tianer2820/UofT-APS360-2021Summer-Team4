import os
import network
import util


import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from torchvision import transforms
import torch.utils.data

from dataset_utils import get_dataset, InfinateLoader


def eval(model_folder, out_folder, batch_size=5, use_cuda=True, only_first_N=20):

    config = {
    'n_resnet': 5,
    'g_features': 32,
    'd_features': 64,
    'img_size': 256,
    'normalize_img': True,
    }

    # results save path
    def ensure_path(path):
        if not os.path.isdir(path):
            os.makedirs(path)
    
    model_path = model_folder
    a2b_path = os.path.join(out_folder, 'A2B')
    b2a_path = os.path.join(out_folder, 'B2A')

    ensure_path(out_folder)
    ensure_path(model_path)
    ensure_path(a2b_path)
    ensure_path(b2a_path)

    # data_loader

    dataset_A = get_dataset('../eval_data2/train/photo/', config['img_size'], use_normalize=config['normalize_img'])
    dataset_B = get_dataset('../eval_data2/train/pixel/', config['img_size'], use_normalize=config['normalize_img'])


    # network
    E_A = network.Encoder(input_nc=3, output_nc=3, ngf=config['g_features'], nb=config['n_resnet'])
    E_B = network.Encoder(input_nc=3, output_nc=3, ngf=config['g_features'], nb=config['n_resnet'])
    G_A = network.Generator(input_nc=3, output_nc=3, ngf=config['g_features'], nb=config['n_resnet'])
    G_B = network.Generator(input_nc=3, output_nc=3, ngf=config['g_features'], nb=config['n_resnet'])
    D_A = network.discriminator(input_nc=3, output_nc=1, ndf=config['d_features'])
    D_B = network.discriminator(input_nc=3, output_nc=1, ndf=config['d_features'])
    
    E_A_state_dict = torch.load(os.path.join(model_path, 'encoderA_param.pkl'))
    E_B_state_dict = torch.load(os.path.join(model_path, 'encoderB_param.pkl'))
    G_A_state_dict = torch.load(os.path.join(model_path, 'generatorA_param.pkl'))
    G_B_state_dict = torch.load(os.path.join(model_path, 'generatorB_param.pkl'))
    D_A_state_dict = torch.load(os.path.join(model_path, 'discriminatorA_param.pkl'))
    D_B_state_dict = torch.load(os.path.join(model_path, 'discriminatorB_param.pkl'))
    E_A.load_state_dict(E_A_state_dict)
    E_B.load_state_dict(E_B_state_dict)
    G_A.load_state_dict(G_A_state_dict)
    G_B.load_state_dict(G_B_state_dict)
    D_A.load_state_dict(D_A_state_dict)
    D_B.load_state_dict(D_B_state_dict)
    
    E_A.eval()
    E_B.eval()
    G_A.eval()
    G_B.eval()
    D_A.eval()
    D_B.eval()

    if use_cuda and torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')

    E_A.to(device)
    E_B.to(device)
    G_A.to(device)
    G_B.to(device)
    D_A.to(device)
    D_B.to(device)

    print('---------- Networks initialized -------------')

    # test A to B
    print('evaluating A2B...')
    loader_A = torch.utils.data.DataLoader(dataset_A, batch_size=batch_size, shuffle=False)
    for i, imgsA in enumerate(loader_A):
        util.save_model_test(imgsA, E_A, E_B, G_A, G_B, i, device, a2b_path)
        print(i)
        if i * batch_size > only_first_N:
            break

    # test B to A
    print('evaluating B2A...')
    loader_B = torch.utils.data.DataLoader(dataset_B, batch_size=batch_size, shuffle=False)
    for i, imgsB in enumerate(loader_B):
        util.save_model_test(imgsB, E_B, E_A, G_B, G_A, i, device, b2a_path)
        print(i)
        if i * batch_size > only_first_N:
            break


if __name__ == "__main__":
    SAVE_ROOT = 'save_root'

    eval('models', 'eval_out', batch_size=4, use_cuda=False, only_first_N=20)
