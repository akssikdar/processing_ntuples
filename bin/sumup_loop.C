/**
\file sumup_loop_up.C
\mainpage The sumup_loop plotting routine.
\brief A flexible plotting program.

The program defines a set of objects (functions, struct-s, map-s, vectors etc)
to be used in the construction of the event loop in the `main` function.
These objects basically define the information about the input datasets,
distributions to record, systematics to apply etc.
They correspond to the old `std_defs.py` module.

The `main` function operates on the defined objects and consists of 3 parts:

1. parsing user's input and filling up the data structures operating the event loop
2. the event loop
3. application of final systematic corrections and normalizations to the recorded histograms and writing the output.

# Naming style

The beginning of the `typedef` names has 1 capital letter mnemonic for the defined type: S for struct, F for function, T for any other type.
The names starting with underscore, such as `_TH1D_histo_def` are not intendet to be used in `main` directly.
The collections of definitions for `main` start with `known_`, like `known_dtags_info`.
The corresponding functions defining these collections start with `create_known_`, like `create_known_dtags_info`.

Now, the names of the functions operating in the namespace of the interface of the TTree, i.e. on variables like `NT_event_leptons`,
start with `NT_` like `NT_distr_leading_lep_pt`.
In future we may try to separate them in an altogether different namespace,
with a separate function to connect an input TTree to that namespace etc.
 */

#include <iostream>

#include "TSystem.h"
#include "TFile.h"
#include "TTree.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "THStack.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TH3F.h"
#include "TProfile.h"
#include "TProfile2D.h"
#include "TEventList.h"
#include "TROOT.h"
#include "TNtuple.h"
#include <Math/VectorUtil.h>

#include "TMath.h" // Cos

#include <map>
#include <string>
#include <vector>
#include <stdlib.h> // abort

#include "UserCode/processing_ntuples/interface/handy_macros.h"

#include "UserCode/processing_ntuples/interface/sumup_loop_ntuple.h"
#include "UserCode/processing_ntuples/interface/ntuple_stage2.h"
#include "UserCode/processing_ntuples/interface/ntuple_ntupler.h"

// the ntuple interface declarations
// to be connected to one of the ntuple_ interfaces in main
T_known_defs_systs    known_systematics;
T_known_defs_channels known_defs_channels;
T_known_defs_distrs   known_defs_distrs;

T_known_defs_procs    known_procs_info;

T_known_MC_normalization_per_somename    known_normalization_per_syst;
T_known_MC_normalization_per_somename    known_normalization_per_proc;
T_known_MC_normalization_per_somename    known_normalization_per_chan;

//typedef int (*F_connect_ntuple_interface)(TTree*);
F_connect_ntuple_interface connect_ntuple_interface;
// -----

using namespace std;

// TODO: turn these into arguments for main
bool do_not_overwrite     = true;
bool normalise_per_weight = true;

/* --------------------------------------------------------------- */
/* main structure of the event loop
// the struct-s of the structure of the event loop
// since systematics affect event selection (final state channel) and distributions
// they must be up the hierarchy
// process definition is purely gen-level, independent from reco
// it can be the top-most level for a dtag
// but in daily usage we usually hadd everything, open a final state and look at distributions in the same or different processes.
// Ok, purely for the sake of symmetry and easy memorization, let's just revert the nesting w.r.t the usual one:
SYSTEMATIC / PROCESS / CHANNEL / channel_process_systematic_distrname
*/



/** \brief An instance of an output histogram.

 The function calculating the parameter, the `TH1D*` to the histogram object, the current calculated value (placeholder for future memoization).
 */

typedef struct {
	string main_name;
	TH1D* histo;
	double (*func)(ObjSystematics);
	double value;
} TH1D_histo;



typedef struct{
	string name;               /**< \brief keep the name of this process to assign final per-proc normalization */
	_F_genproc_def proc_def;    /**< \brief `bool` function defining whether an event passes this gen proc definition */
	vector<TH1D_histo> histos;  /**< \brief the distributions to record */
} T_proc_histos;

typedef struct{
	string name;                 /**< \brief keep the name of this process to assign final per-channel normalization */
	_S_chan_def chan_def;         /**< \brief channel definition: `bool` function selecting events, and the nominal event weight funciton */
	vector<T_proc_histos> procs;  /**< \brief the channels with distributions to record */
	string name_catchall_proc;   /**< \brief the name of the catchall processes */
	vector<TH1D_histo> catchall_proc_histos;  /**< \brief the channels with distributions to record in the catchall process */
} T_chan_proc_histos;

typedef struct{
	string name;                      /**< \brief keep the name of this process to assign final per-systematic normalization */
	_S_systematic_definition syst_def; /**< \brief the definition of a given systematic */
	vector<T_chan_proc_histos> chans;  /**< \brief the per-proc channels with distributions to record */
} T_syst_chan_proc_histos;

/** \brief A helper function creating the instances of TH1D_histos with a specific name from the given _TH1D_histo_def definition.

Creates a `new TH1D(name, ..., range)` according to the linear or custom range in the _TH1D_histo_def definition.

\param  _TH1D_histo_def& def
\param  TString   name
\return TH1D_histo
 */

TH1D_histo create_TH1D_histo(_TH1D_histo_def& def, TString name, string main_name)
{
	TH1D* histo;
	if (def.range.linear)
		{
		//cout << "making linear bins histogram " << endl;
		histo = (TH1D*) new TH1D(name, name, def.range.nbins, def.range.linear_min, def.range.linear_max);
		}
	else
		{
		//cout << "making custom bins histogram " << def.range.nbins << " " << def.range.custom_bins << endl;
		histo = (TH1D*) new TH1D(name, name, def.range.nbins, def.range.custom_bins);
		//cout << "making custom bins histogram DONW" << endl;
		}
	//TH1D_histo a_distr = {ahist, def.func, 0.};
	//distrs.push_back(a_distr);
	return {main_name, histo, def.func, 0.};
}

/* --------------------------------------------------------------- */



// dtag info -- move to yet another src file
typedef struct {
	double       cross_section;
	double       usual_gen_lumi;
	_S_proc_ID_defs std_procs;
	vector<TString> std_systs;
	// all available systematics
} S_dtag_info;

double W_lep_br    = 0.108;
double W_alllep_br = 3*0.108;
double W_qar_br    = 0.676;

double W_lep_br2    = W_lep_br*W_lep_br;
double W_alllep_br2 = W_alllep_br*W_alllep_br;
double W_qar_br2    = W_qar_br*W_qar_br;

double br_tau_electron = 0.1785;
double br_tau_muon     = 0.1736;
double br_tau_lepton   = br_tau_electron + br_tau_muon;
double br_tau_hadronic = 1. - br_tau_lepton;

double ttbar_xsec = 831.76; // at 13 TeV

map<TString, S_dtag_info> create_known_dtags_info(T_known_defs_procs known_procs_info)
	{
	//map<const char*, S_dtag_info> m;
	map<TString, S_dtag_info> m;

	m["MC2017_Fall17_WJetsToLNu_13TeV"              ] = {.cross_section= 52940.                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["wjets"],
		.std_systs = {SYSTS_OTHER_MC}};

	m["MC2016_Summer16_WJets_madgraph"              ] = {.cross_section= 52940.                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["wjets"],
		.std_systs = {SYSTS_OTHER_MC}};
	m["MC2016_Summer16_W1Jets_madgraph"              ] = {.cross_section= 9493.                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["wjets"],
		.std_systs = {SYSTS_OTHER_MC}};
	m["MC2016_Summer16_W2Jets_madgraph"              ] = {.cross_section= 3120.                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["wjets"],
		.std_systs = {SYSTS_OTHER_MC}};
	m["MC2016_Summer16_W3Jets_madgraph"              ] = {.cross_section= 942.29999999999995                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["wjets"],
		.std_systs = {SYSTS_OTHER_MC}};
	m["MC2016_Summer16_W4Jets_madgraph"              ] = {.cross_section= 524.20000000000005                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["wjets"],
		.std_systs = {SYSTS_OTHER_MC}};

	m["MC2016_Summer16_QCD_HT-100-200"              ] = {.cross_section= 27540000 / 0.131                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["qcd"],
		.std_systs = {SYSTS_QCD_MC}};
	m["MC2016_Summer16_QCD_HT-200-300"              ] = {.cross_section= 1717000 / 0.098                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["qcd"],
		.std_systs = {SYSTS_QCD_MC}};
	m["MC2016_Summer16_QCD_HT-300-500"              ] = {.cross_section= 351300 / (0.088 * 100)                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["qcd"],
		.std_systs = {SYSTS_QCD_MC}};
	m["MC2016_Summer16_QCD_HT-500-700"              ] = {.cross_section= 31630 / (0.067 * 2)                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["qcd"],
		.std_systs = {SYSTS_QCD_MC}};
	m["MC2016_Summer16_QCD_HT-700-1000"              ] = {.cross_section= 6802 / (0.066 * 2)                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["qcd"],
		.std_systs = {SYSTS_QCD_MC}};
	m["MC2016_Summer16_QCD_HT-1000-1500"              ] = {.cross_section= 1206 * 10 / 0.059                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["qcd"],
		.std_systs = {SYSTS_QCD_MC}};
	m["MC2016_Summer16_QCD_HT-1500-2000"              ] = {.cross_section= 120.4 / 0.067                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["qcd"],
		.std_systs = {SYSTS_QCD_MC}};
	m["MC2016_Summer16_QCD_HT-2000-Inf"              ] = {.cross_section= 25.25  / 0.07                            ,
		.usual_gen_lumi= 23102470.188817,
		.std_procs = known_procs_info["qcd"],
		.std_systs = {SYSTS_QCD_MC}};

	// there is also MC2016_Summer16_DYJetsToLL_10to50_amcatnlo but it is not important
	m["MC2017legacy_Fall17_DYJetsToLL_50toInf_madgraph" ] = {.cross_section=  6225.42                          ,
		.usual_gen_lumi= 18928303.971956,
		.std_procs = known_procs_info["dy"],
		.std_systs = {SYSTS_OTHER_MC}};
	m["MC2016_Summer16_DYJetsToLL_50toInf_madgraph" ] = {.cross_section=  6225.42                          ,
		.usual_gen_lumi= 18928303.971956,
		.std_procs = known_procs_info["dy"],
		.std_systs = {SYSTS_OTHER_MC}};

	m["MC2017legacy_Fall17_SingleT_tW_5FS_powheg"       ] = {.cross_section=    35.6                           ,
		.usual_gen_lumi=  5099879.048270,
		.std_procs=known_procs_info["stop"],
		.std_systs = {SYSTS_OTHER_MC}};
	m["MC2016_Summer16_SingleT_tW_5FS_powheg"       ] = {.cross_section=    35.6                           ,
		.usual_gen_lumi=  5099879.048270,
		.std_procs=known_procs_info["stop"],
		.std_systs = {SYSTS_OTHER_MC}};

	m["MC2017legacy_Fall17_SingleTbar_tW_5FS_powheg"    ] = {.cross_section=    35.6                           ,
		.usual_gen_lumi=  2349775.859249,
		.std_procs=known_procs_info["stop"],
		.std_systs = {SYSTS_OTHER_MC}};
	m["MC2016_Summer16_SingleTbar_tW_5FS_powheg"    ] = {.cross_section=    35.6                           ,
		.usual_gen_lumi=  2349775.859249,
		.std_procs=known_procs_info["stop"],
		.std_systs = {SYSTS_OTHER_MC}};

	m["MC2017_Fall17_TTToHadronic_13TeV"             ] = {.cross_section=   831.76 * W_qar_br2              ,
		.usual_gen_lumi= 29213134.729453,
		.std_procs=known_procs_info["tt"],
		.std_systs = {SYSTS_TT}};
	m["MC2017_Fall17_TTToSemileptonic_13TeV"            ] = {.cross_section=   831.76 * 2*W_alllep_br*W_qar_br ,
		.usual_gen_lumi= 21966343.919990,
		.std_procs=known_procs_info["tt"],
		.std_systs = {SYSTS_TT}};
	m["MC2017_Fall17_TTTo2L2Nu"                      ] = {.cross_section=   831.76 * W_alllep_br2           ,
		.usual_gen_lumi=  2923730.883332,
		.std_procs=known_procs_info["tt"],
		.std_systs = {SYSTS_TT}};

	m["MC2016_Summer16_TTJets_powheg"                      ] = {.cross_section=   831.76           ,
		.usual_gen_lumi=  1.,
		.std_procs = known_procs_info["tt"],
		.std_systs = {SYSTS_TT}};

	// I probably need some defaults for not found dtags

	// TODO: for now enter Data as any MC
	m["Data2017legacy"                      ] = {.cross_section=   1.           ,
		.usual_gen_lumi=  1.,
		.std_procs = known_procs_info["data"],
		.std_systs = {"NOMINAL"}};

	// the 2016 cross section analysis
	m["Data13TeV_SingleElectron2016"                      ] = {.cross_section=   1.           ,
		.usual_gen_lumi=  1.,
		.std_procs = known_procs_info["data"],
		.std_systs = {"NOMINAL"}};
	m["Data13TeV_SingleMuon2016"                      ] = {.cross_section=   1.           ,
		.usual_gen_lumi=  1.,
		.std_procs = known_procs_info["data"],
		.std_systs = {"NOMINAL"}};

/* there are more:
MC2016_Summer16_DYJetsToLL_10to50_amcatnlo           MC2016_Summer16_QCD_HT-200-300            MC2016_Summer16_W1Jets_madgraph       MC2016_Summer16_WJets_madgraph                MC2016_Summer16_ZZTo2L2Nu_powheg
MC2016_Summer16_DYJetsToLL_10to50_amcatnlo_v1_ext1   MC2016_Summer16_QCD_HT-2000-Inf           MC2016_Summer16_W2Jets_madgraph       MC2016_Summer16_WJets_madgraph_ext2_v1        MC2016_Summer16_ZZTo2L2Q_amcatnlo_madspin
MC2016_Summer16_DYJetsToLL_10to50_amcatnlo_v2        MC2016_Summer16_QCD_HT-300-500            MC2016_Summer16_W2Jets_madgraph_ext1  MC2016_Summer16_WWTo2L2Nu_powheg              MC2016_Summer16_schannel_4FS_leptonicDecays_amcatnlo
MC2016_Summer16_DYJetsToLL_50toInf_madgraph          MC2016_Summer16_QCD_HT-500-700            MC2016_Summer16_W3Jets_madgraph       MC2016_Summer16_WWToLNuQQ_powheg              MC2016_Summer16_tchannel_antitop_4f_leptonicDecays_powheg
MC2016_Summer16_DYJetsToLL_50toInf_madgraph_ext2_v1  MC2016_Summer16_QCD_HT-700-1000           MC2016_Summer16_W3Jets_madgraph_ext1  MC2016_Summer16_WZTo1L1Nu2Q_amcatnlo_madspin  MC2016_Summer16_tchannel_top_4f_leptonicDecays_powheg
MC2016_Summer16_QCD_HT-100-200                       MC2016_Summer16_SingleT_tW_5FS_powheg     MC2016_Summer16_W4Jets_madgraph       MC2016_Summer16_WZTo1L3Nu_amcatnlo_madspin
MC2016_Summer16_QCD_HT-1000-1500                     MC2016_Summer16_SingleTbar_tW_5FS_powheg  MC2016_Summer16_W4Jets_madgraph_ext1  MC2016_Summer16_WZTo2L2Q_amcatnlo_madspin
MC2016_Summer16_QCD_HT-1500-2000                     MC2016_Summer16_TTJets_powheg             MC2016_Summer16_W4Jets_madgraph_ext2  MC2016_Summer16_WZTo3LNu_powheg
*/

	return m;
	}

// ----------------- dtag info


/* it was used for tau ID uncertainty, which is implemented per-channel now
TODO: remove if this system is absolutely not needed
double rogue_mixed_corrections(const TString& name_syst, const TString& name_chan, const TString& name_proc)
	{
	double correction = 1.;

	// tau ID correction
	// apply it in channels with a selected tau
	// to processes with genuine taus
	// TODO: it probably must be done via event weight in stage2
	double tau_ID_correction = 0.95;
	set<TString> tau_channels  = {"mu_sel", "el_sel", "mu_sel_ss", "el_sel_ss", "mu_selSV", "el_selSV", "mu_selSV_ss", "el_selSV_ss", "dy_mutau", "ctr_old_mu_sel", "ctr_old_mu_sel", "ctr_old_el_sel", "optel_tight_2L1M", "optmu_tight_2L1M"};
	set<TString> tau_processes = {"tt_mutau3ch", "tt_eltau3ch", "tt_mutau", "tt_eltau", "tt_taultauh", "dy_tautau", "s_top_eltau", "s_top_mutau"};
	if ((tau_channels.find(name_chan) != tau_channels.end()) && (tau_processes.find(name_proc) != tau_processes.end()))
		correction *= tau_ID_correction;

	return correction;
	}
*/

// --------- final normalizations

// normalization per gen lumi event weight
TH1D* weight_counter = NULL;

// per dtag cross section -- make it a commandline option if you want
bool normalise_per_cross_section = true;

void normalise_final(TH1D* histo, double cross_section, double scale, const TString& name_syst, const TString& name_chan, const TString& name_proc)
	{
	if (normalise_per_weight)
		histo->Scale(1./weight_counter->GetBinContent(2));

	if (normalise_per_cross_section)
		histo->Scale(cross_section);

	/* per-syst/proc/chan systematic corrections
	*/

	double per_syst_factor = (name_syst == "NOMINAL" || known_normalization_per_syst.find(name_syst) == known_normalization_per_syst.end()) ?  known_normalization_per_syst["NOMINAL"] :
		(name_syst == "PUUp" || name_syst == "PUDown" ? known_normalization_per_syst[name_syst] : known_normalization_per_syst["NOMINAL"] * known_normalization_per_syst[name_syst]);

	double per_proc_factor = known_normalization_per_proc.find(name_proc) == known_normalization_per_proc.end() ?
		1. :
		known_normalization_per_proc[name_proc];

	double per_chan_factor = known_normalization_per_chan.find(name_chan) == known_normalization_per_chan.end() ?
		1. :
		known_normalization_per_chan[name_chan];

	//double rogue_mixed_correction = rogue_mixed_corrections(name_syst, name_chan, name_proc);

	histo->Scale(scale * per_syst_factor * per_proc_factor * per_chan_factor /* * rogue_mixed_correction*/);
	}
/* --------------------------------------------------------------- */

/** \brief parse char* coma-separated string into vector<TString>
 */

vector<TString> parse_coma_list(char* coma_list)
	{
	vector<TString> list;

	// the input is so simple, we can just substitute , for \0 and set up char* array
	// ok, lets parse with strtok and push_back into a vector
	char delimeter[] = ",";
	char* txt;
	char* scratch;

	txt = strtok_r(coma_list, delimeter, &scratch);
	list.push_back(TString(txt));
	while ((txt = strtok_r(NULL, delimeter, &scratch)))
		list.push_back(TString(txt));

	return list;
	}


/** \brief generate a tree with the record histograms from requested systematics, channels, processes, and histograms

\return vector<T_syst_chan_proc_histos>
 */

vector<T_syst_chan_proc_histos> setup_record_histos(
	S_dtag_info&     main_dtag_info,
	vector<TString>& requested_systematics,
	vector<TString>& requested_channels   ,
	vector<TString>& requested_procs      ,
	vector<TString>& requested_distrs     )
{
// the output tree
vector<T_syst_chan_proc_histos> distrs_to_record;

// some info for profiling
int n_systs_made = 0, n_chans_made = 0, n_procs_made = 0, n_distrs_made = 0;

// final state channels
vector<TString> requested_channels_all = {
	"el_sel",
	"mu_sel",
	"el_sel_ss",
	"mu_sel_ss",

	"el_sel_tauSV3",
	"mu_sel_tauSV3",
	"el_sel_ss_tauSV3",
	"mu_sel_ss_tauSV3",

	"tt_elmu",
	"tt_elmu_tight",

	"dy_mutau",
	"dy_mutau_ss",
	"dy_eltau",
	"dy_eltau_ss",

	"dy_mutau_tauSV3",
	"dy_mutau_ss_tauSV3",
	"dy_eltau_tauSV3",
	"dy_eltau_ss_tauSV3",

	"dy_elmu",
	"dy_elmu_ss",
	"dy_mumu",
	"dy_elel"};

if (requested_channels[0] == "all")
	requested_channels = requested_channels_all;

//const char* requested_channel_names[] = {"tt_elmu", NULL};
//vector<TString> requested_procs   = {"all"};
//vector<TString> requested_procs   = {"std"};
vector<TString> requested_systematics_test = {"NOMINAL",
	"JERUp",
	"JERDown",
	"JESUp",
	"JESDown",
	"TESUp",
	"TESDown",
	"PUUp",
	"PUDown",
	"bSFUp",
	"bSFDown",
	"LEPelIDUp",
	"LEPelIDDown",
	"LEPelTRGUp",
	"LEPelTRGDown",
	"LEPmuIDUp",
	"LEPmuIDDown",
	"LEPmuTRGUp",
	"LEPmuTRGDown",
	};

if (requested_systematics[0] == "test")
	requested_systematics = requested_systematics_test;
else if (requested_systematics[0] == "std")
	requested_systematics = main_dtag_info.std_systs;

//requested_systematics[0] = "NOMINAL"; requested_systematics[1] = NULL;

//const char* requested_distrs[]        = {"Mt_lep_met_c", "leading_lep_pt", NULL};

// set the known processes according to the request: whetehr groups of processes are requested or not
// check if all known processes are requested
map<TString, _F_genproc_def> known_procs;
if (requested_procs[0] == "all")
	{
	known_procs = main_dtag_info.std_procs.all;
	// and reset the requested processes to all known processes for this dtag
	requested_procs.clear();
	// loop over all known processes
	for (const auto& proc: main_dtag_info.std_procs.all)
		{
		//cout_expr(proc.first);
		requested_procs.push_back(proc.first);
		}
	}

else
	{
	known_procs = main_dtag_info.std_procs.groups;
	//known_procs = main_dtag_info.std_procs.all;
	// populate definitions of groups with the fine-grain definitions of all processes			
	known_procs.insert(main_dtag_info.std_procs.all.begin(), main_dtag_info.std_procs.all.end());
	}


// name of the catchall process for the defined dtag
TString procname_catchall = main_dtag_info.std_procs.catchall_name;
map<TString, vector<TString>>& known_std_procs_per_channel = main_dtag_info.std_procs.channel_standard;

// --------------------------------- SETUP RECORD HISTOS for output from the parsed commandline input
for (const auto& systname: requested_systematics)
	{
	// find the definition of this channel
	Stopif(known_systematics.find(systname) == known_systematics.end(), continue, "Do not know a systematic %s", systname.Data());

	T_syst_chan_proc_histos systematic = {.name=string(systname.Data()), .syst_def = known_systematics[systname]};

	// define channels
	for (const auto& channame: requested_channels)
		{
		// find the definition of this channel
		Stopif(known_defs_channels.find(channame) == known_defs_channels.end(), continue, "Do not know the channel %s", channame.Data());

		T_chan_proc_histos channel          = {
			.name = string(channame.Data()),
			.chan_def = known_defs_channels[channame],
			.procs = {},
			.name_catchall_proc = string(procname_catchall.Data())};

		// check if standard processes per channels are requested
		vector<TString>* process_definitions_to_use = &requested_procs;
		if ((*process_definitions_to_use)[0] == "std")
			{
			// TODO in case of an unknown process set an inclusive definition
			Stopif(known_std_procs_per_channel.find(channame) == known_std_procs_per_channel.end(), continue, "Do not know standard processes for the channel %s", channame.Data())
			// set the standard processes
			process_definitions_to_use = &known_std_procs_per_channel[channame];
			}

		// loop over requested processes and find their definitions for recording in this channel
		//for (const char** requested_proc = requested_procs; *requested_proc != NULL; requested_proc++)
		for (const auto& procname: (*process_definitions_to_use))
			{
			// find the definition of this channel
			//TString procname(*requested_proc);

			Stopif(known_procs.find(procname) == known_procs.end(), continue, "Do not know the process %s", procname.Data());

			T_proc_histos process = {.name=string(procname.Data()), .proc_def=known_procs[procname]};

			// define distributions
			// create the histograms for all of these definitions
			for (const auto& distrname: requested_distrs)
				{
				Stopif(known_defs_distrs.find(distrname) == known_defs_distrs.end(), continue, "Do not know a distribution %s", distrname.Data());

				TH1D_histo a_distr = create_TH1D_histo(known_defs_distrs[distrname], channame + "_" + procname + "_" + systname + "_" + distrname, string(distrname.Data()));
				process.histos.push_back(a_distr);

				n_distrs_made +=1;
				}

			channel.procs.push_back(process);
			n_procs_made +=1;
			}

		// setup catchall process

		// define distributions
		// create the histograms for all of these definitions
		for (const auto& distrname: requested_distrs)
			{
			Stopif(known_defs_distrs.find(distrname) == known_defs_distrs.end(), continue, "Do not know a distribution %s", distrname.Data());

			TH1D_histo a_distr = create_TH1D_histo(known_defs_distrs[distrname], channame + "_" + procname_catchall + "_" + systname + "_" + distrname, string(distrname.Data()));
			channel.catchall_proc_histos.push_back(a_distr);
			n_distrs_made +=1;
			n_procs_made +=1;
			}

		systematic.chans.push_back(channel);
		n_chans_made +=1;
		}

	distrs_to_record.push_back(systematic);
	n_systs_made +=1;
	}

cerr_expr(n_systs_made << " " << n_chans_made << " " << n_procs_made << " " << n_distrs_made);
return distrs_to_record;
}

// this is a pure hack, but the flexibility allows this:
//extern Int_t NT_nup;

void event_loop(TTree* NT_output_ttree, vector<T_syst_chan_proc_histos>& distrs_to_record,
	bool skip_nup5_events, bool isMC)
{
// open the interface to stage2 TTree-s
//#define NTUPLE_INTERFACE_OPEN

//#define OUTNTUPLE NT_output_ttree
//#define NTUPLE_INTERFACE_CONNECT
//#include "stage2_interface.h" // it runs a bunch of branch-connecting commands on TTree* with name OUTNTUPLE
//// this must be done in stage2

//connect_ntuple_interface(NT_output_ttree);
Stopif(connect_ntuple_interface(NT_output_ttree) > 0, exit(55), "could not connect the TTree to the ntuple definitions");

unsigned int n_entries = NT_output_ttree->GetEntries();
//cerr_expr(n_entries);

for (unsigned int ievt = 0; ievt < n_entries; ievt++)
	{
	NT_output_ttree->GetEntry(ievt);

	//if (skip_nup5_events && NT_nup > 5) continue;

	//// tests
	////cerr_expr(NT_runNumber);
	//cerr_expr(NT_event_leptons[0].pt());
	//cerr_expr(NT_event_leptons_genmatch[0]);

	//Stopif(ievt > 10, break, "reached 10 events, exiting");

	// loop over systematics
	for (int si=0; si<distrs_to_record.size(); si++)
		{
		ObjSystematics obj_systematic = distrs_to_record[si].syst_def.obj_sys_id;

		// the factor to the NOMINAL_base weight
		double event_weight_factor    = isMC ? distrs_to_record[si].syst_def.weight_func() : 1.;

		// record distributions in all final states where the event passes
		vector<T_chan_proc_histos>& channels = distrs_to_record[si].chans;
		for (int ci=0; ci<channels.size(); ci++)
			{
			T_chan_proc_histos& chan = channels[ci];

			// check if event passes the channel selection
			if (!chan.chan_def.chan_sel(obj_systematic)) continue;

			// calculate the NOMINAL_base event weight for the channel
			double event_weight = isMC ? chan.chan_def.chan_sel_weight() : 1.;
			// and multiply by the systematic factor
			event_weight *= event_weight_factor;

			// assign the gen process
			// loop over procs check if this event passes
			// if not get the catchall proc

			// set catchall
			vector<TH1D_histo>* histos = &(chan.catchall_proc_histos);

			// check if any specific channel passes
			for (int pi=0; pi<chan.procs.size(); pi++)
				{
				if (chan.procs[pi].proc_def())
					{
					histos = &chan.procs[pi].histos;
					break;
					}
				}

			// record all distributions with the given event weight
			for (int di=0; di<histos->size(); di++)
				{
				TH1D_histo& histo_torecord = (*histos)[di];
				// TODO memoize if possible
				double value = histo_torecord.func(obj_systematic);
				histo_torecord.histo->Fill(value, event_weight);
				//histo_torecord.histo->Fill(value);
				}
			// <-- I keep the loops with explicit indexes, since the indexes can be used to implement memoization

			//for(const auto& histo_torecord: chan.histos)
			//	{
			//	double value = histo_torecord.func(obj_systematic);
			//	histo_torecord.histo->Fill(value, event_weight);
			//	}
			}
		}

	// end of event loop
	}
}

void write_output(const char* output_filename, vector<T_syst_chan_proc_histos>& distrs_to_record,
	S_dtag_info& main_dtag_info,
	Float_t lumi,
	bool isMC, bool save_in_old_order, bool simulate_data)
{
TFile* output_file  = (TFile*) new TFile(output_filename, "RECREATE");
output_file->Write();

if (save_in_old_order)
  {
  for (int si=0; si<distrs_to_record.size(); si++)
	{
	// merge defined processes and the catchall
	TString syst_name(distrs_to_record[si].name.c_str());
	vector<T_chan_proc_histos>& all_chans = distrs_to_record[si].chans;

	output_file->cd();
	//TDirectory* dir_syst = (TDirectory*) output_file->mkdir(syst_name);
	//dir_syst->SetDirectory(output_file);

	for(const auto& chan: all_chans)
		{
		//dir_syst->cd();
		//TDirectory* dir_chan = (TDirectory*) dir_syst->mkdir(chan.name);
		//dir_chan->SetDirectory(dir_syst);
		TString chan_name(chan.name.c_str());
		for(const auto& proc: chan.procs)
			{
			//dir_chan->cd();
			//TDirectory* dir_proc = (TDirectory*) dir_chan->mkdir(proc.name);
			//dir_proc->SetDirectory(dir_chan);
			//dir_proc->cd();
			TString proc_name(proc.name.c_str());
			for(const auto& recorded_histo: proc.histos)
				{
				// the old order of the path
				//TString path = chan.name + "/" + proc.name + "/" + syst_name + "/";

				// get or create this path
				output_file->cd();
				TDirectory* chanpath = output_file->Get(chan_name) ? (TDirectory*) output_file->Get(chan_name) :  (TDirectory*) output_file->mkdir(chan_name);
				chanpath->cd();
				TDirectory* procpath = chanpath->Get(proc_name) ? (TDirectory*) chanpath->Get(proc_name) :  (TDirectory*) chanpath->mkdir(proc_name);
				procpath->cd();
				TDirectory* systpatch = procpath->Get(syst_name) ? (TDirectory*) procpath->Get(syst_name) :  (TDirectory*) procpath->mkdir(syst_name);
				systpatch->cd();

				TString histoname = chan_name + "_" + proc_name + "_" + syst_name + "_" + TString(recorded_histo.main_name);
				recorded_histo.histo->SetName(histoname);

				// all final normalizations of the histogram
				if (isMC)
					normalise_final(recorded_histo.histo, main_dtag_info.cross_section, lumi, syst_name, chan_name, proc_name);

				recorded_histo.histo->Write();
				}
			}

		// same for catchall
		// the old order of the path
		//TString path = chan.name + "/" + chan.name_catchall_proc + "/" + syst_name + "/";

		//for(const auto& recorded_histo: chan.catchall_proc_histos)
		for (unsigned int rec_histo_i = 0; rec_histo_i<chan.catchall_proc_histos.size(); rec_histo_i++)
			{
			const auto& recorded_histo = chan.catchall_proc_histos[rec_histo_i];
			TString chan_name_catchall(chan.name_catchall_proc.c_str());

			// get or create this path
			output_file->cd();
			TDirectory* chanpath = output_file->Get(chan_name) ? (TDirectory*) output_file->Get(chan_name) :  (TDirectory*) output_file->mkdir(chan_name);
			chanpath->cd();
			TDirectory* procpath = chanpath->Get(chan_name_catchall) ? (TDirectory*) chanpath->Get(chan_name_catchall) :  (TDirectory*) chanpath->mkdir(chan_name_catchall);
			procpath->cd();
			TDirectory* systpatch = procpath->Get(syst_name) ? (TDirectory*) procpath->Get(syst_name) :  (TDirectory*) procpath->mkdir(syst_name);
			systpatch->cd();

			TString histoname = chan_name + "_" + chan_name_catchall + "_" + syst_name + "_" + TString(recorded_histo.main_name);
			//cerr_expr(histoname);
			recorded_histo.histo->SetName(histoname);

			if (isMC)
				normalise_final(recorded_histo.histo, main_dtag_info.cross_section, lumi, syst_name, chan_name, chan_name_catchall);
			recorded_histo.histo->Write();

			// data simulation for each recorded distr if requested
			if (simulate_data && syst_name == "NOMINAL")
				{
				output_file->cd();
				TDirectory* chanpath = output_file->Get(chan_name) ? (TDirectory*) output_file->Get(chan_name) :  (TDirectory*) output_file->mkdir(chan_name);
				chanpath->cd();
				TDirectory* procpath = chanpath->Get("data") ? (TDirectory*) chanpath->Get("data") :  (TDirectory*) chanpath->mkdir("data");
				procpath->cd();
				TDirectory* systpatch = procpath->Get("NOMINAL") ? (TDirectory*) procpath->Get("NOMINAL") :  (TDirectory*) procpath->mkdir("NOMINAL");
				systpatch->cd();

				TString data_name = chan_name + "_data_NOMINAL_" + recorded_histo.main_name;
				if (output_file->Get(chan_name + "/data/NOMINAL/" + data_name)) continue;
				TH1D* data_histo = (TH1D*) recorded_histo.histo->Clone();
				data_histo->SetDirectory(systpatch);
				data_histo->SetName(data_name);

				//data_histo->Reset();
				//data_histo->Fill(1);
				// instead, add histograms from all processes
				for(const auto& proc: chan.procs)
					{
					data_histo->Add(proc.histos[rec_histo_i].histo);
					}

				data_histo->Write();
				}

			}
		}
	}
  }

else
  {
  for (int si=0; si<distrs_to_record.size(); si++)
	{
	// merge defined processes and the catchall
	TString syst_name(distrs_to_record[si].name);
	vector<T_chan_proc_histos>& all_chans = distrs_to_record[si].chans;

	output_file->cd();
	TDirectory* dir_syst = (TDirectory*) output_file->mkdir(syst_name);
	//dir_syst->SetDirectory(output_file);

	for(const auto& chan: all_chans)
		{
		TString chan_name(chan.name.c_str());
		dir_syst->cd();
		TDirectory* dir_chan = (TDirectory*) dir_syst->mkdir(chan_name);
		//dir_chan->SetDirectory(dir_syst);
		for(const auto& proc: chan.procs)
			{
			TString proc_name(proc.name.c_str());
			dir_chan->cd();
			TDirectory* dir_proc = (TDirectory*) dir_chan->mkdir(proc_name);
			//dir_proc->SetDirectory(dir_chan);
			dir_proc->cd();

			for(const auto& recorded_histo: proc.histos)
				{
				//recorded_histo.histo->Print();
				// all final normalizations of the histogram
				if (isMC)
					normalise_final(recorded_histo.histo, main_dtag_info.cross_section, lumi, syst_name, chan_name, proc_name);
				recorded_histo.histo->Write();
				}
			}

		//for(const auto& recorded_histo: chan.catchall_proc_histos)
		for (unsigned int rec_histo_i = 0; rec_histo_i<chan.catchall_proc_histos.size(); rec_histo_i++)
			{
			const auto& recorded_histo = chan.catchall_proc_histos[rec_histo_i];
			TString chan_name_catchall_proc(chan.name_catchall_proc.c_str());

			// same for catchall
			dir_chan->cd();
			TDirectory* dir_proc_catchall = dir_chan->Get(chan_name_catchall_proc) ? (TDirectory*) dir_chan->Get(chan_name_catchall_proc) : (TDirectory*) dir_chan->mkdir(chan_name_catchall_proc);
			//dir_proc_catchall->SetDirectory(dir_chan);
			dir_proc_catchall->cd();

			if (isMC)
				normalise_final(recorded_histo.histo, main_dtag_info.cross_section, lumi, syst_name, chan_name, chan_name_catchall_proc);
			recorded_histo.histo->Write();

			// data simulation if requested
			if (simulate_data && syst_name == "NOMINAL")
				{
				dir_syst->cd();

				TDirectory* chanpath = dir_syst->Get(chan_name) ? (TDirectory*) dir_syst->Get(chan_name) :  (TDirectory*) dir_syst->mkdir(chan_name);
				chanpath->cd();
				TDirectory* procpath = chanpath->Get("data") ? (TDirectory*) chanpath->Get("data") :  (TDirectory*) chanpath->mkdir("data");
				procpath->cd();

				TString data_name = TString("NOMINAL_") + chan_name + "_data_" + recorded_histo.main_name;
				if (procpath->Get(data_name)) continue;
				TH1D* data_histo = (TH1D*) recorded_histo.histo->Clone();
				data_histo->SetDirectory(procpath);
				data_histo->SetName(data_name);

				//data_histo->Reset();
				//data_histo->Fill(1);
				// instead, add histograms from all processes
				for(const auto& proc: chan.procs)
					{
					data_histo->Add(proc.histos[rec_histo_i].histo);
					}

				data_histo->Write();
				}

			}
		}
	}
  }

output_file->cd();

if (normalise_per_weight)
	weight_counter->Write();

output_file->Close();
}

/** \brief The main program executes user's request over the given list of files, in all found `TTree`s in the files.

It parses the requested channels, systematics and distributions;
prepares the structure of the loop;
loops over all given files and `TTree`s in them,
recording the distributions at the requested systematics;
applies final corrections to the distributions;
and if asked normalizes the distribution to `cross_section/gen_lumi`;
finally all histograms are written out in the standard format `channel/process/systematic/channel_process_systematic_distr`.

The input now: `input_filename [input_filename+]`.
 */


int main (int argc, char *argv[])
{
argc--;
const char* exec_name = argv[0];
argv++;

if (argc < 7)
	{
	std::cout << "Usage:" << " [0-1]<interface type> 0|1<simulate_data> 0|1<save_in_old_order> 0|1<do_WNJets_stitching> <lumi> <systs coma-separated> <chans> <procs> <distrs> output_filename input_filename [input_filename+]" << std::endl;
	exit(1);
	}

gROOT->Reset();

/* --- input options --- */

// set to normalize per gen lumi number of events
//bool normalise_per_weight = <user input>;

// a special weird feature:
// produce an output as if it were data
// with NOMINAL systematic
// and  data    proc name
// histograms are filled with 1
Int_t interface_type     = Int_t(atoi(*argv++)) == 1; argc--;

bool simulate_data       = Int_t(atoi(*argv++)) == 1; argc--;

bool save_in_old_order   = Int_t(atoi(*argv++)) == 1; argc--;
bool do_WNJets_stitching = Int_t(atoi(*argv++)) == 1; argc--;
Float_t lumi(atof(*argv++)); argc--;

// parse commandline coma-separated lists for main parameters of the record
vector<TString> requested_systematics = parse_coma_list(*argv++); argc--;
vector<TString> requested_channels    = parse_coma_list(*argv++); argc--;
vector<TString> requested_procs       = parse_coma_list(*argv++); argc--;
vector<TString> requested_distrs      = parse_coma_list(*argv++); argc--;

const char* output_filename = *argv++; argc--;

if  (do_not_overwrite)
	Stopif(access(output_filename, F_OK) != -1, exit(2);, "the output file exists %s", output_filename);


cerr_expr(do_WNJets_stitching << " " << output_filename);
/* --------------------- */


// -------------------- set the interface type
string input_path_ttree;
string input_path_weight_counter;

// main record parameters
switch (interface_type)
{
case 0:
	known_systematics   = create_known_defs_systs_stage2();
	known_defs_channels = create_known_defs_channels_stage2();
	known_defs_distrs   = create_known_defs_distrs_stage2();

	known_procs_info    = create_known_defs_procs_stage2();

	known_normalization_per_syst = create_known_MC_normalization_per_syst_stage2();
	known_normalization_per_proc = create_known_MC_normalization_per_proc_stage2();
	known_normalization_per_chan = create_known_MC_normalization_per_chan_stage2();

	connect_ntuple_interface = &connect_ntuple_interface_stage2;

	input_path_ttree = "ttree_out";
	input_path_weight_counter = "weight_counter";
	break;

case 1:
	known_systematics   = create_known_defs_systs_ntupler();
	known_defs_channels = create_known_defs_channels_ntupler();
	known_defs_distrs   = create_known_defs_distrs_ntupler();

	known_procs_info    = create_known_defs_procs_ntupler();

	known_normalization_per_syst = create_known_MC_normalization_per_syst_ntupler();
	known_normalization_per_proc = create_known_MC_normalization_per_proc_ntupler();
	known_normalization_per_chan = create_known_MC_normalization_per_chan_ntupler();

	connect_ntuple_interface = &connect_ntuple_interface_ntupler;

	input_path_ttree = "ntupler/reduced_ttree";
	input_path_weight_counter = "ntupler/weight_counter";
	break;

default:
	Stopif(interface_type != 0 && interface_type != 1, exit(2);, "the interface type %d is not supported, the valid values are 0 (stage2) and 1 (ntupler)", interface_type);
}

map<TString, S_dtag_info> known_dtags_info = create_known_dtags_info(known_procs_info);

// set the interface type --------------------


//Int_t rebin_factor(atoi(argv[3]));
//TString dir(argv[4]);
//TString dtag1(argv[5]);

/* Here we will parse user's request for figures
 * to create the structure filled up in the event loop.
 */

// figure out the dtag of the input files from the first input file
TString first_input_filename(argv[0]);
TString main_dtag("");

// loop over known dtags and find whether any of the matches
map<TString, S_dtag_info>::iterator a_dtag_info = known_dtags_info.begin();
while (a_dtag_info != known_dtags_info.end())
	{
	// Accessing KEY from element pointed by it.
	TString dtag_name = a_dtag_info->first;
	if (first_input_filename.Contains(dtag_name))
		{
		main_dtag = dtag_name;
		break;
		}
	// Increment the Iterator to point to next entry
	a_dtag_info++;
	}

// test if no dtag was recognized
//Stopif(!main_dtag, ;, "could not recognize any known dtag in %s", first_input_filename.Data());
Stopif(main_dtag.EqualTo(""), ;, "could not recognize any known dtag in %s", first_input_filename.Data());
//if (main_dtag.EqualTo(""))
//	{
//	cerr_expr();
//	}

S_dtag_info main_dtag_info = known_dtags_info[main_dtag];
cerr_expr(main_dtag << " : " << main_dtag_info.cross_section);

bool isMC = main_dtag.Contains("MC");
//if (!isMC) normalise_per_weight = false;
normalise_per_weight &= isMC;

// for WNJets stiching
bool skip_nup5_events = do_WNJets_stitching && isMC && main_dtag.Contains("WJets_madgraph");

//// define histograms for the distributions
//vector<TH1D_histo> distrs;



// define a nested list: list of channels, each containing a list of histograms to record
vector<T_syst_chan_proc_histos> distrs_to_record = setup_record_histos(
	main_dtag_info,
	requested_systematics ,
	requested_channels    ,
	requested_procs       ,
	requested_distrs      );

// --------------------------------- EVENT LOOP
// process input files
for (unsigned int cur_var = 0; cur_var<argc; cur_var++)
	{
	TString input_filename(argv[cur_var]);

	cerr_expr(cur_var << " " << input_filename);
	//cerr_expr(input_filename);

	//dtags.push_back(dtag);
	//files.push_back(TFile::Open(dir + "/" + dtag + ".root"));
	//dtags.push_back(5);

	// get input ttree
	TFile* input_file  = TFile::Open(input_filename);
	Stopif(!input_file,  continue, "cannot Open TFile in %s, skipping", input_filename.Data());

	TTree* NT_output_ttree = (TTree*) input_file->Get(input_path_ttree.c_str());
	Stopif(!NT_output_ttree, continue, "cannot Get TTree in file %s, skipping", input_filename.Data());

	if (normalise_per_weight)
		{
		// get weight distribution for the file
		TH1D* weight_counter_in_file = (TH1D*) input_file->Get(input_path_weight_counter.c_str());
		// if the common weight counter is still not set -- clone
		if (!weight_counter)
			{
			weight_counter = (TH1D*) weight_counter_in_file->Clone();
			weight_counter->SetDirectory(0);
			}
		else
			{
			weight_counter->Add(weight_counter_in_file);
			}
		}

	// loop over events in the ttree and record the requested histograms
	event_loop(NT_output_ttree, distrs_to_record, skip_nup5_events, isMC);

	// close the input file
	input_file->Close();
	}

// if there is still no weight counter when it was requested
// then no files were processed (probably all were skipped)
Stopif(normalise_per_weight && !weight_counter, exit(3), "no weight counter even though it was requested, probably no files were processed, exiting")

/*
for(std::map<TString, double>::iterator it = xsecs.begin(); it != xsecs.end(); ++it)
	{
	TString dtag = it->first;
	double xsec  = it->second;
	cout << "For dtag " << dtag << " xsec " << xsec << "\n";
	}
*/


//std::vector < TString > dtags;
//std::vector < TFile * > files;
//std::vector < TH1D * > histos;
//std::vector < TH1D * > weightflows;
//// nick->summed histo
//std::map<TString, TH1D *> nicknamed_mc_histos;
////vector<int> dtags;
////dtags.reserve();

// make stack of MC, scaling according to ratio = lumi * xsec / weightflow4 (bin5?)
// also nickname the MC....
// per-dtag for now..

// --------------------------------- OUTPUT
write_output(output_filename, distrs_to_record, main_dtag_info, lumi, isMC, save_in_old_order, simulate_data);
}
