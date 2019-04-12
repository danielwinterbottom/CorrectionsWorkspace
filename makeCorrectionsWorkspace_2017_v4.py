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

w = ROOT.RooWorkspace('w')

# IC muon ID, iso, trigger SFs

loc = 'inputs/ICSF/'

# Embedded selection efficiencies

histsToWrap = [
    (loc+'2017/EmbedSel/Mu8/muon_SFs.root:data_trg_eff', 'm_sel_trg8_1_data'),
    (loc+'2017/EmbedSel/Mu17/muon_SFs.root:data_trg_eff', 'm_sel_trg17_1_data')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['gt1_pt', 'expr::gt1_abs_eta("TMath::Abs(@0)",gt1_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

histsToWrap = [
    (loc+'2017/EmbedSel/Mu8/muon_SFs.root:data_trg_eff', 'm_sel_trg8_2_data'),
    (loc+'2017/EmbedSel/Mu17/muon_SFs.root:data_trg_eff', 'm_sel_trg17_2_data')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['gt2_pt', 'expr::gt2_abs_eta("TMath::Abs(@0)",gt2_eta[0])'],
                          GetFromTFile(task[0]), name=task[1])

w.factory('expr::m_sel_trg_data("0.9959*(@0*@3+@1*@2-@1*@3)", m_sel_trg8_1_data, m_sel_trg17_1_data, m_sel_trg8_2_data, m_sel_trg17_2_data)')
w.factory('expr::m_sel_trg_ratio("min(1./@0,20)", m_sel_trg_data)')

histsToWrap = [
    (loc+'2017/EmbedSel/Mu8/muon_SFs.root:data_id_eff', 'm_sel_idEmb_data')
]
wsptools.SafeWrapHist(w, ['gt_pt', 'expr::gt_abs_eta("TMath::Abs(@0)",gt_eta[0])'],
                          GetFromTFile(loc+'2017/EmbedSel/Mu8/muon_SFs.root:data_id_eff'), 'm_sel_idEmb_data')

w.factory('expr::m_sel_idEmb_ratio("min(1./@0,20)", m_sel_idEmb_data)')


# trigegr SFs

histsToWrap = [
    (loc+'2017/SingleLepton/muon_SFs.root:data_id_eff', 'm_id_data'),
    (loc+'2017/SingleLepton/muon_SFs.root:ZLL_id_eff', 'm_id_mc'),
    (loc+'2017/SingleLepton/muon_SFs.root:embed_id_eff', 'm_id_embed'),
    (loc+'2017/SingleLepton/muon_SFs.root:data_iso_eff', 'm_iso_data'),
    (loc+'2017/SingleLepton/muon_SFs.root:ZLL_iso_eff', 'm_iso_mc'),
    (loc+'2017/SingleLepton/muon_SFs.root:embed_iso_eff', 'm_iso_embed'),
    (loc+'2017/SingleLepton/muon_SFs.root:data_trg_eff', 'm_trg_data'),
    (loc+'2017/SingleLepton/muon_SFs.root:ZLL_trg_eff', 'm_trg_mc'),
    (loc+'2017/SingleLepton/muon_SFs.root:embed_trg_eff', 'm_trg_embed'),
    (loc+'2017/Mu20/muon20_cross_B/muon_SFs.root:data_trg_eff', 'm_trg20_runB_data'),
    (loc+'2017/Mu20/muon20_cross_B/muon_SFs.root:ZLL_trg_eff', 'm_trg20_mc'),
    (loc+'2017/Mu20/muon20_cross_B/muon_SFs.root:embed_trg_eff', 'm_trg20_embed'),
    (loc+'2017/Mu20/muon20_noB/muon_SFs.root:data_trg_eff', 'm_trg20_runCtoF_data'),
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

# EGamma POG ID SFs

loc = 'inputs/EGammaPOG/'

histsToWrap = [
    (loc+'gammaEffi.txt_EGM2D_runBCDEF_passingMVA94Xwp80noiso.root:EGamma_EffData2D', 'e_id_pog_data'),
    (loc+'gammaEffi.txt_EGM2D_runBCDEF_passingMVA94Xwp80noiso.root:EGamma_EffMC2D', 'e_id_pog_mc'),
    (loc+'gammaEffi.txt_EGM2D_runBCDEF_passingMVA94Xwp80iso.root:EGamma_EffData2D', 'e_idiso_pog_data'),
    (loc+'gammaEffi.txt_EGM2D_runBCDEF_passingMVA94Xwp80iso.root:EGamma_EffMC2D', 'e_idiso_pog_mc'),
    (loc+'gammaEffi.txt_EGM2D_runBCDEF_passingMVA94Xwp90noiso.root:EGamma_EffData2D', 'e_looseid_pog_data'),
    (loc+'gammaEffi.txt_EGM2D_runBCDEF_passingMVA94Xwp90noiso.root:EGamma_EffMC2D', 'e_looseid_pog_mc'),
    (loc+'gammaEffi.txt_EGM2D_runBCDEF_passingMVA94Xwp90iso.root:EGamma_EffData2D', 'e_looseidiso_pog_data'),
    (loc+'gammaEffi.txt_EGM2D_runBCDEF_passingMVA94Xwp90iso.root:EGamma_EffMC2D', 'e_looseidiso_pog_mc')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['e_eta', 'e_pt'],
                          GetFromTFile(task[0]), name=task[1])


# IC em trigger SF
loc = 'inputs/ICSF/2017/ElecIDV2/'

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

loc = 'inputs/ICSF/2017/'

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

# IC EGamma ID, iso, trigger SFs

loc = 'inputs/ICSF/'
        
histsToWrap = [
    (loc+'2017/ElecIDV2/SingleLepton/electron_SFs.root:data_id_eff', 'e_id_data'),
    (loc+'2017/ElecIDV2/SingleLepton/electron_SFs.root:ZLL_id_eff', 'e_id_mc'),
    (loc+'2017/ElecIDV2/SingleLepton/electron_SFs.root:embed_id_eff', 'e_id_embed'),
    (loc+'2017/ElecIDV2/SingleLepton/electron_SFs.root:data_iso_eff', 'e_iso_data'),
    (loc+'2017/ElecIDV2/SingleLepton/electron_SFs.root:ZLL_iso_eff', 'e_iso_mc'),
    (loc+'2017/ElecIDV2/SingleLepton/electron_SFs.root:embed_iso_eff', 'e_iso_embed'),
    (loc+'2017/ElecIDV2/em_lo/aiso/electron_SFs.root:data_iso_eff', 'e_aiso_data'),
    (loc+'2017/ElecIDV2/em_lo/aiso/electron_SFs.root:ZLL_iso_eff', 'e_aiso_mc'),
    (loc+'2017/ElecIDV2/em_lo/aiso/electron_SFs.root:embed_iso_eff', 'e_aiso_embed'),
    (loc+'2017/ElecIDV2/SingleLepton/electron_SFs.root:data_trg_eff', 'e_trg_data'),
    (loc+'2017/ElecIDV2/SingleLepton/electron_SFs.root:ZLL_trg_eff', 'e_trg_mc'),
    (loc+'2017/ElecIDV2/SingleLepton/electron_SFs.root:embed_trg_eff', 'e_trg_embed'),
    (loc+'2017/ElecIDV2/Ele24/electron_SFs.root:data_trg_eff', 'e_trg24_data'),
    (loc+'2017/ElecIDV2/Ele24/electron_SFs.root:ZLL_trg_eff', 'e_trg24_mc'),
    (loc+'2017/ElecIDV2/Ele24/electron_SFs.root:embed_trg_eff', 'e_trg24_embed'),
    (loc+'2017/ElecIDV2/Ele24/fromDoubleE/electron_SFs.root:data_trg_eff', 'e_trg24_fromDoubleE_data'),
    (loc+'2017/ElecIDV2/Ele24/fromDoubleE/electron_SFs.root:ZLL_trg_eff', 'e_trg24_fromDoubleE_mc'),
    (loc+'2017/ElecIDV2/Ele24/fromDoubleE/electron_SFs.root:embed_trg_eff', 'e_trg24_fromDoubleE_embed'),
    #(loc+'2017/SingleElectron_27_32single_35/electron_SFs.root:data_trg_eff','e_trg_27_32_35_data'),
    #(loc+'2017/SingleElectron_27_32single_35/electron_SFs.root:ZLL_trg_eff','e_trg_27_32_35_mc'),
    #(loc+'2017/SingleElectron_27_32single_35/electron_SFs.root:embed_trg_eff','e_trg_27_32_35_embed')
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


## IC em qcd os/ss weights


loc = 'inputs/ICSF/em_osss_2017/'
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


### Muon tracking efficiency scale factor from the muon POG
loc = 'inputs/MuonPOG'

muon_trk_eff_hist = wsptools.TGraphAsymmErrorsToTH1D(GetFromTFile(loc+'/fits.root:ratio_eff_eta3_dr030e030_corr'))
wsptools.SafeWrapHist(w, ['m_eta'], muon_trk_eff_hist, name='m_trk_ratio')

### Electron tracking efficiency scale factor from the egamma POG
loc = 'inputs/EGammaPOG'

electron_trk_eff_hist = GetFromTFile(loc+'/egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root:EGamma_SF2D')
wsptools.SafeWrapHist(w, ['e_eta','e_pt'], electron_trk_eff_hist, name='e_trk_ratio')

## Tau Trigger efficiencies for embedded samples from IC
w.factory('expr::t_pt_trig("min(max(@0,20),450)" ,t_pt[0])')

loc = 'inputs/ICSF/2017/TauTrgFinal/'
loc2 = 'inputs/ICSF/2017/TauTrg/'
tau_id_wps=['vloose','loose','medium','tight']
channels=['tt','et','mt']
#channels=['tt']
for chan in channels:
  tau_trg_file_embed = ROOT.TFile(loc+'/embed_tau_trig_eff_%s.root' % chan)
  for wp in tau_id_wps:
    for dm in ['0','1','10']:
      func = tau_trg_file_embed.Get("eff_gr_%siso_%s_dm%s_pt_fit" % (wp,chan,dm))
      params = func.GetParameters()
      w.factory('expr::t_trg_pt_%s_%s_dm%s_embed("%.12f - ROOT::Math::crystalball_cdf(-@0, %.12f, %.12f, %.12f, %.12f)*(%.12f)", t_pt_trig)' % (wp,chan,dm, params[5],params[0],params[1],params[2],params[3],params[4]))

      histsToWrap = [
        (loc+'/embed_tau_trig_eff_%s.root:eff_%siso_%s_dm%s_eta' % (chan,wp,chan,dm), 't_trg_eta_%s_%s_dm%s_embed' % (wp,chan,dm)),
        (loc+'/embed_tau_trig_eff_%s.root:eff_%siso_%s_dm%s_aveeta' % (chan,wp,chan,dm),'t_trg_ave_eta_%s_%s_dm%s_embed' % (wp,chan,dm))
      ]

      for task in histsToWrap:
        wsptools.SafeWrapHist(w, ['expr::t_abs_eta("TMath::Abs(@0)",t_eta[0])'],
                              GetFromTFile(task[0]), name=task[1])

    w.factory('expr::t_trg_eta_%s_%s_embed("(@0==0)*@1 + (@0==1||@0==2)*@2 + (@0==10)*@3", t_dm[0], t_trg_eta_%s_%s_dm0_embed, t_trg_eta_%s_%s_dm1_embed, t_trg_eta_%s_%s_dm10_embed)' % (wp, chan, wp, chan, wp, chan, wp, chan))
    w.factory('expr::t_trg_ave_eta_%s_%s_embed("(@0==0)*@1 + (@0==1||@0==2)*@2 + (@0==10)*@3", t_dm[0], t_trg_ave_eta_%s_%s_dm0_embed, t_trg_ave_eta_%s_%s_dm1_embed, t_trg_ave_eta_%s_%s_dm10_embed)' % (wp, chan, wp, chan, wp, chan, wp, chan))

    w.factory('expr::t_trg_pt_%s_%s_embed("(@0==0)*@1 + (@0==1||@0==2)*@2 + (@0==10)*@3", t_dm[0], t_trg_pt_%s_%s_dm0_embed, t_trg_pt_%s_%s_dm1_embed, t_trg_pt_%s_%s_dm10_embed)' % (wp, chan, wp, chan, wp, chan, wp, chan))

    chan_label = 'ditau'
    if chan == 'mt': chan_label = 'mutau'
    if chan == 'et': chan_label = 'etau'
    w.factory('expr::t_trg_%s_%s_embed("@0*@1/@2", t_trg_pt_%s_%s_embed, t_trg_eta_%s_%s_embed, t_trg_ave_eta_%s_%s_embed)' % (wp, chan_label, wp, chan, wp, chan, wp, chan))
  
    histsToWrap=[]
    if chan == 'tt' and wp =='tight':
      histsToWrap += [
        ('inputs/ICSF/2017/TauTrg/tau_trg_2017_new/embed_tau_trig_eff_%s_%siso_trig1.root:eff_%siso_pt' % (chan,wp,wp), 't_trg_pt_%s_%s_trig1_mc' % (wp,chan)),
        ('inputs/ICSF/2017/TauTrg/tau_trg_2017_new/embed_tau_trig_eff_%s_%siso_trig2.root:eff_%siso_pt' % (chan,wp,wp), 't_trg_pt_%s_%s_trig2_mc' % (wp,chan)),
        ('inputs/ICSF/2017/TauTrg/tau_trg_2017_new/embed_tau_trig_eff_%s_%siso_trig3.root:eff_%siso_pt' % (chan,wp,wp), 't_trg_pt_%s_%s_trig3_mc' % (wp,chan)),
        ('inputs/ICSF/2017/TauTrg/tau_trg_2017_new/embed_tau_trig_eff_%s_%siso_trig1and2.root:eff_%siso_pt' % (chan,wp,wp), 't_trg_pt_%s_%s_trig1and2_mc' % (wp,chan)),
        ('inputs/ICSF/2017/TauTrg/tau_trg_2017_new/embed_tau_trig_eff_%s_%siso_trig1and3.root:eff_%siso_pt' % (chan,wp,wp), 't_trg_pt_%s_%s_trig1and3_mc' % (wp,chan)),
        ('inputs/ICSF/2017/TauTrg/tau_trg_2017_new/embed_tau_trig_eff_%s_%siso_trig2and3.root:eff_%siso_pt' % (chan,wp,wp), 't_trg_pt_%s_%s_trig2and3_mc' % (wp,chan)),
        ('inputs/ICSF/2017/TauTrg/tau_trg_2017_new/embed_tau_trig_eff_%s_%siso_trig1and2and3.root:eff_%siso_pt' % (chan,wp,wp), 't_trg_pt_%s_%s_trig1and2and3_mc' % (wp,chan)),
        ('inputs/ICSF/2017/TauTrg/tau_trg_2017_new/embed_tau_trig_eff_%s_%siso_or.root:eff_%siso_pt' % (chan,wp,wp), 't_trg_pt_%s_%s_or_mc' % (wp,chan))
      ]
  
    for task in histsToWrap:
      wsptools.SafeWrapHist(w, ['t_pt'],
                            GetFromTFile(task[0]), name=task[1])
      wsptools.SafeWrapHist(w, ['t_pt_1'],
                            GetFromTFile(task[0]), name=task[1]+'_1')
      wsptools.SafeWrapHist(w, ['t_pt_2'],
                            GetFromTFile(task[0]), name=task[1]+'_2')
 

w.factory('expr::t_trg_tt_tight_mc_new("@0*@1 + @2*@3 + @4*@5 - @6*@7 - @8*@9 -@10*@11 + @12*@13", t_trg_pt_tight_tt_trig1_mc_1,t_trg_pt_tight_tt_trig1_mc_2,t_trg_pt_tight_tt_trig2_mc_1,t_trg_pt_tight_tt_trig2_mc_2,t_trg_pt_tight_tt_trig3_mc_1,t_trg_pt_tight_tt_trig3_mc_2,t_trg_pt_tight_tt_trig1and2_mc_1,t_trg_pt_tight_tt_trig1and2_mc_2,t_trg_pt_tight_tt_trig1and3_mc_1,t_trg_pt_tight_tt_trig1and3_mc_2,t_trg_pt_tight_tt_trig2and3_mc_1,t_trg_pt_tight_tt_trig2and3_mc_2, t_trg_pt_tight_tt_trig1and2and3_mc_1,t_trg_pt_tight_tt_trig1and2and3_mc_2)')
 
# MC effieicies for closure tests
histsToWrap = [
    (loc2+'embed_tau_trig_eff_tt_tightiso_mcfull.root:eff_tightiso_pt' , 't_trg_pt_tight_tt_mcfull' ),
    (loc2+'embed_tau_trig_eff_tt_tightiso_mc.root:eff_tightiso_pt' , 't_trg_pt_tight_tt_mccalo' )
]

for task in histsToWrap:
  wsptools.SafeWrapHist(w, ['t_pt'],
                        GetFromTFile(task[0]), name=task[1])

histsToWrap = [
  (loc2+'embed_tau_trig_eff_tt_tightiso_mcfull.root:eff_tightiso_eta', 't_trg_phieta_tight_tt_mcfull'),
  (loc2+'embed_tau_trig_eff_tt_tightiso_mcfull.root:eff_tightiso_aveeta','t_trg_ave_phieta_tight_tt_mcfull'),
  (loc2+'embed_tau_trig_eff_tt_tightiso_mc.root:eff_tightiso_eta', 't_trg_phieta_tight_tt_mccalo'),
  (loc2+'embed_tau_trig_eff_tt_tightiso_mc.root:eff_tightiso_aveeta','t_trg_ave_phieta_tight_tt_mccalo' )
]

for task in histsToWrap:
  wsptools.SafeWrapHist(w, ['t_eta'],
                        GetFromTFile(task[0]), name=task[1])

w.factory('expr::t_trg_tight_tt_mcfull("@0*@1/@2", t_trg_pt_tight_tt_mcfull, t_trg_phieta_tight_tt_mcfull, t_trg_ave_phieta_tight_tt_mcfull)')
w.factory('expr::t_trg_tight_tt_mccalo("@0*@1/@2", t_trg_pt_tight_tt_mccalo, t_trg_phieta_tight_tt_mccalo, t_trg_ave_phieta_tight_tt_mccalo)') 
w.factory('expr::t_trg_tight_tt_mcclose("@0/@1", t_trg_tight_tt_mcfull, t_trg_tight_tt_mccalo)')

for task in histsToWrap:
  wsptools.SafeWrapHist(w, ['t_pt_2','t_pt_1'],
                        GetFromTFile('inputs/ICSF/2017/TauTrg/embed_trg_nonclosure_2017.root:nonclosure'), name='t_trg_nonclosure')

### Tau Trigger scale factors from Tau POG

loc = 'inputs/TauTriggerSFs2017Final/'

tau_id_wps=['vloose','loose','medium','tight','vtight']

tau_trg_file = ROOT.TFile(loc+'tauTriggerEfficiencies2017.root')

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
        
  
        w.factory('expr::t_trg_phieta_%s_%s_%s("(@0==0)*@1 + (@0==1||@0==2)*@2 + (@0==10)*@3", t_dm[0], t_trg_phieta_%s_%s_dm0_%s, t_trg_phieta_%s_%s_dm1_%s, t_trg_phieta_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
        w.factory('expr::t_trg_ave_phieta_%s_%s_%s("(@0==0)*@1 + (@0==1||@0==2)*@2 + (@0==10)*@3", t_dm[0], t_trg_ave_phieta_%s_%s_dm0_%s, t_trg_ave_phieta_%s_%s_dm1_%s, t_trg_ave_phieta_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x))
  
        w.factory('expr::t_trg_pt_%s_%s_%s("(@0==0)*@1 + (@0==1||@0==2)*@2 + (@0==10)*@3", t_dm[0], t_trg_pt_%s_%s_dm0_%s, t_trg_pt_%s_%s_dm1_%s, t_trg_pt_%s_%s_dm10_%s)' % (wp, y, x, wp, y, x, wp, y, x, wp, y, x)) 
  
 
        w.factory('expr::t_trg_%s_%s_data("@0*@1/@2", t_trg_pt_%s_%s_data, t_trg_phieta_%s_%s_data, t_trg_ave_phieta_%s_%s_data)' % (wp, y, wp, y, wp, y, wp, y))  
        w.factory('expr::t_trg_%s_%s_mc("@0*@1/@2", t_trg_pt_%s_%s_mc, t_trg_phieta_%s_%s_mc, t_trg_ave_phieta_%s_%s_mc)' % (wp, y, wp, y, wp, y, wp, y))
        w.factory('expr::t_trg_%s_%s_ratio("@0/@1", t_trg_%s_%s_data, t_trg_%s_%s_mc)' % (wp, y, wp, y, wp, y))

#  # now use the graphs to get the uncertainty variations
#  graphsToWrap = [
#    ('graph_diTauTriggerEfficiency_%sTauMVA_'  % wp, 't_trg_%s_tt' % wp),
#    ('graph_MuTauTriggerEfficiency_%sTauMVA_' % wp, 't_trg_%s_mt' % wp),
#    ('graph_ETauTriggerEfficiency_%sTauMVA_' % wp, 't_trg_%s_et' % wp),
#  ]
#  
#  for task in graphsToWrap:
#    data_hist = tau_trg_file.Get(task[0]+'DATA')
#    mc_hist = tau_trg_file.Get(task[0]+'MC')
#    uncert_hists = wsptools.UncertsFromGraphs(data_hist,mc_hist)
#    wsptools.SafeWrapHist(w, ['t_pt'], uncert_hists[0], name=task[1]+'_up')
#    wsptools.SafeWrapHist(w, ['t_pt'], uncert_hists[1], name=task[1]+'_down')

### Electron leg of etau cross trigger SF -- DESY (for now)
loc = 'inputs/LeptonEfficiencies/Electron/Run2017/'

desyHistsToWrap = [
    (loc+'Electron_EleTau_Ele24.root',           'MC', 'e_trg_EleTau_Ele24Leg_desy_mc'),
    (loc+'Electron_EleTau_Ele24.root',           'Data', 'e_trg_EleTau_Ele24Leg_desy_data'),
]

for task in desyHistsToWrap:
    wsptools.SafeWrapHist(w, ['e_pt', 'expr::e_abs_eta("TMath::Abs(@0)",e_eta[0])'],
                          wsptools.ProcessDESYLeptonSFs(task[0], task[1], task[2]), name=task[2])

for t in ['trg_EleTau_Ele24Leg_desy']:
    w.factory('expr::e_%s_ratio("@0/@1", e_%s_data, e_%s_mc)' % (t, t, t))

histsToWrap = [
    ('inputs/DYWeights/zpt_weights_2017_1D.root:zpt_weight'  , 'zpt_weight_nom'),
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['z_gen_pt'],
                          GetFromTFile(task[0]), name=task[1])

# correction for quark mass dependence to ggH
wsptools.SafeWrapHist(w, ['HpT'],  GetFromTFile('inputs/ICSF/ggH/quarkmass_uncerts_hnnlo.root:nom'), 'ggH_quarkmass_hist')
w.factory('expr::ggH_quarkmass_corr("1.006*@0", ggH_quarkmass_hist)') # the constant factor is to ensure the normalization doesn't change - it is sample specific

wsptools.SafeWrapHist(w, ['HpT'],  GetFromTFile('inputs/ICSF/ggH/quarkmass_uncerts_hnnlo.root:up'), 'ggH_quarkmass_hist_up')
w.factory('expr::ggH_quarkmass_corr_up("1.006*@0", ggH_quarkmass_hist_up)')
wsptools.SafeWrapHist(w, ['HpT'],  GetFromTFile('inputs/ICSF/ggH/quarkmass_uncerts_hnnlo.root:down'), 'ggH_quarkmass_hist_down')
w.factory('expr::ggH_quarkmass_corr_down("1.006*@0", ggH_quarkmass_hist_down)')

wsptools.SafeWrapHist(w, ['HpT'],  GetFromTFile('inputs/ICSF/ggH/top_mass_weights.root:pt_weight'), 'ggH_fullquarkmass_hist')
w.factory('expr::ggH_fullquarkmass_corr("0.985*@0", ggH_fullquarkmass_hist)') # the constant factor is to ensure the normalization doesn't change - it is sample specific

loc = 'inputs/ICSF/ggH/MG_ps_uncerts_2017.root:'
histsToWrap = [
    (loc + 'ps_0jet_up', 'ps_0jet_up'),
    (loc + 'ps_0jet_down', 'ps_0jet_down'),
    (loc + 'ps_1jet_up', 'ps_1jet_up'),
    (loc + 'ps_1jet_down', 'ps_1jet_down'),
    (loc + 'ps_2jet_up', 'ps_2jet_up'),
    (loc + 'ps_2jet_down', 'ps_2jet_down'),
    (loc + 'ps_3jet_up', 'ps_3jet_up'),
    (loc + 'ps_3jet_down', 'ps_3jet_down')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['HpT'],
                          GetFromTFile(task[0]), name=task[1])

for shift in ['up', 'down']:
  wsptools.MakeBinnedCategoryFuncMap(w, 'ngenjets', [0, 1, 2, 3, 1000],
                                     'ggH_mg_ps_%s' % shift, ['ps_0jet_%s' % shift, 'ps_1jet_%s' % shift, 'ps_2jet_%s' % shift, 'ps_3jet_%s' % shift])


histsToWrap = [
    (loc + 'ue_up', 'ggH_mg_ue_up'),
    (loc + 'ue_down', 'ggH_mg_ue_down')
]

for task in histsToWrap:
    wsptools.SafeWrapHist(w, ['ngenjets'],
                          GetFromTFile(task[0]), name=task[1])


w.Print()
w.writeToFile('htt_scalefactors_2017_v4.root')
w.Delete()
