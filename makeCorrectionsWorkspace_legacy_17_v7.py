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
loc = 'inputs/2017/TrackingPOG'

muon_trk_eff_hist = wsptools.TGraphAsymmErrorsToTH1D(GetFromTFile(loc+'/fits_muon_trk_2017.root:ratio_eff_eta3_dr030e030_corr'))
wsptools.SafeWrapHist(w, ['m_eta'], muon_trk_eff_hist, name='m_trk_ratio')

### Electron reconstruction efficiency scale factor from the egamma POG
loc = 'inputs/2017/EGammaPOG'

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
wsptools.SafeWrapHist(w, ['e_eta','e_pt'], electron_reco_eff_hist_full, name='e_trk_ratio')

################################################
### IC muon scale factors for normalisation ####
################################################

loc_ic = 'inputs/2017/ICSF/2017'

histsToWrap = [(loc_ic + '/Mu8/muon_SFs.root:data_trg_eff', 'm_sel_trg8_1_data'),
               (loc_ic + '/Mu17/muon_SFs.root:data_trg_eff','m_sel_trg17_1_data')]

for task in histsToWrap:
    wsptools.SafeWrapHist(
        w, ['gt1_pt', 'expr::gt1_abs_eta("TMath::Abs(@0)",gt1_eta[0])'],
        GetFromTFile(task[0]),
        name=task[1])

histsToWrap = [(loc_ic + '/Mu8/muon_SFs.root:data_trg_eff', 'm_sel_trg8_2_data'),
               (loc_ic + '/Mu17/muon_SFs.root:data_trg_eff','m_sel_trg17_2_data')]

for task in histsToWrap:
    wsptools.SafeWrapHist(
        w, ['gt2_pt', 'expr::gt2_abs_eta("TMath::Abs(@0)",gt2_eta[0])'],
        GetFromTFile(task[0]),
        name=task[1])

    #w.factory('expr::m_sel_trg_data("0.935*(@0*@3+@1*@2-@1*@3)", m_sel_trg8_1_data, m_sel_trg17_1_data, m_sel_trg8_2_data, m_sel_trg17_2_data)')
    w.factory('expr::m_sel_trg_data("0.9959*(@0*@3+@1*@2-@1*@3)", m_sel_trg8_1_data, m_sel_trg17_1_data, m_sel_trg8_2_data, m_sel_trg17_2_data)')
    w.factory('expr::m_sel_trg_ratio("min(1./@0,2)", m_sel_trg_data)')

histsToWrap = [
    (loc_ic + '/Mu8/muon_SFs.root:data_id_eff', 'm_sel_idEmb_data')
]
wsptools.SafeWrapHist(w, ['gt_pt', 'expr::gt_abs_eta("TMath::Abs(@0)",gt_eta[0])'],
                          GetFromTFile(histsToWrap[0][0]),
                          name=histsToWrap[0][1])

w.factory('expr::m_sel_idEmb_ratio("min(1./@0,20)", m_sel_idEmb_data)')


### DESY electron & muon tag and probe results
loc = 'inputs/2017/LeptonEfficiencies'

 #electron triggers
desyHistsToWrap = [
    (loc+'/Electron/Run2017/Electron_EleTau_Ele24.root',           'MC', 'e_trg_EleTau_Ele24Leg_desy_mc'),
    (loc+'/Electron/Run2017/Electron_EleTau_Ele24.root',           'Data', 'e_trg_EleTau_Ele24Leg_desy_data'),
    (loc+'/Electron/Run2017/Electron_Ele32orEle35.root',           'MC', 'e_trg_SingleEle_Ele32OREle35_desy_mc'),
    (loc+'/Electron/Run2017/Electron_Ele32orEle35.root',           'Data', 'e_trg_SingleEle_Ele32OREle35_desy_data')
]

for task in desyHistsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs_2017(task[0], task[1], task[2]), name=task[2])

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
                          wsptools.ProcessDESYLeptonSFs_2017(task[0], task[1], task[2]), name=task[2])

for t in ['trg_MuTau_Mu20Leg_desy','trg_SingleMu_Mu24ORMu27_desy']:
    w.factory('expr::m_%s_ratio("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))


### DESY electron & muon tag and probe results
#loc = 'inputs/2017/LeptonEfficiencies'
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
#                          wsptools.ProcessDESYLeptonSFs_2017(task[0], task[1], task[2]), name=task[2])
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
#                          wsptools.ProcessDESYLeptonSFs_2017(task[0], task[1], task[2]), name=task[2])
#
#for t in ['trg_MuTau_Mu20Leg_desy','trg_SingleMu_Mu24ORMu27_desy']:
#    w.factory('expr::m_%s_ratio("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))
#
### KIT electron/muon tag and probe results

# triggr SFs Muons from KIT
loc = 'inputs/2017/KIT/v17_5/'


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

for t in ['trg24', 'trg24_binned', 'trg27', 'trg27_binned', 'trg24_27', 'trg24_27_binned', 'id', 'iso', 'iso_binned', 'idiso_binned' ]:
    w.factory('expr::m_%s_kit_ratio("@0/@1", m_%s_kit_data, m_%s_kit_mc)' % (t, t, t))
    w.factory('expr::m_%s_embed_kit_ratio("@0/@1", m_%s_kit_data, m_%s_kit_embed)' % (t, t, t))

# trigger SFs Electrons from KIT
loc = 'inputs/2017/KIT/v17_6/'

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

for t in ['trg', 'trg_binned', 'trg27_trg32', 'trg27_trg32_binned', 'trg27_trg35', 'trg27_trg35_binned', 'trg32_trg35', 'trg32_trg35_binned', 'trg27_trg32_trg35', 'trg27_trg32_trg35_binned', 'trg27', 'trg32', 'trg32fb', 'trg35','id90', 'id80', 'iso', 'iso_binned', 'id90iso_binned', 'id80iso_binned']:
    w.factory('expr::e_%s_kit_ratio("@0/@1", e_%s_kit_data, e_%s_kit_mc)' % (t, t, t))
    w.factory('expr::e_%s_embed_kit_ratio("@0/@1", e_%s_kit_data, e_%s_kit_embed)' % (t, t, t))

loc = 'inputs/2017/KIT/v17_5/'
## Tau Leg MuTau ##
pt_bins = [0,20,25,30,35,40,45,50,60,80,100,150,200,10000]
n_bins=len(pt_bins)-1

mt_tau_leg_kit_data = ROOT.TH1F("mt_tau_leg_kit_data","mt_tau_leg_kit_data", n_bins, array("d",pt_bins))
mt_tau_leg_kit_data.SetBinContent(1,1.0)
mt_tau_leg_kit_data.SetBinContent(2,0.07409)
mt_tau_leg_kit_data.SetBinContent(3,0.37295)
mt_tau_leg_kit_data.SetBinContent(4,0.64799)
mt_tau_leg_kit_data.SetBinContent(5,0.71708)
mt_tau_leg_kit_data.SetBinContent(6,1,0.76309)
mt_tau_leg_kit_data.SetBinContent(7,1,0.81818)
mt_tau_leg_kit_data.SetBinContent(8,0.85730)
mt_tau_leg_kit_data.SetBinContent(9,0.89533)
mt_tau_leg_kit_data.SetBinContent(10,0.88384)
mt_tau_leg_kit_data.SetBinContent(11,0.89865)
mt_tau_leg_kit_data.SetBinContent(12,0.83871)
mt_tau_leg_kit_data.SetBinContent(13,1.0)

mt_tau_leg_kit_embed = ROOT.TH1F("mt_tau_leg_kit_embed","mt_tau_leg_kit_embed", n_bins, array("d",pt_bins))
mt_tau_leg_kit_embed.SetBinContent(1,1.0)
mt_tau_leg_kit_embed.SetBinContent(2,0.58277)
mt_tau_leg_kit_embed.SetBinContent(3,0.79469)
mt_tau_leg_kit_embed.SetBinContent(4,0.90020)
mt_tau_leg_kit_embed.SetBinContent(5,0.95345)
mt_tau_leg_kit_embed.SetBinContent(6,1,0.97626)
mt_tau_leg_kit_embed.SetBinContent(7,1,0.98291)
mt_tau_leg_kit_embed.SetBinContent(8,0.98888)
mt_tau_leg_kit_embed.SetBinContent(9,0.99518)
mt_tau_leg_kit_embed.SetBinContent(10,0.99830)
mt_tau_leg_kit_embed.SetBinContent(11,0.99745)
mt_tau_leg_kit_embed.SetBinContent(12,0.99371)
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

## Tau Leg TauTau
tt_tau_leg_kit_data = ROOT.TH1F("tt_tau_leg_kit_data","tt_tau_leg_kit_data", n_bins, array("d",pt_bins))
tt_tau_leg_kit_data.SetBinContent(1,1.0)
tt_tau_leg_kit_data.SetBinContent(2,0.00828)
tt_tau_leg_kit_data.SetBinContent(3,0.02383)
tt_tau_leg_kit_data.SetBinContent(4,0.07391)
tt_tau_leg_kit_data.SetBinContent(5,0.33054)
tt_tau_leg_kit_data.SetBinContent(6,1,0.46670)
tt_tau_leg_kit_data.SetBinContent(7,1,0.59126)
tt_tau_leg_kit_data.SetBinContent(8,0.68031)
tt_tau_leg_kit_data.SetBinContent(9,0.78879)
tt_tau_leg_kit_data.SetBinContent(10,0.83333)
tt_tau_leg_kit_data.SetBinContent(11,0.86486)
tt_tau_leg_kit_data.SetBinContent(12,0.87097)
tt_tau_leg_kit_data.SetBinContent(13,1.0)

tt_tau_leg_kit_embed = ROOT.TH1F("tt_tau_leg_kit_embed","tt_tau_leg_kit_embed", n_bins, array("d",pt_bins))
tt_tau_leg_kit_embed.SetBinContent(1,1.0)
tt_tau_leg_kit_embed.SetBinContent(2,0.04012)
tt_tau_leg_kit_embed.SetBinContent(3,0.15208)
tt_tau_leg_kit_embed.SetBinContent(4,0.40344)
tt_tau_leg_kit_embed.SetBinContent(5,0.61318)
tt_tau_leg_kit_embed.SetBinContent(6,1,0.73313)
tt_tau_leg_kit_embed.SetBinContent(7,1,0.80825)
tt_tau_leg_kit_embed.SetBinContent(8,0.86113)
tt_tau_leg_kit_embed.SetBinContent(9,0.93165)
tt_tau_leg_kit_embed.SetBinContent(10,0.98132)
tt_tau_leg_kit_embed.SetBinContent(11,0.99617)
tt_tau_leg_kit_embed.SetBinContent(12,0.98742)
tt_tau_leg_kit_embed.SetBinContent(13,1.0)

wsptools.SafeWrapHist(w,['t_pt'],tt_tau_leg_kit_data, name="tt_PFTau35OR40_tight_kit_data")
wsptools.SafeWrapHist(w,['t_pt'],tt_tau_leg_kit_embed, name="tt_PFTau35OR40_tight_kit_embed")
w.factory('expr::tt_emb_PFTau35OR40_tight_kit_ratio("@0/@1", tt_PFTau35OR40_tight_kit_data, tt_PFTau35OR40_tight_kit_embed)')

### KIT electron & muon tag and probe results for lepton legs of cross triggers
loc = 'inputs/2017/KIT'

 #electron triggers
kitHistsToWrap = [
    (loc+'/Electron_EleTau_Ele24.root',           'mc', 'e_trg_EleTau_Ele24Leg_kit_mc'),
    (loc+'/Electron_EleTau_Ele24.root',           'data', 'e_trg_EleTau_Ele24Leg_kit_data'),
    (loc+'/Electron_EleTau_Ele24.root',           'emb', 'e_trg_EleTau_Ele24Leg_kit_embed')
]

for task in kitHistsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs_2017(task[0], task[1], task[2]), name=task[2])

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
                          wsptools.ProcessDESYLeptonSFs_2017(task[0], task[1], task[2]), name=task[2])

for t in ['trg_MuTau_Mu20Leg_kit']:
    w.factory('expr::m_%s_ratio_mc("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))
    w.factory('expr::m_%s_ratio_embed("@0/@1", m_%s_data, m_%s_embed)' % (t, t, t))

# IC muon ID, iso, trigger (for mt channel) SFs

loc = 'inputs/2017/ICSF/'

histsToWrap = [
    (loc+'SingleLepton/muon_SFs.root:data_id_eff', 'm_id_data'),
    (loc+'SingleLepton/muon_SFs.root:ZLL_id_eff', 'm_id_mc'),
    (loc+'SingleLepton/muon_SFs.root:embed_id_eff', 'm_id_embed'),
    (loc+'SingleLepton/muon_SFs.root:data_iso_eff', 'm_iso_data'),
    (loc+'SingleLepton/muon_SFs.root:ZLL_iso_eff', 'm_iso_mc'),
    (loc+'SingleLepton/muon_SFs.root:embed_iso_eff', 'm_iso_embed'),
    (loc+'SingleLepton/muon_SFs.root:data_trg_eff', 'm_trg_data'),
    (loc+'SingleLepton/muon_SFs.root:ZLL_trg_eff', 'm_trg_mc'),
    (loc+'SingleLepton/muon_SFs.root:embed_trg_eff', 'm_trg_embed'),
    (loc+'Mu20/muon20_cross_B/muon_SFs.root:data_trg_eff', 'm_trg20_runB_data'),
    (loc+'Mu20/muon20_cross_B/muon_SFs.root:ZLL_trg_eff', 'm_trg20_mc'),
    (loc+'Mu20/muon20_cross_B/muon_SFs.root:embed_trg_eff', 'm_trg20_embed'),
    (loc+'Mu20/muon20_noB/muon_SFs.root:data_trg_eff', 'm_trg20_runCtoF_data'),
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_trg_binned_data', ['m_trg_data', 'm_trg_data', 'm_trg_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_trg_binned_mc', ['m_trg_mc', 'm_trg_mc', 'm_trg_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_trg_binned_embed', ['m_trg_embed', 'm_trg_embed', 'm_trg_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_iso_binned_data', ['m_iso_data', 'm_iso_data', 'm_iso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_iso_binned_mc', ['m_iso_mc', 'm_iso_mc', 'm_iso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_iso_binned_embed', ['m_iso_embed', 'm_iso_embed', 'm_iso_embed'])

for t in ['data', 'mc', 'embed']:
    w.factory('expr::m_idiso_%s("@0*@1", m_id_%s, m_iso_%s)' % (t, t, t))
    w.factory('expr::m_idiso_binned_%s("@0*@1", m_id_%s, m_iso_binned_%s)' % (t, t, t))

w.factory('expr::m_trg20_data("0.1145*@0+0.8855*@1", m_trg20_runB_data, m_trg20_runCtoF_data)')


for t in ['trg', 'trg20', 'trg_binned', 'id', 'iso', 'iso_binned', 'idiso_binned' ]:
    w.factory('expr::m_%s_ratio("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))
    w.factory('expr::m_%s_embed_ratio("@0/@1", m_%s_data, m_%s_embed)' % (t, t, t))

# IC EGamma ID, iso, trigger (for et channel) SFs 

loc = 'inputs/2017/ICSF/'
        
histsToWrap = [
    (loc+'/ElecIDV2/SingleLepton/electron_SFs.root:data_id_eff', 'e_id_data'),
    (loc+'/ElecIDV2/SingleLepton/electron_SFs.root:ZLL_id_eff', 'e_id_mc'),
    (loc+'/ElecIDV2/SingleLepton/electron_SFs.root:embed_id_eff', 'e_id_embed'),
    (loc+'/ElecIDV2/SingleLepton/electron_SFs.root:data_iso_eff', 'e_iso_data'),
    (loc+'/ElecIDV2/SingleLepton/electron_SFs.root:ZLL_iso_eff', 'e_iso_mc'),
    (loc+'/ElecIDV2/SingleLepton/electron_SFs.root:embed_iso_eff', 'e_iso_embed'),
    (loc+'/ElecIDV2/em_lo/aiso/electron_SFs.root:data_iso_eff', 'e_aiso_data'),
    (loc+'/ElecIDV2/em_lo/aiso/electron_SFs.root:ZLL_iso_eff', 'e_aiso_mc'),
    (loc+'/ElecIDV2/em_lo/aiso/electron_SFs.root:embed_iso_eff', 'e_aiso_embed'),
    (loc+'/ElecIDV2/SingleLepton/electron_SFs.root:data_trg_eff', 'e_trg_data'),
    (loc+'/ElecIDV2/SingleLepton/electron_SFs.root:ZLL_trg_eff', 'e_trg_mc'),
    (loc+'/ElecIDV2/SingleLepton/electron_SFs.root:embed_trg_eff', 'e_trg_embed'),
    (loc+'/ElecIDV2/Ele24/electron_SFs.root:data_trg_eff', 'e_trg24_data'),
    (loc+'/ElecIDV2/Ele24/electron_SFs.root:ZLL_trg_eff', 'e_trg24_mc'),
    (loc+'/ElecIDV2/Ele24/electron_SFs.root:embed_trg_eff', 'e_trg24_embed'),
    (loc+'/ElecIDV2/Ele24/fromDoubleE/electron_SFs.root:data_trg_eff', 'e_trg24_fromDoubleE_data'),
    (loc+'/ElecIDV2/Ele24/fromDoubleE/electron_SFs.root:ZLL_trg_eff', 'e_trg24_fromDoubleE_mc'),
    (loc+'/ElecIDV2/Ele24/fromDoubleE/electron_SFs.root:embed_trg_eff', 'e_trg24_fromDoubleE_embed'),
]
for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_data', ['e_trg_data', 'e_trg_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_mc', ['e_trg_mc', 'e_trg_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_trg_binned_embed', ['e_trg_embed', 'e_trg_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_iso_binned_data', ['e_iso_data', 'e_aiso_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_iso_binned_mc', ['e_iso_mc', 'e_aiso_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.50],
                                   'e_iso_binned_embed', ['e_iso_embed', 'e_aiso_embed'])

for t in ['data', 'mc']:
    w.factory('expr::e_idiso_%s("@0*@1", e_id_%s, e_iso_%s)' % (t, t, t))
    w.factory('expr::e_idiso_binned_%s("@0*@1", e_id_%s, e_iso_binned_%s)' % (t, t, t))
w.factory('expr::e_idiso_embed("@0*@1", e_id_embed, e_iso_embed)')
w.factory('expr::e_idiso_binned_embed("@0*@1", e_id_embed, e_iso_binned_embed)')

for t in ['trg', 'trg24', 'trg_27_32_35', 'trg24_fromDoubleE', 'trg_binned', 'id', 'iso', 'iso_binned', 'idiso_binned', 'id_pog', 'idiso_pog', 'looseid_pog', 'looseidiso_pog' ]:
    w.factory('expr::e_%s_ratio("@0/@1", e_%s_data, e_%s_mc)' % (t, t, t))
for t in ['trg', 'trg24', 'trg_27_32_35', 'trg_binned', 'id', 'iso', 'iso_binned', 'idiso_binned']:
    w.factory('expr::e_%s_embed_ratio("@0/@1", e_%s_data, e_%s_embed)' % (t, t, t))

# IC electron em trigger SF
loc = 'inputs/2017/ICSF/ElecIDV2/'

histsToWrap = [
    (loc+'em_lo/electron_SFs.root:data_trg_eff', 'e_trg_12_data'),
    (loc+'em_lo/electron_SFs.root:ZLL_trg_eff', 'e_trg_12_mc'),
    (loc+'em_lo/electron_SFs.root:embed_trg_eff', 'e_trg_12_embed'),
    (loc+'em_hi/electron_SFs.root:data_trg_eff', 'e_trg_23_data'),
    (loc+'em_hi/electron_SFs.root:ZLL_trg_eff', 'e_trg_23_mc'),
    (loc+'em_hi/electron_SFs.root:embed_trg_eff', 'e_trg_23_embed'),

    (loc+'em_lo/aiso/electron_SFs.root:data_trg_eff', 'e_trg_12_aiso_data'),
    (loc+'em_lo/aiso/electron_SFs.root:ZLL_trg_eff', 'e_trg_12_aiso_mc'),
    (loc+'em_lo/aiso/electron_SFs.root:embed_trg_eff', 'e_trg_12_aiso_embed'),
    (loc+'em_hi/aiso/electron_SFs.root:data_trg_eff', 'e_trg_23_aiso_data'),
    (loc+'em_hi/aiso/electron_SFs.root:ZLL_trg_eff', 'e_trg_23_aiso_mc'),
    (loc+'em_hi/aiso/electron_SFs.root:embed_trg_eff', 'e_trg_23_aiso_embed')
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

for t in ['trg','trg_binned']:
    w.factory('expr::e_%s_12_ratio("@0/@1", e_%s_12_data, e_%s_12_mc)' % (t, t, t))
    w.factory('expr::e_%s_23_ratio("@0/@1", e_%s_23_data, e_%s_23_mc)' % (t, t, t))

# IC muon em trigger SF

loc = 'inputs/2017/ICSF/'

histsToWrap = [
    (loc+'em_hi/muon_SFs.root:data_trg_eff', 'm_trg_23_data'),
    (loc+'em_hi/muon_SFs.root:ZLL_trg_eff', 'm_trg_23_mc'),
    (loc+'em_hi/muon_SFs.root:embed_trg_eff', 'm_trg_23_embed'),
    (loc+'em_lo/muon_SFs.root:data_trg_eff', 'm_trg_8_data'),
    (loc+'em_lo/muon_SFs.root:ZLL_trg_eff', 'm_trg_8_mc'),
    (loc+'em_lo/muon_SFs.root:embed_trg_eff', 'm_trg_8_embed'),
    (loc+'em_lo/muon_SFs.root:data_iso_eff', 'm_looseiso_data'),
    (loc+'em_lo/muon_SFs.root:ZLL_iso_eff', 'm_looseiso_mc'),
    (loc+'em_lo/muon_SFs.root:embed_iso_eff', 'm_looseiso_embed'),

    (loc+'em_hi/aiso/muon_SFs.root:data_trg_eff', 'm_trg_23_aiso_data'),
    (loc+'em_hi/aiso/muon_SFs.root:ZLL_trg_eff', 'm_trg_23_aiso_mc'),
    (loc+'em_hi/aiso/muon_SFs.root:embed_trg_eff', 'm_trg_23_aiso_embed'),
    (loc+'em_lo/aiso/muon_SFs.root:data_trg_eff', 'm_trg_8_aiso_data'),
    (loc+'em_lo/aiso/muon_SFs.root:ZLL_trg_eff', 'm_trg_8_aiso_mc'),
    (loc+'em_lo/aiso/muon_SFs.root:embed_trg_eff', 'm_trg_8_aiso_embed'),
    (loc+'em_lo/aiso/muon_SFs.root:data_iso_eff', 'm_looseiso_aiso_data'),
    (loc+'em_lo/aiso/muon_SFs.root:ZLL_iso_eff', 'm_looseiso_aiso_mc'),
    (loc+'em_lo/aiso/muon_SFs.root:embed_iso_eff', 'm_looseiso_aiso_embed') 
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

# IC em qcd os/ss weights

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

### Tau Trigger scale factors from Tau POG

loc = 'inputs/2017/TauPOGTriggerSFs/'
tau_trg_file = ROOT.TFile(loc+'tauTriggerEfficiencies2017.root')
w.factory('expr::t_pt_trig("min(max(@0,20),450)" ,t_pt[0])')
tau_id_wps=['vloose','loose','medium','tight','vtight']

for wp in tau_id_wps:
  for dm in ['0','1','10']:
    histsToWrap = [
      (loc+'tauTriggerEfficiencies2017.root:ditau_%sMVAv2_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2017.root:ditau_%sMVAv2_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_ditau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2017.root:ditau_%sMVAv2_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2017.root:ditau_%sMVAv2_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_ditau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2017.root:mutau_%sMVAv2_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2017.root:mutau_%sMVAv2_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_mutau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2017.root:mutau_%sMVAv2_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2017.root:mutau_%sMVAv2_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_mutau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2017.root:etau_%sMVAv2_dm%s_DATA' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2017.root:etau_%sMVAv2_dm%s_MC' % (wp,dm),  't_trg_phieta_%s_etau_dm%s_mc' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2017.root:etau_%sMVAv2_dm%s_DATA_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_data' % (wp,dm)),
      (loc+'tauTriggerEfficiencies2017.root:etau_%sMVAv2_dm%s_MC_AVG' % (wp,dm),  't_trg_ave_phieta_%s_etau_dm%s_mc' % (wp,dm))
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

loc='inputs/2017/TauPOGIDSFs/'

histsToWrap = [
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2017.root:VLoose', 't_id_dm_vloose'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2017.root:Loose',  't_id_dm_loose'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2017.root:Medium', 't_id_dm_medium'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2017.root:Tight',  't_id_dm_tight'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2017.root:VTight', 't_id_dm_vtight'),
  (loc+'/TauID_SF_dm_MVAoldDM2017v2_2017.root:VVTight', 't_id_dm_vvtight')
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

sf_funcs['vloose'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.7680031+ ( x > 25 && x <=30)*0.8770162+ ( x > 30 && x <=35)*0.8864078+ ( x > 35 && x <=40)*0.8575877+ (x > 40)*0.908802967687'
sf_funcs['vloose_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8890281+ ( x > 25 && x <=30)*0.9469252+ ( x > 30 && x <=35)*0.9380708+ ( x > 35 && x <=40)*0.9044377+ (x > 40 && x <= 500)*0.949084749706+ (x > 500 && x <= 1000)*(0.908802967687 +0.0402817820196*(x/500.))+ (x > 1000)*(0.908802967687 + 0.0805635640393)'
sf_funcs['vloose_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.6469781+ ( x > 25 && x <=30)*0.8071072+ ( x > 30 && x <=35)*0.8347448+ ( x > 35 && x <=40)*0.8107377+ (x > 40 && x <= 500)*0.861070663387+ (x > 500 && x <= 1000)*(0.908802967687 -0.0477323042994*(x/500.))+ (x > 1000)*(0.908802967687 - 0.0954646085989)'
sf_funcs['loose'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8666298+ ( x > 25 && x <=30)*0.8612201+ ( x > 30 && x <=35)*0.8722173+ ( x > 35 && x <=40)*0.8877534+ (x > 40)*0.94820719806'
sf_funcs['loose_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9511748+ ( x > 25 && x <=30)*0.9251961+ ( x > 30 && x <=35)*0.9088133+ ( x > 35 && x <=40)*0.9270814+ (x > 40 && x <= 500)*0.986524358469+ (x > 500 && x <= 1000)*(0.94820719806 +0.0383171604096*(x/500.))+ (x > 1000)*(0.94820719806 + 0.0766343208191)'
sf_funcs['loose_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.7820848+ ( x > 25 && x <=30)*0.7972441+ ( x > 30 && x <=35)*0.8356213+ ( x > 35 && x <=40)*0.8484254+ (x > 40 && x <= 500)*0.899402790402+ (x > 500 && x <= 1000)*(0.94820719806 -0.0488044076576*(x/500.))+ (x > 1000)*(0.94820719806 - 0.0976088153153)'
sf_funcs['medium'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.91902+ ( x > 25 && x <=30)*0.8435835+ ( x > 30 && x <=35)*0.8852934+ ( x > 35 && x <=40)*0.8848557+ (x > 40)*0.906817421521'
sf_funcs['medium_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.984677+ ( x > 25 && x <=30)*0.8896395+ ( x > 30 && x <=35)*0.9164874+ ( x > 35 && x <=40)*0.9181077+ (x > 40 && x <= 500)*0.951709411669+ (x > 500 && x <= 1000)*(0.906817421521 +0.0448919901481*(x/500.))+ (x > 1000)*(0.906817421521 + 0.0897839802962)'
sf_funcs['medium_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.853363+ ( x > 25 && x <=30)*0.7975275+ ( x > 30 && x <=35)*0.8540994+ ( x > 35 && x <=40)*0.8516037+ (x > 40 && x <= 500)*0.860601947029+ (x > 500 && x <= 1000)*(0.906817421521 -0.0462154744917*(x/500.))+ (x > 1000)*(0.906817421521 - 0.0924309489835)'
sf_funcs['tight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9368875+ ( x > 25 && x <=30)*0.8456867+ ( x > 30 && x <=35)*0.8688679+ ( x > 35 && x <=40)*0.8719202+ (x > 40)*0.8984880855'
sf_funcs['tight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9935635+ ( x > 25 && x <=30)*0.8866707+ ( x > 30 && x <=35)*0.8973459+ ( x > 35 && x <=40)*0.9072442+ (x > 40 && x <= 500)*0.935249492999+ (x > 500 && x <= 1000)*(0.8984880855 +0.0367614074987*(x/500.))+ (x > 1000)*(0.8984880855 + 0.0735228149975)'
sf_funcs['tight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8802115+ ( x > 25 && x <=30)*0.8047027+ ( x > 30 && x <=35)*0.8403899+ ( x > 35 && x <=40)*0.8365962+ (x > 40 && x <= 500)*0.859400181792+ (x > 500 && x <= 1000)*(0.8984880855 -0.0390879037079*(x/500.))+ (x > 1000)*(0.8984880855 - 0.0781758074157)'
sf_funcs['vtight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9230896+ ( x > 25 && x <=30)*0.8675593+ ( x > 30 && x <=35)*0.8532677+ ( x > 35 && x <=40)*0.8516027+ (x > 40)*0.861147095013'
sf_funcs['VTight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9710176+ ( x > 25 && x <=30)*0.8988653+ ( x > 30 && x <=35)*0.8781697+ ( x > 35 && x <=40)*0.8848917+ (x > 40 && x <= 500)*0.900692367516+ (x > 500 && x <= 1000)*(0.861147095013 +0.0395452725033*(x/500.))+ (x > 1000)*(0.861147095013 + 0.0790905450065)'
sf_funcs['vtight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8751616+ ( x > 25 && x <=30)*0.8362533+ ( x > 30 && x <=35)*0.8283657+ ( x > 35 && x <=40)*0.8183137+ (x > 40 && x <= 500)*0.821314916483+ (x > 500 && x <= 1000)*(0.861147095013 -0.0398321785294*(x/500.))+ (x > 1000)*(0.861147095013 - 0.0796643570588)'
sf_funcs['vvtight'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8824266+ ( x > 25 && x <=30)*0.8587208+ ( x > 30 && x <=35)*0.8414515+ ( x > 35 && x <=40)*0.8518679+ (x > 40)*0.87882485674'
sf_funcs['vvtight_up'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.9222016+ ( x > 25 && x <=30)*0.8868838+ ( x > 30 && x <=35)*0.8645885+ ( x > 35 && x <=40)*0.9197789+ (x > 40 && x <= 500)*0.926167548222+ (x > 500 && x <= 1000)*(0.87882485674 +0.0473426914828*(x/500.))+ (x > 1000)*(0.87882485674 + 0.0946853829656)'
sf_funcs['vvtight_down'] = '(x<=20)*0+ ( x > 20 && x <=25)*0.8426516+ ( x > 25 && x <=30)*0.8305578+ ( x > 30 && x <=35)*0.8183145+ ( x > 35 && x <=40)*0.7839569+ (x > 40 && x <= 500)*0.829600880712+ (x > 500 && x <= 1000)*(0.87882485674 -0.049223976028*(x/500.))+ (x > 1000)*(0.87882485674 - 0.098447952056)'

import re
for x in sf_funcs:
  func = re.sub('x','@0',sf_funcs[x])
  w.factory('expr::t_id_pt_%s("%s",t_pt[0])' % (x, func))

# LO DYJetsToLL Z mass vs pT correction
histsToWrap = [
    ('inputs/2017/KIT/zpt_reweighting/zptm_weights_2017_kit.root:zptmass_histo', 'zptmass_weight_nom')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['z_gen_mass', 'z_gen_pt'],
                          GetFromTFile(task[0]), name=task[1])

w.importClassCode('CrystalBallEfficiency')

#w.Print()
w.writeToFile('htt_scalefactors_v17_7.root')
w.Delete()
