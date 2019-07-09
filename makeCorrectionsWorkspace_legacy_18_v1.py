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

muon_trk_eff_hist = wsptools.TGraphAsymmErrorsToTH1D(GetFromTFile(loc+'/fits_muon_trk_2017.root:ratio_eff_eta3_dr030e030_corr'))
wsptools.SafeWrapHist(w, ['m_eta'], muon_trk_eff_hist, name='m_trk_ratio')

### Electron reconstruction efficiency scale factor from the egamma POG
loc = 'inputs/2018/EGammaPOG'

electron_reco_eff_hist = GetFromTFile(loc+'/egammaEffi.txt_EGM2D_run2017BCDEF_passingRECO.root:EGamma_SF2D')
electron_reco_eff_hist_lowEt = GetFromTFile(loc+'/egammaEffi.txt_EGM2D_run2017BCDEF_passingRECO_lowEt.root:EGamma_SF2D')

eta_bins = set()
pt_bins = set()

for i in range(electron_reco_eff_hist.GetXaxis().GetNbins()):
    lowbin = electron_reco_eff_hist.GetXaxis().GetBinLowEdge(i+1)
    upbin = lowbin + electron_reco_eff_hist.GetXaxis().GetBinWidth(i+1)
    eta_bins.add(lowbin)
    eta_bins.add(upbin)

for i in range(electron_reco_eff_hist_lowEt.GetYaxis().GetNbins()):
    lowbin = electron_reco_eff_hist_lowEt.GetYaxis().GetBinLowEdge(i+1)
    upbin = lowbin + electron_reco_eff_hist_lowEt.GetYaxis().GetBinWidth(i+1)
    pt_bins.add(lowbin)
    pt_bins.add(upbin)

for i in range(electron_reco_eff_hist.GetYaxis().GetNbins()):
    lowbin = electron_reco_eff_hist.GetYaxis().GetBinLowEdge(i+1)
    upbin = lowbin + electron_reco_eff_hist.GetYaxis().GetBinWidth(i+1)
    pt_bins.add(lowbin)
    pt_bins.add(upbin)

eta_bins = np.array(sorted(eta_bins))
pt_bins = np.array(sorted(pt_bins))

electron_reco_eff_hist_full = ROOT.TH2F("eGammaSFs","eGammaSFs",len(eta_bins)-1,eta_bins,len(pt_bins)-1,pt_bins)

for i in range(len(eta_bins)-1):
    for j in range(len(pt_bins)-1):
        value = 0.0
        if j == 0:
            searched_bin = electron_reco_eff_hist_lowEt.FindBin(eta_bins[i],pt_bins[j])
            value = electron_reco_eff_hist_lowEt.GetBinContent(searched_bin)
        else:
            value = electron_reco_eff_hist.GetBinContent(i+1,j)
        electron_reco_eff_hist_full.SetBinContent(i+1,j+1,value)

wsptools.SafeWrapHist(w, ['e_eta','e_pt'], electron_reco_eff_hist_full, name='e_reco_ratio')

################################################
### IC muon scale factors for normalisation ####
################################################

# loc_ic = 'inputs/2018/ICSF/2017'

# histsToWrap = [(loc_ic + '/Mu8/muon_SFs.root:data_trg_eff', 'm_sel_trg8_1_data'),
#                (loc_ic + '/Mu17/muon_SFs.root:data_trg_eff','m_sel_trg17_1_data')]

# for task in histsToWrap:
#     wsptools.SafeWrapHist(
#         w, ['gt1_pt', 'expr::gt1_abs_eta("TMath::Abs(@0)",gt1_eta[0])'],
#         GetFromTFile(task[0]),
#         name=task[1])

# histsToWrap = [(loc_ic + '/Mu8/muon_SFs.root:data_trg_eff', 'm_sel_trg8_2_data'),
#                (loc_ic + '/Mu17/muon_SFs.root:data_trg_eff','m_sel_trg17_2_data')]

# for task in histsToWrap:
#     wsptools.SafeWrapHist(
#         w, ['gt2_pt', 'expr::gt2_abs_eta("TMath::Abs(@0)",gt2_eta[0])'],
#         GetFromTFile(task[0]),
#         name=task[1])

#     #w.factory('expr::m_sel_trg_data("0.935*(@0*@3+@1*@2-@1*@3)", m_sel_trg8_1_data, m_sel_trg17_1_data, m_sel_trg8_2_data, m_sel_trg17_2_data)')
#     w.factory('expr::m_sel_trg_data("0.9959*(@0*@3+@1*@2-@1*@3)", m_sel_trg8_1_data, m_sel_trg17_1_data, m_sel_trg8_2_data, m_sel_trg17_2_data)')
#     w.factory('expr::m_sel_trg_ratio("min(1./@0,2)", m_sel_trg_data)')

# histsToWrap = [
#     (loc_ic + '/Mu8/muon_SFs.root:data_id_eff', 'm_sel_idEmb_data')
# ]
# wsptools.SafeWrapHist(w, ['gt_pt', 'expr::gt_abs_eta("TMath::Abs(@0)",gt_eta[0])'],
#                           GetFromTFile(histsToWrap[0][0]),
#                           name=histsToWrap[0][1])

# w.factory('expr::m_sel_idEmb_ratio("min(1./@0,20)", m_sel_idEmb_data)')

loc_ic = 'inputs/2018/ICSF/2018'

histsToWrap = [(loc_ic + '/Mu8/muon_SFs.root:Mu8_pt_eta_bins', 'm_sel_trg8_1_data'),
               (loc_ic + '/Mu17/muon_SFs.root:Mu17_pt_eta_bins','m_sel_trg17_1_data')]

for task in histsToWrap:
    wsptools.SafeWrapHist(
        w, ['gt1_pt', 'expr::gt1_abs_eta("TMath::Abs(@0)",gt1_eta[0])'],
        GetFromTFile(task[0]),
        name=task[1])

histsToWrap = [(loc_ic + '/Mu8/muon_SFs.root:Mu8_pt_eta_bins', 'm_sel_trg8_2_data'),
               (loc_ic + '/Mu17/muon_SFs.root:Mu17_pt_eta_bins','m_sel_trg17_2_data')]

for task in histsToWrap:
    wsptools.SafeWrapHist(
        w, ['gt2_pt', 'expr::gt2_abs_eta("TMath::Abs(@0)",gt2_eta[0])'],
        GetFromTFile(task[0]),
        name=task[1])

    #w.factory('expr::m_sel_trg_data("0.935*(@0*@3+@1*@2-@1*@3)", m_sel_trg8_1_data, m_sel_trg17_1_data, m_sel_trg8_2_data, m_sel_trg17_2_data)')
    w.factory('expr::m_sel_trg_data("0.9946*(@0*@3+@1*@2-@1*@3)", m_sel_trg8_1_data, m_sel_trg17_1_data, m_sel_trg8_2_data, m_sel_trg17_2_data)')
    w.factory('expr::m_sel_trg_ratio("min(1./@0,2)", m_sel_trg_data)')

histsToWrap = [
    (loc_ic + '/muonEmbID.root:ID_pt_eta_bins', 'm_sel_idEmb_data')
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




### DESY electron & muon tag and probe results
#loc = 'inputs/2018/LeptonEfficiencies'
#
## electron triggers
#desyHistsToWrap = [
#    (loc+'/Electron/Run2017/Electron_EleTau_Ele24.root',           'MC', 'e_trg_EleTau_Ele24Leg_desy_mc'),
#    (loc+'/Electron/Run2017/Electron_EleTau_Ele24.root',           'Data', 'e_trg_EleTau_Ele24Leg_desy_data'),
#    (loc+'/Electron/Run2017/Electron_Ele32orEle35.root',           'MC', 'e_trg_SingleEle_Ele32OREle35_desy_mc'),
#    (loc+'/Electron/Run2017/Electron_Ele32orEle35.root',           'Data', 'e_trg_SingleEle_Ele32OREle35_desy_data')
#]
#
#for task in desyHistsToWrap:
#    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
#                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])
#
#for t in ['trg_EleTau_Ele24Leg_desy','trg_SingleEle_Ele32OREle35_desy']:
#    w.factory('expr::e_%s_ratio("@0/@1", e_%s_data, e_%s_mc)' % (t, t, t))
#
## muon triggers
#desyHistsToWrap = [
#    (loc+'/Muon/Run2017/Muon_MuTau_IsoMu20.root',           'MC', 'm_trg_MuTau_Mu20Leg_desy_mc'),
#    (loc+'/Muon/Run2017/Muon_MuTau_IsoMu20.root',           'Data', 'm_trg_MuTau_Mu20Leg_desy_data'),
#    (loc+'/Muon/Run2017/Muon_IsoMu24orIsoMu27.root',           'MC', 'm_trg_SingleMu_Mu24ORMu27_desy_mc'),
#    (loc+'/Muon/Run2017/Muon_IsoMu24orIsoMu27.root',           'Data', 'm_trg_SingleMu_Mu24ORMu27_desy_data')
#]
#
#for task in desyHistsToWrap:
#    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
#                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])
#
#for t in ['trg_MuTau_Mu20Leg_desy','trg_SingleMu_Mu24ORMu27_desy']:
#    w.factory('expr::m_%s_ratio("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))
#
### KIT electron/muon tag and probe results

# triggr SFs Muons from KIT
loc = 'inputs/2018/KIT/v18_1/'


histsToWrap = [
    (loc+'ZmmTP_Data_sm_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',                'm_id_kit_data'),
    (loc+'ZmmTP_DY_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',                  'm_id_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',           'm_id_kit_embed'),

    (loc+'ZmmTP_Data_sm_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',              'm_iso_kit_data'),
    (loc+'ZmmTP_DY_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                'm_iso_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',         'm_iso_kit_embed'),

    (loc+'ZmmTP_Data_sm_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',              'm_aiso1_kit_data'),
    (loc+'ZmmTP_DY_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',                'm_aiso1_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',         'm_aiso1_kit_embed'),

    (loc+'ZmmTP_Data_sm_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',              'm_aiso2_kit_data'),
    (loc+'ZmmTP_DY_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',                'm_aiso2_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',         'm_aiso2_kit_embed'),

    (loc+'ZmmTP_Data_sm_Fits_Trg_IsoMu24_pt_eta_bins.root:Trg_IsoMu24_pt_eta_bins',      'm_trg24_kit_data'),
    (loc+'ZmmTP_DY_Fits_Trg_IsoMu24_pt_eta_bins.root:Trg_IsoMu24_pt_eta_bins',        'm_trg24_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Trg_IsoMu24_pt_eta_bins.root:Trg_IsoMu24_pt_eta_bins', 'm_trg24_kit_embed'),
    (loc+'ZmmTP_Data_sm_Fits_Trg_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu24_AIso1_pt_bins_inc_eta',      'm_trg24_aiso1_kit_data'),
    (loc+'ZmmTP_DY_Fits_Trg_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu24_AIso1_pt_bins_inc_eta',        'm_trg24_aiso1_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Trg_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu24_AIso1_pt_bins_inc_eta', 'm_trg24_aiso1_kit_embed'),
    (loc+'ZmmTP_Data_sm_Fits_Trg_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu24_AIso2_pt_bins_inc_eta',      'm_trg24_aiso2_kit_data'),
    (loc+'ZmmTP_DY_Fits_Trg_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu24_AIso2_pt_bins_inc_eta',        'm_trg24_aiso2_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Trg_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu24_AIso2_pt_bins_inc_eta', 'm_trg24_aiso2_kit_embed'),

    (loc+'ZmmTP_Data_sm_Fits_Trg_IsoMu27_pt_eta_bins.root:Trg_IsoMu27_pt_eta_bins',      'm_trg27_kit_data'),
    (loc+'ZmmTP_DY_Fits_Trg_IsoMu27_pt_eta_bins.root:Trg_IsoMu27_pt_eta_bins',        'm_trg27_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Trg_IsoMu27_pt_eta_bins.root:Trg_IsoMu27_pt_eta_bins', 'm_trg27_kit_embed'),
    (loc+'ZmmTP_Data_sm_Fits_Trg_IsoMu27_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_AIso1_pt_bins_inc_eta',      'm_trg27_aiso1_kit_data'),
    (loc+'ZmmTP_DY_Fits_Trg_IsoMu27_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_AIso1_pt_bins_inc_eta',        'm_trg27_aiso1_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Trg_IsoMu27_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_AIso1_pt_bins_inc_eta', 'm_trg27_aiso1_kit_embed'),
    (loc+'ZmmTP_Data_sm_Fits_Trg_IsoMu27_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_AIso2_pt_bins_inc_eta',      'm_trg27_aiso2_kit_data'),
    (loc+'ZmmTP_DY_Fits_Trg_IsoMu27_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_AIso2_pt_bins_inc_eta',        'm_trg27_aiso2_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Trg_IsoMu27_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_AIso2_pt_bins_inc_eta', 'm_trg27_aiso2_kit_embed'),

    (loc+'ZmmTP_Data_sm_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root:Trg_IsoMu27_or_IsoMu24_pt_eta_bins',      'm_trg24_27_kit_data'),
    (loc+'ZmmTP_DY_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root:Trg_IsoMu27_or_IsoMu24_pt_eta_bins',        'm_trg24_27_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root:Trg_IsoMu27_or_IsoMu24_pt_eta_bins', 'm_trg24_27_kit_embed'),
    (loc+'ZmmTP_Data_sm_Fits_Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta',      'm_trg24_27_aiso1_kit_data'),
    (loc+'ZmmTP_DY_Fits_Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta',        'm_trg24_27_aiso1_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso1_pt_bins_inc_eta', 'm_trg24_27_aiso1_kit_embed'),
    (loc+'ZmmTP_Data_sm_Fits_Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta',      'm_trg24_27_aiso2_kit_data'),
    (loc+'ZmmTP_DY_Fits_Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta',        'm_trg24_27_aiso2_kit_mc'),
    (loc+'ZmmTP_Embedding_Fits_Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta.root:Trg_IsoMu27_or_IsoMu24_AIso2_pt_bins_inc_eta', 'm_trg24_27_aiso2_kit_embed'),
 
    (loc+'ZmmTP_Data_sm_Fits_Trg_Mu20_pt_eta_bins.root:Trg_Mu20_pt_eta_bins',           'm_trg_MuTau_Mu20Leg_kit_data'), 
    (loc+'ZmmTP_DY_Fits_Trg_Mu20_pt_eta_bins.root:Trg_Mu20_pt_eta_bins',           'm_trg_MuTau_Mu20Leg_kit_mc'), 
    (loc+'ZmmTP_Embedding_Fits_Trg_Mu20_pt_eta_bins.root:Trg_Mu20_pt_eta_bins',           'm_trg_MuTau_Mu20Leg_kit_embed'),

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

# trigger SFs Electrons from KIT
loc = 'inputs/2018/KIT/v18_1/'

histsToWrap = [
    (loc+'ZeeTP_Data_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                'e_id90_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                  'e_id90_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',           'e_id90_kit_embed'),
    (loc+'ZeeTP_Data_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',                'e_id80_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',                  'e_id80_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',           'e_id80_kit_embed'),

    (loc+'ZeeTP_Data_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',              'e_iso_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                'e_iso_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',         'e_iso_kit_embed'),
    (loc+'ZeeTP_Data_Fits_AIso_pt_eta_bins.root:AIso_pt_eta_bins',              'e_aiso_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_AIso_pt_eta_bins.root:AIso_pt_eta_bins',                'e_aiso_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_AIso_pt_eta_bins.root:AIso_pt_eta_bins',         'e_aiso_kit_embed'),
    # (loc+'ZeeTP_Data_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',              'e_aiso2_kit_data'),
    # (loc+'ZeeTP_DYJetsToLL_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',                'e_aiso2_kit_mc'),
    # (loc+'ZeeTP_Embedding_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',         'e_aiso2_kit_embed'),

    (loc+'ZeeTP_Data_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',      'e_trg_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',        'e_trg_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins', 'e_trg_kit_embed'),
    (loc+'ZeeTP_Data_Fits_Trg_AIso_pt_bins_inc_eta.root:Trg_AIso_pt_bins_inc_eta',      'e_trg_aiso_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg_AIso_pt_bins_inc_eta.root:Trg_AIso_pt_bins_inc_eta',        'e_trg_aiso_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg_AIso_pt_bins_inc_eta.root:Trg_AIso_pt_bins_inc_eta', 'e_trg_aiso_kit_embed'),
    # (loc+'ZeeTP_Data_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',      'e_trg_aiso2_kit_data'),
    # (loc+'ZeeTP_DYJetsToLL_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',        'e_trg_aiso2_kit_mc'),
    # (loc+'ZeeTP_Embedding_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta', 'e_trg_aiso2_kit_embed'),

    (loc+'ZeeTP_Data_Fits_Trg27_Iso_pt_eta_bins.root:Trg27_Iso_pt_eta_bins',      'e_trg27_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg27_Iso_pt_eta_bins.root:Trg27_Iso_pt_eta_bins',        'e_trg27_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg27_Iso_pt_eta_bins.root:Trg27_Iso_pt_eta_bins', 'e_trg27_kit_embed'),
    (loc+'ZeeTP_Data_Fits_Trg27_AIso_pt_bins_inc_eta.root:Trg27_AIso_pt_bins_inc_eta',      'e_trg27_aiso_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg27_AIso_pt_bins_inc_eta.root:Trg27_AIso_pt_bins_inc_eta',        'e_trg27_aiso_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg27_AIso_pt_bins_inc_eta.root:Trg27_AIso_pt_bins_inc_eta', 'e_trg27_aiso_kit_embed'),

    (loc+'ZeeTP_Data_Fits_Trg32_Iso_pt_eta_bins.root:Trg32_Iso_pt_eta_bins',      'e_trg32_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg32_Iso_pt_eta_bins.root:Trg32_Iso_pt_eta_bins',        'e_trg32_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg32_Iso_pt_eta_bins.root:Trg32_Iso_pt_eta_bins', 'e_trg32_kit_embed'),
    (loc+'ZeeTP_Data_Fits_Trg32_AIso_pt_bins_inc_eta.root:Trg32_AIso_pt_bins_inc_eta',      'e_trg32_aiso_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg32_AIso_pt_bins_inc_eta.root:Trg32_AIso_pt_bins_inc_eta',        'e_trg32_aiso_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg32_AIso_pt_bins_inc_eta.root:Trg32_AIso_pt_bins_inc_eta', 'e_trg32_aiso_kit_embed'),

    (loc+'ZeeTP_Data_Fits_Trg32_fb_Iso_pt_eta_bins.root:Trg32_fb_Iso_pt_eta_bins',      'e_trg32fb_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg32_fb_Iso_pt_eta_bins.root:Trg32_fb_Iso_pt_eta_bins',        'e_trg32fb_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg32_fb_Iso_pt_eta_bins.root:Trg32_fb_Iso_pt_eta_bins', 'e_trg32fb_kit_embed'),
    (loc+'ZeeTP_Data_Fits_Trg32_fb_AIso_pt_bins_inc_eta.root:Trg32_fb_AIso_pt_bins_inc_eta',      'e_trg32fb_aiso_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg32_fb_AIso_pt_bins_inc_eta.root:Trg32_fb_AIso_pt_bins_inc_eta',        'e_trg32fb_aiso_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg32_fb_AIso_pt_bins_inc_eta.root:Trg32_fb_AIso_pt_bins_inc_eta', 'e_trg32fb_aiso_kit_embed'),

    (loc+'ZeeTP_Data_Fits_Trg35_Iso_pt_eta_bins.root:Trg35_Iso_pt_eta_bins',      'e_trg35_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg35_Iso_pt_eta_bins.root:Trg35_Iso_pt_eta_bins',        'e_trg35_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg35_Iso_pt_eta_bins.root:Trg35_Iso_pt_eta_bins', 'e_trg35_kit_embed'),
    (loc+'ZeeTP_Data_Fits_Trg35_AIso_pt_bins_inc_eta.root:Trg35_AIso_pt_bins_inc_eta',      'e_trg35_aiso_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg35_AIso_pt_bins_inc_eta.root:Trg35_AIso_pt_bins_inc_eta',        'e_trg35_aiso_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg35_AIso_pt_bins_inc_eta.root:Trg35_AIso_pt_bins_inc_eta', 'e_trg35_aiso_kit_embed'),

    (loc+'ZeeTP_Data_Fits_Trg27_or_Trg32_Iso_pt_eta_bins.root:Trg27_or_Trg32_Iso_pt_eta_bins',      'e_trg27_trg32_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg27_or_Trg32_Iso_pt_eta_bins.root:Trg27_or_Trg32_Iso_pt_eta_bins',        'e_trg27_trg32_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg27_or_Trg32_Iso_pt_eta_bins.root:Trg27_or_Trg32_Iso_pt_eta_bins', 'e_trg27_trg32_kit_embed'),
    (loc+'ZeeTP_Data_Fits_Trg27_or_Trg32_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_AIso_pt_bins_inc_eta',      'e_trg27_trg32_aiso_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg27_or_Trg32_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_AIso_pt_bins_inc_eta',        'e_trg27_trg32_aiso_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg27_or_Trg32_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_AIso_pt_bins_inc_eta', 'e_trg27_trg32_aiso_kit_embed'),

    (loc+'ZeeTP_Data_Fits_Trg27_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg35_Iso_pt_eta_bins',      'e_trg27_trg35_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg27_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg35_Iso_pt_eta_bins',        'e_trg27_trg35_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg27_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg35_Iso_pt_eta_bins', 'e_trg27_trg35_kit_embed'),
    (loc+'ZeeTP_Data_Fits_Trg27_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg35_AIso_pt_bins_inc_eta',      'e_trg27_trg35_aiso_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg27_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg35_AIso_pt_bins_inc_eta',        'e_trg27_trg35_aiso_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg27_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg35_AIso_pt_bins_inc_eta', 'e_trg27_trg35_aiso_kit_embed'),


    (loc+'ZeeTP_Data_Fits_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg32_or_Trg35_Iso_pt_eta_bins',      'e_trg32_trg35_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg32_or_Trg35_Iso_pt_eta_bins',        'e_trg32_trg35_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg32_or_Trg35_Iso_pt_eta_bins', 'e_trg32_trg35_kit_embed'),
    (loc+'ZeeTP_Data_Fits_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg32_or_Trg35_AIso_pt_bins_inc_eta',      'e_trg32_trg35_aiso_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg32_or_Trg35_AIso_pt_bins_inc_eta',        'e_trg32_trg35_aiso_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg32_or_Trg35_AIso_pt_bins_inc_eta', 'e_trg32_trg35_aiso_kit_embed'),

    (loc+'ZeeTP_Data_Fits_Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins',      'e_trg27_trg32_trg35_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins',        'e_trg27_trg32_trg35_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins.root:Trg27_or_Trg32_or_Trg35_Iso_pt_eta_bins', 'e_trg27_trg32_trg35_kit_embed'),
    (loc+'ZeeTP_Data_Fits_Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta',      'e_trg27_trg32_trg35_aiso_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta',        'e_trg27_trg32_trg35_aiso_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta.root:Trg27_or_Trg32_or_Trg35_AIso_pt_bins_inc_eta', 'e_trg27_trg32_trg35_aiso_kit_embed'),

    (loc+'ZeeTP_Data_Fits_Ele24_Iso_pt_eta_bins.root:Ele24_Iso_pt_eta_bins',      'e_trg_EleTau_Ele24Leg_kit_data'),
    (loc+'ZeeTP_DYJetsToLL_Fits_Ele24_Iso_pt_eta_bins.root:Ele24_Iso_pt_eta_bins',        'e_trg_EleTau_Ele24Leg_kit_mc'),
    (loc+'ZeeTP_Embedding_Fits_Ele24_Iso_pt_eta_bins.root:Ele24_Iso_pt_eta_bins',      'e_trg_EleTau_Ele24Leg_kit_embed'),
    

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

for t in ['trg', 'trg_binned', 'trg27_trg32', 'trg27_trg32_binned', 'trg27_trg35', 'trg27_trg35_binned', 'trg32_trg35', 'trg32_trg35_binned', 'trg27_trg32_trg35', 'trg27_trg32_trg35_binned', 'trg27', 'trg32', 'trg32fb', 'trg35','id90', 'id80', 'iso', 'iso_binned', 'id90iso_binned', 'id80iso_binned', 'trg_EleTau_Ele24Leg']:
    w.factory('expr::e_%s_kit_ratio("@0/@1", e_%s_kit_data, e_%s_kit_mc)' % (t, t, t))
    w.factory('expr::e_%s_embed_kit_ratio("@0/@1", e_%s_kit_data, e_%s_kit_embed)' % (t, t, t))

loc = 'inputs/2018/KIT/v17_5/'
## Tau Leg MuTau ##
pt_bins = [0,20,25,30,35,40,45,50,60,80,100,150,200,10000]
n_bins=len(pt_bins)-1

mt_tau_leg_kit_data = ROOT.TH1F("mt_tau_leg_kit_data","mt_tau_leg_kit_data", n_bins, array("d",pt_bins))
mt_tau_leg_kit_data.SetBinContent(1,1.0)
mt_tau_leg_kit_data.SetBinContent(2,0.03861)
mt_tau_leg_kit_data.SetBinContent(3,0.3874)
mt_tau_leg_kit_data.SetBinContent(4,0.71877)
mt_tau_leg_kit_data.SetBinContent(5,0.7767)
mt_tau_leg_kit_data.SetBinContent(6,0.80382)
mt_tau_leg_kit_data.SetBinContent(7,0.82577)
mt_tau_leg_kit_data.SetBinContent(8,0.84958)
mt_tau_leg_kit_data.SetBinContent(9,0.878947)
mt_tau_leg_kit_data.SetBinContent(10,0.982456)
mt_tau_leg_kit_data.SetBinContent(11,0.9107)
mt_tau_leg_kit_data.SetBinContent(12,1.0)
mt_tau_leg_kit_data.SetBinContent(13,1.0)

mt_tau_leg_kit_embed = ROOT.TH1F("mt_tau_leg_kit_embed","mt_tau_leg_kit_embed", n_bins, array("d",pt_bins))
mt_tau_leg_kit_embed.SetBinContent(1,1.0)
mt_tau_leg_kit_embed.SetBinContent(2,0.02954)
mt_tau_leg_kit_embed.SetBinContent(3,0.1082)
mt_tau_leg_kit_embed.SetBinContent(4,0.3031)
mt_tau_leg_kit_embed.SetBinContent(5,0.52798)
mt_tau_leg_kit_embed.SetBinContent(6,0.6543)
mt_tau_leg_kit_embed.SetBinContent(7,0.7351)
mt_tau_leg_kit_embed.SetBinContent(8,0.8669)
mt_tau_leg_kit_embed.SetBinContent(9,0.9571)
mt_tau_leg_kit_embed.SetBinContent(10,0.95)
mt_tau_leg_kit_embed.SetBinContent(11,0.953)
mt_tau_leg_kit_embed.SetBinContent(12,1.0)
mt_tau_leg_kit_embed.SetBinContent(13,1.0)

wsptools.SafeWrapHist(w,['t_pt'],mt_tau_leg_kit_data, name="mt_LooseChargedIsoPFTau27_kit_data")
wsptools.SafeWrapHist(w,['t_pt'],mt_tau_leg_kit_embed, name="mt_LooseChargedIsoPFTau27_kit_embed")
w.factory('expr::mt_emb_LooseChargedIsoPFTau27_kit_ratio("@0/@1", mt_LooseChargedIsoPFTau27_kit_data, mt_LooseChargedIsoPFTau27_kit_embed)')

##TauLeg TauTau
et_tau_leg_kit_data = ROOT.TH1F("et_tau_leg_kit_data","et_tau_leg_kit_data", n_bins, array("d",pt_bins))
et_tau_leg_kit_data.SetBinContent(1,1.0)
et_tau_leg_kit_data.SetBinContent(2,0.03907)
et_tau_leg_kit_data.SetBinContent(3,0.12258)
et_tau_leg_kit_data.SetBinContent(4,0.54274)
et_tau_leg_kit_data.SetBinContent(5,0.67389)
et_tau_leg_kit_data.SetBinContent(6,1,0.74097)
et_tau_leg_kit_data.SetBinContent(7,1,0.81055)
et_tau_leg_kit_data.SetBinContent(8,0.85177)
et_tau_leg_kit_data.SetBinContent(9,0.89533)
et_tau_leg_kit_data.SetBinContent(10,0.88384)
et_tau_leg_kit_data.SetBinContent(11,0.89865)
et_tau_leg_kit_data.SetBinContent(12,0.83871)
et_tau_leg_kit_data.SetBinContent(13,1.0)

et_tau_leg_kit_embed = ROOT.TH1F("et_tau_leg_kit_embed","et_tau_leg_kit_embed", n_bins, array("d",pt_bins))
et_tau_leg_kit_embed.SetBinContent(1,1.0)
et_tau_leg_kit_embed.SetBinContent(2,0.08679)
et_tau_leg_kit_embed.SetBinContent(3,0.24961)
et_tau_leg_kit_embed.SetBinContent(4,0.42047)
et_tau_leg_kit_embed.SetBinContent(5,0.63273)
et_tau_leg_kit_embed.SetBinContent(6,1,0.78850)
et_tau_leg_kit_embed.SetBinContent(7,1,0.88177)
et_tau_leg_kit_embed.SetBinContent(8,0.95065)
et_tau_leg_kit_embed.SetBinContent(9,0.98826)
et_tau_leg_kit_embed.SetBinContent(10,0.99576)
et_tau_leg_kit_embed.SetBinContent(11,0.99617)
et_tau_leg_kit_embed.SetBinContent(12,0.98742)
et_tau_leg_kit_embed.SetBinContent(13,1.0)

wsptools.SafeWrapHist(w,['t_pt'],et_tau_leg_kit_data, name="et_LooseChargedIsoPFTau30_kit_data")
wsptools.SafeWrapHist(w,['t_pt'],et_tau_leg_kit_embed, name="et_LooseChargedIsoPFTau30_kit_embed")
w.factory('expr::et_emb_LooseChargedIsoPFTau30_kit_ratio("@0/@1", et_LooseChargedIsoPFTau30_kit_data, et_LooseChargedIsoPFTau30_kit_embed)')

tt_tau_leg_kit_data = ROOT.TH1F("tt_tau_leg_kit_data","tt_tau_leg_kit_data", n_bins, array("d",pt_bins))
tt_tau_leg_kit_data.SetBinContent(1,1.0)
tt_tau_leg_kit_data.SetBinContent(2,0.0030)
tt_tau_leg_kit_data.SetBinContent(3,0.0086)
tt_tau_leg_kit_data.SetBinContent(4,0.0317)
tt_tau_leg_kit_data.SetBinContent(5,0.2727)
tt_tau_leg_kit_data.SetBinContent(6,0.4235)
tt_tau_leg_kit_data.SetBinContent(7,0.5061)
tt_tau_leg_kit_data.SetBinContent(8,0.6098)
tt_tau_leg_kit_data.SetBinContent(9,0.6877)
tt_tau_leg_kit_data.SetBinContent(10,0.7565)
tt_tau_leg_kit_data.SetBinContent(11,0.6973)
tt_tau_leg_kit_data.SetBinContent(12,0.7019)
tt_tau_leg_kit_data.SetBinContent(13,0.6579)

tt_tau_leg_kit_embed = ROOT.TH1F("tt_tau_leg_kit_embed","tt_tau_leg_kit_embed", n_bins, array("d",pt_bins))
tt_tau_leg_kit_data.SetBinContent(1,1.0)
tt_tau_leg_kit_embed.SetBinContent(2,0.0287)
tt_tau_leg_kit_embed.SetBinContent(3,0.1099)
tt_tau_leg_kit_embed.SetBinContent(4,0.3018)
tt_tau_leg_kit_embed.SetBinContent(5,0.5256)
tt_tau_leg_kit_embed.SetBinContent(6,0.6567)
tt_tau_leg_kit_embed.SetBinContent(7,0.7417)
tt_tau_leg_kit_embed.SetBinContent(8,0.7963)
tt_tau_leg_kit_embed.SetBinContent(9,0.8754)
tt_tau_leg_kit_embed.SetBinContent(10,0.9413)
tt_tau_leg_kit_embed.SetBinContent(11,0.9489)
tt_tau_leg_kit_embed.SetBinContent(12,0.9615)
tt_tau_leg_kit_embed.SetBinContent(13,0.9639)


wsptools.SafeWrapHist(w,['t_pt'],tt_tau_leg_kit_data, name="tt_PFTau35OR40_tight_kit_data")
wsptools.SafeWrapHist(w,['t_pt'],tt_tau_leg_kit_embed, name="tt_PFTau35OR40_tight_kit_embed")
w.factory('expr::tt_emb_PFTau35OR40_tight_kit_ratio("@0/@1", tt_PFTau35OR40_tight_kit_data, tt_PFTau35OR40_tight_kit_embed)')


'''
loc = 'inputs/2018/ICSF/em_osss_2017/'
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
loc = 'inputs/2018/ICSF/em_osss_2017/'
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



### KIT electron & muon tag and probe results for lepton legs of cross triggers
loc = 'inputs/2018/KIT'

 #electron triggers
kitHistsToWrap = [
    (loc+'/Electron_EleTau_Ele24.root',           'mc', 'e_trg_EleTau_Ele24Leg_kit_mc'),
    (loc+'/Electron_EleTau_Ele24.root',           'data', 'e_trg_EleTau_Ele24Leg_kit_data'),
    (loc+'/Electron_EleTau_Ele24.root',           'emb', 'e_trg_EleTau_Ele24Leg_kit_embed')
]

for task in kitHistsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])

for t in ['trg_EleTau_Ele24Leg_kit']:
    w.factory('expr::e_%s_ratio_mc("@0/@1", e_%s_data, e_%s_mc)' % (t, t, t))
    w.factory('expr::e_%s_ratio_embed("@0/@1", e_%s_data, e_%s_embed)' % (t, t, t))

 # muon triggers
kitHistsToWrap = [
    (loc+'/Muon_MuTau_IsoMu20.root',           'mc', 'm_trg_MuTau_Mu20Leg_kit_mc'),
    (loc+'/Muon_MuTau_IsoMu20.root',           'data', 'm_trg_MuTau_Mu20Leg_kit_data'),
    (loc+'/Muon_MuTau_IsoMu20.root',           'emb', 'm_trg_MuTau_Mu20Leg_kit_embed'),
]

for task in kitHistsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])

for t in ['trg_MuTau_Mu20Leg_kit']:
    w.factory('expr::m_%s_ratio_mc("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))
    w.factory('expr::m_%s_ratio_embed("@0/@1", m_%s_data, m_%s_embed)' % (t, t, t))
'''
w.importClassCode('CrystalBallEfficiency')

w.Print()
w.writeToFile('htt_scalefactors_v18_1.root')
w.Delete()
