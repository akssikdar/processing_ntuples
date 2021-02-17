//This file finds number of generated events from nt=94v22


#include <TFile.h>
#include <TTree.h>
#include <TROOT.h>
#include <TH1.h>
#include <TH2.h>
#include <TSystem.h>
#include <vector>
#include <TLorentzVector.h>
#include <math.h>
#include "TMath.h"
#include <iostream>
#include <fstream>
#include <algorithm>
#include <map>
#include <TFileMerger.h>



using namespace ROOT::Math;

void gendistrs()
{
TH1 *elel_l0_pt       = new TH1D("elel_l0",";p_{T}(leading Electron);Events",100,0,500);
TH1 *elel_l1_pt       = new TH1D("elel_l1",";p_{T}(subleading Electron);Events",100,0,500);
TH1 *mumu_l0_pt       = new TH1D("mumu_l0",";p_{T}(leading #mu);Events",100,0,500);
TH1 *mumu_l1_pt       = new TH1D("mumu_l1",";p_{T}(subleading Muon);Events",100,0,500);
TH1 *elmu_l0_pt       = new TH1D("elmu_l0",";p_{T}^{e};Events",100,0,500);
TH1 *elmu_l1_pt       = new TH1D("elmu_l1",";p_{T}^{#mu};Events",100,0,500);
TH1 *eltaul_l0_pt     = new TH1D("eltaul_l0",";p_{T}^{e};Events",100,0,500);
TH1 *eltaul_l1_pt     = new TH1D("eltaul_l1",";p_{T};Events",100,0,500);
TH1 *eltau1h_l0_pt    = new TH1D("eltau1h_l0",";p_{T}^{e};Events",100,0,500);
TH1 *eltau1h_l1_pt    = new TH1D("eltau1h_l1",";p_{T};Events",100,0,500);
TH1 *eltau3h_l0_pt    = new TH1D("eltau3h_l0",";p_{T}^{e};Events",100,0,500);
TH1 *eltau3h_l1_pt    = new TH1D("eltau3h_l1",";p_{T};Events",100,0,500);
TH1 *mutau1h_l0_pt    = new TH1D("mutau1h_l0",";p_{T}^{#mu};Events",100,0,500);
TH1 *mutau1h_l1_pt    = new TH1D("mutau1h_l1",";p_{T};Events",100,0,500);
TH1 *mutau3h_l0_pt    = new TH1D("mutau3h_l0",";p_{T}^{#mu};Events",100,0,500);
TH1 *mutau3h_l1_pt    = new TH1D("mutau3h_l1",";p_{T};Events",100,0,500);
TH1 *taueltauh_l0_pt = new TH1D("taueltauh_l0",";p_{T};Events",100,0,500);
TH1 *taueltauh_l1_pt = new TH1D("taueltauh_l1",";p_{T};Events",100,0,500);
TH1 *taumutauh_l0_pt = new TH1D("taumutauh_l0",";p_{T};Events",100,0,500);
TH1 *taumutauh_l1_pt = new TH1D("taumutauh_l1",";p_{T};Events",100,0,500);

TH1 *eltaul_l0_eta    = new TH1D("eltaul_l0",";#eta;Events",100,-3,3);
TH1 *eltaul_l1_eta    = new TH1D("eltaul_l1",";#eta;Events",100,-3,3);
TH1 *eltau1h_l0_eta   = new TH1D("eltau1h_l0",";#eta;Events",100,-3,3);
TH1 *eltau1h_l1_eta   = new TH1D("eltau1h_l1",";#eta;Events",100,-3,3);
TH1 *eltau3h_l0_eta   = new TH1D("eltau3h_l0",";#eta;Events",100,-3,3);
TH1 *eltau3h_l1_eta   = new TH1D("eltau3h_l1",";#eta;Events",100,-3,3);
TH1 *mutau1h_l0_eta   = new TH1D("mutau1h_l0",";#eta;Events",100,-3,3);
TH1 *mutau1h_l1_eta   = new TH1D("mutau1h_l1",";#eta;Events",100,-3,3);
TH1 *mutau3h_l0_eta   = new TH1D("mutau3h_l0",";#eta;Events",100,-3,3);
TH1 *mutau3h_l1_eta   = new TH1D("mutau3h_l1",";#eta;Events",100,-3,3);

TH1 *eltau1h_b1_pt    = new TH1D("eltau1h_b1","",100,0,500);
TH1 *eltau1h_j1_pt    = new TH1D("eltau1h_j1","",100,0,500);

TH1 *mutau1h_b1_pt    = new TH1D("mutau1h_b1","",100,0,500);
TH1 *mutau1h_j1_pt    = new TH1D("mutau1h_j1","",100,0,500);


TH1 *eltau1h_b1_eta    = new TH1D("eltau1h_b1","",100,-3,3);
TH1 *eltau1h_j1_eta    = new TH1D("eltau1h_j1","",100,-3,3);

TH1 *mutau1h_b1_eta    = new TH1D("mutau1h_b1","",100,-3,3);
TH1 *mutau1h_j1_eta    = new TH1D("mutau1h_j1","",100,-3,3);


//TFile *f1= TFile::Open("MC2017legacy_Fall17_TTTo2L2Nu_1.root");
TFile *f1= TFile::Open("/eos/user/a/asikdar/94v22/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/Ntupler_94v22_MC2017_Fall17_TTTo2L2Nu/200526_142616/0000/MC2017_Fall17_TTTo2L2Nu_all.root");

elel_l0_pt       = (TH1D*)f1->Get("ntupler/elel_l0_pt");
elel_l1_pt       = (TH1D*)f1->Get("ntupler/elel_l1_pt");
mumu_l0_pt       = (TH1D*)f1->Get("ntupler/mumu_l0_pt");
mumu_l1_pt       = (TH1D*)f1->Get("ntupler/mumu_l1_pt");
elmu_l0_pt       = (TH1D*)f1->Get("ntupler/elmu_l0_pt");
elmu_l1_pt       = (TH1D*)f1->Get("ntupler/elmu_l1_pt");
eltaul_l0_pt     = (TH1D*)f1->Get("ntupler/eltaul_l0_pt");
eltaul_l1_pt     = (TH1D*)f1->Get("ntupler/eltaul_l1_pt");
eltau1h_l0_pt    = (TH1D*)f1->Get("ntupler/eltau1h_l0_pt");
eltau1h_l1_pt    = (TH1D*)f1->Get("ntupler/eltau1h_l1_pt");
eltau3h_l0_pt    = (TH1D*)f1->Get("ntupler/eltau3h_l0_pt");
eltau3h_l1_pt    = (TH1D*)f1->Get("ntupler/eltau3h_l1_pt");
mutau1h_l0_pt    = (TH1D*)f1->Get("ntupler/mutau1h_l0_pt");
mutau1h_l1_pt    = (TH1D*)f1->Get("ntupler/mutau1h_l1_pt");
mutau3h_l0_pt    = (TH1D*)f1->Get("ntupler/mutau3h_l0_pt");
mutau3h_l1_pt    = (TH1D*)f1->Get("ntupler/mutau3h_l1_pt");
taueltauh_l0_pt = (TH1D*)f1->Get("ntupler/taueltauh_l0_pt");
taueltauh_l1_pt = (TH1D*)f1->Get("ntupler/taueltauh_l1_pt");
taumutauh_l0_pt = (TH1D*)f1->Get("ntupler/taumutauh_l0_pt");
taumutauh_l1_pt = (TH1D*)f1->Get("ntupler/taumutauh_l0_pt");

eltaul_l0_eta    = (TH1D*)f1->Get("ntupler/eltaul_l0_eta");
eltaul_l1_eta    = (TH1D*)f1->Get("ntupler/eltaul_l1_eta");
eltau1h_l0_eta   = (TH1D*)f1->Get("ntupler/eltau1h_l0_eta");
eltau1h_l1_eta   = (TH1D*)f1->Get("ntupler/eltau1h_l1_eta");
eltau3h_l0_eta   = (TH1D*)f1->Get("ntupler/eltau3h_l0_eta");
eltau3h_l1_eta   = (TH1D*)f1->Get("ntupler/eltau3h_l1_eta");
mutau1h_l0_eta   = (TH1D*)f1->Get("ntupler/mutau1h_l0_eta");
mutau1h_l1_eta   = (TH1D*)f1->Get("ntupler/mutau1h_l1_eta");
mutau3h_l0_eta   = (TH1D*)f1->Get("ntupler/mutau3h_l0_eta");
mutau3h_l1_eta   = (TH1D*)f1->Get("ntupler/mutau3h_l1_eta");


eltau1h_b1_pt = (TH1D*)f1->Get("ntupler/eltau1h_b1_pt");
eltau1h_j1_pt = (TH1D*)f1->Get("ntupler/eltau1h_j1_pt");
mutau1h_l1_pt = (TH1D*)f1->Get("ntupler/mutau1h_l1_pt");
mutau1h_b1_pt = (TH1D*)f1->Get("ntupler/mutau1h_b1_pt");
mutau1h_j1_pt = (TH1D*)f1->Get("ntupler/mutau1h_j1_pt");

eltau1h_b1_eta = (TH1D*)f1->Get("ntupler/eltau1h_b1_eta");
eltau1h_j1_eta = (TH1D*)f1->Get("ntupler/eltau1h_j1_eta");
mutau1h_l1_eta = (TH1D*)f1->Get("ntupler/mutau1h_l1_eta");
mutau1h_b1_eta = (TH1D*)f1->Get("ntupler/mutau1h_b1_eta");
mutau1h_j1_eta = (TH1D*)f1->Get("ntupler/mutau1h_j1_eta");

//Normalize by hand first
//double nevts = ((TH1D*)f1->Get("ntupler/weight_counter"))->GetBinContent(2); //=63946427

double lumi = 41530;
double xsec_TTTo2L2Nu = 9.701; //TODO: get this value by parsing from XML file
double xsec_TTToSemileptonic = 60.55;
double xsec_TTToHadronic = 377.96;

double evts_TTTo2L2Nu        = 6700672;
double evts_TTToSemileptonic = 28032620;
double evts_TTToHadronic     = 29213134;

double scale_TTTo2L2Nu = (xsec_TTTo2L2Nu * lumi)/evts_TTTo2L2Nu;
double scale_TTToSemileptonic = (xsec_TTToSemileptonic * lumi)/evts_TTToSemileptonic;
double scale_TTToHadronic = (xsec_TTToHadronic * lumi)/evts_TTToHadronic;

cout << "number of events: " << evts_TTTo2L2Nu << endl;
cout << "luminosity: "<< lumi <<endl;
cout << "Scale factor for TTTo2L2Nu: " << scale_TTTo2L2Nu << endl;

elel_l0_pt       -> Scale(scale_TTTo2L2Nu);
elel_l1_pt       -> Scale(scale_TTTo2L2Nu);
mumu_l0_pt       -> Scale(scale_TTTo2L2Nu);
mumu_l1_pt       -> Scale(scale_TTTo2L2Nu);
elmu_l0_pt       -> Scale(scale_TTTo2L2Nu);
elmu_l1_pt       -> Scale(scale_TTTo2L2Nu);
eltaul_l0_pt     -> Scale(scale_TTTo2L2Nu);
eltaul_l1_pt     -> Scale(scale_TTTo2L2Nu);
eltau1h_l0_pt    -> Scale(scale_TTTo2L2Nu);
eltau1h_l1_pt    -> Scale(scale_TTTo2L2Nu);
eltau3h_l0_pt    -> Scale(scale_TTTo2L2Nu);
eltau3h_l1_pt    -> Scale(scale_TTTo2L2Nu);
mutau1h_l0_pt    -> Scale(scale_TTTo2L2Nu);
mutau1h_l1_pt    -> Scale(scale_TTTo2L2Nu);
mutau3h_l0_pt    -> Scale(scale_TTTo2L2Nu);
mutau3h_l1_pt    -> Scale(scale_TTTo2L2Nu);
taueltauh_l0_pt -> Scale(scale_TTTo2L2Nu);
taueltauh_l1_pt -> Scale(scale_TTTo2L2Nu);
taumutauh_l0_pt -> Scale(scale_TTTo2L2Nu);
taumutauh_l1_pt -> Scale(scale_TTTo2L2Nu);

eltaul_l0_eta    -> Scale(scale_TTTo2L2Nu);
eltaul_l1_eta    -> Scale(scale_TTTo2L2Nu);
eltau1h_l0_eta   -> Scale(scale_TTTo2L2Nu);
eltau1h_l1_eta   -> Scale(scale_TTTo2L2Nu);
eltau3h_l0_eta   -> Scale(scale_TTTo2L2Nu);
eltau3h_l1_eta   -> Scale(scale_TTTo2L2Nu);
mutau1h_l0_eta   -> Scale(scale_TTTo2L2Nu);
mutau1h_l1_eta   -> Scale(scale_TTTo2L2Nu);
mutau3h_l0_eta   -> Scale(scale_TTTo2L2Nu);
mutau3h_l1_eta   -> Scale(scale_TTTo2L2Nu);


 eltau1h_b1_pt->Scale(scale_TTTo2L2Nu);
 eltau1h_j1_pt->Scale(scale_TTTo2L2Nu);
 mutau1h_l1_pt->Scale(scale_TTTo2L2Nu);
 mutau1h_b1_pt->Scale(scale_TTTo2L2Nu);
 mutau1h_j1_pt->Scale(scale_TTTo2L2Nu);

  eltau1h_b1_eta->Scale(scale_TTTo2L2Nu);
  eltau1h_j1_eta->Scale(scale_TTTo2L2Nu);
  mutau1h_l1_eta->Scale(scale_TTTo2L2Nu);
  mutau1h_b1_eta->Scale(scale_TTTo2L2Nu);
  mutau1h_j1_eta->Scale(scale_TTTo2L2Nu);

TH1* elel_l0_cumulative_pt       = elel_l0_pt->GetCumulative(false);
TH1* elel_l1_cumulative_pt       = elel_l1_pt->GetCumulative(kFALSE);
TH1* mumu_l0_cumulative_pt       = mumu_l0_pt->GetCumulative(kFALSE);
TH1* mumu_l1_cumulative_pt       = mumu_l1_pt->GetCumulative(kFALSE);
TH1* elmu_l0_cumulative_pt       = elmu_l0_pt->GetCumulative(kFALSE);
TH1* elmu_l1_cumulative_pt       = elmu_l1_pt->GetCumulative(kFALSE);
TH1* eltaul_l0_cumulative_pt     = eltaul_l0_pt->GetCumulative(kFALSE);
TH1* eltaul_l1_cumulative_pt     = eltaul_l1_pt->GetCumulative(kFALSE);
TH1* eltau1h_l0_cumulative_pt    = eltau1h_l0_pt->GetCumulative(kFALSE);
TH1* eltau1h_l1_cumulative_pt    = eltau1h_l1_pt->GetCumulative(kFALSE);
TH1* eltau3h_l0_cumulative_pt    = eltau3h_l0_pt->GetCumulative(kFALSE);
TH1* eltau3h_l1_cumulative_pt    = eltau3h_l1_pt->GetCumulative(kFALSE);
TH1* mutau1h_l0_cumulative_pt    = mutau1h_l0_pt->GetCumulative(kFALSE);
TH1* mutau1h_l1_cumulative_pt    = mutau1h_l1_pt->GetCumulative(kFALSE);
TH1* mutau3h_l0_cumulative_pt    = mutau3h_l0_pt->GetCumulative(kFALSE);
TH1* mutau3h_l1_cumulative_pt    = mutau3h_l1_pt->GetCumulative(kFALSE);
TH1* taueltauh_l0_cumulative_pt  = taueltauh_l0_pt->GetCumulative(kFALSE);
TH1* taueltauh_l1_cumulative_pt  = taueltauh_l1_pt->GetCumulative(kFALSE);
TH1* taumutauh_l0_cumulative_pt  = taumutauh_l0_pt->GetCumulative(kFALSE);
TH1* taumutauh_l1_cumulative_pt  = taumutauh_l1_pt->GetCumulative(kFALSE);


cout <<"PRINTING TOTAL NUMBER OF GENERATED EVENTS FOR TTTo2L2Nu"<< endl;
cout << "elel_elpt: " << endl;
double elpt_bin1 = elel_l0_cumulative_pt->GetBinContent(1);
cout << "elel_elpt0_bin1: " << elpt_bin1 << endl; 

double elpt_bin4 = elel_l0_cumulative_pt->GetBinContent(4);
cout << "elel_elpt20_bin4: " << elpt_bin4 << endl; 

double elpt_bin6 = elel_l0_cumulative_pt->GetBinContent(6);
cout << "elel_elpt30_bin6: " << elpt_bin6 << endl;

double elpt_bin7 = elel_l0_cumulative_pt->GetBinContent(7);
cout << "elel_elpt35_bin7: " << elpt_bin7 << endl; 

 
cout << "mumu_mupt: " << endl;
double mupt_bin1 = mumu_l0_cumulative_pt->GetBinContent(1);
cout << "mumu_mupt0_bin1: " << mupt_bin1 << endl; 

double mupt_bin4 = mumu_l0_cumulative_pt->GetBinContent(4);
cout << "mumu_mupt20_bin4: " << mupt_bin4 << endl; 

double mupt_bin5 = mumu_l0_cumulative_pt->GetBinContent(5);
cout << "mumu_mupt25_bin5: " << mupt_bin5 << endl;

double mupt_bin6 = mumu_l0_cumulative_pt->GetBinContent(6);
cout << "mumu_mupt30_bin6: " << mupt_bin6 << endl;

double mupt_bin7 = mumu_l0_cumulative_pt->GetBinContent(7);
cout << "mumu_mupt35_bin7: " << mupt_bin7 << endl;

//print elmu_elpt
//Note: l0 for lowes id; if l0 and l1 has same id then l0 will have lowset pt
 
cout << "elmu_elpt: " << endl;
double elmu_elpt_bin1 = elmu_l0_cumulative_pt->GetBinContent(1);
cout << "elmu_elpt0_bin1: " << elmu_elpt_bin1 << endl; 

double elmu_elpt_bin4 = elmu_l0_cumulative_pt->GetBinContent(4);
cout << "elmu_elpt20_bin4: " << elmu_elpt_bin4 << endl; 

double elmu_elpt_bin5 = elmu_l0_cumulative_pt->GetBinContent(5);
cout << "elmu_elpt25_bin5: " << elmu_elpt_bin5 << endl;

double elmu_elpt_bin6 = elmu_l0_cumulative_pt->GetBinContent(6);
cout << "elmu_elpt30_bin6: " << elmu_elpt_bin6 << endl;

double elmu_elpt_bin7 = elmu_l0_cumulative_pt->GetBinContent(7);
cout << "elmu_elpt35_bin7: " << elmu_elpt_bin7 << endl;

cout << "elmu_mupt: " << endl;
double elmu_mupt_bin1 = elmu_l1_cumulative_pt->GetBinContent(1);
cout << "elmu_mupt0_bin1: " << elmu_mupt_bin1 << endl; 

double elmu_mupt_bin4 = elmu_l1_cumulative_pt->GetBinContent(4);
cout << "elmu_mupt20_bin4: " << elmu_mupt_bin4 << endl; 

double elmu_mupt_bin5 = elmu_l1_cumulative_pt->GetBinContent(5);
cout << "elmu_mupt25_bin5: " << elmu_mupt_bin5 << endl;

double elmu_mupt_bin6 = elmu_l1_cumulative_pt->GetBinContent(6);
cout << "elmu_mupt30_bin6: " << elmu_mupt_bin6 << endl;

double elmu_mupt_bin7 = elmu_l1_cumulative_pt->GetBinContent(7);
cout << "elmu_mupt35_bin7: " << elmu_mupt_bin7 << endl;



cout << "eltaul_elpt: " << endl;
double eltaul_elpt_bin1 = eltaul_l0_cumulative_pt->GetBinContent(1);
cout << "eltaul_elpt0_bin1: " << eltaul_elpt_bin1 << endl; 

double eltaul_elpt_bin4 = eltaul_l0_cumulative_pt->GetBinContent(4);
cout << "eltaul_elpt20_bin4: " << eltaul_elpt_bin4 << endl; 

double eltaul_elpt_bin5 = eltaul_l0_cumulative_pt->GetBinContent(5);
cout << "eltaul_elpt25_bin5: " << eltaul_elpt_bin5 << endl;

double eltaul_elpt_bin6 = eltaul_l0_cumulative_pt->GetBinContent(6);
cout << "eltaul_elpt30_bin6: " << eltaul_elpt_bin6 << endl;

double eltaul_elpt_bin7 = eltaul_l0_cumulative_pt->GetBinContent(7);
cout << "eltaul_elpt35_bin7: " << eltaul_elpt_bin7 << endl;


cout << "eltau1h_elpt: " << endl;
double eltau1h_elpt_bin1 = eltau1h_l0_cumulative_pt->GetBinContent(1);
cout << "eltau1h_elpt0_bin1: " << eltau1h_elpt_bin1 << endl; 

double eltau1h_elpt_bin4 = eltau1h_l0_cumulative_pt->GetBinContent(4);
cout << "eltau1h_elpt20_bin4: " << eltau1h_elpt_bin4 << endl; 

double eltau1h_elpt_bin5 = eltau1h_l0_cumulative_pt->GetBinContent(5);
cout << "eltau1h_elpt25_bin5: " << eltau1h_elpt_bin5 << endl;

double eltau1h_elpt_bin6 = eltau1h_l0_cumulative_pt->GetBinContent(6);
cout << "eltau1h_elpt30_bin6: " << eltau1h_elpt_bin6 << endl;

double eltau1h_elpt_bin7 = eltau1h_l0_cumulative_pt->GetBinContent(7);
cout << "eltau1h_elpt35_bin7: " << eltau1h_elpt_bin7 << endl;


cout << "eltau3h_elpt: " << endl;
double eltau3h_elpt_bin1 = eltau3h_l0_cumulative_pt->GetBinContent(1);
cout << "eltau3h_elpt0_bin1: " << eltau3h_elpt_bin1 << endl; 

double eltau3h_elpt_bin4 = eltau3h_l0_cumulative_pt->GetBinContent(4);
cout << "eltau3h_elpt20_bin4: " << eltau3h_elpt_bin4 << endl; 

double eltau3h_elpt_bin5 = eltau3h_l0_cumulative_pt->GetBinContent(5);
cout << "eltau3h_elpt25_bin5: " << eltau3h_elpt_bin5 << endl;

double eltau3h_elpt_bin6 = eltau3h_l0_cumulative_pt->GetBinContent(6);
cout << "eltau3h_elpt30_bin6: " << eltau3h_elpt_bin6 << endl;

double eltau3h_elpt_bin7 = eltau3h_l0_cumulative_pt->GetBinContent(7);
cout << "eltau3h_elpt35_bin7: " << eltau3h_elpt_bin7 << endl;


cout << "mutau1h_mupt: " << endl;
double mutau1h_mupt_bin1 = mutau1h_l0_cumulative_pt->GetBinContent(1);
cout << "mutau1h_mupt0_bin1: " << mutau1h_mupt_bin1 << endl; 

double mutau1h_mupt_bin4 = mutau1h_l0_cumulative_pt->GetBinContent(4);
cout << "mutau1h_mupt20_bin4: " << mutau1h_mupt_bin4 << endl; 

double mutau1h_mupt_bin5 = mutau1h_l0_cumulative_pt->GetBinContent(5);
cout << "mutau1h_mupt25_bin5: " << mutau1h_mupt_bin5 << endl;

double mutau1h_mupt_bin6 = mutau1h_l0_cumulative_pt->GetBinContent(6);
cout << "mutau1h_mupt30_bin6: " << mutau1h_mupt_bin6 << endl;

double mutau1h_mupt_bin7 = mutau1h_l0_cumulative_pt->GetBinContent(7);
cout << "mutau1h_mupt35_bin7: " << mutau1h_mupt_bin7 << endl;


cout << "mutau3h_mupt: " << endl;
double mutau3h_mupt_bin1 = mutau3h_l0_cumulative_pt->GetBinContent(1);
cout << "mutau3h_mupt0_bin1: " << mutau3h_mupt_bin1 << endl; 

double mutau3h_mupt_bin4 = mutau3h_l0_cumulative_pt->GetBinContent(4);
cout << "mutau3h_mupt20_bin4: " << mutau3h_mupt_bin4 << endl; 

double mutau3h_mupt_bin5 = mutau3h_l0_cumulative_pt->GetBinContent(5);
cout << "mutau3h_mupt25_bin5: " << mutau3h_mupt_bin5 << endl;

double mutau3h_mupt_bin6 = mutau3h_l0_cumulative_pt->GetBinContent(6);
cout << "mutau3h_mupt30_bin6: " << mutau3h_mupt_bin6 << endl;

double mutau3h_mupt_bin7 = mutau3h_l0_cumulative_pt->GetBinContent(7);
cout << "mutau3h_mupt35_bin7: " << mutau3h_mupt_bin7 << endl;

/*
TH1* h_cumulative = h->GetCumulative(false);//false because this is cumulative in a backward direction
h_cumulative->GetYaxis()->SetTitle("Percentage of muons with higher p_{T} [%]");
h_cumulative->Scale(100./h_cumulative->GetBinContent(1));
  */

// elel_l0_cumulative_pt       ->Scale(1.0/elel_l0_cumulative_pt->GetBinContent(1));
// elel_l1_cumulative_pt       ->Scale(1.0/elel_l1_cumulative_pt->GetBinContent(1));
// mumu_l0_cumulative_pt       ->Scale(1.0/mumu_l0_cumulative_pt->GetBinContent(1));
// mumu_l1_cumulative_pt       ->Scale(1.0/mumu_l1_cumulative_pt->GetBinContent(1));
// elmu_l0_cumulative_pt       ->Scale(1.0/elmu_l0_cumulative_pt->GetBinContent(1));
// elmu_l1_cumulative_pt       ->Scale(1.0/elmu_l1_cumulative_pt->GetBinContent(1));
// eltaul_l0_cumulative_pt     ->Scale(1.0/eltaul_l0_cumulative_pt->GetBinContent(1));
// eltaul_l1_cumulative_pt     ->Scale(1.0/eltaul_l1_cumulative_pt->GetBinContent(1));
// eltau1h_l0_cumulative_pt    ->Scale(1.0/eltau1h_l0_cumulative_pt->GetBinContent(1));
// eltau1h_l1_cumulative_pt    ->Scale(1.0/eltau1h_l1_cumulative_pt->GetBinContent(1));
// eltau3h_l0_cumulative_pt    ->Scale(1.0/eltau3h_l0_cumulative_pt->GetBinContent(1));
// eltau3h_l1_cumulative_pt    ->Scale(1.0/eltau3h_l1_cumulative_pt->GetBinContent(1));
// mutau1h_l0_cumulative_pt    ->Scale(1.0/mutau1h_l0_cumulative_pt->GetBinContent(1));
// mutau1h_l1_cumulative_pt    ->Scale(1.0/mutau1h_l1_cumulative_pt->GetBinContent(1));
// mutau3h_l0_cumulative_pt    ->Scale(1.0/mutau3h_l0_cumulative_pt->GetBinContent(1));
// mutau3h_l1_cumulative_pt    ->Scale(1.0/mutau3h_l1_cumulative_pt->GetBinContent(1));
// taueltauh_l0_cumulative_pt  ->Scale(1.0/taueltauh_l0_cumulative_pt->GetBinContent(1));
// taueltauh_l1_cumulative_pt  ->Scale(1.0/taueltauh_l1_cumulative_pt->GetBinContent(1));
// taumutauh_l0_cumulative_pt  ->Scale(1.0/taumutauh_l0_cumulative_pt->GetBinContent(1));
// taumutauh_l1_cumulative_pt  ->Scale(1.0/taumutauh_l1_cumulative_pt->GetBinContent(1));

  TH1* eltau1h_b1_cumulative_pt = eltau1h_b1_pt->GetCumulative(kFALSE);
  TH1* eltau1h_j1_cumulative_pt = eltau1h_j1_pt->GetCumulative(kFALSE);

  TH1* mutau1h_b1_cumulative_pt = mutau1h_b1_pt->GetCumulative(kFALSE);
  TH1* mutau1h_j1_cumulative_pt = mutau1h_j1_pt->GetCumulative(kFALSE);




//parsing xsection from xml file
/*
>>> import get_xsec_for_file as xsec
>>> dir(xsec)
['DsetsInfo', 'ET', '__builtins__', '__doc__', '__file__', '__name__', '__package__', 'argparse', 'logging']
>>> di = xsec.DsetsInfo()
>>> dir(di)
['__doc__', '__init__', '__module__', '_dsets_info_file', '_hps', '_root', 'match_hp_by_dtag']
>>> di.match_hp_by_dtag('WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/Ntupler_94v15_MC2017legacy_Fall17_WJets_madgraph_v2/200225_120706/00')
(<Element 'hard_process' at 0x7f2c10fdc590>, 'MC2017legacy_Fall17_WJets_madgraph_v2')
>>> hard_process, matched_dtag = di.match_hp_by_dtag('WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/Ntupler_94v15_MC2017legacy_Fall17_WJets_madgraph_v2/200225_120706/00')
>>> float(hard_process.get('xsec'))
50690.0
>>> matched_dtag
'MC2017legacy_Fall17_WJets_madgraph_v2'
*/

/*
#include <Riostream.h>
#include <TDOMParser.h>
#include <TXMLAttr.h>
#include <TXMLNode.h>
#include <TList.h>

class hardprocess: public TObject
{
  private: 
  TString lumimask;
  bool isMC;
  double xsec;
public:
   hardprocess() { }
   hardprocess( TString l, bool isMC, double x) :
      lumimask(l), isMC(isMC),xsec(x){ }

double Getxsec() const { return xsec; } ;

} ;
*/



TFile out_file("gendistrs_temp1.root","RECREATE");

elel_l0_pt       ->Write();
elel_l1_pt       ->Write();
mumu_l0_pt       ->Write();
mumu_l1_pt       ->Write();
elmu_l0_pt       ->Write();
elmu_l1_pt       ->Write();
eltaul_l0_pt     ->Write();
eltaul_l1_pt     ->Write();
eltau1h_l0_pt    ->Write();
eltau1h_l1_pt    ->Write();
eltau3h_l0_pt    ->Write();
eltau3h_l1_pt    ->Write();
mutau1h_l0_pt    ->Write();
mutau1h_l1_pt    ->Write();
mutau3h_l0_pt    ->Write();
mutau3h_l1_pt    ->Write();
taueltauh_l0_pt ->Write();
taueltauh_l1_pt ->Write();
taumutauh_l0_pt ->Write();
taumutauh_l1_pt ->Write();

eltaul_l0_eta    ->Write();
eltaul_l1_eta    ->Write();
eltau1h_l0_eta   ->Write();
eltau1h_l1_eta   -> Write();
eltau3h_l0_eta   -> Write();
eltau3h_l1_eta   -> Write();
mutau1h_l0_eta   -> Write();
mutau1h_l1_eta   -> Write();
mutau3h_l0_eta   -> Write();
mutau3h_l1_eta   -> Write();

 elel_l0_cumulative_pt       ->Write();
 elel_l1_cumulative_pt       ->Write();
 mumu_l0_cumulative_pt       ->Write();
 mumu_l1_cumulative_pt       ->Write();
 elmu_l0_cumulative_pt       ->Write();
 elmu_l1_cumulative_pt       ->Write();
 eltaul_l0_cumulative_pt     ->Write();
 eltaul_l1_cumulative_pt     ->Write();
 eltau1h_l0_cumulative_pt    ->Write();
 eltau1h_l1_cumulative_pt    ->Write();
 eltau3h_l0_cumulative_pt    ->Write();
 eltau3h_l1_cumulative_pt    ->Write();
 mutau1h_l0_cumulative_pt    ->Write();
 mutau1h_l1_cumulative_pt    ->Write();
 mutau3h_l0_cumulative_pt    ->Write();
 mutau3h_l1_cumulative_pt    ->Write();
 taueltauh_l0_cumulative_pt ->Write();
 taueltauh_l1_cumulative_pt ->Write();
 taumutauh_l0_cumulative_pt ->Write();
 taumutauh_l1_cumulative_pt ->Write();




   eltau1h_b1_pt->Write();
   eltau1h_j1_pt->Write();
 
   mutau1h_b1_pt->Write();
   mutau1h_j1_pt->Write();

   eltau1h_b1_cumulative_pt->Write();
   eltau1h_j1_cumulative_pt->Write();
   
   mutau1h_b1_cumulative_pt->Write();
   mutau1h_j1_cumulative_pt->Write();


   eltau1h_b1_eta->Write();
   eltau1h_j1_eta->Write();
  
   mutau1h_b1_eta->Write();
   mutau1h_j1_eta->Write();



   out_file.Close();


}
