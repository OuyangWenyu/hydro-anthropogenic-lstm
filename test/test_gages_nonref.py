import os
import unittest

from data import *
from explore.stat import statError
from hydroDL.master import *
from utils import hydro_util
from utils.dataset_format import subset_of_dict
from visual import *
import numpy as np
import definitions
from visual.plot_model import plot_boxes_inds


class MyTestCaseGagesNonref(unittest.TestCase):
    def setUp(self) -> None:
        """before all of these, natural flow model need to be generated by config.ini of gages dataset, and it need
        to be moved to right dir manually """
        config_dir = definitions.CONFIG_DIR
        # self.config_file = os.path.join(config_dir, "nonref/config_nonref_exp1.ini")
        # self.subdir = r"nonref/exp1"
        self.config_file = os.path.join(config_dir, "nonref/config_nonref_exp2.ini")
        self.subdir = r"nonref/exp2"
        self.config_data = GagesConfig.set_subdir(self.config_file, self.subdir)

    def test_gages_nonref_train(self):
        print('Starting ...')
        os.environ["CUDA_VISIBLE_DEVICES"] = "2"
        config_data = self.config_data
        # 准备训练数据
        source_data = GagesSource(config_data, config_data.model_dict["data"]["tRangeTrain"])
        # 构建输入数据类对象
        data_model = DataModel(source_data)
        # 进行模型训练
        # train model
        master_train(data_model)

    def test_gages_nonref_test(self):
        config_data = self.config_data
        # 准备训练数据
        source_data = GagesSource(config_data, config_data.model_dict["data"]["tRangeTest"])
        data_model_test = DataModel(source_data)
        pred, obs = master_test(data_model_test)
        pred = pred.reshape(pred.shape[0], pred.shape[1])
        obs = obs.reshape(pred.shape[0], pred.shape[1])

        inds = statError(obs, pred)
        show_me_num = 5
        t_s_dict = data_model_test.t_s_dict
        sites = np.array(t_s_dict["sites_id"])
        t_range = np.array(t_s_dict["t_final_range"])
        ts_fig = plot_ts_obs_pred(obs, pred, sites, t_range, show_me_num)
        ts_fig.savefig(os.path.join(config_data.data_path["Out"], "ts_fig.png"))
        # plot box，使用seaborn库
        keys = ["Bias", "RMSE", "NSE"]
        inds_test = subset_of_dict(inds, keys)
        box_fig = plot_boxes_inds(inds_test)
        box_fig.savefig(os.path.join(config_data.data_path["Out"], "box_fig.png"))


if __name__ == '__main__':
    unittest.main()