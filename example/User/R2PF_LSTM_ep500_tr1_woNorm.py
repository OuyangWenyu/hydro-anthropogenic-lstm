from data import dbCsv
from hydroDL import rnn, crit, train

import os
import torch

cDir = os.path.dirname(os.path.abspath(__file__))
cDir = r'/mnt/sdc/SUR_VIC/'

rootDB = os.path.join(cDir, 'input_VIC')

df = dbCsv.DataframeCsv(
    rootDB=rootDB, subset='CONUS_VICv16f1', tRange=[20150401, 20160401]
    )

varC = [
      'DEPTH_1', 'DEPTH_2', 'DEPTH_3', 'Ds', 'Ds_MAX', 'EXPT_1', 'EXPT_2', 'EXPT_3',
      'INFILT', 'Ws'
]

Parameters = df.getDataConst(dbCsv.varConst, doNorm=False, rmNan=True)

Forcing = df.getDataTs(dbCsv.varForcing, doNorm=False, rmNan=True)
Raw_data = df.getDataConst(dbCsv.varRaw, doNorm=False, rmNan=True)

Target = df.getDataTs(['SOILM_lev1_VIC'], doNorm=False, rmNan=True)

# transfer to tensor
Parameters_tensor = torch.from_numpy(Parameters)
Forcing_tensor = torch.from_numpy(Forcing)
Raw_tensor = torch.from_numpy(Raw_data)

nx = (Forcing.shape[-1] + Raw_data.shape[-1], Raw_data.shape[-1], len(varC))
ny = 1

filename = '/mnt/sdc/SUR_VIC/multiOutput_CONUSv16f1_VIC/CONUS_v16f1_SOILM_lev1_PF_LSTM_woNorm/PF_LSTM_Ep500.pt'
# model_PF_loaded = torch.load(filename)
# model_PF_loaded.eval()
# train.testModel(model_PF_loaded, Forcing_tensor, Parameters_tensor)

path_R2PF = 'multiOutput_CONUSv16f1_VIC/CONUS_v16f1_SOILM_lev1_R2PF_LSTM_woNorm'
outFolder = os.path.join(cDir, path_R2PF)
if os.path.exists(outFolder) is False:
   os.mkdir(outFolder)

epoch=500
model_R2PF = rnn.CudnnLstmModel_R2P(nx=nx, ny=ny, hiddenSize=256, filename=filename)
lossFun_R2PF = crit.RmseLoss()
model_R2PF = train.model_train(
    model_R2PF, Forcing, Target, Raw_data, lossFun_R2PF, nEpoch=epoch, miniBatch=[100, 60], saveFolder=outFolder)
modelName = 'R2PF_LSTM'
train.model_save(outFolder, model_R2PF, epoch, modelName=modelName)