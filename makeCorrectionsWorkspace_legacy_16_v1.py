#!/usr/bin/env python
import ROOT
import imp
import json
from array import array
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

# Hadronic tau trigger efficiencies
with open('inputs/2016/triggerSF-Moriond17/di-tau/fitresults_tt_moriond2017.json') as jsonfile:
    pars = json.load(jsonfile)
    for tautype in ['genuine', 'fake']:
        for iso in ['VLooseIso', 'LooseIso', 'MediumIso', 'TightIso', 'VTightIso', 'VVTightIso']:
            for dm in ['dm0', 'dm1', 'dm10']:
                label = '%s_%s_%s' % (tautype, iso, dm)
                x = pars['data_%s' % (label)]
                w.factory('CrystalBallEfficiency::t_%s_tt_data(t_pt[0],%g,%g,%g,%g,%g)' % (
                    label, x['m_{0}'], x['sigma'], x['alpha'], x['n'], x['norm']
                ))

                x = pars['mc_%s' % (label)]
                w.factory('CrystalBallEfficiency::t_%s_tt_mc(t_pt[0],%g,%g,%g,%g,%g)' % (
                    label, x['m_{0}'], x['sigma'], x['alpha'], x['n'], x['norm']
                ))
            label = '%s_%s' % (tautype, iso)
            wsptools.MakeBinnedCategoryFuncMap(w, 't_dm', [-0.5, 0.5, 9.5, 10.5],
                                               't_%s_tt_data' % label, ['t_%s_dm0_tt_data' % label, 't_%s_dm1_tt_data' % label, 't_%s_dm10_tt_data' % label])
            wsptools.MakeBinnedCategoryFuncMap(w, 't_dm', [-0.5, 0.5, 9.5, 10.5],
                                               't_%s_tt_mc' % label, ['t_%s_dm0_tt_mc' % label, 't_%s_dm1_tt_mc' % label, 't_%s_dm10_tt_mc' % label])
            w.factory('expr::t_%s_tt_ratio("@0/@1", t_%s_tt_data, t_%s_tt_mc)' %
                      (label, label, label))

# EGamma tracking SFs from https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaRunIIRecommendations#Electron_Scale_Factors
loc = 'inputs/2016/EGammaPOG'

histsToWrap = [
    (loc+'/EGM2D_BtoH_low_RecoSF_Legacy2016.root:EGamma_EffData2D',         'e_trk_ST20_data'),
    (loc+'/EGM2D_BtoH_low_RecoSF_Legacy2016.root:EGamma_EffMC2D',           'e_trk_ST20_mc'),
    (loc+'/EGM2D_BtoH_low_RecoSF_Legacy2016.root:EGamma_SF2D',              'e_trk_ST20_ratio'),
    (loc+'/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root:EGamma_EffData2D',         'e_trk_GT20_data'),
    (loc+'/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root:EGamma_EffMC2D',           'e_trk_GT20_mc'),
    (loc+'/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root:EGamma_SF2D',              'e_trk_GT20_ratio')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['e_eta', 'e_pt'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_pt', [10., 20., 500.],
                                   'e_trk_data', ['e_trk_ST20_data', 'e_trk_GT20_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_pt', [10., 20., 500.],
                                   'e_trk_mc', ['e_trk_ST20_mc', 'e_trk_GT20_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_pt', [10., 20., 500.],
                                   'e_trk_ratio', ['e_trk_ST20_ratio', 'e_trk_GT20_ratio'])

### KIT electron/muon tag and probe results
# The trigger refers to OR(IsoMu22, IsoTkMu22, IsoMu22_eta2p1, IsoTkMu22_eta2p1)
loc = 'inputs/2016/KIT/legacy_16_v1'

histsToWrap = [
    (loc+'/ZmmTP_Data_sm_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',                    'm_id_data'),
    (loc+'/ZmmTP_DYJetsToLL_sm_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',              'm_id_mc'),
    (loc+'/ZmmTP_Embedding_sm_Fits_ID_pt_eta_bins.root:ID_pt_eta_bins',              'm_id_emb'),
    (loc+'/ZmmTP_Data_sm_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                        'm_iso_data'),
    (loc+'/ZmmTP_DYJetsToLL_sm_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                  'm_iso_mc'),
    (loc+'/ZmmTP_Embedding_sm_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                  'm_iso_emb'),
    (loc+'/ZmmTP_Data_sm_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',                    'm_aiso1_data'),
    (loc+'/ZmmTP_DYJetsToLL_sm_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',              'm_aiso1_mc'),
    (loc+'/ZmmTP_Embedding_sm_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',              'm_aiso1_emb'),
    (loc+'/ZmmTP_Data_sm_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',                    'm_aiso2_data'),
    (loc+'/ZmmTP_DYJetsToLL_sm_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',              'm_aiso2_mc'),
    (loc+'/ZmmTP_Embedding_sm_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',              'm_aiso2_emb'),
    (loc+'/ZmmTP_Data_sm_Fits_Trg_IsoMu22_Iso_pt_eta_bins.root:Trg_IsoMu22_Iso_pt_eta_bins',                'm_trg_data'),
    (loc+'/ZmmTP_DYJetsToLL_sm_Fits_Trg_IsoMu22_Iso_pt_eta_bins.root:Trg_IsoMu22_Iso_pt_eta_bins',                'm_trg_mc'),
    (loc+'/ZmmTP_Embedding_sm_Fits_Trg_IsoMu22_Iso_pt_eta_bins.root:Trg_IsoMu22_Iso_pt_eta_bins',                'm_trg_emb'),
    (loc+'/ZmmTP_Data_sm_Fits_Trg_IsoMu22_AIso1_pt_bins_inc_eta.root:Trg_IsoMu22_AIso1_pt_bins_inc_eta',    'm_trg_aiso1_data'),
    (loc+'/ZmmTP_DYJetsToLL_sm_Fits_Trg_IsoMu22_AIso1_pt_bins_inc_eta.root:Trg_IsoMu22_AIso1_pt_bins_inc_eta',    'm_trg_aiso1_mc'),
    (loc+'/ZmmTP_Embedding_sm_Fits_Trg_IsoMu22_AIso1_pt_bins_inc_eta.root:Trg_IsoMu22_AIso1_pt_bins_inc_eta',    'm_trg_aiso1_emb'),
    (loc+'/ZmmTP_Data_sm_Fits_Trg_IsoMu22_AIso2_pt_bins_inc_eta.root:Trg_IsoMu22_AIso2_pt_bins_inc_eta',    'm_trg_aiso2_data'),
    (loc+'/ZmmTP_DYJetsToLL_sm_Fits_Trg_IsoMu22_AIso2_pt_bins_inc_eta.root:Trg_IsoMu22_AIso2_pt_bins_inc_eta',    'm_trg_aiso2_mc'),
    (loc+'/ZmmTP_Embedding_sm_Fits_Trg_IsoMu22_AIso2_pt_bins_inc_eta.root:Trg_IsoMu22_AIso2_pt_bins_inc_eta',    'm_trg_aiso2_emb')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])


wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_data', ['m_iso_data', 'm_aiso1_data', 'm_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_mc', ['m_iso_mc', 'm_aiso1_mc', 'm_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_iso_binned_emb', ['m_iso_emb', 'm_aiso1_emb', 'm_aiso2_emb'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_data', ['m_trg_data', 'm_trg_aiso1_data', 'm_trg_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_mc', ['m_trg_mc', 'm_trg_aiso1_mc', 'm_trg_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.25, 0.50],
                                   'm_trg_binned_emb', ['m_trg_emb', 'm_trg_aiso1_emb', 'm_trg_aiso2_emb'])


for t in ['id', 'iso', 'aiso1', 'aiso2', 'iso_binned', 'trg', 'trg_aiso1', 'trg_aiso2', 'trg_binned']:
    w.factory('expr::m_%s_ratio("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))

for t in ['id', 'iso', 'aiso1', 'aiso2', 'iso_binned', 'trg', 'trg_aiso1', 'trg_aiso2', 'trg_binned']:
    w.factory('expr::m_%s_ratio_emb("@0/@1", m_%s_data, m_%s_emb)' % (t, t, t))

for t in ['data', 'mc', 'emb', 'ratio', 'ratio_emb']:
    w.factory('expr::m_idiso_%s("@0*@1", m_id_%s, m_iso_%s)' % (t, t, t))

loc = 'inputs/2016/KIT/legacy_16_v1'

histsToWrap = [
    (loc+'/ZeeTP_Data_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',                          'e_id80_data'),
    (loc+'/ZeeTP_DYJetsToLL_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',                    'e_id80_mc'),
    (loc+'/ZeeTP_Embedding_Fits_ID80_pt_eta_bins.root:ID80_pt_eta_bins',                    'e_id80_emb'),
    (loc+'/ZeeTP_Data_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                          'e_id90_data'),
    (loc+'/ZeeTP_DYJetsToLL_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                    'e_id90_mc'),
    (loc+'/ZeeTP_Embedding_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                    'e_id90_emb'),
    (loc+'/ZeeTP_Data_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                          'e_id_data'),
    (loc+'/ZeeTP_DYJetsToLL_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                    'e_id_mc'),
    (loc+'/ZeeTP_Embedding_Fits_ID90_pt_eta_bins.root:ID90_pt_eta_bins',                    'e_id_emb'),
    (loc+'/ZeeTP_Data_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                        'e_iso_data'),
    (loc+'/ZeeTP_DYJetsToLL_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                  'e_iso_mc'),
    (loc+'/ZeeTP_Embedding_Fits_Iso_pt_eta_bins.root:Iso_pt_eta_bins',                  'e_iso_emb'),
    (loc+'/ZeeTP_Data_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',                    'e_aiso1_data'),
    (loc+'/ZeeTP_DYJetsToLL_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',              'e_aiso1_mc'),
    (loc+'/ZeeTP_Embedding_Fits_AIso1_pt_eta_bins.root:AIso1_pt_eta_bins',              'e_aiso1_emb'),
    (loc+'/ZeeTP_Data_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',                    'e_aiso2_data'),
    (loc+'/ZeeTP_DYJetsToLL_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',              'e_aiso2_mc'),
    (loc+'/ZeeTP_Embedding_Fits_AIso2_pt_eta_bins.root:AIso2_pt_eta_bins',              'e_aiso2_emb'),
    (loc+'/ZeeTP_Data_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',                'e_trg_data'),
    (loc+'/ZeeTP_DYJetsToLL_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',                'e_trg_mc'),
    (loc+'/ZeeTP_Embedding_Fits_Trg_Iso_pt_eta_bins.root:Trg_Iso_pt_eta_bins',                'e_trg_emb'),
    (loc+'/ZeeTP_Data_Fits_Trg_AIso1_pt_bins_inc_eta.root:Trg_AIso1_pt_bins_inc_eta',    'e_trg_aiso1_data'),
    (loc+'/ZeeTP_DYJetsToLL_Fits_Trg_AIso1_pt_bins_inc_eta.root:Trg_AIso1_pt_bins_inc_eta',    'e_trg_aiso1_mc'),
    (loc+'/ZeeTP_Embedding_Fits_Trg_AIso1_pt_bins_inc_eta.root:Trg_AIso1_pt_bins_inc_eta',    'e_trg_aiso1_emb'),
    (loc+'/ZeeTP_Data_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',    'e_trg_aiso2_data'),
    (loc+'/ZeeTP_DYJetsToLL_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',    'e_trg_aiso2_mc'),
    (loc+'/ZeeTP_Embedding_Fits_Trg_AIso2_pt_bins_inc_eta.root:Trg_AIso2_pt_bins_inc_eta',    'e_trg_aiso2_emb')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])


wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.20, 0.50],
                                   'e_iso_binned_data', ['e_iso_data', 'e_aiso1_data', 'e_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.20, 0.50],
                                   'e_iso_binned_mc', ['e_iso_mc', 'e_aiso1_mc', 'e_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.20, 0.50],
                                   'e_iso_binned_emb', ['e_iso_emb', 'e_aiso1_emb', 'e_aiso2_emb'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.20, 0.50],
                                   'e_trg_binned_data', ['e_trg_data', 'e_trg_aiso1_data', 'e_trg_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.20, 0.50],
                                   'e_trg_binned_mc', ['e_trg_mc', 'e_trg_aiso1_mc', 'e_trg_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.20, 0.50],
                                   'e_trg_binned_emb', ['e_trg_emb', 'e_trg_aiso1_emb', 'e_trg_aiso2_emb'])


for t in ['id', 'iso', 'aiso1', 'aiso2', 'iso_binned', 'trg', 'trg_aiso1', 'trg_aiso2', 'trg_binned']:
    w.factory('expr::e_%s_ratio("@0/@1", e_%s_data, e_%s_mc)' % (t, t, t))

for t in ['id', 'iso', 'aiso1', 'aiso2', 'iso_binned', 'trg', 'trg_aiso1', 'trg_aiso2', 'trg_binned']:
    w.factory('expr::e_%s_ratio_emb("@0/@1", e_%s_data, e_%s_emb)' % (t, t, t))

for t in ['data', 'mc', 'emb', 'ratio', 'ratio_emb']:
    w.factory('expr::e_idiso_%s("@0*@1", e_id_%s, e_iso_%s)' % (t, t, t))

# addressing muon selection for embedding:
loc = 'inputs/2016/KIT' # so far not remeasured for legacy
Sel_histsToWrap = [
    (loc+'/ZmmTP_Data_Fits_muon_Selection_EmbeddedID.root:muon_Selection_EmbeddedID',                    'm_sel_idEmb_data'),
    (loc+'/ZmmTP_Data_Fits_muon_Selection_VVLIso.root:muon_Selection_VVLIso',                    'm_sel_vvliso_data')
]
for task in Sel_histsToWrap:
    wsptools.SafeWrapHist(w, ['gt_pt', 'expr::gt_abs_eta("TMath::Abs(@0)",gt_eta[0])'],
            GetFromTFile(task[0]), name=task[1])
for t in ['sel_idEmb','sel_vvliso']:
    w.factory('expr::m_%s_ratio("(1.0)/@0", m_%s_data)' % (t, t))


# DESY electron/muon tag and probe results
# Muons
loc = 'inputs/2016/LeptonEfficiencies'

desyHistsToWrap = [
    (loc+'/Muon/Run2016_legacy/Muon_Run2016_legacy_IdIso.root',
     'MC',   'm_idiso_desy_mc'),
    (loc+'/Muon/Run2016_legacy/Muon_Run2016_legacy_IdIso.root',
     'Data', 'm_idiso_desy_data'),
    (loc+'/Muon/Run2016_legacy/Muon_Run2016_legacy_IsoMu22.root',
     'MC',   'm_trgIsoMu22_desy_mc'),
    (loc+'/Muon/Run2016_legacy/Muon_Run2016_legacy_IsoMu22.root',
     'Data', 'm_trgIsoMu22_desy_data'),
    (loc+'/Muon/Run2016_legacy/Muon_Run2016_legacy_IsoMu24.root',
     'MC',   'm_trgIsoMu24_desy_mc'),
    (loc+'/Muon/Run2016_legacy/Muon_Run2016_legacy_IsoMu24.root',
     'Data', 'm_trgIsoMu24_desy_data'),

    # old crosstrigger weights for now
    (loc+'/Muon/Run2016BtoH/Muon_Mu19leg_2016BtoH_eff.root',
     'MC', 'm_trgMu19leg_eta2p1_desy_mc'),
    (loc+'/Muon/Run2016BtoH/Muon_Mu19leg_2016BtoH_eff.root',
     'Data', 'm_trgMu19leg_eta2p1_desy_data'),
]

for task in desyHistsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])
for t in ['idiso_desy', 'trgIsoMu22_desy', 'trgIsoMu24_desy', 'trgMu19leg_eta2p1_desy']:
    w.factory('expr::m_%s_ratio("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))

# Electrons
desyHistsToWrap = [
    (loc+'/Electron/Run2016_legacy/Electron_Run2016_legacy_IdIso.root',
     'MC',   'e_idiso_desy_mc'),
    (loc+'/Electron/Run2016_legacy/Electron_Run2016_legacy_IdIso.root',
     'Data', 'e_idiso_desy_data'),
    (loc+'/Electron/Run2016_legacy/Electron_Run2016_legacy_Ele25.root',
     'MC',   'e_trgEle25_desy_mc'),
    (loc+'/Electron/Run2016_legacy/Electron_Run2016_legacy_Ele25.root',
     'Data', 'e_trgEle25_desy_data')
]
for task in desyHistsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])

for t in ['idiso_desy', 'trgEle25_desy']:
    w.factory('expr::e_%s_ratio("@0/@1", e_%s_data, e_%s_mc)' % (t, t, t))


### IC electron/muon embedded scale factors
loc_ic = 'inputs/2016/ICSF/'

histsToWrap = [
    (loc_ic+'MuMu8/muon_SFs.root:trg_data', 'm_sel_trg8_1_data'),
    (loc_ic+'MuMu17/muon_SFs.root:trg_data', 'm_sel_trg17_1_data')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['gt1_pt', 'expr::gt1_abs_eta("TMath::Abs(@0)",gt1_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

histsToWrap = [
    (loc_ic+'MuMu8/muon_SFs.root:trg_data', 'm_sel_trg8_2_data'),
    (loc_ic+'MuMu17/muon_SFs.root:trg_data', 'm_sel_trg17_2_data')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['gt2_pt', 'expr::gt2_abs_eta("TMath::Abs(@0)",gt2_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])
    
    w.factory('expr::m_sel_trg_data("0.935*(@0*@3+@1*@2-@1*@3)", m_sel_trg8_1_data, m_sel_trg17_1_data, m_sel_trg8_2_data, m_sel_trg17_2_data)')
w.factory('expr::m_sel_trg_ratio("min(1./@0,2)", m_sel_trg_data)')

# LO DYJetsToLL Z mass vs pT correction
histsToWrap = [
    ('inputs/2016/KIT/zpt_reweighting/zptm_weights_2016_kit.root:zptmass_histo', 'zptmass_weight_nom')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['z_gen_mass', 'z_gen_pt'],
                          GetFromTFile(task[0]), name=task[1])
    

w.importClassCode('CrystalBallEfficiency')

w.Print()
w.writeToFile('output/htt_scalefactors_legacy_v16_1.root')
w.Delete()
