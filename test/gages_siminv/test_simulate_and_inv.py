import copy
import unittest

import torch

import definitions
from data import GagesConfig
from data.data_config import add_model_param
from data.data_input import save_datamodel, GagesModel, _basin_norm
from data.gages_input_dataset import GagesSimInvDataModel
from explore.stat import statError
from hydroDL.master.master import train_lstm_siminv, test_lstm_siminv
import numpy as np
import os
import pandas as pd
from utils import serialize_numpy, unserialize_numpy
from utils.dataset_format import subset_of_dict
from visual import plot_ts_obs_pred
from visual.plot_model import plot_boxes_inds, plot_map
from visual.plot_stat import plot_ecdf


class MyTestCaseSimulateAndInv(unittest.TestCase):
    def setUp(self) -> None:
        """before all of these, natural flow model need to be generated by config.ini of gages dataset, and it need
        to be moved to right dir manually """
        config_dir = definitions.CONFIG_DIR
        # self.config_file_1 = os.path.join(config_dir, "siminv/config_siminv_1_exp2.ini")
        # self.config_file_2 = os.path.join(config_dir, "siminv/config_siminv_2_exp2.ini")
        # self.config_file_3 = os.path.join(config_dir, "siminv/config_siminv_3_exp2.ini")
        # self.subdir = r"siminv/exp2"
        # self.config_file_1 = os.path.join(config_dir, "siminv/config_siminv_1_exp3.ini")
        # self.config_file_2 = os.path.join(config_dir, "siminv/config_siminv_2_exp3.ini")
        # self.config_file_3 = os.path.join(config_dir, "siminv/config_siminv_3_exp3.ini")
        # self.subdir = r"siminv/exp3"
        # self.config_file_1 = os.path.join(config_dir, "siminv/config_siminv_1_exp4.ini")
        # self.config_file_2 = os.path.join(config_dir, "siminv/config_siminv_2_exp4.ini")
        # self.config_file_3 = os.path.join(config_dir, "siminv/config_siminv_3_exp4.ini")
        # self.subdir = r"siminv/exp4"

        # self.config_file_1 = os.path.join(config_dir, "siminv/config1_exp10.ini")
        # self.config_file_2 = os.path.join(config_dir, "siminv/config2_exp10.ini")
        # self.config_file_3 = os.path.join(config_dir, "siminv/config3_exp10.ini")
        # self.subdir = r"siminv/exp10"
        self.config_file_1 = os.path.join(config_dir, "siminv/config1_exp1.ini")
        self.config_file_2 = os.path.join(config_dir, "siminv/config2_exp1.ini")
        self.config_file_3 = os.path.join(config_dir, "siminv/config3_exp1.ini")
        self.subdir = r"siminv/exp1"
        self.config_data_sim = GagesConfig.set_subdir(self.config_file_1, self.subdir)
        self.config_data_inv = GagesConfig.set_subdir(self.config_file_2, self.subdir)
        self.config_data = GagesConfig.set_subdir(self.config_file_3, self.subdir)
        add_model_param(self.config_data_inv, "model", seqLength=7)
        test_epoch_lst = [100, 200, 220, 250, 280, 290, 295, 300, 305, 310, 320]
        # self.test_epoch = test_epoch_lst[0]
        # self.test_epoch = test_epoch_lst[1]
        # self.test_epoch = test_epoch_lst[2]
        # self.test_epoch = test_epoch_lst[3]
        # self.test_epoch = test_epoch_lst[4]
        # self.test_epoch = test_epoch_lst[5]
        # self.test_epoch = test_epoch_lst[6]
        self.test_epoch = test_epoch_lst[7]
        # self.test_epoch = test_epoch_lst[8]
        # self.test_epoch = test_epoch_lst[9]
        # self.test_epoch = test_epoch_lst[10]

    def test_siminv_data_temp(self):
        quick_data_dir = os.path.join(self.config_data_sim.data_path["DB"], "quickdata")
        data_dir_allref = os.path.join(quick_data_dir, "allref_85-05_nan-0.1_00-1.0")
        data_dir_allnonref = os.path.join(quick_data_dir, "allnonref_85-05_nan-0.1_00-1.0")
        data_model_allref_8595 = GagesModel.load_datamodel(data_dir_allref,
                                                           data_source_file_name='data_source.txt',
                                                           stat_file_name='Statistics.json', flow_file_name='flow.npy',
                                                           forcing_file_name='forcing.npy', attr_file_name='attr.npy',
                                                           f_dict_file_name='dictFactorize.json',
                                                           var_dict_file_name='dictAttribute.json',
                                                           t_s_dict_file_name='dictTimeSpace.json')
        data_model_allref_9505 = GagesModel.load_datamodel(data_dir_allref,
                                                           data_source_file_name='test_data_source.txt',
                                                           stat_file_name='test_Statistics.json',
                                                           flow_file_name='test_flow.npy',
                                                           forcing_file_name='test_forcing.npy',
                                                           attr_file_name='test_attr.npy',
                                                           f_dict_file_name='test_dictFactorize.json',
                                                           var_dict_file_name='test_dictAttribute.json',
                                                           t_s_dict_file_name='test_dictTimeSpace.json')
        data_model_allnonref_8595 = GagesModel.load_datamodel(data_dir_allnonref,
                                                              data_source_file_name='data_source.txt',
                                                              stat_file_name='Statistics.json',
                                                              flow_file_name='flow.npy',
                                                              forcing_file_name='forcing.npy',
                                                              attr_file_name='attr.npy',
                                                              f_dict_file_name='dictFactorize.json',
                                                              var_dict_file_name='dictAttribute.json',
                                                              t_s_dict_file_name='dictTimeSpace.json')
        data_model_allnonref_9505 = GagesModel.load_datamodel(data_dir_allnonref,
                                                              data_source_file_name='test_data_source.txt',
                                                              stat_file_name='test_Statistics.json',
                                                              flow_file_name='test_flow.npy',
                                                              forcing_file_name='test_forcing.npy',
                                                              attr_file_name='test_attr.npy',
                                                              f_dict_file_name='test_dictFactorize.json',
                                                              var_dict_file_name='test_dictAttribute.json',
                                                              t_s_dict_file_name='test_dictTimeSpace.json')
        t_range_sim_train = self.config_data_sim.model_dict["data"]["tRangeTrain"]
        t_range_sim_test = self.config_data_sim.model_dict["data"]["tRangeTest"]
        sim_gages_model_train = GagesModel.update_data_model(self.config_data_sim, data_model_allref_8595,
                                                             t_range_sim_train, data_attr_update=True)
        sim_gages_model_test = GagesModel.update_data_model(self.config_data_sim, data_model_allref_8595,
                                                            t_range_sim_test, data_attr_update=True)
        t_range_inv_train = self.config_data_inv.model_dict["data"]["tRangeTrain"]
        t_range_inv_test = self.config_data_inv.model_dict["data"]["tRangeTest"]
        inv_gages_model_train = GagesModel.update_data_model(self.config_data_inv, data_model_allnonref_8595,
                                                             t_range_inv_train, data_attr_update=True)
        inv_gages_model_test = GagesModel.update_data_model(self.config_data_inv, data_model_allnonref_8595,
                                                            t_range_inv_test, data_attr_update=True)
        t_range_train = self.config_data.model_dict["data"]["tRangeTrain"]
        t_range_test = self.config_data.model_dict["data"]["tRangeTest"]
        gages_model_train = GagesModel.update_data_model(self.config_data, data_model_allnonref_8595, t_range_train,
                                                         data_attr_update=True)
        gages_model_test = GagesModel.update_data_model(self.config_data, data_model_allnonref_9505, t_range_test,
                                                        data_attr_update=True,
                                                        train_stat_dict=gages_model_train.stat_dict)

        save_datamodel(sim_gages_model_train, "1", data_source_file_name='data_source.txt',
                       stat_file_name='Statistics.json', flow_file_name='flow', forcing_file_name='forcing',
                       attr_file_name='attr', f_dict_file_name='dictFactorize.json',
                       var_dict_file_name='dictAttribute.json', t_s_dict_file_name='dictTimeSpace.json')
        save_datamodel(sim_gages_model_test, "1", data_source_file_name='test_data_source.txt',
                       stat_file_name='test_Statistics.json', flow_file_name='test_flow',
                       forcing_file_name='test_forcing', attr_file_name='test_attr',
                       f_dict_file_name='test_dictFactorize.json', var_dict_file_name='test_dictAttribute.json',
                       t_s_dict_file_name='test_dictTimeSpace.json')
        save_datamodel(inv_gages_model_train, "2", data_source_file_name='data_source.txt',
                       stat_file_name='Statistics.json', flow_file_name='flow', forcing_file_name='forcing',
                       attr_file_name='attr', f_dict_file_name='dictFactorize.json',
                       var_dict_file_name='dictAttribute.json', t_s_dict_file_name='dictTimeSpace.json')
        save_datamodel(inv_gages_model_test, "2", data_source_file_name='test_data_source.txt',
                       stat_file_name='test_Statistics.json', flow_file_name='test_flow',
                       forcing_file_name='test_forcing', attr_file_name='test_attr',
                       f_dict_file_name='test_dictFactorize.json', var_dict_file_name='test_dictAttribute.json',
                       t_s_dict_file_name='test_dictTimeSpace.json')
        save_datamodel(gages_model_train, "3", data_source_file_name='data_source.txt',
                       stat_file_name='Statistics.json', flow_file_name='flow', forcing_file_name='forcing',
                       attr_file_name='attr', f_dict_file_name='dictFactorize.json',
                       var_dict_file_name='dictAttribute.json', t_s_dict_file_name='dictTimeSpace.json')
        save_datamodel(gages_model_test, "3", data_source_file_name='test_data_source.txt',
                       stat_file_name='test_Statistics.json', flow_file_name='test_flow',
                       forcing_file_name='test_forcing', attr_file_name='test_attr',
                       f_dict_file_name='test_dictFactorize.json', var_dict_file_name='test_dictAttribute.json',
                       t_s_dict_file_name='test_dictTimeSpace.json')
        print("read and save data model")

    def test_siminv_train(self):
        with torch.cuda.device(0):
            df1 = GagesModel.load_datamodel(self.config_data_sim.data_path["Temp"], "1",
                                            data_source_file_name='data_source.txt',
                                            stat_file_name='Statistics.json', flow_file_name='flow.npy',
                                            forcing_file_name='forcing.npy', attr_file_name='attr.npy',
                                            f_dict_file_name='dictFactorize.json',
                                            var_dict_file_name='dictAttribute.json',
                                            t_s_dict_file_name='dictTimeSpace.json')
            df1.update_model_param('train', nEpoch=300)
            df2 = GagesModel.load_datamodel(self.config_data_inv.data_path["Temp"], "2",
                                            data_source_file_name='data_source.txt',
                                            stat_file_name='Statistics.json', flow_file_name='flow.npy',
                                            forcing_file_name='forcing.npy', attr_file_name='attr.npy',
                                            f_dict_file_name='dictFactorize.json',
                                            var_dict_file_name='dictAttribute.json',
                                            t_s_dict_file_name='dictTimeSpace.json')
            df3 = GagesModel.load_datamodel(self.config_data.data_path["Temp"], "3",
                                            data_source_file_name='data_source.txt',
                                            stat_file_name='Statistics.json', flow_file_name='flow.npy',
                                            forcing_file_name='forcing.npy', attr_file_name='attr.npy',
                                            f_dict_file_name='dictFactorize.json',
                                            var_dict_file_name='dictAttribute.json',
                                            t_s_dict_file_name='dictTimeSpace.json')
            data_model = GagesSimInvDataModel(df1, df2, df3)
            pre_trained_model_epoch = 90
            train_lstm_siminv(data_model, pre_trained_model_epoch=pre_trained_model_epoch)
            # train_lstm_siminv(data_model)

    def test_siminv_test(self):
        with torch.cuda.device(0):
            df1 = GagesModel.load_datamodel(self.config_data_sim.data_path["Temp"], "1",
                                            data_source_file_name='test_data_source.txt',
                                            stat_file_name='test_Statistics.json', flow_file_name='test_flow.npy',
                                            forcing_file_name='test_forcing.npy', attr_file_name='test_attr.npy',
                                            f_dict_file_name='test_dictFactorize.json',
                                            var_dict_file_name='test_dictAttribute.json',
                                            t_s_dict_file_name='test_dictTimeSpace.json')
            df1.update_model_param('train', nEpoch=300)
            df2 = GagesModel.load_datamodel(self.config_data_inv.data_path["Temp"], "2",
                                            data_source_file_name='test_data_source.txt',
                                            stat_file_name='test_Statistics.json', flow_file_name='test_flow.npy',
                                            forcing_file_name='test_forcing.npy', attr_file_name='test_attr.npy',
                                            f_dict_file_name='test_dictFactorize.json',
                                            var_dict_file_name='test_dictAttribute.json',
                                            t_s_dict_file_name='test_dictTimeSpace.json')
            df3 = GagesModel.load_datamodel(self.config_data.data_path["Temp"], "3",
                                            data_source_file_name='test_data_source.txt',
                                            stat_file_name='test_Statistics.json', flow_file_name='test_flow.npy',
                                            forcing_file_name='test_forcing.npy', attr_file_name='test_attr.npy',
                                            f_dict_file_name='test_dictFactorize.json',
                                            var_dict_file_name='test_dictAttribute.json',
                                            t_s_dict_file_name='test_dictTimeSpace.json')
            data_model = GagesSimInvDataModel(df1, df2, df3)
            test_epoch = self.test_epoch
            pred, obs = test_lstm_siminv(data_model, epoch=test_epoch)
            basin_area = df3.data_source.read_attr(df3.t_s_dict["sites_id"], ['DRAIN_SQKM'], is_return_dict=False)
            mean_prep = df3.data_source.read_attr(df3.t_s_dict["sites_id"], ['PPTAVG_BASIN'], is_return_dict=False)
            mean_prep = mean_prep / 365 * 10
            pred = _basin_norm(pred, basin_area, mean_prep, to_norm=False)
            obs = _basin_norm(obs, basin_area, mean_prep, to_norm=False)
            flow_pred_file = os.path.join(df3.data_source.data_config.data_path['Temp'],
                                          'epoch' + str(test_epoch) + 'flow_pred')
            flow_obs_file = os.path.join(df3.data_source.data_config.data_path['Temp'],
                                         'epoch' + str(test_epoch) + 'flow_obs')
            serialize_numpy(pred, flow_pred_file)
            serialize_numpy(obs, flow_obs_file)

    def test_siminv_plot(self):
        data_model = GagesModel.load_datamodel(self.config_data.data_path["Temp"], "3",
                                               data_source_file_name='test_data_source.txt',
                                               stat_file_name='test_Statistics.json', flow_file_name='test_flow.npy',
                                               forcing_file_name='test_forcing.npy', attr_file_name='test_attr.npy',
                                               f_dict_file_name='test_dictFactorize.json',
                                               var_dict_file_name='test_dictAttribute.json',
                                               t_s_dict_file_name='test_dictTimeSpace.json')
        test_epoch = self.test_epoch
        flow_pred_file = os.path.join(data_model.data_source.data_config.data_path['Temp'],
                                      'epoch' + str(test_epoch) + 'flow_pred.npy')
        flow_obs_file = os.path.join(data_model.data_source.data_config.data_path['Temp'],
                                     'epoch' + str(test_epoch) + 'flow_obs.npy')
        pred = unserialize_numpy(flow_pred_file)
        obs = unserialize_numpy(flow_obs_file)
        pred = pred.reshape(pred.shape[0], pred.shape[1])
        obs = obs.reshape(obs.shape[0], obs.shape[1])

        inds = statError(obs, pred)
        inds['STAID'] = data_model.t_s_dict["sites_id"]
        inds_df = pd.DataFrame(inds)
        inds_df.to_csv(os.path.join(self.config_data.data_path["Out"], 'data_df.csv'))
        # plot box，使用seaborn库
        keys = ["Bias", "RMSE", "NSE"]
        inds_test = subset_of_dict(inds, keys)
        box_fig = plot_boxes_inds(inds_test)
        box_fig.savefig(os.path.join(self.config_data.data_path["Out"], "box_fig.png"))
        # plot ts
        show_me_num = 5
        t_s_dict = data_model.t_s_dict
        sites = np.array(t_s_dict["sites_id"])
        t_range = np.array(t_s_dict["t_final_range"])
        time_seq_length = self.config_data_inv.model_dict["model"]["seqLength"]
        time_start = np.datetime64(t_range[0]) + np.timedelta64(time_seq_length - 1, 'D')
        t_range[0] = np.datetime_as_string(time_start, unit='D')
        ts_fig = plot_ts_obs_pred(obs, pred, sites, t_range, show_me_num)
        ts_fig.savefig(os.path.join(self.config_data.data_path["Out"], "ts_fig.png"))

        # plot nse ecdf
        sites_df_nse = pd.DataFrame({"sites": sites, keys[2]: inds_test[keys[2]]})
        plot_ecdf(sites_df_nse, keys[2])
        # plot map
        gauge_dict = data_model.data_source.gage_dict
        plot_map(gauge_dict, sites_df_nse, id_col="STAID", lon_col="LNG_GAGE", lat_col="LAT_GAGE")


if __name__ == '__main__':
    unittest.main()
