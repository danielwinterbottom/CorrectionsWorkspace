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


### IC electron/muon tag and probe results
loc = 'inputs/ICSF/'

histsToWrap = [
    (loc+'SingleLepton/muon_SFs.root:idiso_data', 'm_idiso_data'),
    (loc+'SingleLepton/muon_SFs.root:idiso_mc', 'm_idiso_mc'),
    (loc+'SingleLepton/muon_SFs.root:idiso_embed', 'm_idiso_embed'),
    (loc+'SingleLepton/aiso1/muon_SFs.root:idiso_data', 'm_idiso_aiso1_data'),
    (loc+'SingleLepton/aiso1/muon_SFs.root:idiso_mc', 'm_idiso_aiso1_mc'),
    (loc+'SingleLepton/aiso1/muon_SFs.root:idiso_embed', 'm_idiso_aiso1_embed'),
    (loc+'SingleLepton/aiso2/muon_SFs.root:idiso_data', 'm_idiso_aiso2_data'),
    (loc+'SingleLepton/aiso2/muon_SFs.root:idiso_mc', 'm_idiso_aiso2_mc'),
    (loc+'SingleLepton/aiso2/muon_SFs.root:idiso_embed', 'm_idiso_aiso2_embed'),
    (loc+'El12Mu23/muon_SFs.root:idiso_data', 'm_idiso_em_data'),
    (loc+'El12Mu23/muon_SFs.root:idiso_mc', 'm_idiso_em_mc'),
    (loc+'El12Mu23/muon_SFs.root:idiso_embed', 'm_idiso_em_embed'),
    (loc+'El12Mu23/aiso1/muon_SFs.root:idiso_data', 'm_idiso_aiso1_em_data'),
    (loc+'El12Mu23/aiso1/muon_SFs.root:idiso_mc', 'm_idiso_aiso1_em_mc'),
    (loc+'El12Mu23/aiso1/muon_SFs.root:idiso_embed', 'm_idiso_aiso1_em_embed'),
    (loc+'El12Mu23/aiso2/muon_SFs.root:idiso_data', 'm_idiso_aiso2_em_data'),
    (loc+'El12Mu23/aiso2/muon_SFs.root:idiso_mc', 'm_idiso_aiso2_em_mc'),
    (loc+'El12Mu23/aiso2/muon_SFs.root:idiso_embed', 'm_idiso_aiso2_em_embed'),
    (loc+'SingleLepton/muon_SFs.root:trg_data', 'm_trg22_data'),
    (loc+'SingleLepton/muon_SFs.root:trg_mc', 'm_trg22_mc'),
    (loc+'SingleLepton/muon_SFs.root:trg_embed', 'm_trg22_embed'),
    (loc+'SingleLepton/aiso1/muon_SFs.root:trg_data', 'm_trg22_aiso1_data'),
    (loc+'SingleLepton/aiso1/muon_SFs.root:trg_mc', 'm_trg22_aiso1_mc'),
    (loc+'SingleLepton/aiso1/muon_SFs.root:trg_embed', 'm_trg22_aiso1_embed'),
    (loc+'SingleLepton/aiso2/muon_SFs.root:trg_data', 'm_trg22_aiso2_data'),
    (loc+'SingleLepton/aiso2/muon_SFs.root:trg_mc', 'm_trg22_aiso2_mc'),
    (loc+'SingleLepton/aiso2/muon_SFs.root:trg_embed', 'm_trg22_aiso2_embed'),
    (loc+'MuTau/muon_SFs.root:trg_data', 'm_trg19_data'),
    (loc+'MuTau/muon_SFs.root:trg_mc', 'm_trg19_mc'),
    (loc+'MuTau/muon_SFs.root:trg_embed', 'm_trg19_embed'),
    (loc+'MuTau/aiso1/muon_SFs.root:trg_data', 'm_trg19_aiso1_data'),
    (loc+'MuTau/aiso1/muon_SFs.root:trg_mc', 'm_trg19_aiso1_mc'),
    (loc+'MuTau/aiso1/muon_SFs.root:trg_embed', 'm_trg19_aiso1_embed'),
    (loc+'MuTau/aiso2/muon_SFs.root:trg_data', 'm_trg19_aiso2_data'),
    (loc+'MuTau/aiso2/muon_SFs.root:trg_mc', 'm_trg19_aiso2_mc'),
    (loc+'MuTau/aiso2/muon_SFs.root:trg_embed', 'm_trg19_aiso2_embed'),
    (loc+'El23Mu8/muon_SFs.root:trg_data', 'm_trg8_data'),
    (loc+'El23Mu8/muon_SFs.root:trg_mc', 'm_trg8_mc'),
    (loc+'El23Mu8/muon_SFs.root:trg_embed', 'm_trg8_embed'),
    (loc+'El23Mu8/aiso1/muon_SFs.root:trg_data', 'm_trg8_aiso1_data'),
    (loc+'El23Mu8/aiso1/muon_SFs.root:trg_mc', 'm_trg8_aiso1_mc'),
    (loc+'El23Mu8/aiso1/muon_SFs.root:trg_embed', 'm_trg8_aiso1_embed'),
    (loc+'El23Mu8/aiso2/muon_SFs.root:trg_data', 'm_trg8_aiso2_data'),
    (loc+'El23Mu8/aiso2/muon_SFs.root:trg_mc', 'm_trg8_aiso2_mc'),
    (loc+'El23Mu8/aiso2/muon_SFs.root:trg_embed', 'm_trg8_aiso2_embed'),
    (loc+'El12Mu23/muon_SFs.root:trg_data', 'm_trg23_data'),
    (loc+'El12Mu23/muon_SFs.root:trg_mc', 'm_trg23_mc'),
    (loc+'El12Mu23/muon_SFs.root:trg_embed', 'm_trg23_embed'),
    (loc+'El12Mu23/aiso1/muon_SFs.root:trg_data', 'm_trg23_aiso1_data'),
    (loc+'El12Mu23/aiso1/muon_SFs.root:trg_mc', 'm_trg23_aiso1_mc'),
    (loc+'El12Mu23/aiso1/muon_SFs.root:trg_embed', 'm_trg23_aiso1_embed'),
    (loc+'El12Mu23/aiso2/muon_SFs.root:trg_data', 'm_trg23_aiso2_data'),
    (loc+'El12Mu23/aiso2/muon_SFs.root:trg_mc', 'm_trg23_aiso2_mc'),
    (loc+'El12Mu23/aiso2/muon_SFs.root:trg_embed', 'm_trg23_aiso2_embed')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['m_pt', 'expr::m_abs_eta("TMath::Abs(@0)",m_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_idiso_binned_data', ['m_idiso_data', 'm_idiso_aiso1_data', 'm_idiso_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_idiso_binned_mc', ['m_idiso_mc', 'm_idiso_aiso1_mc', 'm_idiso_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_idiso_binned_embed', ['m_idiso_embed', 'm_idiso_aiso1_embed', 'm_idiso_aiso2_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.20, 0.30, 0.50],
                                   'm_idiso_binned_em_data', ['m_idiso_em_data', 'm_idiso_aiso1_em_data', 'm_idiso_aiso2_em_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_idiso_binned_em_mc', ['m_idiso_em_mc', 'm_idiso_aiso1_em_mc', 'm_idiso_aiso2_em_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_idiso_binned_em_embed', ['m_idiso_em_embed', 'm_idiso_aiso1_em_embed', 'm_idiso_aiso2_em_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_trg22_binned_data', ['m_trg22_data', 'm_trg22_aiso1_data', 'm_trg22_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_trg22_binned_mc', ['m_trg22_mc', 'm_trg22_aiso1_mc', 'm_trg22_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_trg22_binned_embed', ['m_trg22_embed', 'm_trg22_aiso1_embed', 'm_trg22_aiso2_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_trg19_binned_data', ['m_trg19_data', 'm_trg19_aiso1_data', 'm_trg19_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_trg19_binned_mc', ['m_trg19_mc', 'm_trg19_aiso1_mc', 'm_trg19_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.15, 0.30, 0.50],
                                   'm_trg19_binned_embed', ['m_trg19_embed', 'm_trg19_aiso1_embed', 'm_trg19_aiso2_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.20, 0.30, 0.50],
                                   'm_trg8_binned_data', ['m_trg8_data', 'm_trg8_aiso1_data', 'm_trg8_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.20, 0.30, 0.50],
                                   'm_trg8_binned_mc', ['m_trg8_mc', 'm_trg8_aiso1_mc', 'm_trg8_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.20, 0.30, 0.50],
                                   'm_trg8_binned_embed', ['m_trg8_embed', 'm_trg8_aiso1_embed', 'm_trg8_aiso2_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.20, 0.30, 0.50],
                                   'm_trg23_binned_data', ['m_trg23_data', 'm_trg23_aiso1_data', 'm_trg23_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.20, 0.30, 0.50],
                                   'm_trg23_binned_mc', ['m_trg23_mc', 'm_trg23_aiso1_mc', 'm_trg23_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'm_iso', [0., 0.20, 0.30, 0.50],
                                   'm_trg23_binned_embed', ['m_trg23_embed', 'm_trg23_aiso1_embed', 'm_trg23_aiso2_embed'])


for t in ['idiso', 'idiso_aiso1', 'idiso_aiso2', 'idiso_binned', 'idiso_em', 'idiso_aiso1_em', 'idiso_aiso2_em', 'idiso_binned_em', 'trg22', 'trg22_aiso1', 'trg22_aiso2', 'trg22_binned', 'trg19', 'trg19_aiso1', 'trg19_aiso2', 'trg19_binned', 'trg8', 'trg8_aiso1', 'trg8_aiso2', 'trg8_binned', 'trg23', 'trg23_aiso1', 'trg23_aiso2', 'trg23_binned']:
    w.factory('expr::m_%s_ratio("@0/@1", m_%s_data, m_%s_mc)' % (t, t, t))
    w.factory('expr::m_%s_embed_ratio("@0/@1", m_%s_data, m_%s_embed)' % (t, t, t))

loc = 'inputs/ICSF/'

histsToWrap = [
    (loc+'SingleLepton/electron_SFs.root:idiso_data', 'e_idiso_data'),
    (loc+'SingleLepton/electron_SFs.root:idiso_mc', 'e_idiso_mc'),
    (loc+'SingleLepton/electron_SFs.root:idiso_embed', 'e_idiso_embed'),
    (loc+'SingleLepton/aiso1/electron_SFs.root:idiso_data', 'e_idiso_aiso1_data'),
    (loc+'SingleLepton/aiso1/electron_SFs.root:idiso_mc', 'e_idiso_aiso1_mc'),
    (loc+'SingleLepton/aiso1/electron_SFs.root:idiso_embed', 'e_idiso_aiso1_embed'),
    (loc+'SingleLepton/aiso2/electron_SFs.root:idiso_data', 'e_idiso_aiso2_data'),
    (loc+'SingleLepton/aiso2/electron_SFs.root:idiso_mc', 'e_idiso_aiso2_mc'),
    (loc+'SingleLepton/aiso2/electron_SFs.root:idiso_embed', 'e_idiso_aiso2_embed'),
    (loc+'El12Mu23/electron_SFs.root:idiso_data', 'e_idiso_em_data'),
    (loc+'El12Mu23/electron_SFs.root:idiso_mc', 'e_idiso_em_mc'),
    (loc+'El12Mu23/electron_SFs.root:idiso_embed', 'e_idiso_em_embed'),
    (loc+'El12Mu23/aiso1/electron_SFs.root:idiso_data', 'e_idiso_aiso1_em_data'),
    (loc+'El12Mu23/aiso1/electron_SFs.root:idiso_mc', 'e_idiso_aiso1_em_mc'),
    (loc+'El12Mu23/aiso1/electron_SFs.root:idiso_embed', 'e_idiso_aiso1_em_embed'),
    (loc+'El12Mu23/aiso2/electron_SFs.root:idiso_data', 'e_idiso_aiso2_em_data'),
    (loc+'El12Mu23/aiso2/electron_SFs.root:idiso_mc', 'e_idiso_aiso2_em_mc'),
    (loc+'El12Mu23/aiso2/electron_SFs.root:idiso_embed', 'e_idiso_aiso2_em_embed'),
    (loc+'SingleLepton/electron_SFs.root:trg_data', 'e_trg25_data'),
    (loc+'SingleLepton/electron_SFs.root:trg_mc', 'e_trg25_mc'),
    (loc+'SingleLepton/electron_SFs.root:trg_embed', 'e_trg25_embed'),
    (loc+'SingleLepton/aiso1/electron_SFs.root:trg_data', 'e_trg25_aiso1_data'),
    (loc+'SingleLepton/aiso1/electron_SFs.root:trg_mc', 'e_trg25_aiso1_mc'),
    (loc+'SingleLepton/aiso1/electron_SFs.root:trg_embed', 'e_trg25_aiso1_embed'),
    (loc+'SingleLepton/aiso2/electron_SFs.root:trg_data', 'e_trg25_aiso2_data'),
    (loc+'SingleLepton/aiso2/electron_SFs.root:trg_mc', 'e_trg25_aiso2_mc'),
    (loc+'SingleLepton/aiso2/electron_SFs.root:trg_embed', 'e_trg25_aiso2_embed'),
    (loc+'El12Mu23/electron_SFs.root:trg_data', 'e_trg12_data'),
    (loc+'El12Mu23/electron_SFs.root:trg_mc', 'e_trg12_mc'),
    (loc+'El12Mu23/electron_SFs.root:trg_embed', 'e_trg12_embed'),
    (loc+'El12Mu23/aiso1/electron_SFs.root:trg_data', 'e_trg12_aiso1_data'),
    (loc+'El12Mu23/aiso1/electron_SFs.root:trg_mc', 'e_trg12_aiso1_mc'),
    (loc+'El12Mu23/aiso1/electron_SFs.root:trg_embed', 'e_trg12_aiso1_embed'),
    (loc+'El12Mu23/aiso2/electron_SFs.root:trg_data', 'e_trg12_aiso2_data'),
    (loc+'El12Mu23/aiso2/electron_SFs.root:trg_mc', 'e_trg12_aiso2_mc'),
    (loc+'El12Mu23/aiso2/electron_SFs.root:trg_embed', 'e_trg12_aiso2_embed'),
    (loc+'El23Mu8/electron_SFs.root:trg_data', 'e_trg23_data'),
    (loc+'El23Mu8/electron_SFs.root:trg_mc', 'e_trg23_mc'),
    (loc+'El23Mu8/electron_SFs.root:trg_embed', 'e_trg23_embed'),
    (loc+'El23Mu8/aiso1/electron_SFs.root:trg_data', 'e_trg23_aiso1_data'),
    (loc+'El23Mu8/aiso1/electron_SFs.root:trg_mc', 'e_trg23_aiso1_mc'),
    (loc+'El23Mu8/aiso1/electron_SFs.root:trg_embed', 'e_trg23_aiso1_embed'),
    (loc+'El23Mu8/aiso2/electron_SFs.root:trg_data', 'e_trg23_aiso2_data'),
    (loc+'El23Mu8/aiso2/electron_SFs.root:trg_mc', 'e_trg23_aiso2_mc'),
    (loc+'El23Mu8/aiso2/electron_SFs.root:trg_embed', 'e_trg23_aiso2_embed')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.30, 0.50],
                                   'e_idiso_binned_data', ['e_idiso_data', 'e_idiso_aiso1_data', 'e_idiso_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.30, 0.50],
                                   'e_idiso_binned_mc', ['e_idiso_mc', 'e_idiso_aiso1_mc', 'e_idiso_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.30, 0.50],
                                   'e_idiso_binned_embed', ['e_idiso_embed', 'e_idiso_aiso1_embed', 'e_idiso_aiso2_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.30, 0.50],
                                   'e_idiso_binned_em_data', ['e_idiso_em_data', 'e_idiso_aiso1_em_data', 'e_idiso_aiso2_em_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.30, 0.50],
                                   'e_idiso_binned_em_mc', ['e_idiso_em_mc', 'e_idiso_aiso1_em_mc', 'e_idiso_aiso2_em_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.30, 0.50],
                                   'e_idiso_binned_em_embed', ['e_idiso_em_embed', 'e_idiso_aiso1_em_embed', 'e_idiso_aiso2_em_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.30, 0.50],
                                   'e_trg25_binned_data', ['e_trg25_data', 'e_trg25_aiso1_data', 'e_trg25_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.30, 0.50],
                                   'e_trg25_binned_mc', ['e_trg25_mc', 'e_trg25_aiso1_mc', 'e_trg25_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.10, 0.30, 0.50],
                                   'e_trg25_binned_embed', ['e_trg25_embed', 'e_trg25_aiso1_embed', 'e_trg25_aiso2_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.30, 0.50],
                                   'e_trg12_binned_data', ['e_trg12_data', 'e_trg12_aiso1_data', 'e_trg12_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.30, 0.50],
                                   'e_trg12_binned_mc', ['e_trg12_mc', 'e_trg12_aiso1_mc', 'e_trg12_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.30, 0.50],
                                   'e_trg12_binned_embed', ['e_trg12_embed', 'e_trg12_aiso1_embed', 'e_trg12_aiso2_embed'])

wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.30, 0.50],
                                   'e_trg23_binned_data', ['e_trg23_data', 'e_trg23_aiso1_data', 'e_trg23_aiso2_data'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.30, 0.50],
                                   'e_trg23_binned_mc', ['e_trg23_mc', 'e_trg23_aiso1_mc', 'e_trg23_aiso2_mc'])
wsptools.MakeBinnedCategoryFuncMap(w, 'e_iso', [0., 0.15, 0.30, 0.50],
                                   'e_trg23_binned_embed', ['e_trg23_embed', 'e_trg23_aiso1_embed', 'e_trg23_aiso2_embed'])


for t in ['idiso', 'idiso_aiso1', 'idiso_aiso2', 'idiso_binned', 'idiso_em', 'idiso_aiso1_em', 'idiso_aiso2_em', 'idiso_binned_em', 'trg25', 'trg25_aiso1', 'trg25_aiso2', 'trg25_binned', 'trg12', 'trg12_aiso1', 'trg12_aiso2', 'trg12_binned', 'trg23', 'trg23_aiso1', 'trg23_aiso2', 'trg23_binned']:
    w.factory('expr::e_%s_ratio("@0/@1", e_%s_data, e_%s_mc)' % (t, t, t))
    w.factory('expr::e_%s_embed_ratio("@0/@1", e_%s_data, e_%s_embed)' % (t, t, t))

### Muon tracking efficiency scale factor from the muon POG
loc = 'inputs/MuonPOG'

muon_trk_eff_hist = wsptools.TGraphAsymmErrorsToTH1D(GetFromTFile(loc+'/Tracking_EfficienciesAndSF_BCDEFGH.root:ratio_eff_eta3_dr030e030_corr'))
wsptools.SafeWrapHist(w, ['m_eta'], muon_trk_eff_hist, name='m_trk_ratio')

### Electron tracking efficiency scale factor from the egamma POG
loc = 'inputs/EGammaPOG'

electron_trk_eff_hist = GetFromTFile(loc+'/egammaEffi.txt_EGM2D.root:EGamma_SF2D')
wsptools.SafeWrapHist(w, ['e_eta','e_pt'], electron_trk_eff_hist, name='e_trk_ratio')


### Hadronic tau trigger efficiencies
with open('inputs/triggerSF-Moriond17/di-tau/fitresults_tt_moriond2017.json') as jsonfile:
    pars = json.load(jsonfile)
    for tautype in ['genuine', 'fake']:
        for iso in ['VLooseIso','LooseIso','MediumIso','TightIso','VTightIso','VVTightIso']:
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
            w.factory('expr::t_%s_tt_ratio("@0/@1", t_%s_tt_data, t_%s_tt_mc)' % (label, label, label))


### LO DYJetsToLL Z mass vs pT correction
histsToWrap = [
    ('inputs/DYWeights/zpt_weights_summer2016_v5.root:zptmass_histo'                 , 'zpt_weight_nom'         ),
    ('inputs/DYWeights/zpt_weights_summer2016_v5.root:zptmass_histo_ESUp'            , 'zpt_weight_esup'        ),
    ('inputs/DYWeights/zpt_weights_summer2016_v5.root:zptmass_histo_ESDown'          , 'zpt_weight_esdown'      ),
    ('inputs/DYWeights/zpt_weights_summer2016_v5.root:zptmass_histo_TTUp'            , 'zpt_weight_ttup'        ),
    ('inputs/DYWeights/zpt_weights_summer2016_v5.root:zptmass_histo_TTDown'          , 'zpt_weight_ttdown'      ),
    ('inputs/DYWeights/zpt_weights_summer2016_v5.root:zptmass_histo_StatM400pT0Up'   , 'zpt_weight_statpt0up'   ),
    ('inputs/DYWeights/zpt_weights_summer2016_v5.root:zptmass_histo_StatM400pT0Down' , 'zpt_weight_statpt0down' ),
    ('inputs/DYWeights/zpt_weights_summer2016_v5.root:zptmass_histo_StatM400pT40Up'  , 'zpt_weight_statpt40up'  ),
    ('inputs/DYWeights/zpt_weights_summer2016_v5.root:zptmass_histo_StatM400pT40Down', 'zpt_weight_statpt40down'),
    ('inputs/DYWeights/zpt_weights_summer2016_v5.root:zptmass_histo_StatM400pT80Up'  , 'zpt_weight_statpt80up'  ),
    ('inputs/DYWeights/zpt_weights_summer2016_v5.root:zptmass_histo_StatM400pT80Down', 'zpt_weight_statpt80down')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['z_gen_mass', 'z_gen_pt'],
                          GetFromTFile(task[0]), name=task[1])

w.importClassCode('CrystalBallEfficiency')

w.Print()
w.writeToFile('htt_scalefactors_embedding_v1.root')
w.Delete()
