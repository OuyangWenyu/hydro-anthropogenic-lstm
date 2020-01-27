""" data source for simulated flow generated by model trained by dataset of ref basins"""
import numpy as np
import torch

from data import GagesConfig, GagesSource, DataModel
from explore import trans_norm
from hydroDL.model import model_run
from utils import serialize_numpy, serialize_pickle, serialize_json, unserialize_pickle, unserialize_json, \
    unserialize_numpy


class SimNatureFlowSource(object):
    def __init__(self, config_data, t_range, sim_config_file, *args):
        self.data_config = config_data
        self.t_range = t_range
        if len(args) == 0:
            self.all_configs = config_data.read_data_config()
            sim_config_data = GagesConfig(sim_config_file)
            source_data = GagesSource(sim_config_data, t_range)
            self.sim_model_data = DataModel(source_data)
        else:
            self.all_configs = args[0]
            self.sim_model_data = args[1]

    def prepare_flow_data(self):
        """generate flow from model, reshape to a 3d array, and transform to tensor:
        1d: nx * ny_per_nx
        2d: miniBatch[1]
        3d: length of time sequence, now also miniBatch[1]
        """
        # read data for model of allref
        sim_model_data = self.sim_model_data
        sim_config_data = sim_model_data.data_source.data_config
        batch_size = sim_config_data.model_dict["train"]["miniBatch"][0]
        x, y, c = sim_model_data.load_data(sim_config_data.model_dict)
        # read model, TODO: model file need to be copied to out folder mannually
        out_folder = self.data_config.data_path["Out"]
        epoch = sim_config_data.model_dict["train"]["nEpoch"]
        model = model_run.model_load(out_folder, epoch, model_name='model')
        # run the model
        all_configs = self.all_configs
        file_path = all_configs["natural_flow_file"]
        natural_flow = model_run.model_test(model, x, c, file_path=file_path, batch_size=batch_size)
        np_natural_flow = natural_flow.numpy()
        nx = np_natural_flow.shape[0]
        all_time_length = np_natural_flow.shape[1]
        np_natural_flow_2d = np_natural_flow.reshape(nx, all_time_length)
        rho = self.data_config.model_dict["train"]["miniBatch"][1]
        x_np = np.zeros([nx, all_time_length - rho + 1, rho])
        for i in range(nx):
            for j in range(all_time_length - rho + 1):
                x_np[i, j, :] = np_natural_flow_2d[i][j:j + rho]
        ny_per_nx = x_np.shape[1] - rho + 1
        x_tensor = torch.zeros([nx * ny_per_nx, rho, rho], requires_grad=False)
        for i in range(nx):
            per_x_np = np.zeros([ny_per_nx, rho, rho])
            for j in range(ny_per_nx):
                per_x_np[j, :, :] = x_np[i, j:j + rho, :]
            x_tensor[(i * ny_per_nx):((i + 1) * ny_per_nx), :, :] = torch.from_numpy(per_x_np)
        print("streamflow data Ready! ...")
        return x_tensor

    def write_temp_source(self):
        """wirte source object to some temp files"""
        serialize_pickle(self.sim_model_data.data_source, self.all_configs["sim_source_data_file"])
        serialize_json(self.sim_model_data.stat_dict, self.all_configs["sim_stat_dict_file"])
        serialize_numpy(self.sim_model_data.data_flow, self.all_configs["sim_data_flow_file"])
        serialize_numpy(self.sim_model_data.data_forcing, self.all_configs["sim_data_forcing_file"])
        serialize_numpy(self.sim_model_data.data_attr, self.all_configs["sim_data_attr_file"])
        # dictFactorize.json is the explanation of value of categorical variables
        serialize_json(self.sim_model_data.f_dict, self.all_configs["sim_f_dict_file"])
        serialize_json(self.sim_model_data.var_dict, self.all_configs["sim_var_dict_file"])
        serialize_json(self.sim_model_data.t_s_dict, self.all_configs["sim_t_s_dict_file"])

    @classmethod
    def get_sim_nature_flow_source(cls, config_data, t_range, sim_config_file):
        all_configs = config_data.read_data_config()
        source_data = unserialize_pickle(all_configs["sim_source_data_file"])
        # 存储data_model，因为data_model里的数据如果直接序列化会比较慢，所以各部分分别序列化，dict的直接序列化为json文件，数据的HDF5
        stat_dict = unserialize_json(all_configs["sim_stat_dict_file"])
        data_flow = unserialize_numpy(all_configs["sim_data_flow_file"] + ".npy")
        data_forcing = unserialize_numpy(all_configs["sim_data_forcing_file"] + ".npy")
        data_attr = unserialize_numpy(all_configs["sim_data_attr_file"] + ".npy")
        # dictFactorize.json is the explanation of value of categorical variables
        var_dict = unserialize_json(all_configs["sim_var_dict_file"])
        f_dict = unserialize_json(all_configs["sim_f_dict_file"])
        t_s_dict = unserialize_json(all_configs["sim_t_s_dict_file"])
        sim_model_data = DataModel(source_data, data_flow, data_forcing, data_attr, var_dict, f_dict, stat_dict,
                                   t_s_dict)
        sim_nature_flow_source = cls(config_data, t_range, sim_config_file, all_configs, sim_model_data)
        return sim_nature_flow_source

    def read_outflow(self):
        """read streamflow data as observation data, transform array to tensor"""
        print("reading outflow:")
        sim_model_data = self.sim_model_data
        data_flow = sim_model_data.data_flow
        data = np.expand_dims(data_flow, axis=2)
        stat_dict = sim_model_data.stat_dict
        data = trans_norm(data, 'usgsFlow', stat_dict, to_norm=True)
        # cut the first rho data to match generated flow time series
        rho = self.data_config.model_dict["train"]["miniBatch"][1]
        data_chosen = data[:, rho - 1:, :]
        nx = data_chosen.shape[0]
        ny_per_nx = data_chosen.shape[1] - rho + 1
        x_tensor = torch.zeros([nx * ny_per_nx, rho, 1], requires_grad=False)
        for i in range(nx):
            per_x_np = np.zeros([ny_per_nx, rho, 1])
            for j in range(ny_per_nx):
                per_x_np[j, :, :] = data_chosen[i, j:j + rho, :]
            x_tensor[(i * ny_per_nx):((i + 1) * ny_per_nx), :, :] = torch.from_numpy(per_x_np)
        return x_tensor
