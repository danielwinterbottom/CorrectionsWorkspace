#!/usr/bin/env python
import ROOT
import imp
import json
from array import array
import numpy as np

wsptools = imp.load_source('wsptools', 'workspaceTools.py')

def GetFromTFile(str):
    f = ROOT.TFile(str.split(':')[0])
    obj = f.Get(str.split(':')[1]).Clone()
    f.Close()
    return obj

# Boilerplate
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.RooWorkspace.imp = getattr(ROOT.RooWorkspace, 'import')
ROOT.TH1.AddDirectory(0)
ROOT.gROOT.LoadMacro("CrystalBallEfficiency.cxx+")

w = ROOT.RooWorkspace('w')

### Muon tracking efficiency scale factor from the Tracking POG
loc = 'inputs/2018/TrackingPOG'

muon_trk_eff_hist = wsptools.TGraphAsymmErrorsToTH1D(GetFromTFile(loc+'/fits.root:ratio_eff_eta3_dr030e030_corr'))
wsptools.SafeWrapHist(w, ['m_eta'], muon_trk_eff_hist, name='m_trk_ratio')

### Electron reconstruction efficiency scale factor from the egamma POG
loc = 'inputs/2018/EGammaPOG'

electron_trk_eff_hist = GetFromTFile(loc+'/egammaEffi.txt_EGM2D_updatedAll_2018.root:EGamma_SF2D')
electron_reco_eff_hist = GetFromTFile(loc+'/egammaEffi.txt_EGM2D_updatedAll_2018.root:EGamma_SF2D')
wsptools.SafeWrapHist(w, ['e_eta','e_pt'], electron_trk_eff_hist, name='e_trk_ratio')

wsptools.SafeWrapHist(w, ['e_eta','e_pt'], electron_reco_eff_hist, name='e_reco_ratio')

################################################
### IC muon scale factors for normalisation ####
################################################

loc_kit = 'inputs/2018/KIT/2018'

histsToWrap = [(loc_kit + '/Mu8/muon_SFs.root:Mu8_pt_eta_bins', 'm_sel_trg8_1_data'),
               (loc_kit + '/Mu17/muon_SFs.root:Mu17_pt_eta_bins','m_sel_trg17_1_data')]

for task in histsToWrap:
    wsptools.SafeWrapHist(
        w, ['gt1_pt', 'expr::gt1_abs_eta("TMath::Abs(@0)",gt1_eta[0])'],
        GetFromTFile(task[0]),
        name=task[1])

histsToWrap = [(loc_kit + '/Mu8/muon_SFs.root:Mu8_pt_eta_bins', 'm_sel_trg8_2_data'),
               (loc_kit + '/Mu17/muon_SFs.root:Mu17_pt_eta_bins','m_sel_trg17_2_data')]

for task in histsToWrap:
    wsptools.SafeWrapHist(
        w, ['gt2_pt', 'expr::gt2_abs_eta("TMath::Abs(@0)",gt2_eta[0])'],
        GetFromTFile(task[0]),
        name=task[1])

    w.factory('expr::m_sel_trg_data("0.9946*(@0*@3+@1*@2-@1*@3)", m_sel_trg8_1_data, m_sel_trg17_1_data, m_sel_trg8_2_data, m_sel_trg17_2_data)')
    w.factory('expr::m_sel_trg_ratio("min(1./@0,2)", m_sel_trg_data)')

histsToWrap = [
    (loc_kit + '/muonEmbID.root:ID_pt_eta_bins', 'm_sel_idEmb_data')
]
wsptools.SafeWrapHist(w, ['gt_pt', 'expr::gt_abs_eta("TMath::Abs(@0)",gt_eta[0])'],
                          GetFromTFile(histsToWrap[0][0]),
                          name=histsToWrap[0][1])

w.factory('expr::m_sel_idEmb_ratio("min(1./@0,20)", m_sel_idEmb_data)')

### DESY electron & muon tag and probe results
loc = 'inputs/2018/LeptonEfficiencies'

 #electron triggers
desyHistsToWrap = [
    (loc+'/Electron/Run2017/Electron_EleTau_Ele24.root',           'MC', 'e_trg_EleTau_Ele24Leg_desy_mc'),
    (loc+'/Electron/Run2017/Electron_EleTau_Ele24.root',           'Data', 'e_trg_EleTau_Ele24Leg_desy_data'),
    (loc+'/Electron/Run2017/Electron_Ele32orEle35.root',           'MC', 'e_trg_SingleEle_Ele32OREle35_desy_mc'),
    (loc+'/Electron/Run2017/Electron_Ele32orEle35.root',           'Data', 'e_trg_SingleEle_Ele32OREle35_desy_data')
]

for task in desyHistsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])

for t in ['trg_EleTau_Ele24Leg_desy','trg_SingleEle_Ele32OREle35_desy']:
    w.factory('expr::e_%s_ratio("@0/@1", e_%s_data, e_%s_mc)' % (t, t, t))

# muon triggers
desyHistsToWrap = [
    (loc+'/Muon/Run2017/Muon_MuTau_IsoMu20.root',           'MC', 'm_trg_MuTau_Mu20Leg_desy_mc'),
    (loc+'/Muon/Run2017/Muon_MuTau_IsoMu20.root',           'Data', 'm_trg_MuTau_Mu20Leg_desy_data'),
    (loc+'/Muon/Run2017/Muon_IsoMu24orIsoMu27.root',           'MC', 'm_trg_SingleMu_Mu24ORMu27_desy_mc'),
    (loc+'/Muon/Run2017/Muon_IsoMu24orIsoMu27.root',           'Data', 'm_trg_SingleMu_Mu24ORMu27_desy_data')
]

for task in desyHistsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])

for t in ['trg_MuTau_Mu20Leg_desy','trg_SingleMu_Mu24ORMu27_desy']:
    w.factory('expr::m_%s_ratio("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))



# triggr SFs Muons from KIT
loc = 'inputs/2018/KIT/v18_2/'


histsToWrap = [
    (loc+'muon_TP_Data_2018_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',                'm_id_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',                  'm_id_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',           'm_id_kit_embed'),

    (loc+'muon_TP_Data_2018_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',              'm_iso_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                'm_iso_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',         'm_iso_kit_embed'),

    (loc+'muon_TP_Data_2018_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',              'm_aiso1_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',                'm_aiso1_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',         'm_aiso1_kit_embed'),

    (loc+'muon_TP_Data_2018_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',              'm_aiso2_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',                'm_aiso2_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',         'm_aiso2_kit_embed'),

    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu24_pt_eta_bins.root:Trg_IsoMu24_pt_eta_bins',      'm_trg24_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu24_pt_eta_bins.root:Trg_IsoMu24_pt_eta_bins',        'm_trg24_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu24_pt_eta_bins.root:Trg_IsoMu24_pt_eta_bins', 'm_trg24_kit_embed'),
    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu24_AIso1_pt_bins_inc_eta',      'm_trg24_aiso1_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu24_AIso1_pt_bins_inc_eta',        'm_trg24_aiso1_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu24_AIso1_pt_bins_inc_eta', 'm_trg24_aiso1_kit_embed'),
    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu24_AIso2_pt_bins_inc_eta',      'm_trg24_aiso2_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu24_AIso2_pt_bins_inc_eta',        'm_trg24_aiso2_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu24_AIso2_pt_bins_inc_eta', 'm_trg24_aiso2_kit_embed'),

    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu27_pt_eta_bins.root:Trg_IsoMu27_pt_eta_bins',      'm_trg27_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu27_pt_eta_bins.root:Trg_IsoMu27_pt_eta_bins',        'm_trg27_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu27_pt_eta_bins.root:Trg_IsoMu27_pt_eta_bins', 'm_trg27_kit_embed'),
    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu27_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_AIso1_pt_bins_inc_eta',      'm_trg27_aiso1_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu27_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_AIso1_pt_bins_inc_eta',        'm_trg27_aiso1_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu27_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_AIso1_pt_bins_inc_eta', 'm_trg27_aiso1_kit_embed'),
    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu27_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_AIso2_pt_bins_inc_eta',      'm_trg27_aiso2_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu27_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_AIso2_pt_bins_inc_eta',        'm_trg27_aiso2_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu27_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_AIso2_pt_bins_inc_eta', 'm_trg27_aiso2_kit_embed'),

    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root:Trg_IsoMu27_or_IsoMu24_pt_eta_bins',      'm_trg24_27_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root:Trg_IsoMu27_or_IsoMu24_pt_eta_bins',        'm_trg24_27_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root:Trg_IsoMu27_or_IsoMu24_pt_eta_bins', 'm_trg24_27_kit_embed'),
    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta',      'm_trg24_27_aiso1_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta',        'm_trg24_27_aiso1_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta', 'm_trg24_27_aiso1_kit_embed'),
    (loc+'muon_TP_Data_2018_Fits_Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta',      'm_trg24_27_aiso2_kit_data'),
    (loc+'muon_TP_DY_2018_Fits_Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta',        'm_trg24_27_aiso2_kit_mc'),
    (loc+'muon_TP_Embedding_2018_Fits_Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta', 'm_trg24_27_aiso2_kit_embed'),
 
    (loc+'crossmuon_TP_Data_2018_Fits_Trg_Mu20_pt_eta_bins.root:Trg_Mu20_pt_eta_bins',           'm_trg_MuTau_Mu20Leg_kit_data'), 
    (loc+'crossmuon_TP_DY_2018_Fits_Trg_Mu20_pt_eta_bins.root:Trg_Mu20_pt_eta_bins',           'm_trg_MuTau_Mu20Leg_kit_mc'), 
    (loc+'crossmuon_TP_Embedding_2018_Fits_Trg_Mu20_pt_eta_bins.root:Trg_Mu20_pt_eta_bins',           'm_trg_MuTau_Mu20Leg_kit_embed'),

]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg24_binned_kit_data', ['m_trg24_kit_data', 'm_trg24_aiso1_kit_data', 'm_trg24_aiso2_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg24_binned_kit_mc', ['m_trg24_kit_mc', 'm_trg24_aiso1_kit_mc', 'm_trg24_aiso2_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg24_binned_kit_embed', ['m_trg24_kit_embed', 'm_trg24_aiso1_kit_embed', 'm_trg24_aiso2_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg27_binned_kit_data', ['m_trg27_kit_data', 'm_trg27_aiso1_kit_data', 'm_trg27_aiso2_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg27_binned_kit_mc', ['m_trg27_kit_mc', 'm_trg27_aiso1_kit_mc', 'm_trg27_aiso2_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg27_binned_kit_embed', ['m_trg27_kit_embed', 'm_trg27_aiso1_kit_embed', 'm_trg27_aiso2_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg24_27_binned_kit_data', ['m_trg24_27_kit_data', 'm_trg24_27_aiso1_kit_data', 'm_trg24_27_aiso2_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg24_27_binned_kit_mc', ['m_trg24_27_kit_mc', 'm_trg24_27_aiso1_kit_mc', 'm_trg24_27_aiso2_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg24_27_binned_kit_embed', ['m_trg24_27_kit_embed', 'm_trg24_27_aiso1_kit_embed', 'm_trg24_27_aiso2_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_kit_data', ['m_iso_kit_data', 'm_aiso1_kit_data', 'm_aiso2_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_kit_mc', ['m_iso_kit_mc', 'm_aiso1_kit_mc', 'm_aiso2_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_kit_embed', ['m_iso_kit_embed', 'm_aiso1_kit_embed', 'm_aiso2_kit_embed'])

for t in ['data', 'mc', 'embed']:
    w.factory('expr::m_idiso_kit_%s("@0*@1", m_id_kit_%s, m_iso_kit_%s)' % (t, t, t))
    w.factory('expr::m_idiso_binned_kit_%s("@0*@1", m_id_kit_%s, m_iso_binned_kit_%s)' % (t, t, t))

for t in ['trg24', 'trg24_binned', 'trg27', 'trg27_binned', 'trg24_27', 'trg24_27_binned', 'id', 'iso', 'iso_binned', 'idiso_binned', 'trg_MuTau_Mu20Leg' ]:
    w.factory('expr::m_%s_kit_ratio("@0/@1", m_%s_kit_data, m_%s_kit_mc)' % (t, t, t))
    w.factory('expr::m_%s_embed_kit_ratio("@0/@1", m_%s_kit_data, m_%s_kit_embed)' % (t, t, t))

# emu and mu+tau trigger and loose (<0.2) muon isolation scale factors from IC

loc = 'inputs/2018/ICSF/'

histsToWrap = [
    (loc+'EM_HI/muon_SFs.root:data_trg_eff', 'm_trg_23_data'),
    (loc+'EM_HI/muon_SFs.root:ZLL_trg_eff', 'm_trg_23_mc'),
    (loc+'EM_HI/muon_SFs.root:embed_trg_eff', 'm_trg_23_embed'),
    (loc+'EM_LO/muon_SFs.root:data_trg_eff', 'm_trg_8_data'),
    (loc+'EM_LO/muon_SFs.root:ZLL_trg_eff', 'm_trg_8_mc'),
    (loc+'EM_LO/muon_SFs.root:embed_trg_eff', 'm_trg_8_embed'),
    (loc+'EM_LO/muon_SFs.root:data_iso_eff', 'm_looseiso_data'),
    (loc+'EM_LO/muon_SFs.root:ZLL_iso_eff', 'm_looseiso_mc'),
    (loc+'EM_LO/muon_SFs.root:embed_iso_eff', 'm_looseiso_embed'),

    (loc+'EM_HI/aiso/muon_SFs.root:data_trg_eff', 'm_trg_23_aiso_data'),
    (loc+'EM_HI/aiso/muon_SFs.root:ZLL_trg_eff', 'm_trg_23_aiso_mc'),
    (loc+'EM_HI/aiso/muon_SFs.root:embed_trg_eff', 'm_trg_23_aiso_embed'),
    (loc+'EM_LO/aiso/muon_SFs.root:data_trg_eff', 'm_trg_8_aiso_data'),
    (loc+'EM_LO/aiso/muon_SFs.root:ZLL_trg_eff', 'm_trg_8_aiso_mc'),
    (loc+'EM_LO/aiso/muon_SFs.root:embed_trg_eff', 'm_trg_8_aiso_embed'),
    (loc+'EM_LO/aiso/muon_SFs.root:data_iso_eff', 'm_looseiso_aiso_data'),
    (loc+'EM_LO/aiso/muon_SFs.root:ZLL_iso_eff', 'm_looseiso_aiso_mc'),
    (loc+'EM_LO/aiso/muon_SFs.root:embed_iso_eff', 'm_looseiso_aiso_embed'), 

    (loc+'MU20/muon_SFs.root:data_trg_eff', 'm_trg_20_data'),
    (loc+'MU20/muon_SFs.root:ZLL_trg_eff', 'm_trg_20_mc'),
    (loc+'MU20/muon_SFs.root:embed_trg_eff', 'm_trg_20_embed'),
    (loc+'MU20/aiso1/muon_SFs.root:data_trg_eff', 'm_trg_20_aiso1_data'),
    (loc+'MU20/aiso1/muon_SFs.root:ZLL_trg_eff', 'm_trg_20_aiso1_mc'),
    (loc+'MU20/aiso1/muon_SFs.root:embed_trg_eff', 'm_trg_20_aiso1_embed'),
    (loc+'MU20/aiso2/muon_SFs.root:data_trg_eff', 'm_trg_20_aiso2_data'),
    (loc+'MU20/aiso2/muon_SFs.root:ZLL_trg_eff', 'm_trg_20_aiso2_mc'),
    (loc+'MU20/aiso2/muon_SFs.root:embed_trg_eff', 'm_trg_20_aiso2_embed'),
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_binned_23_data', ['m_trg_23_data', 'm_trg_23_aiso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_binned_23_mc', ['m_trg_23_mc', 'm_trg_23_aiso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_binned_23_embed', ['m_trg_23_embed', 'm_trg_23_aiso_embed'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_binned_8_data', ['m_trg_8_data', 'm_trg_8_aiso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_binned_8_mc', ['m_trg_8_mc', 'm_trg_8_aiso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_trg_binned_8_embed', ['m_trg_8_embed', 'm_trg_8_aiso_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_20_data', ['m_trg_20_data', 'm_trg_20_aiso1_data', 'm_trg_20_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_20_embed', ['m_trg_20_embed', 'm_trg_20_aiso1_embed', 'm_trg_20_aiso2_embed'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_20_mc', ['m_trg_20_mc', 'm_trg_20_aiso1_mc', 'm_trg_20_aiso2_mc'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_looseiso_binned_data', ['m_looseiso_data', 'm_looseiso_aiso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_looseiso_binned_mc', ['m_looseiso_mc', 'm_looseiso_aiso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.2, 0.50],
                                   'm_looseiso_binned_embed', ['m_looseiso_embed', 'm_looseiso_aiso_embed'])

w.factory('expr::m_looseiso_ratio("@0/@1", m_looseiso_data, m_looseiso_mc)')
w.factory('expr::m_looseiso_embed_ratio("@0/@1", m_looseiso_data, m_looseiso_embed)')

w.factory('expr::m_looseiso_binned_ratio("@0/@1", m_looseiso_binned_data, m_looseiso_binned_mc)')
w.factory('expr::m_looseiso_binned_embed_ratio("@0/@1", m_looseiso_binned_data, m_looseiso_binned_embed)')

for t in ['trg','trg_binned']:
    w.factory('expr::m_%s_23_ratio("@0/@1", m_%s_23_data, m_%s_23_mc)' % (t, t, t))
    w.factory('expr::m_%s_8_ratio("@0/@1", m_%s_8_data, m_%s_8_mc)' % (t, t, t))
    w.factory('expr::m_%s_20_ratio("@0/@1", m_%s_20_data, m_%s_20_mc)' % (t, t, t))
    w.factory('expr::m_%s_23_embed_ratio("@0/@1", m_%s_23_data, m_%s_23_embed)' % (t, t, t))
    w.factory('expr::m_%s_8_embed_ratio("@0/@1", m_%s_8_data, m_%s_8_embed)' % (t, t, t))
    w.factory('expr::m_%s_20_embed_ratio("@0/@1", m_%s_20_data, m_%s_20_embed)' % (t, t, t))

# trigger SFs Electrons from KIT
loc = 'inputs/2018/KIT/v18_2/'

histsToWrap = [
    (loc+'electron_TP_Data_2018_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                'e_id90_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                  'e_id90_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',           'e_id90_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',                'e_id80_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',                  'e_id80_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',           'e_id80_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',              'e_iso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                'e_iso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',         'e_iso_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_AIso_pt_eta_bins.root:AIso_pt_eta_bins',              'e_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_AIso_pt_eta_bins.root:AIso_pt_eta_bins',                'e_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_AIso_pt_eta_bins.root:AIso_pt_eta_bins',         'e_aiso_kit_embed'),
    # (loc+'electron_TP_Data_2018_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',              'e_aiso2_kit_data'),
    # (loc+'electron_TP_DY_2018_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',                'e_aiso2_kit_mc'),
    # (loc+'electron_TP_Embedding_2018_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',         'e_aiso2_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',      'e_trg_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',        'e_trg_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins', 'e_trg_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg_AIso_pt_bins_inc_eta.root:Trg_AIso_pt_bins_inc_eta',      'e_trg_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg_AIso_pt_bins_inc_eta.root:Trg_AIso_pt_bins_inc_eta',        'e_trg_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg_AIso_pt_bins_inc_eta.root:Trg_AIso_pt_bins_inc_eta', 'e_trg_aiso_kit_embed'),
    # (loc+'electron_TP_Data_2018_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',      'e_trg_aiso2_kit_data'),
    # (loc+'electron_TP_DY_2018_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',        'e_trg_aiso2_kit_mc'),
    # (loc+'electron_TP_Embedding_2018_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta', 'e_trg_aiso2_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg27_Iso_pt_eta_bins.root:Trg27_Iso_pt_eta_bins',      'e_trg27_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_Iso_pt_eta_bins.root:Trg27_Iso_pt_eta_bins',        'e_trg27_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_Iso_pt_eta_bins.root:Trg27_Iso_pt_eta_bins', 'e_trg27_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg27_AIso_pt_bins_inc_eta.root:Trg27_AIso_pt_bins_inc_eta',      'e_trg27_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_AIso_pt_bins_inc_eta.root:Trg27_AIso_pt_bins_inc_eta',        'e_trg27_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_AIso_pt_bins_inc_eta.root:Trg27_AIso_pt_bins_inc_eta', 'e_trg27_aiso_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg32_Iso_pt_eta_bins.root:Trg32_Iso_pt_eta_bins',      'e_trg32_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg32_Iso_pt_eta_bins.root:Trg32_Iso_pt_eta_bins',        'e_trg32_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg32_Iso_pt_eta_bins.root:Trg32_Iso_pt_eta_bins', 'e_trg32_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg32_AIso_pt_bins_inc_eta.root:Trg32_AIso_pt_bins_inc_eta',      'e_trg32_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg32_AIso_pt_bins_inc_eta.root:Trg32_AIso_pt_bins_inc_eta',        'e_trg32_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg32_AIso_pt_bins_inc_eta.root:Trg32_AIso_pt_bins_inc_eta', 'e_trg32_aiso_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg32_fb_Iso_pt_eta_bins.root:Trg32_fb_Iso_pt_eta_bins',      'e_trg32fb_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg32_fb_Iso_pt_eta_bins.root:Trg32_fb_Iso_pt_eta_bins',        'e_trg32fb_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg32_fb_Iso_pt_eta_bins.root:Trg32_fb_Iso_pt_eta_bins', 'e_trg32fb_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg32_fb_AIso_pt_bins_inc_eta.root:Trg32_fb_AIso_pt_bins_inc_eta',      'e_trg32fb_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg32_fb_AIso_pt_bins_inc_eta.root:Trg32_fb_AIso_pt_bins_inc_eta',        'e_trg32fb_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg32_fb_AIso_pt_bins_inc_eta.root:Trg32_fb_AIso_pt_bins_inc_eta', 'e_trg32fb_aiso_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg35_Iso_pt_eta_bins.root:Trg35_Iso_pt_eta_bins',      'e_trg35_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg35_Iso_pt_eta_bins.root:Trg35_Iso_pt_eta_bins',        'e_trg35_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg35_Iso_pt_eta_bins.root:Trg35_Iso_pt_eta_bins', 'e_trg35_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg35_AIso_pt_bins_inc_eta.root:Trg35_AIso_pt_bins_inc_eta',      'e_trg35_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg35_AIso_pt_bins_inc_eta.root:Trg35_AIso_pt_bins_inc_eta',        'e_trg35_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg35_AIso_pt_bins_inc_eta.root:Trg35_AIso_pt_bins_inc_eta', 'e_trg35_aiso_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg27_or_Trg32_Iso_pt_eta_bins.root:Trg27_or_Trg32_Iso_pt_eta_bins',      'e_trg27_trg32_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_or_Trg32_Iso_pt_eta_bins.root:Trg27_or_Trg32_Iso_pt_eta_bins',        'e_trg27_trg32_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_or_Trg32_Iso_pt_eta_bins.root:Trg27_or_Trg32_Iso_pt_eta_bins', 'e_trg27_trg32_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg27_or_Trg32_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_AIso_pt_bins_inc_eta',      'e_trg27_trg32_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_or_Trg32_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_AIso_pt_bins_inc_eta',        'e_trg27_trg32_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_or_Trg32_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_AIso_pt_bins_inc_eta', 'e_trg27_trg32_aiso_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg27_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg35_Iso_pt_eta_bins',      'e_trg27_trg35_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg35_Iso_pt_eta_bins',        'e_trg27_trg35_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg35_Iso_pt_eta_bins', 'e_trg27_trg35_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg27_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg35_AIso_pt_bins_inc_eta',      'e_trg27_trg35_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg35_AIso_pt_bins_inc_eta',        'e_trg27_trg35_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg35_AIso_pt_bins_inc_eta', 'e_trg27_trg35_aiso_kit_embed'),


    (loc+'electron_TP_Data_2018_Fits_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg32_or_Trg35_Iso_pt_eta_bins',      'e_trg32_trg35_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg32_or_Trg35_Iso_pt_eta_bins',        'e_trg32_trg35_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg32_or_Trg35_Iso_pt_eta_bins', 'e_trg32_trg35_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg32_or_Trg35_AIso_pt_bins_inc_eta',      'e_trg32_trg35_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg32_or_Trg35_AIso_pt_bins_inc_eta',        'e_trg32_trg35_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg32_or_Trg35_AIso_pt_bins_inc_eta', 'e_trg32_trg35_aiso_kit_embed'),

    (loc+'electron_TP_Data_2018_Fits_Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins',      'e_trg27_trg32_trg35_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins',        'e_trg27_trg32_trg35_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins', 'e_trg27_trg32_trg35_kit_embed'),
    (loc+'electron_TP_Data_2018_Fits_Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta',      'e_trg27_trg32_trg35_aiso_kit_data'),
    (loc+'electron_TP_DY_2018_Fits_Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta',        'e_trg27_trg32_trg35_aiso_kit_mc'),
    (loc+'electron_TP_Embedding_2018_Fits_Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta', 'e_trg27_trg32_trg35_aiso_kit_embed'),

    (loc+'crosselectron_TP_Data_2018_Fits_Ele24_Iso_pt_eta_bins.root:Ele24_Iso_pt_eta_bins',      'e_trg_EleTau_Ele24Leg_kit_data'),
    (loc+'crosselectron_TP_DY_2018_Fits_Ele24_Iso_pt_eta_bins.root:Ele24_Iso_pt_eta_bins',        'e_trg_EleTau_Ele24Leg_kit_mc'),
    (loc+'crosselectron_TP_Embedding_2018_Fits_Ele24_Iso_pt_eta_bins.root:Ele24_Iso_pt_eta_bins',      'e_trg_EleTau_Ele24Leg_kit_embed'),
    

]
for task in histsToWrap:
    print task
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])


wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg_binned_kit_data', ['e_trg_kit_data', 'e_trg_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg_binned_kit_mc', ['e_trg_kit_mc', 'e_trg_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg_binned_kit_embed', ['e_trg_kit_embed', 'e_trg_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_binned_kit_data', ['e_trg27_kit_data', 'e_trg27_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_binned_kit_mc', ['e_trg27_kit_mc', 'e_trg27_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_binned_kit_embed', ['e_trg27_kit_embed', 'e_trg27_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32_binned_kit_data', ['e_trg32_kit_data', 'e_trg32_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32_binned_kit_mc', ['e_trg32_kit_mc', 'e_trg32_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32_binned_kit_embed', ['e_trg32_kit_embed', 'e_trg32_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32fb_binned_kit_data', ['e_trg32fb_kit_data', 'e_trg32fb_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32fb_binned_kit_mc', ['e_trg32fb_kit_mc', 'e_trg32fb_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32fb_binned_kit_embed', ['e_trg32fb_kit_embed', 'e_trg32fb_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg35_binned_kit_data', ['e_trg35_kit_data', 'e_trg35_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg35_binned_kit_mc', ['e_trg35_kit_mc', 'e_trg35_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg35_binned_kit_embed', ['e_trg35_kit_embed', 'e_trg35_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg32_binned_kit_data', ['e_trg27_trg32_kit_data', 'e_trg27_trg32_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg32_binned_kit_mc', ['e_trg27_trg32_kit_mc', 'e_trg27_trg32_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg32_binned_kit_embed', ['e_trg27_trg32_kit_embed', 'e_trg27_trg32_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg35_binned_kit_data', ['e_trg27_trg35_kit_data', 'e_trg27_trg35_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg35_binned_kit_mc', ['e_trg27_trg35_kit_mc', 'e_trg27_trg35_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg35_binned_kit_embed', ['e_trg27_trg35_kit_embed', 'e_trg27_trg35_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32_trg35_binned_kit_data', ['e_trg32_trg35_kit_data', 'e_trg32_trg35_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32_trg35_binned_kit_mc', ['e_trg32_trg35_kit_mc', 'e_trg32_trg35_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg32_trg35_binned_kit_embed', ['e_trg32_trg35_kit_embed', 'e_trg32_trg35_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg32_trg35_binned_kit_data', ['e_trg27_trg32_trg35_kit_data', 'e_trg27_trg32_trg35_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg32_trg35_binned_kit_mc', ['e_trg27_trg32_trg35_kit_mc', 'e_trg27_trg32_trg35_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_trg27_trg32_trg35_binned_kit_embed', ['e_trg27_trg32_trg35_kit_embed', 'e_trg27_trg32_trg35_aiso_kit_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_iso_binned_kit_data', ['e_iso_kit_data', 'e_aiso_kit_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_iso_binned_kit_mc', ['e_iso_kit_mc', 'e_aiso_kit_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15,  0.50],
                                   'e_iso_binned_kit_embed', ['e_iso_kit_embed', 'e_aiso_kit_embed'])


w.factory('expr::e_id90iso_kit_embed("@0*@1", e_id90_kit_embed, e_iso_kit_embed)')
w.factory('expr::e_id90iso_binned_kit_embed("@0*@1", e_id90_kit_embed, e_iso_binned_kit_embed)')
w.factory('expr::e_id80iso_kit_embed("@0*@1", e_id80_kit_embed, e_iso_kit_embed)')
w.factory('expr::e_id80iso_binned_kit_embed("@0*@1", e_id80_kit_embed, e_iso_binned_kit_embed)')

w.factory('expr::e_id90iso_kit_data("@0*@1", e_id90_kit_data, e_iso_kit_data)')
w.factory('expr::e_id90iso_binned_kit_data("@0*@1", e_id90_kit_data, e_iso_binned_kit_data)')
w.factory('expr::e_id80iso_kit_data("@0*@1", e_id80_kit_data, e_iso_kit_data)')
w.factory('expr::e_id80iso_binned_kit_data("@0*@1", e_id80_kit_data, e_iso_binned_kit_data)')

w.factory('expr::e_id90iso_kit_mc("@0*@1", e_id90_kit_mc, e_iso_kit_mc)')
w.factory('expr::e_id90iso_binned_kit_mc("@0*@1", e_id90_kit_mc, e_iso_binned_kit_mc)')
w.factory('expr::e_id80iso_kit_mc("@0*@1", e_id80_kit_mc, e_iso_kit_mc)')
w.factory('expr::e_id80iso_binned_kit_mc("@0*@1", e_id80_kit_mc, e_iso_binned_kit_mc)')

for t in ['trg', 'trg_binned', 'trg27_trg32', 'trg27_trg32_binned', 'trg27_trg35', 'trg27_trg35_binned', 'trg32_trg35', 'trg32_trg35_binned', 'trg27_trg32_trg35', 'trg27_trg32_trg35_binned', 'trg27', 'trg32', 'trg32fb', 'trg35','id90', 'id80', 'iso', 'iso_binned', 'id90iso_binned', 'id80iso_binned', 'trg_EleTau_Ele24Leg']:
    w.factory('expr::e_%s_kit_ratio("@0/@1", e_%s_kit_data, e_%s_kit_mc)' % (t, t, t))
    w.factory('expr::e_%s_embed_kit_ratio("@0/@1", e_%s_kit_data, e_%s_kit_embed)' % (t, t, t))

# emu and e+tau trigger electron scale factors from IC

loc = 'inputs/2018/ICSF/'

histsToWrap = [
    (loc+'EM_LO/electron_SFs.root:data_trg_eff', 'e_trg_12_data'),
    (loc+'EM_LO/electron_SFs.root:ZLL_trg_eff', 'e_trg_12_mc'),
    (loc+'EM_LO/electron_SFs.root:embed_trg_eff', 'e_trg_12_embed'),
    (loc+'EM_HI/electron_SFs.root:data_trg_eff', 'e_trg_23_data'),
    (loc+'EM_HI/electron_SFs.root:ZLL_trg_eff', 'e_trg_23_mc'),
    (loc+'EM_HI/electron_SFs.root:embed_trg_eff', 'e_trg_23_embed'),

    (loc+'EM_LO/aiso/electron_SFs.root:data_trg_eff', 'e_trg_12_aiso_data'),
    (loc+'EM_LO/aiso/electron_SFs.root:ZLL_trg_eff', 'e_trg_12_aiso_mc'),
    (loc+'EM_LO/aiso/electron_SFs.root:embed_trg_eff', 'e_trg_12_aiso_embed'),
    (loc+'EM_HI/aiso/electron_SFs.root:data_trg_eff', 'e_trg_23_aiso_data'),
    (loc+'EM_HI/aiso/electron_SFs.root:ZLL_trg_eff', 'e_trg_23_aiso_mc'),
    (loc+'EM_HI/aiso/electron_SFs.root:embed_trg_eff', 'e_trg_23_aiso_embed'),

    (loc+'EL24/electron_SFs.root:data_trg_eff', 'e_trg_24_data'),
    (loc+'EL24/electron_SFs.root:ZLL_trg_eff', 'e_trg_24_mc'),
    (loc+'EL24/electron_SFs.root:embed_trg_eff', 'e_trg_24_embed'),
    (loc+'EL24/aiso1/electron_SFs.root:data_trg_eff', 'e_trg_24_aiso1_data'),
    (loc+'EL24/aiso1/electron_SFs.root:ZLL_trg_eff', 'e_trg_24_aiso1_mc'),
    (loc+'EL24/aiso1/electron_SFs.root:embed_trg_eff', 'e_trg_24_aiso1_embed'),
    (loc+'EL24/aiso2/electron_SFs.root:data_trg_eff', 'e_trg_24_aiso2_data'),
    (loc+'EL24/aiso2/electron_SFs.root:ZLL_trg_eff', 'e_trg_24_aiso2_mc'),
    (loc+'EL24/aiso2/electron_SFs.root:embed_trg_eff', 'e_trg_24_aiso2_embed'),

]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.5],
                                   'e_trg_binned_23_data', ['e_trg_23_data', 'e_trg_23_aiso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_23_mc', ['e_trg_23_mc', 'e_trg_23_aiso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_23_embed', ['e_trg_23_embed', 'e_trg_23_aiso_embed'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_12_data', ['e_trg_12_data', 'e_trg_12_aiso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_12_mc', ['e_trg_12_mc', 'e_trg_12_aiso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_12_embed', ['e_trg_12_embed', 'e_trg_12_aiso_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.5],
                                   'e_trg_binned_24_data', ['e_trg_24_data', 'e_trg_24_aiso1_data', 'e_trg_24_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.5],
                                   'e_trg_binned_24_mc', ['e_trg_24_mc', 'e_trg_24_aiso1_mc', 'e_trg_24_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.25, 0.5],
                                   'e_trg_binned_24_embed', ['e_trg_24_embed', 'e_trg_24_aiso1_embed', 'e_trg_24_aiso2_embed'])

for t in ['trg','trg_binned']:
    w.factory('expr::e_%s_12_ratio("@0/@1", e_%s_12_data, e_%s_12_mc)' % (t, t, t))
    w.factory('expr::e_%s_23_ratio("@0/@1", e_%s_23_data, e_%s_23_mc)' % (t, t, t))
    w.factory('expr::e_%s_24_ratio("@0/@1", e_%s_24_data, e_%s_24_mc)' % (t, t, t))
    w.factory('expr::e_%s_12_embed_ratio("@0/@1", e_%s_12_data, e_%s_12_embed)' % (t, t, t))
    w.factory('expr::e_%s_23_embed_ratio("@0/@1", e_%s_23_data, e_%s_23_embed)' % (t, t, t))
    w.factory('expr::e_%s_24_embed_ratio("@0/@1", e_%s_24_data, e_%s_24_embed)' % (t, t, t))

# KIT tau trigger scale factors

loc = 'inputs/2018/KIT/TauTrigger/'
TauTriggerFile = ROOT.TFile(loc+"output_2018_tau_leg.root", "read")
for wp in ["vloose", "loose", "medium", "tight", "vtight", "vvtight"]:
    ## Tau Leg MuTau ##
    mt_tau_leg_kit_data = TauTriggerFile.Get("hist_MuTauTriggerEfficiency_{}TauMVA_DATA".format(wp))
    mt_tau_leg_kit_embed = TauTriggerFile.Get("hist_MuTauTriggerEfficiency_{}TauMVA_EMB".format(wp))
    mt_tau_leg_kit_mc = TauTriggerFile.Get("hist_MuTauTriggerEfficiency_{}TauMVA_MC".format(wp))

    wsptools.SafeWrapHist(w,['t_pt'],mt_tau_leg_kit_data, name="mt_LooseChargedIsoPFTau27_{}_kit_data".format(wp))
    wsptools.SafeWrapHist(w,['t_pt'],mt_tau_leg_kit_mc, name="mt_LooseChargedIsoPFTau27_{}_kit_mc".format(wp))
    wsptools.SafeWrapHist(w,['t_pt'],mt_tau_leg_kit_embed, name="mt_LooseChargedIsoPFTau27_{}_kit_embed".format(wp))
    w.factory('expr::mt_LooseChargedIsoPFTau27_{}_kit_ratio("@0/@1", mt_LooseChargedIsoPFTau27_{}_kit_data, mt_LooseChargedIsoPFTau27_{}_kit_mc)'.format(wp,wp,wp))
    w.factory('expr::mt_emb_LooseChargedIsoPFTau27_{}_kit_ratio("@0/@1", mt_LooseChargedIsoPFTau27_{}_kit_data, mt_LooseChargedIsoPFTau27_{}_kit_embed)'.format(wp,wp,wp))

    ## Tau Leg ETau ##
    et_tau_leg_kit_data = TauTriggerFile.Get("hist_ETauTriggerEfficiency_{}TauMVA_DATA".format(wp))
    et_tau_leg_kit_embed = TauTriggerFile.Get("hist_ETauTriggerEfficiency_{}TauMVA_EMB".format(wp))
    et_tau_leg_kit_mc = TauTriggerFile.Get("hist_ETauTriggerEfficiency_{}TauMVA_MC".format(wp))

    wsptools.SafeWrapHist(w,['t_pt'],et_tau_leg_kit_data, name="et_LooseChargedIsoPFTau30_{}_kit_data".format(wp))
    wsptools.SafeWrapHist(w,['t_pt'],et_tau_leg_kit_mc, name="et_LooseChargedIsoPFTau30_{}_kit_mc".format(wp))
    wsptools.SafeWrapHist(w,['t_pt'],et_tau_leg_kit_embed, name="et_LooseChargedIsoPFTau30_{}_kit_embed".format(wp))
    w.factory('expr::et_LooseChargedIsoPFTau30_{}_kit_ratio("@0/@1", et_LooseChargedIsoPFTau30_{}_kit_data, et_LooseChargedIsoPFTau30_{}_kit_mc)'.format(wp,wp,wp))
    w.factory('expr::et_emb_LooseChargedIsoPFTau30_{}_kit_ratio("@0/@1", et_LooseChargedIsoPFTau30_{}_kit_data, et_LooseChargedIsoPFTau30_{}_kit_embed)'.format(wp,wp,wp))

    ## Tau Leg TauTau ##
    tt_tau_leg_kit_data = TauTriggerFile.Get("hist_TauLeadTriggerEfficiency_{}TauMVA_DATA".format(wp))
    tt_tau_leg_kit_embed = TauTriggerFile.Get("hist_TauLeadTriggerEfficiency_{}TauMVA_EMB".format(wp))
    tt_tau_leg_kit_mc = TauTriggerFile.Get("hist_TauLeadTriggerEfficiency_{}TauMVA_MC".format(wp))

    wsptools.SafeWrapHist(w,['t_pt'],tt_tau_leg_kit_data, name="tt_PFTau35OR40_{}_kit_data".format(wp))
    wsptools.SafeWrapHist(w,['t_pt'],tt_tau_leg_kit_mc, name="tt_PFTau35OR40_{}_kit_mc".format(wp))
    wsptools.SafeWrapHist(w,['t_pt'],tt_tau_leg_kit_embed, name="tt_PFTau35OR40_{}_kit_embed".format(wp))
    w.factory('expr::tt_PFTau35OR40_{}_kit_ratio("@0/@1", tt_PFTau35OR40_{}_kit_data, tt_PFTau35OR40_{}_kit_mc)'.format(wp,wp,wp))
    w.factory('expr::tt_emb_PFTau35OR40_{}_kit_ratio("@0/@1", tt_PFTau35OR40_{}_kit_data, tt_PFTau35OR40_{}_kit_embed)'.format(wp,wp,wp))
TauTriggerFile.Close()

### Tau Trigger scale factors from Tau POG

loc = 'inputs/2018/TauPOGTriggerSFs/'
tau_trg_file = ROOT.TFile(loc+'tauTriggerEfficiencies2018.root')
w.factory('expr::t_pt_trig("min(max(@0,20),450)" ,t_pt[0])')
tau_id_wps=['vloose','loose','medium','tight','vtight']

for wp in tau_id_wps:
  for dm in ['0','1','10']:
    histsToWrap = [
      (loc+'tauTriggerEfficiencies2018.root:ditau_%sMVAv2_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:ditau_%sMVAv2_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:ditau_%sMVAv2_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:ditau_%sMVAv2_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:mutau_%sMVAv2_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:mutau_%sMVAv2_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:mutau_%sMVAv2_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:mutau_%sMVAv2_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:etau_%sMVAv2_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:etau_%sMVAv2_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:etau_%sMVAv2_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2018.root:etau_%sMVAv2_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_mc' % (wp,dm))
    ]
    for task in histsToWrap:  
      wsptools.SafeWrapHist(w, ['t_eta','t_phi'],
                            GetFromTFile(task[0]), name=task[1])

    for x in ['data', 'mc']:
      for y in ['ditau','mutau','etau']:
        func = tau_trg_file.Get("%s_%sMVAv2_dm%s_%s_fit" % (y,wp,dm,x.upper())) 
        params = func.GetParameters()
        w.factory('expr::t_trg_pt_%s_%s_dm%s_%s("%.12f - ROOT::Math::crystalball_cdf(-@0, %.12f, %.12f, %.12f, %.12f)*(%.12f)", t_pt_trig)' % (wp,y,dm,x, params[5],params[0],params[1],params[2],params[3],params[4]))
  
        w.factory('expr::t_trg_phieta_%s_%s_%s("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_phieta_%s_%s_dm0_%s, t_trg_phieta_%s_%s_dm1_%s, t_trg_phieta_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
        w.factory('expr::t_trg_ave_phieta_%s_%s_%s("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_ave_phieta_%s_%s_dm0_%s, t_trg_ave_phieta_%s_%s_dm1_%s, t_trg_ave_phieta_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
  
        w.factory('expr::t_trg_pt_%s_%s_%s("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_pt_%s_%s_dm0_%s, t_trg_pt_%s_%s_dm1_%s, t_trg_pt_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x)) 

        w.factory('expr::t_trg_%s_%s_data("@0*@1/@2", t_trg_pt_%s_%s_data, t_trg_phieta_%s_%s_data, t_trg_ave_phieta_%s_%s_data)' % (wp, y, wp, y, wp, y, wp, y))  
        w.factory('expr::t_trg_%s_%s_mc("@0*@1/@2", t_trg_pt_%s_%s_mc, t_trg_phieta_%s_%s_mc, t_trg_ave_phieta_%s_%s_mc)' % (wp, y, wp, y, wp, y, wp, y))
        w.factory('expr::t_trg_%s_%s_ratio("@0/@1", t_trg_%s_%s_data, t_trg_%s_%s_mc)' % (wp, y, wp, y, wp, y))


# now use the histograms to get the uncertainty variations
for wp in tau_id_wps:
  for dm in ['0','1','10']:
     histsToWrap = [
      ('ditau_%sMVAv2_dm%s_DATA_errorBand' % (wp,dm), 't_trg_uncert_%s_ditau_dm%s_data' % (wp,dm)),
      ('mutau_%sMVAv2_dm%s_DATA_errorBand' % (wp,dm), 't_trg_uncert_%s_mutau_dm%s_data' % (wp,dm)),
      ('etau_%sMVAv2_dm%s_DATA_errorBand' % (wp,dm), 't_trg_uncert_%s_etau_dm%s_data' % (wp,dm)),
      ('ditau_%sMVAv2_dm%s_MC_errorBand' % (wp,dm), 't_trg_uncert_%s_ditau_dm%s_mc' % (wp,dm)),
      ('mutau_%sMVAv2_dm%s_MC_errorBand' % (wp,dm), 't_trg_uncert_%s_mutau_dm%s_mc' % (wp,dm)),
      ('etau_%sMVAv2_dm%s_MC_errorBand' % (wp,dm), 't_trg_uncert_%s_etau_dm%s_mc' % (wp,dm))
    ]

     for task in histsToWrap:
       hist = tau_trg_file.Get(task[0])
       uncert_hists = wsptools.UncertsFromHist(hist) 
       wsptools.SafeWrapHist(w, ['t_pt'], uncert_hists[0], name=task[1]+'_up')
       wsptools.SafeWrapHist(w, ['t_pt'], uncert_hists[1], name=task[1]+'_down')

  for y in ['ditau','mutau','etau']:
    for x in ['data', 'mc']:
      w.factory('expr::t_trg_pt_uncert_%s_%s_%s_up("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_uncert_%s_%s_dm0_%s_up, t_trg_uncert_%s_%s_dm1_%s_up, t_trg_uncert_%s_%s_dm10_%s_up)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
      w.factory('expr::t_trg_pt_uncert_%s_%s_%s_down("(@0==0)*@1 + (@0==1)*@2 + (@0>=3)*@3", t_dm[0], t_trg_uncert_%s_%s_dm0_%s_down, t_trg_uncert_%s_%s_dm1_%s_down, t_trg_uncert_%s_%s_dm10_%s_down)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))

      w.factory('expr::t_trg_uncert_%s_%s_%s_up("1.+@1/@0", t_trg_pt_%s_%s_%s, t_trg_pt_uncert_%s_%s_%s_up)' % (wp, y, x, wp, y, x, wp, y, x))
      w.factory('expr::t_trg_uncert_%s_%s_%s_down("1.-@1/@0", t_trg_pt_%s_%s_%s, t_trg_pt_uncert_%s_%s_%s_down)' % (wp, y, x, wp, y, x, wp, y, x))

    w.factory('expr::t_trg_uncert_%s_%s_ratio_up("1.+sqrt(pow(@2/@0,2) + pow(@3/@1,2))", t_trg_%s_%s_data, t_trg_%s_%s_mc, t_trg_pt_uncert_%s_%s_data_up, t_trg_pt_uncert_%s_%s_mc_up)' % (wp, y, wp, y, wp, y, wp, y, wp, y))
    w.factory('expr::t_trg_uncert_%s_%s_ratio_down("1.-sqrt(pow(@2/@0,2) + pow(@3/@1,2))", t_trg_%s_%s_data, t_trg_%s_%s_mc, t_trg_pt_uncert_%s_%s_data_up, t_trg_pt_uncert_%s_%s_mc_up)' % (wp, y, wp, y, wp, y, wp, y, wp, y))

# differential tau ID SFs from tau POG

# dm binned SFs

loc='inputs/2018/TauPOGIDSFs/'

histsToWrap = [
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2018.root:VLoose', 't_id_dm_vloose'), 
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2018.root:Loose',  't_id_dm_loose'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2018.root:Medium', 't_id_dm_medium'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2018.root:Tight',  't_id_dm_tight'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2018.root:VTight', 't_id_dm_vtight'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2018.root:VVTight', 't_id_dm_vvtight')
]

w.factory('expr::t_dm_bounded("(@0<2)*@0 + (@0>2)*10" ,t_dm[0])')

for task in histsToWrap: 
  wsptools.SafeWrapHist(w, ['t_dm_bounded'], GetFromTFile(task[0]), name=task[1])
  uncert_hists = wsptools.UncertsFromHist(GetFromTFile(task[0]))
  wsptools.SafeWrapHist(w, ['t_dm_bounded'], uncert_hists[0], name=task[1]+'_abs_up')
  wsptools.SafeWrapHist(w, ['t_dm_bounded'], uncert_hists[1], name=task[1]+'_abs_down')
  w.factory('expr::%s_up("1.+@0/@1",%s_abs_up,%s)' % (task[1],task[1],task[1]))
  w.factory('expr::%s_down("1.-@0/@1",%s_abs_down,%s)' % (task[1],task[1],task[1]))

# pT dependent SFs

sf_funcs = {}

sf_funcs['vloose'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9662711+ ( x > 25 && x <=30)*0.9841571+ ( x > 30 && x <=35)*0.8992864+ ( x > 35 && x <=40)*0.8736828+ (x > 40)*0.977607152447'
sf_funcs['vloose_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0660781+ ( x > 25 && x <=30)*1.0602211+ ( x > 30 && x <=35)*0.9593934+ ( x > 35 && x <=40)*0.9217598+ (x > 40 && x <=500)*1.01133836263+ (x > 500 && x <= 1000)*(0.977607152447 + 0.0337312101811*(x/500.))+ (x > 1000)*(0.977607152447 + 0.0674624203623)'
sf_funcs['vloose_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8664641+ ( x > 25 && x <=30)*0.9080931+ ( x > 30 && x <=35)*0.8391794+ ( x > 35 && x <=40)*0.8256058+ (x > 40 && x <=500)*0.915656669816+ (x > 500 && x <= 1000)*(0.977607152447 - 0.0619504826307*(x/500.))+ (x > 1000)*(0.977607152447 - 0.123900965261)'
sf_funcs['loose'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9724238+ ( x > 25 && x <=30)*0.9414591+ ( x > 30 && x <=35)*0.903099+ ( x > 35 && x <=40)*0.8897563+ (x >40)*0.961412176205'
sf_funcs['loose_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0508898+ ( x > 25 && x <=30)*0.9908071+ ( x > 30 && x <=35)*0.945873+ ( x > 35 && x <=40)*0.9242753+ (x > 40 && x <=500)*0.993036992306+ (x > 500 && x <= 1000)*(0.961412176205 + 0.0316248161005*(x/500.))+ (x > 1000)*(0.961412176205 + 0.0632496322009)'
sf_funcs['loose_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8939578+ ( x > 25 && x <=30)*0.8921111+ ( x > 30 && x <=35)*0.860325+ ( x > 35 && x <=40)*0.8552373+ (x > 40 && x <=500)*0.913623368498+ (x > 500 && x <= 1000)*(0.961412176205 - 0.0477888077072*(x/500.))+ (x > 1000)*(0.961412176205 - 0.0955776154145)'
sf_funcs['medium'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9899992+ ( x > 25 && x <=30)*0.9200476+ ( x > 30 && x <=35)*0.9028496+ ( x > 35 && x <=40)*0.8714629+ (x >40)*0.976360249307'
sf_funcs['medium_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0547492+ ( x > 25 && x <=30)*0.9669146+ ( x > 30 && x <=35)*0.9358836+ ( x > 35 && x <=40)*0.9006419+ (x > 40 && x <=500)*1.00618490594+ (x > 500 && x <= 1000)*(0.976360249307 + 0.0298246566306*(x/500.))+ (x > 1000)*(0.976360249307 + 0.0596493132613)'
sf_funcs['medium_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9252492+ ( x > 25 && x <=30)*0.8731806+ ( x > 30 && x <=35)*0.8698156+ ( x > 35 && x <=40)*0.8422839+ (x > 40 && x <= 500)*0.916024740558+ (x > 500 && x <= 1000)*(0.976360249307 - 0.0603355087495*(x/500.))+ (x > 1000)*(0.976360249307 - 0.120671017499)'
sf_funcs['tight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8956998+ ( x > 25 && x <=30)*0.9134051+ ( x > 30 && x <=35)*0.906231+ ( x > 35 && x <=40)*0.8671195+ (x >40)*0.979299687738'
sf_funcs['tight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9573188+ ( x > 25 && x <=30)*0.9505101+ ( x > 30 && x <=35)*0.932251+ ( x > 35 && x <=40)*0.8922515+ (x > 40 && x <= 500)*1.01259447442+ (x > 500 && x <= 1000)*(0.979299687738 + 0.0332947866851*(x/500.))+ (x > 1000)*(0.979299687738 + 0.0665895733703)'
sf_funcs['tight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8340808+ ( x > 25 && x <=30)*0.8763001+ ( x > 30 && x <=35)*0.880211+ ( x > 35 && x <=40)*0.8419875+ (x > 40 && x <=500)*0.914072075099+ (x > 500 && x <= 1000)*(0.979299687738 - 0.0652276126396*(x/500.))+ (x > 1000)*(0.979299687738 - 0.130455225279)'
sf_funcs['vtight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9564608+ ( x > 25 && x <=30)*0.8996362+ ( x > 30 && x <=35)*0.9040256+ ( x > 35 && x <=40)*0.8576584+ (x >40)*0.947281869975'
sf_funcs['VTight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0015008+ ( x > 25 && x <=30)*0.9295192+ ( x > 30 && x <=35)*0.9267386+ ( x > 35 && x <=40)*0.8813924+ (x > 40 && x <=500)*0.978743245481+ (x > 500 && x <= 1000)*(0.947281869975 + 0.0314613755062*(x/500.))+ (x > 1000)*(0.947281869975 + 0.0629227510125)'
sf_funcs['vtight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9114208+ ( x > 25 && x <=30)*0.8697532+ ( x > 30 && x <=35)*0.8813126+ ( x > 35 && x <=40)*0.8339244+ (x > 40 && x <=500)*0.892528698913+ (x > 500 && x <= 1000)*(0.947281869975 - 0.054753171062*(x/500.))+ (x > 1000)*(0.947281869975 - 0.109506342124)'
sf_funcs['vvtight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9238749+ ( x > 25 && x <=30)*0.8854644+ ( x > 30 && x <=35)*0.8998929+ ( x > 35 && x <=40)*0.9066453+ (x>40)*0.918508990609'
sf_funcs['vvtight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9696919+ ( x > 25 && x <=30)*0.9120364+ ( x > 30 && x <=35)*0.9227749+ ( x > 35 && x <=40)*0.9542053+ (x > 40 && x <=500)*0.951544127496+ (x > 500 && x <= 1000)*(0.918508990609 + 0.0330351368866*(x/500.))+ (x > 1000)*(0.918508990609 + 0.0660702737733)'
sf_funcs['vvtight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8780579+ ( x > 25 && x <=30)*0.8588924+ ( x > 30 && x <=35)*0.8770109+ ( x > 35 && x <=40)*0.8590853+ (x > 40 && x <= 500)*0.884945512573+ (x > 500 && x <= 1000)*(0.918508990609 - 0.0335634780354*(x/500.))+ (x > 1000)*(0.918508990609 - 0.0671269560709)'

import re
for x in sf_funcs:
  func = re.sub('x','@0',sf_funcs[x])
  w.factory('expr::t_id_pt_%s("%s",t_pt[0])' % (x, func))

# PRELIMINARY differential tau ID SFs for deepTau ID from Yuta

# dm binned SFs

loc='inputs/2018/TauPOGIDSFs/'

histsToWrap = [
  (loc+'/TauID_SF_dm_DeepTau2017v2_2018.root:VVVLoose', 't_deeptauid_dm_vvvloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2_2018.root:VVLoose',  't_deeptauid_dm_vvloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2_2018.root:VLoose',   't_deeptauid_dm_vloose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2_2018.root:Loose',    't_deeptauid_dm_loose'),
  (loc+'/TauID_SF_dm_DeepTau2017v2_2018.root:Medium',   't_deeptauid_dm_medium'),
  (loc+'/TauID_SF_dm_DeepTau2017v2_2018.root:Tight',    't_deeptauid_dm_tight'),
  (loc+'/TauID_SF_dm_DeepTau2017v2_2018.root:VTight',   't_deeptauid_dm_vtight'),
  (loc+'/TauID_SF_dm_DeepTau2017v2_2018.root:VVTight',  't_deeptauid_dm_vvtight')
]

for task in histsToWrap:
  wsptools.SafeWrapHist(w, ['t_dm_bounded'], GetFromTFile(task[0]), name=task[1])
  uncert_hists = wsptools.UncertsFromHist(GetFromTFile(task[0]))
  wsptools.SafeWrapHist(w, ['t_dm_bounded'], uncert_hists[0], name=task[1]+'_abs_up')
  wsptools.SafeWrapHist(w, ['t_dm_bounded'], uncert_hists[1], name=task[1]+'_abs_down')
  w.factory('expr::%s_up("1.+@0/@1",%s_abs_up,%s)' % (task[1],task[1],task[1]))
  w.factory('expr::%s_down("1.-@0/@1",%s_abs_down,%s)' % (task[1],task[1],task[1]))

# pT dependent SFs

sf_funcs = {}
sf_funcs['vvvloose'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.022628+ ( x > 25 && x <=30)*1.025368+ ( x > 30 && x <=35)*0.8378989+ ( x > 35 && x <=40)*0.8431093+ (x >40)*0.898236562595'
sf_funcs['vvvloose_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.241701+ ( x > 25 && x <=30)*1.226502+ ( x > 30 && x <=35)*0.9331719+ ( x > 35 && x <=40)*0.9589953+ (x > 40 && x <=500)*0.948360448315+ (x > 500 && x <= 1000)*(0.898236562595 + 0.0501238857201*(x/500.))+ (x > 1000)*(0.898236562595 + 0.10024777144)'
sf_funcs['vvvloose_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.803555+ ( x > 25 && x <=30)*0.824234+ ( x > 30 && x <=35)*0.7426259+ ( x > 35 && x <=40)*0.7272233+ (x > 40 && x <=500)*0.841033785652+ (x > 500 && x <= 1000)*(0.898236562595 - 0.057202776943*(x/500.))+ (x > 1000)*(0.898236562595 - 0.114405553886)'
sf_funcs['vvloose'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.7695165+ ( x > 25 && x <=30)*0.9379907+ ( x > 30 && x <=35)*0.9058222+ ( x > 35 && x <=40)*0.8612596+ (x >40)*0.959292980876'
sf_funcs['vvloose_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9703445+ ( x > 25 && x <=30)*1.0991827+ ( x > 30 && x <=35)*0.9759832+ ( x > 35 && x <=40)*0.9689606+ (x > 40 && x <=500)*1.00079332594+ (x > 500 && x <= 1000)*(0.959292980876 + 0.0415003450619*(x/500.))+ (x > 1000)*(0.959292980876 + 0.0830006901238)'
sf_funcs['vvloose_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.5686885+ ( x > 25 && x <=30)*0.7767987+ ( x > 30 && x <=35)*0.8356612+ ( x > 35 && x <=40)*0.7535586+ (x > 40 && x <=500)*0.895067482966+ (x > 500 && x <= 1000)*(0.959292980876 - 0.0642254979098*(x/500.))+ (x > 1000)*(0.959292980876 - 0.12845099582)'
sf_funcs['vloose'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9758505+ ( x > 25 && x <=30)*0.9454159+ ( x > 30 && x <=35)*0.9117065+ ( x > 35 && x <=40)*0.8707643+ (x >40)*1.00896632423'
sf_funcs['vloose_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.1011895+ ( x > 25 && x <=30)*1.0028749+ ( x > 30 && x <=35)*0.9667175+ ( x > 35 && x <=40)*0.9315753+ (x > 40 && x <=500)*1.06427543027+ (x > 500 && x <= 1000)*(1.00896632423 + 0.0553091060347*(x/500.))+ (x > 1000)*(1.00896632423 + 0.110618212069)'
sf_funcs['vloose_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8505115+ ( x > 25 && x <=30)*0.8879569+ ( x > 30 && x <=35)*0.8566955+ ( x > 35 && x <=40)*0.8099533+ (x > 40 && x <=500)*0.920456171788+ (x > 500 && x <= 1000)*(1.00896632423 - 0.0885101524455*(x/500.))+ (x > 1000)*(1.00896632423 - 0.177020304891)'
sf_funcs['loose'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9427491+ ( x > 25 && x <=30)*0.9921432+ ( x > 30 && x <=35)*0.9047577+ ( x > 35 && x <=40)*0.9372355+ (x >40)*1.02152557932'
sf_funcs['loose_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*1.0346271+ ( x > 25 && x <=30)*1.0620402+ ( x > 30 && x <=35)*0.9546057+ ( x > 35 && x <=40)*0.9930685+ (x > 40 && x <=500)*1.07641736749+ (x > 500 && x <= 1000)*(1.02152557932 + 0.0548917881767*(x/500.))+ (x > 1000)*(1.02152557932 + 0.109783576353)'
sf_funcs['loose_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8508711+ ( x > 25 && x <=30)*0.9222462+ ( x > 30 && x <=35)*0.8549097+ ( x > 35 && x <=40)*0.8814025+ (x > 40 && x <=500)*0.952320718382+ (x > 500 && x <= 1000)*(1.02152557932 - 0.0692048609353*(x/500.))+ (x > 1000)*(1.02152557932 - 0.138409721871)'
sf_funcs['medium'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9340947+ ( x > 25 && x <=30)*0.9124892+ ( x > 30 && x <=35)*0.9252691+ ( x > 35 && x <=40)*0.8989708+ (x >40)*0.934786129776'
sf_funcs['medium_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9709057+ ( x > 25 && x <=30)*0.9730152+ ( x > 30 && x <=35)*0.9944251+ ( x > 35 && x <=40)*0.9502378+ (x > 40 && x <=500)*0.968887248473+ (x > 500 && x <= 1000)*(0.934786129776 + 0.0341011186968*(x/500.))+ (x > 1000)*(0.934786129776 + 0.0682022373937)'
sf_funcs['medium_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8972837+ ( x > 25 && x <=30)*0.8519632+ ( x > 30 && x <=35)*0.8561131+ ( x > 35 && x <=40)*0.8477038+ (x > 40 && x <=500)*0.896268980893+ (x > 500 && x <= 1000)*(0.934786129776 - 0.0385171488836*(x/500.))+ (x > 1000)*(0.934786129776 - 0.0770342977671)'
sf_funcs['tight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9132831+ ( x > 25 && x <=30)*0.9402059+ ( x > 30 && x <=35)*0.8591068+ ( x > 35 && x <=40)*0.896654+ (x >40)*0.95185417361'
sf_funcs['tight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9671791+ ( x > 25 && x <=30)*1.0064559+ ( x > 30 && x <=35)*0.8915508+ ( x > 35 && x <=40)*0.931219+ (x > 40 && x <=500)*0.991951122569+ (x > 500 && x <= 1000)*(0.95185417361 + 0.0400969489595*(x/500.))+ (x > 1000)*(0.95185417361 + 0.0801938979191)'
sf_funcs['tight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8593871+ ( x > 25 && x <=30)*0.8739559+ ( x > 30 && x <=35)*0.8266628+ ( x > 35 && x <=40)*0.862089+ (x > 40 && x <=500)*0.903176354149+ (x > 500 && x <= 1000)*(0.95185417361 - 0.0486778194613*(x/500.))+ (x > 1000)*(0.95185417361 - 0.0973556389226)'
sf_funcs['vtight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8544218+ ( x > 25 && x <=30)*0.8442694+ ( x > 30 && x <=35)*0.846554+ ( x > 35 && x <=40)*0.8260763+ (x >40)*0.893067204066'
sf_funcs['vtight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8902098+ ( x > 25 && x <=30)*0.8990684+ ( x > 30 && x <=35)*0.90067+ ( x > 35 && x <=40)*0.8597243+ (x > 40 && x <=500)*0.930514984317+ (x > 500 && x <= 1000)*(0.893067204066 + 0.0374477802511*(x/500.))+ (x > 1000)*(0.893067204066 + 0.0748955605022)'
sf_funcs['vtight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8186338+ ( x > 25 && x <=30)*0.7894704+ ( x > 30 && x <=35)*0.792438+ ( x > 35 && x <=40)*0.7924283+ (x > 40 && x <=500)*0.842824975287+ (x > 500 && x <= 1000)*(0.893067204066 - 0.0502422287785*(x/500.))+ (x > 1000)*(0.893067204066 - 0.100484457557)'
sf_funcs['vvtight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8079734+ ( x > 25 && x <=30)*0.8089597+ ( x > 30 && x <=35)*0.8666843+ ( x > 35 && x <=40)*0.7777208+ (x >40)*0.837573262152'
sf_funcs['vvtight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8511824+ ( x > 25 && x <=30)*0.9360727+ ( x > 30 && x <=35)*0.9398643+ ( x > 35 && x <=40)*0.7972798+ (x > 40 && x <=500)*0.87664108387+ (x > 500 && x <= 1000)*(0.837573262152 + 0.0390678217175*(x/500.))+ (x > 1000)*(0.837573262152 + 0.078135643435)'
sf_funcs['vvtight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.7647644+ ( x > 25 && x <=30)*0.6818467+ ( x > 30 && x <=35)*0.7935043+ ( x > 35 && x <=40)*0.7581618+ (x > 40 && x <=500)*0.788360723098+ (x > 500 && x <= 1000)*(0.837573262152 - 0.0492125390544*(x/500.))+ (x > 1000)*(0.837573262152 - 0.0984250781087)'

for x in sf_funcs:
  func = re.sub('x','@0',sf_funcs[x])
  w.factory('expr::t_deeptauid_pt_%s("%s",t_pt[0])' % (x, func))

# IC em qcd os/ss weights - these are the 2017 values which will need updating for 2018!

loc = 'inputs/2017/ICSF/em_osss_2017/'

wsptools.SafeWrapHist(w, ['expr::m_pt_max100("min(@0,100)",m_pt[0])', 'expr::e_pt_max100("min(@0,100)",e_pt[0])'],  GetFromTFile(loc+'/em_osss_2017.root:pt_closure'), 'em_qcd_factors')
wsptools.SafeWrapHist(w, ['expr::m_pt_max100("min(@0,100)",m_pt[0])', 'expr::e_pt_max100("min(@0,100)",e_pt[0])'],  GetFromTFile(loc+'/em_osss_2017.root:pt_closure_aiso'), 'em_qcd_factors_bothaiso')
wsptools.SafeWrapHist(w, ['expr::m_pt_max40("min(@0,40)",m_pt[0])','expr::e_pt_max40("min(@0,40)",e_pt[0])'],  GetFromTFile(loc+'/em_osss_2017.root:iso_extrap'), 'em_qcd_extrap_uncert')

w.factory('expr::em_qcd_osss_binned("((@0<0.15)*((@1==0)*(2.505-0.1545*@2) + (@1>0)*(2.896-0.3304*@2))*@3 + (@0>=0.15)*((@1==0)*(3.048-0.1726*@2) + (@1>0)*(3.398-0.3965*@2))*@4)*@5" ,iso[0],njets[0],dR[0],em_qcd_factors,em_qcd_factors_bothaiso, em_qcd_extrap_uncert)')

w.factory('expr::em_qcd_osss_0jet_rateup("((@0<0.15)*((@1==0)*(2.660-0.1545*@2) + (@1>0)*(2.896-0.3304*@2))*@3 + (@0>=0.15)*((@1==0)*(3.173-0.1726*@2) + (@1>0)*(3.398-0.3965*@2))*@4)*@5" ,iso[0],njets[0],dR[0],em_qcd_factors,em_qcd_factors_bothaiso, em_qcd_extrap_uncert)')
w.factory('expr::em_qcd_osss_0jet_ratedown("((@0<0.15)*((@1==0)*(2.350-0.1545*@2) + (@1>0)*(2.896-0.3304*@2))*@3 + (@0>=0.15)*((@1==0)*(2.923-0.1726*@2) + (@1>0)*(3.398-0.3965*@2))*@4)*@5" ,iso[0],njets[0],dR[0],em_qcd_factors,em_qcd_factors_bothaiso, em_qcd_extrap_uncert)')
w.factory('expr::em_qcd_osss_0jet_shapeup  ("((@0<0.15)*((@1==0)*(2.505-0.1075*@2) + (@1>0)*(2.896-0.3304*@2))*@3 + (@0>=0.15)*((@1==0)*(3.048-0.2110*@2) + (@1>0)*(3.398-0.3965*@2))*@4)*@5" ,iso[0],njets[0],dR[0],em_qcd_factors,em_qcd_factors_bothaiso, em_qcd_extrap_uncert)')
w.factory('expr::em_qcd_osss_0jet_shapedown("((@0<0.15)*((@1==0)*(2.505-0.2015*@2) + (@1>0)*(2.896-0.3304*@2))*@3 + (@0>=0.15)*((@1==0)*(3.048-0.2110*@2) + (@1>0)*(3.398-0.3965*@2))*@4)*@5" ,iso[0],njets[0],dR[0],em_qcd_factors,em_qcd_factors_bothaiso, em_qcd_extrap_uncert)')


w.factory('expr::em_qcd_osss_1jet_rateup("((@0<0.15)*((@1==0)*(2.505-0.1545*@2) + (@1>0)*(2.978-0.3304*@2))*@3 + (@0>=0.15)*((@1==0)*(3.048-0.1726*@2) + (@1>0)*(3.459-0.3965*@2))*@4)*@5" ,iso[0],njets[0],dR[0],em_qcd_factors,em_qcd_factors_bothaiso, em_qcd_extrap_uncert)')
w.factory('expr::em_qcd_osss_1jet_ratedown("((@0<0.15)*((@1==0)*(2.505-0.1545*@2) + (@1>0)*(2.814-0.3304*@2))*@3 + (@0>=0.15)*((@1==0)*(3.048-0.1726*@2) + (@1>0)*(3.337-0.3965*@2))*@4)*@5" ,iso[0],njets[0],dR[0],em_qcd_factors,em_qcd_factors_bothaiso, em_qcd_extrap_uncert)')
w.factory('expr::em_qcd_osss_1jet_shapeup("((@0<0.15)*((@1==0)*(2.505-0.1545*@2) + (@1>0)*(2.896-0.3019*@2))*@3 + (@0>=0.15)*((@1==0)*(3.048-0.1726*@2) + (@1>0)*(3.398-0.3753*@2))*@4)*@5" ,iso[0],njets[0],dR[0],em_qcd_factors,em_qcd_factors_bothaiso, em_qcd_extrap_uncert)')
w.factory('expr::em_qcd_osss_1jet_shapedown("((@0<0.15)*((@1==0)*(2.505-0.1545*@2) + (@1>0)*(2.896-0.3589*@2))*@3 + (@0>=0.15)*((@1==0)*(3.048-0.1726*@2) + (@1>0)*(3.398-0.4177*@2))*@4)*@5" ,iso[0],njets[0],dR[0],em_qcd_factors,em_qcd_factors_bothaiso, em_qcd_extrap_uncert)')


wsptools.MakeBinnedCategoryFuncMap(w, 'njets', [0,1,10000],
                                   'em_qcd_osss_shapeup_binned', ['em_qcd_osss_0jet_shapeup','em_qcd_osss_1jet_shapeup'])

wsptools.MakeBinnedCategoryFuncMap(w, 'njets', [0,1,10000],
                                   'em_qcd_osss_shapedown_binned', ['em_qcd_osss_0jet_shapedown','em_qcd_osss_1jet_shapedown'])

wsptools.MakeBinnedCategoryFuncMap(w, 'njets', [0,1,10000],
                                   'em_qcd_osss_rateup_binned', ['em_qcd_osss_0jet_rateup','em_qcd_osss_1jet_rateup'])

wsptools.MakeBinnedCategoryFuncMap(w, 'njets', [0,1,10000],
                                   'em_qcd_osss_ratedown_binned', ['em_qcd_osss_0jet_ratedown','em_qcd_osss_1jet_ratedown'])


w.factory('expr::em_qcd_extrap_up("@0*@1",em_qcd_osss_binned,em_qcd_extrap_uncert)')
w.factory('expr::em_qcd_extrap_down("@0/@1",em_qcd_osss_binned,em_qcd_extrap_uncert)')


# LO DYJetsToLL Z mass vs pT correction
histsToWrap = [
    ('inputs/2018/KIT/zpt_reweighting/zptm_weights_2018_kit.root:zptmass_histo', 'zptmass_weight_nom')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['z_gen_mass', 'z_gen_pt'],
                          GetFromTFile(task[0]), name=task[1])
    
w.importClassCode('CrystalBallEfficiency')

w.Print()
w.writeToFile('htt_scalefactors_v18_3.root')
w.Delete()
