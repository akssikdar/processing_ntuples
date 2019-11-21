import argparse
import logging # as Logging
from math import sqrt

#logging = Logging.getLogger("common")

if __name__ == '__main__':
    # parse commandline arguments first

    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = "tests of lepton SFs",
        epilog = """Example:\npython module_leptons.py electron_trig_sf.root gstore_outdirs/v19/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/Ntupler_v19_MC2016_Summer16_TTJets_powheg/180226_022336/0000/MC2016_Summer16_TTJets_powheg_*.root"""
        )

    parser.add_argument("output_file", type=str, default="output.root", help="filename for output")
    parser.add_argument("--test-sfs",  action='store_true', help="just print ele trig SF for typical values")
    parser.add_argument("--debug",  action='store_true', help="DEBUG level of logging")
    parser.add_argument('input_files', nargs='+', help="""the files to sum up, passed by shell, as:
    /gstore/t3cms/store/user/otoldaie/v19/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/Ntupler_v19_MC2016_Summer16_TTJets_powheg/180226_022336/0000/MC2016_Summer16_TTJets_powheg_*.root""")


    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

logging.info('importing ROOT')
import ROOT
from ROOT import TFile, TTree, TH1D, TH2D, TMath, gSystem

#ROOT.gROOT.Reset()


logging.info("leptonic SFs")

# ------------------------------------------------------------------
# Muon Reco (tracking), ID, ISO and trigger SF
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonWorkInProgressAndPagResults
# it also links to tracking
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2#Tracking_efficiency_provided_by
# 
# says
# > usual systematic ID uncertainty from tag-n-probe is 1%
# > add 0.5 for tracking HIP issue in quadrature
# > and 1% for PF Tight isolation
# -- therefore there is no shape?
#    what are the uncertainties in these histograms?

# <--- this quote is invalid now, the twiki was updated and it is gone
#      now the first link says absolutely nothing about systematic ID uncertainty for full 2016 result

# it seems the old page was revision 29
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonWorkInProgressAndPagResults?rev=29#Results_on_the_full_2016_data

# https://twiki.cern.ch/twiki/bin/view/CMS/MuonTagAndProbe
# says recommended systematic uncertainties due to tag-n-probe method are
# T&P Resonance          Id        Isolation  Single Mu trigger
#             Z          0.5%      0.2%       0.2% 

muon_unc_sys_id  = 0.005
muon_unc_sys_iso = 0.002
muon_unc_sys_trg = 0.002

# here https://twiki.cern.ch/twiki/bin/view/CMS/MuonWorkInProgressAndPagResults
# they recommend to use 2015 systematics from here:
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2#Results_for_CMSSW_7_6_X_dataset
# and they are about twice more conservative

muon_unc_sys_id  = 0.01
muon_unc_sys_iso = 0.005
muon_unc_sys_trg = 0.005


"""
tests:

root -l ../lab_log/muon-effs//2016_23Sep_tracking_more_BCDEF_fits.root
root -l ../lab_log/muon-effs//2016_23Sep_MuonID_EfficienciesAndSF_BCDEF.root
root -l ../lab_log/muon-effs//2016_23Sep_MuonISO_EfficienciesAndSF_BCDEF.root
root -l ../lab_log/muon-effs//2016_23Sep_SingleMuonTrigger_EfficienciesAndSF_RunBtoF.root

root -l ../lab_log/muon-effs//2016_23Sep_tracking_more_GH_fits.root
root -l ../lab_log/muon-effs//2016_23Sep_MuonID_EfficienciesAndSF_GH.root
root -l ../lab_log/muon-effs//2016_23Sep_MuonISO_EfficienciesAndSF_GH.root
root -l ../lab_log/muon-effs//2016_23Sep_SingleMuonTrigger_EfficienciesAndSF_Period4.root

ratio_eff_aeta_dr030e030_corr->Draw()
ratio_eff_vtx_dr030e030_corr->Draw()

MC_NUM_TightID_DEN_genTracks_PAR_pt_eta->Get("pt_abseta_ratio")->Draw("colz")
TightISO_TightID_pt_eta->Get("pt_abseta_ratio")->Draw("colz")
IsoMu24_OR_IsoTkMu24_PtEtaBins->Get("pt_abseta_ratio")->Draw("colz")
"""

muon_effs_dirname = "${CMSSW_BASE}/src/UserCode/proc/common_info/muon-effs/"
gSystem.ExpandPathName(muon_effs_dirname    )
#TString muon_effs_dirname = "lab_log/muon-effs/";
logging.info("muon SFs from " + muon_effs_dirname)

muon_effs_tracking_BCDEF_file  = TFile(muon_effs_dirname + "/2016_23Sep_tracking_more_BCDEF_fits.root" )
muon_effs_tracking_GH_file     = TFile(muon_effs_dirname + "/2016_23Sep_tracking_more_GH_fits.root" )
muon_effs_tracking_BCDEF_graph = muon_effs_tracking_BCDEF_file.Get("ratio_eff_aeta_dr030e030_corr")
muon_effs_tracking_GH_graph    = muon_effs_tracking_GH_file   .Get("ratio_eff_aeta_dr030e030_corr")

muon_effs_tracking_BCDEF_graph_vtx = muon_effs_tracking_BCDEF_file.Get("ratio_eff_vtx_dr030e030_corr")
muon_effs_tracking_GH_graph_vtx    = muon_effs_tracking_GH_file   .Get("ratio_eff_vtx_dr030e030_corr")

print type(muon_effs_tracking_BCDEF_graph)

muon_effs_id_BCDEF_file  = TFile(muon_effs_dirname + "/2016_23Sep_MuonID_EfficienciesAndSF_BCDEF.root" )
muon_effs_id_GH_file     = TFile(muon_effs_dirname + "/2016_23Sep_MuonID_EfficienciesAndSF_GH.root" )

muon_effs_id_BCDEF_histo     = muon_effs_id_BCDEF_file.Get("MC_NUM_TightID_DEN_genTracks_PAR_pt_eta").Get("pt_abseta_ratio")
muon_effs_id_GH_histo        = muon_effs_id_GH_file   .Get("MC_NUM_TightID_DEN_genTracks_PAR_pt_eta").Get("pt_abseta_ratio")
muon_effs_id_vtx_BCDEF_histo = muon_effs_id_BCDEF_file.Get("MC_NUM_TightID_DEN_genTracks_PAR_vtx")   .Get("tag_nVertices_ratio")
muon_effs_id_vtx_GH_histo    = muon_effs_id_GH_file   .Get("MC_NUM_TightID_DEN_genTracks_PAR_vtx")   .Get("tag_nVertices_ratio")

print type(muon_effs_id_BCDEF_histo)

muon_effs_iso_BCDEF_file  = TFile(muon_effs_dirname + "/2016_23Sep_MuonISO_EfficienciesAndSF_BCDEF.root" )
muon_effs_iso_GH_file     = TFile(muon_effs_dirname + "/2016_23Sep_MuonISO_EfficienciesAndSF_GH.root" )

muon_effs_iso_BCDEF_histo     = muon_effs_iso_BCDEF_file.Get("TightISO_TightID_pt_eta").Get("pt_abseta_ratio")
muon_effs_iso_GH_histo        = muon_effs_iso_GH_file   .Get("TightISO_TightID_pt_eta").Get("pt_abseta_ratio")
muon_effs_iso_vtx_BCDEF_histo = muon_effs_iso_BCDEF_file.Get("TightISO_TightID_vtx").Get("tag_nVertices_ratio")
muon_effs_iso_vtx_GH_histo    = muon_effs_iso_GH_file   .Get("TightISO_TightID_vtx").Get("tag_nVertices_ratio")

print type(muon_effs_iso_BCDEF_histo)

# --- yep, everywhere here Tight ID and ISO is used, since that's the leptons I use

# ------------------------ Muon trigger SF
# 

muon_effs_trg_BCDEF_file  = TFile(muon_effs_dirname + "/2016_23Sep_SingleMuonTrigger_EfficienciesAndSF_RunBtoF.root" )
muon_effs_trg_GH_file     = TFile(muon_effs_dirname + "/2016_23Sep_SingleMuonTrigger_EfficienciesAndSF_Period4.root" )
muon_effs_trg_BCDEF_histo = muon_effs_trg_BCDEF_file.Get("IsoMu24_OR_IsoTkMu24_PtEtaBins").Get("pt_abseta_ratio")
muon_effs_trg_GH_histo    = muon_effs_trg_GH_file   .Get("IsoMu24_OR_IsoTkMu24_PtEtaBins").Get("pt_abseta_ratio")

# somehow mu trig sets weight to 0 up to 26 pt
# testing it:
print 'testing mu trg on 25 25.5 26 26.5 GeV pt and 0 eta'
print 'B', muon_effs_trg_BCDEF_histo.GetBinContent(muon_effs_trg_BCDEF_histo.FindBin(25, 0)), muon_effs_trg_BCDEF_histo.GetBinContent(muon_effs_trg_BCDEF_histo.FindBin(25.5, 0)), muon_effs_trg_BCDEF_histo.GetBinContent(muon_effs_trg_BCDEF_histo.FindBin(26, 0)), muon_effs_trg_BCDEF_histo.GetBinContent(muon_effs_trg_BCDEF_histo.FindBin(26.5, 0))
print 'H', muon_effs_trg_GH_histo.GetBinContent(muon_effs_trg_GH_histo.FindBin(25, 0)), muon_effs_trg_GH_histo.GetBinContent(muon_effs_trg_GH_histo.FindBin(25.5, 0)), muon_effs_trg_GH_histo.GetBinContent(muon_effs_trg_GH_histo.FindBin(26, 0)), muon_effs_trg_GH_histo.GetBinContent(muon_effs_trg_GH_histo.FindBin(26.5, 0))

# and one of the weights sets 0 after 120 GeV now

print type(muon_effs_trg_BCDEF_file)

muon_effs_id_BCDEF_histo_max_x  = muon_effs_id_BCDEF_histo.GetXaxis().GetXmax()
muon_effs_iso_BCDEF_histo_max_x = muon_effs_iso_BCDEF_histo.GetXaxis().GetXmax()
muon_effs_id_BCDEF_histo_min_x  = muon_effs_id_BCDEF_histo.GetXaxis().GetXmin()
muon_effs_iso_BCDEF_histo_min_x = muon_effs_iso_BCDEF_histo.GetXaxis().GetXmin()

muon_effs_id_BCDEF_histo_max_y  = muon_effs_id_BCDEF_histo.GetYaxis().GetXmax()
muon_effs_iso_BCDEF_histo_max_y = muon_effs_iso_BCDEF_histo.GetYaxis().GetXmax()
muon_effs_id_BCDEF_histo_min_y  = muon_effs_id_BCDEF_histo.GetYaxis().GetXmin()
muon_effs_iso_BCDEF_histo_min_y = muon_effs_iso_BCDEF_histo.GetYaxis().GetXmin()

print "muon eff ID ISO BCDEF", muon_effs_id_BCDEF_histo_min_x, muon_effs_id_BCDEF_histo_max_x, muon_effs_id_BCDEF_histo_min_y, muon_effs_id_BCDEF_histo_max_y, muon_effs_iso_BCDEF_histo_min_x, muon_effs_iso_BCDEF_histo_max_x, muon_effs_iso_BCDEF_histo_min_y, muon_effs_iso_BCDEF_histo_max_y

muon_effs_id_GH_histo_max_x  = muon_effs_id_GH_histo.GetXaxis().GetXmax()
muon_effs_iso_GH_histo_max_x = muon_effs_iso_GH_histo.GetXaxis().GetXmax()
muon_effs_id_GH_histo_min_x  = muon_effs_id_GH_histo.GetXaxis().GetXmin()
muon_effs_iso_GH_histo_min_x = muon_effs_iso_GH_histo.GetXaxis().GetXmin()

muon_effs_id_GH_histo_max_y  = muon_effs_id_GH_histo.GetYaxis().GetXmax()
muon_effs_iso_GH_histo_max_y = muon_effs_iso_GH_histo.GetYaxis().GetXmax()
muon_effs_id_GH_histo_min_y  = muon_effs_id_GH_histo.GetYaxis().GetXmin()
muon_effs_iso_GH_histo_min_y = muon_effs_iso_GH_histo.GetYaxis().GetXmin()

print "muon eff ID ISO GH", muon_effs_id_GH_histo_min_x, muon_effs_id_GH_histo_max_x, muon_effs_id_GH_histo_min_y, muon_effs_id_GH_histo_max_y, muon_effs_iso_GH_histo_min_x, muon_effs_iso_GH_histo_max_x, muon_effs_iso_GH_histo_min_y, muon_effs_iso_GH_histo_max_y

h_weight_mu_trk_bcdef_pt = TH1D("weight_mu_trk_bcdef_pt", "", 50, 0, 200)
h_weight_mu_idd_bcdef_pt = TH1D("weight_mu_idd_bcdef_pt", "", 50, 0, 200)
h_weight_mu_iso_bcdef_pt = TH1D("weight_mu_iso_bcdef_pt", "", 50, 0, 200)
h_weight_mu_trg_bcdef_pt = TH1D("weight_mu_trg_bcdef_pt", "", 50, 0, 200)

h_weight_mu_trk_bcdef_eta = TH1D("weight_mu_trk_bcdef_eta", "", 50, 0, 3)
h_weight_mu_idd_bcdef_eta = TH1D("weight_mu_idd_bcdef_eta", "", 50, 0, 3)
h_weight_mu_iso_bcdef_eta = TH1D("weight_mu_iso_bcdef_eta", "", 50, 0, 3)
h_weight_mu_trg_bcdef_eta = TH1D("weight_mu_trg_bcdef_eta", "", 50, 0, 3)

#
#h_weight_mu_idd_bcdef_nbins = TH2D("weight_mu_idd_bcdef_nbins", "", 100, 0, muon_effs_id_BCDEF_histo.GetSize(), 100, 0, muon_effs_id_BCDEF_histo.GetSize())

'''
reco*ID*ISO*Trigger
-- some can be missing
histos can be 1D or 2D, or with vtx
-- the inputs are pt, eta and vtx, there can be only 3 topologies of the call

the access is TFile/TDir/THisto

there can be several Run epochs, which must be taken in arithmetical average

the histo might or might not have the oveerflows for the leptons ourside the range of the bins

trigger must be separate, because we do not always trigger on all leptons

I need to
open histos,
not prepare range-handling for now!
calculate weights for each correction according to the particular prescription
multiply them,
average epochs

-- let's make a couple helpers and implement the rest in a function with loop etc
'''

class GeneralLeptonSF_21:
    def __init__(self, histo_path_pt_eta=None, histo_path_vtx=None, invert_call=False, protect_range=True):
        '''
        the format is filename/path/to/histo
        '''

        self.file_pt_eta = None
        self.file_vtx    = None
        self.histo_pt_eta = None
        self.histo_vtx    = None
        self.histo_pt_eta_range = None
        self.histo_vtx_range    = None
        self.invert_call = invert_call

        if histo_path_pt_eta:
            filename_pt_eta, path_pt_eta = histo_path_pt_eta
            self.file_pt_eta  = TFile(filename_pt_eta)
            self.histo_pt_eta = self.file_pt_eta.Get(path_pt_eta)

            if protect_range:
                # min, max
                self.histo_pt_eta_range = (self.histo_pt_eta.GetXaxis().GetXmin()+0.001, self.histo_pt_eta.GetXaxis().GetXmax()-0.001), \
                    (self.histo_pt_eta.GetYaxis().GetXmin()+0.001, self.histo_pt_eta.GetYaxis().GetXmax()-0.001)

        if histo_path_vtx:
            filename_vtx = histo_path_vtx.split('/')[0]
            path_vtx     = '/'.join(histo_path_vtx.split('/')[1:])
            self.file_vtx  = TFile(filename_vtx)
            self.histo_vtx = self.file_vtx.Get(path_vtx)

            if protect_range:
                self.histo_vtx_range = self.histo_vtx.GetXaxis().GetXmin()+0.001, self.histo_vtx.GetXaxis().GetXmax()-0.001

    def __call__(self, pt_or_eta, eta_or_pt, vtx=None):
        '''(pt_or_eta, eta_or_pt, vtx=None)

        return weight, weight_uncertainty
        '''

        weight_pt_eta     = 1.
        weight_pt_eta_unc = 0.
        if self.histo_pt_eta:
            x, y = (eta_or_pt, pt_or_eta) if self.invert_call else (pt_or_eta, eta_or_pt)

            if self.histo_pt_eta_range is not None:
                (x_min, x_max), (y_min, y_max) = self.histo_pt_eta_range
                if x < x_min: x = x_min
                if x > x_max: x = x_max
                if y < y_min: y = y_min
                if y > y_max: y = y_max

            weight_pt_eta_bin = self.histo_pt_eta.FindBin(x, y)
            weight_pt_eta     = self.histo_pt_eta.GetBinContent(weight_pt_eta_bin)
            weight_pt_eta_unc = self.histo_pt_eta.GetBinError(weight_pt_eta_bin)

        if vtx is None:
            return weight_pt_eta, weight_pt_eta_unc

        if self.histo_vtx_range is not None:
            vtx_min, vtx_max = self.histo_vtx_range
            if vtx < vtx_min: vtx = vtx_min
            if vtx > vtx_max: vtx = vtx_max

        if self.histo_vtx:
            weight_vtx_bin = self.histo_vtx.FindBin(vtx)
            weight_vtx     = self.histo_vtx.GetBinContent(weight_vtx_bin)
            weight_vtx_unc = self.histo_vtx.GetBinError(weight_vtx_bin)

        return weight_pt_eta * weight_vtx, sqrt(weight_pt_eta_unc**2 + weight_vtx_unc**2)

'''
muon-effs/Run2017-Nov17_Re-Reco_RunBCDEF_SF_ID_syst_preliminary.root
muon-effs/Run2017-Nov17_Re-Reco_RunBCDEF_SF_ISO_syst_preliminary.root
muon-effs/Run2017-Nov17_Re-Reco_Trigger_EfficienciesAndSF_RunBtoF_Nov17Nov2017.root
'''

lepton_muon_SF_2017_v1_ID  = GeneralLeptonSF_21(('common_info/muon-effs/Run2017-Nov17_Re-Reco_RunBCDEF_SF_ID_syst_preliminary.root',  'NUM_TightID_DEN_genTracks_pt_abseta'))
lepton_muon_SF_2017_v1_ISO = GeneralLeptonSF_21(('common_info/muon-effs/Run2017-Nov17_Re-Reco_RunBCDEF_SF_ISO_syst_preliminary.root', 'NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta'))
lepton_muon_SF_2017_v1_Trg = GeneralLeptonSF_21(('common_info/muon-effs/Run2017-Nov17_Re-Reco_Trigger_EfficienciesAndSF_RunBtoF_Nov17Nov2017.root',  'IsoMu27_PtEtaBins/pt_abseta_ratio'))

def lepton_muon_SF_2017_v1(pt, eta):
    '''
    the standardized output format, with the epochs are accounted for

    old format:
    return bcdef_weight_trk * bcdef_weight_trk_vtx_gen, trk_gen_unc_bcdef, bcdef_weight_trk_vtx, (bcdef_weight_id, bcdef_weight_id_unc), (bcdef_weight_iso, bcdef_weight_iso_unc)

    return (trk, unc), (id, unc), (iso, unc)
    '''

    abseta = abs(eta)
    return (1., 0.), lepton_muon_SF_2017_v1_ID(pt, abseta), lepton_muon_SF_2017_v1_ISO(pt, abseta)

def lepton_muon_SF_2017_v1_trigger(pt, eta):
    abseta = abs(eta)
    return lepton_muon_SF_2017_v1_Trg(pt, abseta)


lepton_electron_SF_2017_v1_RECO = GeneralLeptonSF_21(('common_info/electron-effs/2017_Fall17-94X-V1_egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root', 'EGamma_SF2D'), invert_call=True)
lepton_electron_SF_2017_v1_ID   = GeneralLeptonSF_21(('common_info/electron-effs/2017_Fall17-94X-V1_egammaEffi.txt_EGM2D_runBCDEF_passingTight94X.root', 'EGamma_SF2D'), invert_call=True)

lepton_electron_SF_2017_v1_Trg  = GeneralLeptonSF_21(('common_info/electron-effs//2016_03Feb_TriggerSF_Run2016All_v1.root', 'Ele27_WPTight_Gsf'))

def lepton_electron_SF_2017_v1(pt, eta):
    '''
    the standardized output format, with the epochs are accounted for

    return (trk, unc), (id, unc), (iso, unc)
    '''

    return lepton_electron_SF_2017_v1_RECO(pt, eta), lepton_electron_SF_2017_v1_ID(pt, eta), (1., 0.)

def lepton_electron_SF_2017_v1_trigger(pt, eta):
    return lepton_electron_SF_2017_v1_Trg(pt, eta)





def lepton_muon_SF(eta, pt, vtx, vtx_gen): #SingleMuon_data_bcdef_fraction, SingleMuon_data_gh_fraction):
    abs_eta = abs(eta)
    #weight *= 0.98; // average mu trig SF
    #weight *= 0.97; // average mu ID
    weight_muon_sfs = 1

    # muon ID SFs:
    #double weight_muon_sfs = 1;
    bcdef_weight = 1
    gh_weight = 1
    #double SingleMuon_data_bcdef_fraction = 19716.274 / (19716.274 + 15931.028);
    #double SingleMuon_data_gh_fraction    = 15931.028 / (19716.274 + 15931.028);

    #double abs_eta = abs(lep0_eta);
    #double pt = lep0_pt;

    # hopefully tracking won't overflow in eta range:
    bcdef_weight_trk     = muon_effs_tracking_BCDEF_graph.Eval(abs_eta)
    bcdef_weight_trk_vtx = muon_effs_tracking_BCDEF_graph_vtx.Eval(vtx)
    bcdef_weight_trk_vtx_gen = muon_effs_tracking_BCDEF_graph_vtx.Eval(vtx_gen)

    # uncertainty (statistical from the SF study?)
    trk_gen_unc_bcdef = 0. # muon_effs_tracking_BCDEF_graph.GetErrorY(abs_eta)
    #trk_gen_unc_bcdef = sqrt(trk_gen_unc_bcdef**2 + muon_effs_tracking_BCDEF_graph_vtx.GetErrorY(vtx_gen)**2)
    #h_weight_mu_trk_bcdef_pt = TH1D("weight_mu_trk_bcdef_pt", "", 50, 0, 200),
    h_weight_mu_trk_bcdef_eta.Fill(abs_eta)

    # the id-s totally can overflow:
    if   pt < muon_effs_id_BCDEF_histo_min_x:
      bin_x = muon_effs_id_BCDEF_histo_min_x + 0.01
    elif pt > muon_effs_id_BCDEF_histo_max_x:
      bin_x = muon_effs_id_BCDEF_histo_max_x - 1
    else:
      bin_x = pt

    bin_y = abs_eta if abs_eta < muon_effs_id_BCDEF_histo_max_y else muon_effs_id_BCDEF_histo_max_y - 0.01 # checked. the binnint is about 0.2 there
    id_bin = muon_effs_id_BCDEF_histo.FindBin(bin_x, bin_y)
    bcdef_weight_id     = muon_effs_id_BCDEF_histo.GetBinContent (id_bin)
    bcdef_weight_id_unc = muon_effs_id_BCDEF_histo.GetBinError   (id_bin)
    # adding systematics
    bcdef_weight_id_unc = sqrt(bcdef_weight_id_unc**2 + muon_unc_sys_id**2)
    # leftover from tests
    #h_weight_mu_idd_bcdef_pt .Fill(bin_x)
    #h_weight_mu_idd_bcdef_eta.Fill(bin_y)

    # and add vtx ID SF
    #bcdef_weight_id     *= muon_effs_id_vtx_BCDEF_histo.GetBinContent (muon_effs_id_vtx_BCDEF_histo.FindBin(vtx))
    bcdef_weight_id     *= muon_effs_id_vtx_BCDEF_histo.GetBinContent (muon_effs_id_vtx_BCDEF_histo.FindBin(vtx_gen))

    # these too:
    if   pt < muon_effs_iso_BCDEF_histo_min_x:
      bin_x = muon_effs_iso_BCDEF_histo_min_x + 0.01
    elif pt > muon_effs_iso_BCDEF_histo_max_x:
      bin_x = muon_effs_iso_BCDEF_histo_max_x - 1
    else:
      bin_x = pt

    bin_y = abs_eta if abs_eta < muon_effs_iso_BCDEF_histo_max_y else muon_effs_iso_BCDEF_histo_max_y - 0.01
    iso_bin = muon_effs_iso_BCDEF_histo.FindBin(bin_x, bin_y)
    bcdef_weight_iso     = muon_effs_iso_BCDEF_histo.GetBinContent (iso_bin)
    bcdef_weight_iso_unc = muon_effs_iso_BCDEF_histo.GetBinError   (iso_bin)
    # adding systematic
    bcdef_weight_iso_unc = sqrt(bcdef_weight_iso_unc**2 + muon_unc_sys_iso**2)
    # leftover from tests
    #h_weight_mu_iso_bcdef_pt .Fill(bin_x)
    #h_weight_mu_iso_bcdef_eta.Fill(bin_y)
    #bin_x = (pt < muon_effs_iso_BCDEF_histo->GetXaxis()->GetXmax()      ? pt : muon_effs_iso_BCDEF_histo->GetXaxis()->GetXmax() - 1);
    #bin_y = (abs_eta < muon_effs_iso_BCDEF_histo->GetYaxis()->GetXmax() ? abs_eta : muon_effs_iso_BCDEF_histo->GetYaxis()->GetXmax() - 1);
    #bcdef_weight_iso = muon_effs_iso_BCDEF_histo->GetBinContent (muon_effs_iso_BCDEF_histo->FindBin(bin_x, bin_y));

    # and vtx
    #bcdef_weight_iso     *= muon_effs_iso_vtx_BCDEF_histo.GetBinContent (muon_effs_iso_vtx_BCDEF_histo.FindBin(vtx))
    bcdef_weight_iso     *= muon_effs_iso_vtx_BCDEF_histo.GetBinContent (muon_effs_iso_vtx_BCDEF_histo.FindBin(vtx_gen))

    #fill_1d(string("weight_muon_effs_BCDEF_trk"),  200, 0., 1.1,   bcdef_weight_trk, 1);
    #fill_1d(string("weight_muon_effs_BCDEF_id"),   200, 0., 1.1,   bcdef_weight_id,  1);
    #fill_1d(string("weight_muon_effs_BCDEF_iso"),  200, 0., 1.1,   bcdef_weight_iso, 1);
    #bcdef_weight *= bcdef_weight_trk * bcdef_weight_id * bcdef_weight_iso;

    gh_weight_trk     = muon_effs_tracking_GH_graph    .Eval(abs_eta)
    gh_weight_trk_vtx = muon_effs_tracking_GH_graph_vtx.Eval(vtx)
    gh_weight_trk_vtx_gen = muon_effs_tracking_GH_graph_vtx.Eval(vtx_gen)
    #h_weight_mu_trk_gh_eta.Fill(abs_eta)
    trk_gen_unc_gh = 0. # muon_effs_tracking_GH_graph.GetErrorY(abs_eta)
    #trk_gen_unc_gh = sqrt(trk_gen_unc_gh**2 + muon_effs_tracking_GH_graph_vtx.GetErrorY(vtx_gen)**2)

    # the id-s totally can overflow:
    if   pt < muon_effs_id_GH_histo_min_x:
      bin_x = muon_effs_id_GH_histo_min_x + 0.01
    elif pt > muon_effs_id_GH_histo_max_x:
      bin_x = muon_effs_id_GH_histo_max_x - 1
    else:
      bin_x = pt

    bin_y = abs_eta if abs_eta < muon_effs_id_GH_histo_max_y else muon_effs_id_GH_histo_max_y - 0.01
    id_bin = muon_effs_id_GH_histo.FindBin(bin_x, bin_y)
    gh_weight_id     = muon_effs_id_GH_histo.GetBinContent (id_bin)
    gh_weight_id_unc = muon_effs_id_GH_histo.GetBinError   (id_bin)
    # adding systematic
    gh_weight_id_unc = sqrt(gh_weight_id_unc**2 + muon_unc_sys_id**2)
    #h_weight_mu_idd_gh_pt .Fill(bin_x)
    #h_weight_mu_idd_gh_eta.Fill(bin_y)

    #gh_weight_id     *= muon_effs_id_vtx_GH_histo.GetBinContent (muon_effs_id_vtx_GH_histo.FindBin(vtx))
    gh_weight_id     *= muon_effs_id_vtx_GH_histo.GetBinContent (muon_effs_id_vtx_GH_histo.FindBin(vtx_gen))

    # these too:
    if   pt < muon_effs_iso_GH_histo_min_x:
      bin_x = muon_effs_iso_GH_histo_min_x + 0.01
    elif pt > muon_effs_iso_GH_histo_max_x:
      bin_x = muon_effs_iso_GH_histo_max_x - 1
    else:
      bin_x = pt

    bin_y = abs_eta if abs_eta < muon_effs_iso_GH_histo_max_y else muon_effs_iso_GH_histo_max_y - 0.01
    iso_bin = muon_effs_iso_GH_histo.FindBin(bin_x, bin_y)
    gh_weight_iso     = muon_effs_iso_GH_histo.GetBinContent (iso_bin)
    gh_weight_iso_unc = muon_effs_iso_GH_histo.GetBinError   (iso_bin)
    # adding systematic
    gh_weight_iso_unc = sqrt(gh_weight_iso_unc**2 + muon_unc_sys_iso**2)
    #h_weight_mu_iso_gh_pt .Fill(bin_x)
    #h_weight_mu_iso_gh_eta.Fill(bin_y)

    #gh_weight_iso     *= muon_effs_iso_vtx_GH_histo.GetBinContent (muon_effs_iso_vtx_GH_histo.FindBin(vtx))
    gh_weight_iso     *= muon_effs_iso_vtx_GH_histo.GetBinContent (muon_effs_iso_vtx_GH_histo.FindBin(vtx_gen))

    # for tracking 0 and 1 are used now
    return (bcdef_weight_trk * bcdef_weight_trk_vtx_gen, trk_gen_unc_bcdef, bcdef_weight_trk_vtx, (bcdef_weight_id, bcdef_weight_id_unc), (bcdef_weight_iso, bcdef_weight_iso_unc)), \
           (gh_weight_trk    * gh_weight_trk_vtx_gen,    trk_gen_unc_gh,    gh_weight_trk_vtx,    (gh_weight_id, gh_weight_id_unc), (gh_weight_iso, gh_weight_iso_unc))


muon_effs_trg_BCDEF_histo_max_x = muon_effs_trg_BCDEF_histo.GetXaxis().GetXmax()
muon_effs_trg_BCDEF_histo_max_y = muon_effs_trg_BCDEF_histo.GetYaxis().GetXmax()
muon_effs_trg_BCDEF_histo_min_x = muon_effs_trg_BCDEF_histo.GetXaxis().GetXmin()
muon_effs_trg_BCDEF_histo_min_y = muon_effs_trg_BCDEF_histo.GetYaxis().GetXmin()

print 'muon effs trg BCDEF (assume the same for GH)', muon_effs_trg_BCDEF_histo_min_x, muon_effs_trg_BCDEF_histo_max_x, muon_effs_trg_BCDEF_histo_min_y, muon_effs_trg_BCDEF_histo_max_y

# MUON Trigger
#double lepton_muon_trigger_SF ()
def lepton_muon_trigger_SF(eta, pt): #, double SingleMuon_data_bcdef_fraction, double SingleMuon_data_gh_fraction)
    abs_eta = abs(eta)
    no_mu_trig = 1;
    #double mu_trig_weight = 1;
    # calculate it the inverse-probbility way
    #double abs_eta = abs(NT_lep_eta_0);
    #double pt = NT_lep_pt_0;
    if   pt <= muon_effs_trg_BCDEF_histo_min_x:
      bin_x  = muon_effs_trg_BCDEF_histo_min_x + 0.01
    elif pt >= muon_effs_trg_BCDEF_histo_max_x:
      bin_x  = muon_effs_trg_BCDEF_histo_max_x - 0.01
    else:
      bin_x = pt

    if   abs_eta <= muon_effs_trg_BCDEF_histo_min_y:
           bin_y  = muon_effs_trg_BCDEF_histo_min_y + 0.01
    elif abs_eta >= muon_effs_trg_BCDEF_histo_max_y:
           bin_y  = muon_effs_trg_BCDEF_histo_max_y - 0.01
    else:
           bin_y = abs_eta
    #no_mu_trig *= SingleMuon_data_bcdef_fraction * (1 - muon_effs_trg_BCDEF_histo->GetBinContent( muon_effs_trg_BCDEF_histo->FindBin(bin_x, bin_y) )) +
    #        SingleMuon_data_gh_fraction * (1 - muon_effs_trg_GH_histo->GetBinContent( muon_effs_trg_GH_histo->FindBin(bin_x, bin_y) ));
    #mu_trig_weight = 1 - no_trig; // so for 1 muon it will = to the SF, for 2 there will be a mix
    #fill_1d(string("weight_trigger_no_muon"),  200, 0., 1.1,   no_mu_trig, 1);

    # from tests
    #h_weight_mu_trg_bcdef_pt .Fill(bin_x)
    #h_weight_mu_trg_bcdef_eta.Fill(bin_y)

    #weight_muon_trig = 1 - no_mu_trig;
    trg_bin_b = muon_effs_trg_BCDEF_histo.FindBin(bin_x, bin_y)
    trg_bin_h = muon_effs_trg_GH_histo.FindBin(bin_x, bin_y)

    bcdef_trg_unc = muon_effs_trg_BCDEF_histo .GetBinError(trg_bin_b)
    gh_trg_unc    = muon_effs_trg_GH_histo    .GetBinError(trg_bin_h)
    # adding systematics
    bcdef_trg_unc = sqrt( bcdef_trg_unc**2 + muon_unc_sys_trg**2)
    gh_trg_unc    = sqrt(    gh_trg_unc**2 + muon_unc_sys_trg**2)
    return (muon_effs_trg_BCDEF_histo.GetBinContent(trg_bin_b), bcdef_trg_unc), (muon_effs_trg_GH_histo.GetBinContent(trg_bin_h), gh_trg_unc)


def dilepton_or_sfs(eff1, unc1, eff2, unc2):
    """dilepton_sfs(eff1, unc1, eff2, unc2)

    use for the case of OR selection on 2 leptons,
    like single-muon HLT on 2 muons:
    """

    eff = 1. - (1. - eff1) * (1. - eff2)
    unc = unc1*(1. - eff2) + unc2*(1. - eff1)
    # differencials for the uncertainties
    # d(mu_trg_sf_b1)(1 - mu_trg_sf_b2) + d(mu_trg_sf_b2)(1 - mu_trg_sf_b1)

    return eff, unc

def dilepton_and_sfs(eff1, unc1, eff2, unc2):
    """dilepton_and_sfs(eff1, unc1, eff2, unc2)

    the SFs for an AND of 2 identical leptons, like the IDs in mumu or elel
    """

    eff = eff1*eff2
    unc = unc1*eff2 + eff1*unc2

    return eff, unc


'''
 ---------------------------------------------------
 now, electrons have
      track(reconstruction) efficiency
      and ID sf
      also trigger

 https://twiki.cern.ch/twiki/bin/view/CMS/EgammaIDRecipesRun2#Efficiencies_and_scale_factors
 > The value can be access with usual GetBinContent and the recommended systematic is the error (GetBinError).
 > The pT range is limited to 150GeV. For pT > 150 GeV the highest pT bin scale factor should to be used.
 -- more logic here!

 presentation on HLTs:
 https://indico.cern.ch/event/604912/#3-sf-of-hlt_ele25_eta2p1_wptig
 slide 25 "Summary"
 > Bin errors (TH1::GetBinError) give full uncertainties
 -- and more logic!

 the trig eff for dilepton case is: apply negative of it for both leptons

root -l ../lab_log/electron-effs//2016_Sept23_ElectronReconstructionSF_egammaEffi.txt_EGM2D.root
root -l ../lab_log/electron-effs//2016_Sept23_ElectronID_TightCutBased_egammaEffi.txt_EGM2D.root
root -l ../lab_log/electron-effs//2016_03Feb_TriggerSF_Run2016All_v1.root

EGamma_EffData2D->GetZaxis()->SetRangeUser(0.9,1.1)
EGamma_SF2D->GetZaxis()->SetRangeUser(0.9,1.1)
Ele27_WPTight_Gsf->GetZaxis()->SetRangeUser(0.8,1.2)

EGamma_SF2D->Draw("colz")
EGamma_SF2D->Draw("colz")
Ele27_WPTight_Gsf->Draw("colz")

gStyle->SetPaintTextFormat("4.2f")

EGamma_SF2D->Draw("colz text")
Ele27_WPTight_Gsf->Draw("colz text")
'''

logging.info("unpacking electron eff SFs")

electron_effs_dirname = "${CMSSW_BASE}/src/UserCode/proc/common_info/electron-effs"
gSystem.ExpandPathName(electron_effs_dirname)

electron_effs_tracking_all_file  = TFile(electron_effs_dirname + "/2016_Sept23_ElectronReconstructionSF_egammaEffi.txt_EGM2D.root")
electron_effs_tracking_all_histo = electron_effs_tracking_all_file.Get("EGamma_SF2D")
logging.info("Y tracking (reconstruction)")

# for the selected electrons, Tight ID
# not for Veto
electron_effs_id_all_file  = TFile(electron_effs_dirname + "/2016_Sept23_ElectronID_TightCutBased_egammaEffi.txt_EGM2D.root")
electron_effs_id_all_histo = electron_effs_id_all_file.Get("EGamma_SF2D")
logging.info("Y id")

#lab_log/electron-effs/2016_03Feb_TriggerSF_Run2016All_v1.root
electron_effs_trg_all_file  = TFile(electron_effs_dirname + "/2016_03Feb_TriggerSF_Run2016All_v1.root")
electron_effs_trg_all_histo = electron_effs_trg_all_file.Get("Ele27_WPTight_Gsf")
logging.info("Y trigger")

# --- these SFs will be applied to the selected leptons independently

electron_effs_tracking_all_histo_max_y = electron_effs_tracking_all_histo.GetYaxis().GetXmax()
electron_effs_tracking_all_histo_min_y = electron_effs_tracking_all_histo.GetYaxis().GetXmin()
electron_effs_id_all_histo_max_y = electron_effs_id_all_histo.GetYaxis().GetXmax()
electron_effs_id_all_histo_min_y = electron_effs_id_all_histo.GetYaxis().GetXmin()

h_weight_el_trk_pt = TH1D("weight_mu_trk_bcdef_pt", "", 50, 0, 200)
h_weight_el_idd_pt = TH1D("weight_mu_idd_bcdef_pt", "", 50, 0, 200)
h_weight_mu_iso_bcdef_pt = TH1D("weight_mu_iso_bcdef_pt", "", 50, 0, 200)
h_weight_mu_trg_bcdef_pt = TH1D("weight_mu_trg_bcdef_pt", "", 50, 0, 200)

def lepton_electron_SF(eta, pt):
    #double weight_reco, weight_id;

    # here X axis is eta, Y axis is pt
    # X is from -2.5 to 2.5 -- our eta is up to 2.4 (2.5 in wide ntuples), should be ok
    #double bin_x = (pt < electron_effs_tracking_all_histo->GetXaxis()->GetXmax()      ? pt : muon_effs_id_BCDEF_histo->GetXaxis()->GetXmax() - 1);
    if   eta >=  2.5: bin_x =  2.499
    elif eta <= -2.5: bin_x = -2.499
    else: bin_x = eta

    if   pt >= electron_effs_tracking_all_histo_max_y:
      bin_y  = electron_effs_tracking_all_histo_max_y - 0.01
    elif pt <= electron_effs_tracking_all_histo_min_y:
      bin_y  = electron_effs_tracking_all_histo_min_y + 0.01
    else:
      bin_y = pt
    reco_bin = electron_effs_tracking_all_histo.FindBin(bin_x, bin_y)
    sf_reco     = electron_effs_tracking_all_histo.GetBinContent (reco_bin)
    sf_reco_unc = electron_effs_tracking_all_histo.GetBinError   (reco_bin)

    #bin_x = eta;
    if   pt > electron_effs_id_all_histo_max_y:
      bin_y = electron_effs_id_all_histo_max_y - 0.01
    elif pt < electron_effs_id_all_histo_min_y:
      bin_y = electron_effs_id_all_histo_min_y + 0.01
    else:
      bin_y = pt
    id_bin = electron_effs_id_all_histo.FindBin(bin_x, bin_y)
    sf_id     = electron_effs_id_all_histo.GetBinContent (id_bin)
    sf_id_unc = electron_effs_id_all_histo.GetBinError   (id_bin)

    return (sf_reco, sf_reco_unc), (sf_id, sf_id_unc)

electron_effs_trg_all_histo_max_x = electron_effs_trg_all_histo.GetXaxis().GetXmax()
electron_effs_trg_all_histo_max_y = electron_effs_trg_all_histo.GetYaxis().GetXmax()
electron_effs_trg_all_histo_min_x = electron_effs_trg_all_histo.GetXaxis().GetXmin()

def lepton_electron_trigger_SF(eta, pt):
    #double no_ele_trig = 1;
    # (calculate it the inverse-probbility way)
    # no, just return the SF, assume 1-lepton case
    #pat::Electron& el = selElectrons[i];
    #double eta = el.superCluster()->position().eta();
    #double pt = el.pt();
    # here X axis is pt, Y axis is eta (from -2.5 to 2.5)
    # TODO: actually need to check the ROOT thing here -- does max bin actually fall within the hist range?
    if   pt >= electron_effs_trg_all_histo_max_x:
        bin_x = electron_effs_trg_all_histo_max_x - 1
    elif pt <= electron_effs_trg_all_histo_min_x:
        bin_x = electron_effs_trg_all_histo_min_x + 0.01
    else:
        bin_x = pt

    if eta >= electron_effs_trg_all_histo_max_y:
        bin_y = electron_effs_trg_all_histo_max_y - 0.01
    elif eta <= - electron_effs_trg_all_histo_max_y:
        bin_y = - electron_effs_trg_all_histo_max_y + 0.01
    else:
        bin_y = eta

    trg_bin = electron_effs_trg_all_histo.FindBin(bin_x, bin_y)
    return electron_effs_trg_all_histo.GetBinContent(trg_bin), electron_effs_trg_all_histo.GetBinError(trg_bin)
    #el_trig_weight = 1 - no_trig; // so for 1 lepton it will = to the SF, for 2 there will be a mix
    #fill_1d(string("weight_trigger_no_electron"),  200, 0., 1.1,   no_ele_trig, 1);


if __name__ == '__main__':
    from os.path import isfile, basename
    from sys import exit

    # args are parsed before the import of ROOT
    if args.test_sfs:
        # test
        test_points  = [(-2.5, 89.), (-2.4, 89.), (-2.1, 89.), (-1.1, 89.), (-0.1, 89.), (0.1, 89.), (1.1, 89.), (2.1, 89.), (2.4, 89.), (2.5, 89.)]
        test_points += [(1.0, 10), (1.0, 20), (1.0, 24), (1.0, 26), (1.0, 28), (1.0, 30), (1.0, 50), (1.0, 80), (1.0, 150)]
        for name, func in [('lepton_electron_SF_2017_v1',         lepton_electron_SF_2017_v1),
                           ('lepton_electron_SF_2017_v1_trigger', lepton_electron_SF_2017_v1_trigger),
                           ('lepton_muon_SF_2017_v1',         lepton_muon_SF_2017_v1),
                           ('lepton_muon_SF_2017_v1_trigger', lepton_muon_SF_2017_v1_trigger)]:
          for eta, pt in test_points:
            print ("%50s" % name), pt, eta, func(pt, eta)

        exit(0)

    trig_sf = TH1D("el_trig_sf", "", 100, 0., 2.)

    for filename in args.input_files:
        if not isfile(filename):
            logging.info("missing: " + filename)
            continue

        logging.debug(filename)

        tfile = TFile(filename)
        ttree = tfile.Get("ntupler/reduced_ttree")

        for iev, ev in enumerate(ttree):
            #if iev > 1000: break
            # only elmu selection
            pass_elmu_id = ev.leps_ID == -11*13 and ev.HLT_mu and ev.no_iso_veto_leps and \
                ev.lep_matched_HLT[0] and \
                (ev.lep_p4[0].pt() > 30 and abs(ev.lep_p4[0].eta()) < 2.4) and \
                (ev.lep_p4[1].pt() > 30 and abs(ev.lep_p4[1].eta()) < 2.4)

            if not pass_elmu_id: continue

            scale_factor = lepton_electron_trigger_SF(abs(ev.lep_p4[1].eta()), ev.lep_p4[1].pt())[0]
            trig_sf.Fill(scale_factor)

        tfile.Close()

    #
    trig_sf.Print()

    fout = TFile(args.output_file, "RECREATE")
    fout.Write()
    
    trig_sf        .Write()
    
    fout.Write()
    fout.Close()



