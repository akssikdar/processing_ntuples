import argparse
import logging
from os.path import isfile, basename
import ctypes




parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description = "sumup TTree Draw",
    epilog = """Example:\npython sumup_ttree_draw.py "met_init.pt()" --histo-range 200,0,200 --histo-name data_met_init --output data_met_init.root gstore_outdirs/v28/SingleMuon/Ntupler_v28_Data13TeV_SingleMuon2016*/1*/*/*root
python sumup_ttree_draw.py "event_leptons[0].pt()" --ttree ttree_out --cond-com "selection_stage == 5" --histo-range 50,0,200 --output test1_lep_pt.root --histo-name foo/bar/test1_lep_pt --save-weight MC2016_Summer16_TTJets_powheg_test1.root """
    )

parser.add_argument('draw_com', type=str, help='Draw("??")')
parser.add_argument('--cond-com', type=str, default="", help='Draw("", "??")')
parser.add_argument('--ttree',    type=str, default="ntupler/reduced_ttree", help='path to the TTree in the file')
parser.add_argument('--histo-name',  type=str, default="out_histo", help='the ROOTName for output')
parser.add_argument('--std-histo-name',  type=str, default="distr", help='construct standard name for histogram: take "path" part from --histo-name and "distr" part from here, attach as chan_proc_sys_distr')
parser.add_argument('--histo-color', type=str, default=None, help='optional rgb color, like `255,255,255`')
parser.add_argument('--histo-range',  type=str, default=None, help='optionally set the range')
parser.add_argument('--custom-range', type=str, default=None, help='optionally set the range in custom bins')
parser.add_argument("--try-xsec",  action='store_true', help="try to normalize to cross-section, if the output filename contains dtag")

parser.add_argument("--std-histos",  action='store_true', help="parse standard histo names, support standard channels, processes and systematics")

parser.add_argument("--debug",  action='store_true', help="DEBUG level of logging")
parser.add_argument("--output", type=str, default="output.root", help="filename for output")

parser.add_argument("--save-weight", action='store_true', help="save the weight counters in the output file")
parser.add_argument("--per-weight",  action='store_true', help="normalize by event weight of datasets")
parser.add_argument("--scale", type=float, help="the value to scale histo")
parser.add_argument("--scan",        action='store_true', help="also scan events ant print out")
parser.add_argument("--get-maximum", action='store_true', help="just find maxima on the draw_com")

parser.add_argument('input_files', nargs='+', help="""the files to sum up, passed by shell, as:

/gstore/t3cms/store/user/otoldaie/v19/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/Ntupler_v19_MC2016_Summer16_TTJets_powheg/180226_022336/0000/MC2016_Summer16_TTJets_powheg_*.root""")


args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

# [/]histo_path/histo_name
histo_name = args.histo_name.split('/')[-1]
histo_path = args.histo_name.split('/')[:-1]
# skip empty parts in the path (sequences of ////)
histo_path = [part for part in histo_path if part]

condition_string = args.cond_com

if args.std_histos:
    # 4 strings for names and they are not empty
    assert len(args.histo_name.split('/')) == 4 and all(args.histo_name.split('/'))
    chan, proc, sys, histo_name = args.histo_name.split('/')
    histo_path = [chan, proc, sys]
    # later proc and sys are expanded to standard definitions
    # if proc == 'std_procs': ...
    # if sys  == 'std_sys': ,,,




logging.info("import ROOT")

import ROOT
from ROOT import TH1D, TFile, TTree, gROOT
from ROOT import kGreen, kYellow, kOrange, kViolet, kAzure, kWhite, kGray, kRed, kCyan, TColor
from ROOT import TLegend
#from ROOT import THStack

logging.info("done")

from plotting_root import rgb

gROOT.SetBatch()



input_files = args.input_files


'''
out_histo  = TH1D("os_tauall", "", 44, -2, 20)
tau_b      = TH1D("os_taub", "", 44, -2, 20)
tau_w      = TH1D("os_tauw", "", 44, -2, 20)
tau_w_c    = TH1D("os_tauw_c", "", 44, -2, 20)
tau_w_notc = TH1D("os_tauw_notc", "", 44, -2, 20)

ss_tau_all    = TH1D("ss_tauall", "", 44, -2, 20)
ss_tau_b      = TH1D("ss_taub", "", 44, -2, 20)
ss_tau_w      = TH1D("ss_tauw", "", 44, -2, 20)
ss_tau_w_c    = TH1D("ss_tauw_c", "", 44, -2, 20)
ss_tau_w_notc = TH1D("ss_tauw_notc", "", 44, -2, 20)
'''


if args.histo_color:
    logging.debug("color: " + args.histo_color)
else:
    logging.debug("no color")

'''
root [4] double pt_bins[] = {20, 30, 40, 50, 70, 90, 120, 150, 200, 300, 2000};
root [5] 
root [5] sizeof
ROOT_prompt_5:2:1: error: expected expression
;
^
root [6] sizeof(pt_bins)
(unsigned long) 88
root [7] 
root [7] sizeof(double)
(unsigned long) 8
root [8] 
root [8] int pt_bins_n = 10
(int) 10
root [9] 
root [9] 
root [9] TH1D* hpts = new TH1D("hpts", "", pt_bins_n, pt_bins)
(TH1D *) 0x4db6750
root [10] hpts
(TH1D *) 0x4db6750
root [11] 
root [11] 
root [11] ttree_out->Draw("event_leptons[0].pt()>>hpts")
'''

if args.try_xsec:
    from per_dtag_script import dtags

# Draw command
# 
temp_output_histo = None # histo-template for custom bins
if args.custom_range:
    bin_edges = [float(b) for b in args.custom_range.split(',')]
    n_bin_edges = len(bin_edges)
    n_bins = n_bin_edges - 1
    logging.debug("making %d bins from %s" % (n_bins, args.custom_range))

    # first method
    root_bin_edges = (ctypes.c_double * n_bin_edges)(*bin_edges)
    temp_output_histo = TH1D("histotemp", "", n_bins, root_bin_edges) # root commands can access it by the name

    draw_command = args.draw_com + '>>' + "histotemp"
elif args.histo_range:
    draw_command = args.draw_com + ">>h(%s)" % args.histo_range
else:
    # TOFIX: without explicit range the histos won't add up
    draw_command = args.draw_com

logging.debug("draw: " + draw_command)
logging.debug("cond: " + args.cond_com)
if temp_output_histo:
    logging.debug("temp: " + temp_output_histo.GetName())
    #temp_output_histo.SetDirectory(0)
    # and some preparation for root stuff
    ROOT.gROOT.ProcessLine('TFile* intfile;')
    ROOT.gROOT.ProcessLine('TTree* inttree;')

out_histo = None
weight_counter = None



'''
contruct the output histos
for standard outputs
definitions of:
* sub-processes
* main selections
* systematics

condition string is defined by chan, proc and systematic like:
(chan && proc) * sys_weight

and I use the chan in 1 of systematics: LEP el or LEP mu


for a given dtag (a file or a bunch of them)
all chan/proc/sys apply independently
-- a list of (name, 'def_string') for each


if the std-histos option is given
the chan, proc, sys are parsed for names of standard defs or special names as 'std_procs' or 'all'
'''

all_std_channels = {
'mu_sel':          '{selection_stage}==107',
'mu_sel_ss':       '{selection_stage}==106',
'el_sel':          '{selection_stage}==117',
'el_sel_ss':       '{selection_stage}==116',
'mu_selVloose':    '({selection_stage}==107 || {selection_stage}==105)',
'mu_selVloose_ss': '({selection_stage}==106 || {selection_stage}==104)',
'el_selVloose':    '({selection_stage}==117 || {selection_stage}==115)',
'el_selVloose_ss': '({selection_stage}==116 || {selection_stage}==114)',

'mu_sel_ljout':          '{selection_stage}==107 && event_jets_lj_var >  60.',
'mu_sel_ljout_ss':       '{selection_stage}==106 && event_jets_lj_var >  60.',
'el_sel_ljout':          '{selection_stage}==117 && event_jets_lj_var >  60.',
'el_sel_ljout_ss':       '{selection_stage}==116 && event_jets_lj_var >  60.',
'mu_selVloose_ljout':    '({selection_stage}==107 || {selection_stage}==105) && event_jets_lj_var >  60.',
'mu_selVloose_ljout_ss': '({selection_stage}==106 || {selection_stage}==104) && event_jets_lj_var >  60.',
'el_selVloose_ljout':    '({selection_stage}==117 || {selection_stage}==115) && event_jets_lj_var >  60.',
'el_selVloose_ljout_ss': '({selection_stage}==116 || {selection_stage}==114) && event_jets_lj_var >  60.',

'mu_sel_lj':          '{selection_stage}==107 && event_jets_lj_var <= 60.',
'mu_sel_lj_ss':       '{selection_stage}==106 && event_jets_lj_var <= 60.',
'el_sel_lj':          '{selection_stage}==117 && event_jets_lj_var <= 60.',
'el_sel_lj_ss':       '{selection_stage}==116 && event_jets_lj_var <= 60.',
'mu_selVloose_lj':    '({selection_stage}==107 || {selection_stage}==105) && event_jets_lj_var <= 60.',
'mu_selVloose_lj_ss': '({selection_stage}==106 || {selection_stage}==104) && event_jets_lj_var <= 60.',
'el_selVloose_lj':    '({selection_stage}==117 || {selection_stage}==115) && event_jets_lj_var <= 60.',
'el_selVloose_lj_ss': '({selection_stage}==116 || {selection_stage}==114) && event_jets_lj_var <= 60.',
}

# object systematics change the selection
#"selection_stage_JERDown ${cond}" 'JERDown': event_weight  ${merge_dir}/${nt}/${p}/*${dtag}*.root
#"selection_stage_JERUp   ${cond}" 'JERUp'  : event_weight  ${merge_dir}/${nt}/${p}/*${dtag}*.root
#"selection_stage_JESDown ${cond}" 'JESDown': event_weight  ${merge_dir}/${nt}/${p}/*${dtag}*.root
#"selection_stage_JESUp   ${cond}" 'JESUp'  : event_weight  ${merge_dir}/${nt}/${p}/*${dtag}*.root
#"selection_stage_TESDown ${cond}" 'TESDown': event_weight  ${merge_dir}/${nt}/${p}/*${dtag}*.root
#"selection_stage_TESUp   ${cond}" 'TESUp'  : event_weight  ${merge_dir}/${nt}/${p}/*${dtag}*.root

systs_objects = {
'JERDown':  'selection_stage_JERDown',
'JERUp'  :  'selection_stage_JERUp'  ,
'JESDown':  'selection_stage_JESDown',
'JESUp'  :  'selection_stage_JESUp'  ,
'TESDown':  'selection_stage_TESDown',
'TESUp'  :  'selection_stage_TESUp'  ,
}

# check is a syst name is in objects
#    if so -> change the selection and pick up nominal weight
#    else  -> check it's in the weights

systs_weights_nominal = {
'NOMINAL': 'event_weight',
}

systs_weights_common = {
'PUUp'   : "event_weight*event_weight_PUUp/event_weight_PU"    ,
'PUDown' : "event_weight*event_weight_PUUp/event_weight_PU"    ,
'bSFUp'  : "event_weight*event_weight_bSFUp/event_weight_bSF"  ,
'bSFDown': "event_weight*event_weight_bSFDown/event_weight_bSF",

'LEPelIDUp'   : "event_weight*event_weight_LEPidUp"   ,
'LEPelIDDown' : "event_weight*event_weight_LEPidDown" ,
'LEPelTRGUp'  : "event_weight*event_weight_LEPtrgUp"  ,
'LEPelTRGDown': "event_weight*event_weight_LEPtrgDown",
'LEPmuIDUp'   : "event_weight*event_weight_LEPidUp"   ,
'LEPmuIDDown' : "event_weight*event_weight_LEPidDown" ,
'LEPmuTRGUp'  : "event_weight*event_weight_LEPtrgUp"  ,
'LEPmuTRGDown': "event_weight*event_weight_LEPtrgDown",
}

systs_weights_tt = {
'TOPPTDown'     : 'event_weight'                           ,
'TOPPTUp'       : 'event_weight*event_weight_toppt'        ,
'FragUp'        : 'event_weight*event_weight_FragUp'       ,
'FragDown'      : 'event_weight*event_weight_FragDown'     ,
'SemilepBRUp'   : 'event_weight*event_weight_SemilepBRUp'  ,
'SemilepBRDown' : 'event_weight*event_weight_SemilepBRDown',
'PetersonUp'    : 'event_weight*event_weight_PetersonUp'   ,
'PetersonDown'  : 'event_weight'                           ,
}

systs_weights_tt_hard = {
"MrUp"    : "event_weight*event_weight_me_f_rUp",
"MrDown"  : "event_weight*event_weight_me_f_rDn",
"MfUp"    : "event_weight*event_weight_me_fUp_r",
"MfDown"  : "event_weight*event_weight_me_fDn_r",
"MfrUp"   : "event_weight*event_weight_me_frUp" ,
"MfrDown" : "event_weight*event_weight_me_frDn" ,
}

systs_weights_tt_alpha_pdf = {
'AlphaSUp'  : "event_weight*event_weight_AlphaS_up",
'AlphaSDown': "event_weight*event_weight_AlphaS_dn",

'PDFCT14n1Up'     : "event_weight*event_weight_pdf[0]" ,
'PDFCT14n2Up'     : "event_weight*event_weight_pdf[1]" ,
'PDFCT14n3Up'     : "event_weight*event_weight_pdf[2]" ,
'PDFCT14n4Up'     : "event_weight*event_weight_pdf[3]" ,
'PDFCT14n5Up'     : "event_weight*event_weight_pdf[4]" ,
'PDFCT14n6Up'     : "event_weight*event_weight_pdf[5]" ,
'PDFCT14n7Up'     : "event_weight*event_weight_pdf[6]" ,
'PDFCT14n8Up'     : "event_weight*event_weight_pdf[7]" ,
'PDFCT14n9Up'     : "event_weight*event_weight_pdf[8]" ,
'PDFCT14n10Up'    : "event_weight*event_weight_pdf[9]" ,
'PDFCT14n11Up'    : "event_weight*event_weight_pdf[10]",
'PDFCT14n12Up'    : "event_weight*event_weight_pdf[11]",
'PDFCT14n13Up'    : "event_weight*event_weight_pdf[12]",
'PDFCT14n14Up'    : "event_weight*event_weight_pdf[13]",
'PDFCT14n15Up'    : "event_weight*event_weight_pdf[14]",
'PDFCT14n16Up'    : "event_weight*event_weight_pdf[15]",
'PDFCT14n17Up'    : "event_weight*event_weight_pdf[16]",
'PDFCT14n18Up'    : "event_weight*event_weight_pdf[17]",
'PDFCT14n19Up'    : "event_weight*event_weight_pdf[18]",
'PDFCT14n20Up'    : "event_weight*event_weight_pdf[19]",
'PDFCT14n21Up'    : "event_weight*event_weight_pdf[20]",
'PDFCT14n22Up'    : "event_weight*event_weight_pdf[21]",
'PDFCT14n23Up'    : "event_weight*event_weight_pdf[22]",
'PDFCT14n24Up'    : "event_weight*event_weight_pdf[23]",
'PDFCT14n25Up'    : "event_weight*event_weight_pdf[24]",
'PDFCT14n26Up'    : "event_weight*event_weight_pdf[25]",
'PDFCT14n27Up'    : "event_weight*event_weight_pdf[26]",
'PDFCT14n28Up'    : "event_weight*event_weight_pdf[27]",
'PDFCT14n29Up'    : "event_weight*event_weight_pdf[28]",
'PDFCT14n30Up'    : "event_weight*event_weight_pdf[29]",
'PDFCT14n31Up'    : "event_weight*event_weight_pdf[30]",
'PDFCT14n32Up'    : "event_weight*event_weight_pdf[31]",
'PDFCT14n33Up'    : "event_weight*event_weight_pdf[32]",
'PDFCT14n34Up'    : "event_weight*event_weight_pdf[33]",
'PDFCT14n35Up'    : "event_weight*event_weight_pdf[34]",
'PDFCT14n36Up'    : "event_weight*event_weight_pdf[35]",
'PDFCT14n37Up'    : "event_weight*event_weight_pdf[36]",
'PDFCT14n38Up'    : "event_weight*event_weight_pdf[37]",
'PDFCT14n39Up'    : "event_weight*event_weight_pdf[38]",
'PDFCT14n40Up'    : "event_weight*event_weight_pdf[39]",
'PDFCT14n41Up'    : "event_weight*event_weight_pdf[40]",
'PDFCT14n42Up'    : "event_weight*event_weight_pdf[41]",
'PDFCT14n43Up'    : "event_weight*event_weight_pdf[42]",
'PDFCT14n44Up'    : "event_weight*event_weight_pdf[43]",
'PDFCT14n45Up'    : "event_weight*event_weight_pdf[44]",
'PDFCT14n46Up'    : "event_weight*event_weight_pdf[45]",
'PDFCT14n47Up'    : "event_weight*event_weight_pdf[46]",
'PDFCT14n48Up'    : "event_weight*event_weight_pdf[47]",
'PDFCT14n49Up'    : "event_weight*event_weight_pdf[48]",
'PDFCT14n50Up'    : "event_weight*event_weight_pdf[49]",
'PDFCT14n51Up'    : "event_weight*event_weight_pdf[50]",
'PDFCT14n52Up'    : "event_weight*event_weight_pdf[51]",
'PDFCT14n53Up'    : "event_weight*event_weight_pdf[52]",
'PDFCT14n54Up'    : "event_weight*event_weight_pdf[53]",
'PDFCT14n55Up'    : "event_weight*event_weight_pdf[54]",
'PDFCT14n56Up'    : "event_weight*event_weight_pdf[55]",
}

named_systs_weights_all = {'nom': systs_weights_nominal,
'common': systs_weights_common,
'tt_weights': systs_weights_tt,
'tt_hard': systs_weights_tt_hard,
'tt_pdf':  systs_weights_tt_alpha_pdf,
}

systs_weights_all = {}
for systs in named_systs_weights_all.values():
    systs_weights_all.update(systs)


if args.get_maximum:
   maximum = -1111111.

for filename in input_files:
    if not isfile(filename):
        logging.info("missing: " + filename)
        continue

    logging.debug(filename)

    tfile = TFile(filename)
    ttree = tfile.Get(args.ttree)
    if temp_output_histo:
        temp_output_histo.SetDirectory(tfile)
        # in ROOT the TTree.Draw command "sees" only histograms in current working directory
        # after opening new file ROOT moves working directory into that file
        # therefore move temp tehre too
        # probably it moving current directory to some 0 directory could work
        # and as probable is the possibility to bring more troubles that way

    # Draw the file and sum up
    # 
    # TOFIX: without explicit range the histos won't add up, need to pick up the range of the first histo and propagate to the following?

    if args.get_maximum:
        m = ttree.GetMaximum(args.draw_com)
        print "%30s %f" % (basename(filename), m)
        maximum = max(m, maximum)
    else:
        ttree.Draw(draw_command, condition_string)

        if temp_output_histo:
            # if there is temp histo then the histo was written there
            logging.debug(temp_output_histo.Integral())
            logging.debug(ROOT.histotemp.Integral())
            histo = temp_output_histo
        else:
            histo = ttree.GetHistogram()
            histo.SetDirectory(0)

        # handle errors
        histo.Sumw2()

        if args.per_weight or args.save_weight:
            wcounter = tfile.Get('ntupler/weight_counter')
            if not wcounter:
                # try top level
                wcounter = tfile.Get('weight_counter')
            assert bool(wcounter)
            if not weight_counter:
                weight_counter = wcounter
                weight_counter.SetDirectory(0)
                weight_counter.SetName("sumup_weight_counter")
            else:
                weight_counter.Add(wcounter)

        if not out_histo:
            out_histo = histo.Clone()
            out_histo.SetName(histo_name)
            out_histo.SetDirectory(0)
            out_histo.Sumw2()
        else:
            out_histo.Add(histo)

    if args.scan:
        print filename
        ttree.Scan(args.draw_com, args.cond_com)

    # on closing the file all objects in it might be deleted
    # therefore move away the temp histo
    if temp_output_histo:
        temp_output_histo.SetDirectory(0)

    tfile.Close()

if args.per_weight:
    #weight_counter = tfile.Get('ntupler/weight_counter')
    out_histo.Scale(1./weight_counter.GetBinContent(2))

if args.try_xsec:
    matched_dtag = None
    for dtag in dtags:
        if dtag in args.output:
            matched_dtag = dtag
            break

    nickname, xsec = dtags.get(matched_dtag, 1.)
    out_histo.Scale(xsec)

if args.scale:
    out_histo.Scale(args.scale)

if args.histo_color:
    out_histo.SetLineColor(rgb(*(int(i) for i in args.histo_color.split(','))))


if args.get_maximum:
   print "Max:", maximum

''' no legend for now
leg = TLegend(0.5, 0.5, 0.9, 0.9)
leg.SetName("legOS")

leg.AddEntry(tau_all    , "tt->lj, OS, all", 'L')
leg.AddEntry(tau_b      , "tt->lj, OS, b prod", 'L')
leg.AddEntry(tau_w      , "tt->lj, OS, w prod", 'L')
leg.AddEntry(tau_w_c    , "tt->lj, OS, w, C flav", 'L')
leg.AddEntry(tau_w_notc , "tt->lj, OS, w, not C", 'L')

leg2 = TLegend(0.5, 0.5, 0.9, 0.9)
leg2.SetName("legSS")

leg2.AddEntry(tau_all    , "tt->lj, SS, all", 'L')
leg2.AddEntry(tau_b      , "tt->lj, SS, b prod", 'L')
leg2.AddEntry(tau_w      , "tt->lj, SS, w prod", 'L')
leg2.AddEntry(tau_w_c    , "tt->lj, SS, w, C flav", 'L')
leg2.AddEntry(tau_w_notc , "tt->lj, SS, w, not C", 'L')
'''


fout = TFile(args.output, "RECREATE")
fout.Write()

fout.cd()

# corresponding to old protocol everything is saved as
# channel/process/systematic/channel_process_systematic_distr
# -- the final part is the name of the histogram, which must be unique in root
#    the rest is for convenience
# in principle, root handles many same name histos in different directories, but can run into some weirdness on practice
# that's why this protocol is still kept

# if trying the xsec -- plug the nickname too and construct standard name if needed
if args.try_xsec and len(histo_path) > 1:
    histo_path[1] = nickname
    logging.debug("new path: " + '/'.join(histo_path))
    if args.std_histo_name:
        #
        distr = args.std_histo_name
        histo_name = "{path_part}_{distr}".format(path_part='_'.join(histo_path), distr=distr)
        logging.debug("new histo name: " + histo_name)
        out_histo.SetName(histo_name)

# check if this directory already exists in the file (a feature for future)
out_dir_name = ''.join(part + '/' for part in histo_path)
if out_dir_name and fout.Get(out_dir_name):
    logging.debug('found  ' + out_dir_name)
    out_dir = fout.Get(out_dir_name)
else:
    logging.debug('making ' + out_dir_name)
    # iteratively create each directory fout -> part0 -> part1 -> ...
    # somehow root did not work for creating them in 1 go
    out_dir = fout
    for directory in histo_path:
        nested_dir = out_dir.Get(directory) if out_dir.Get(directory) else out_dir.mkdir(directory)
        nested_dir.cd()
        out_dir = nested_dir

# save the histogram in this nested directory
#for histo in histos.values():
#    histo.SetDirectory(out_dir)
#    histo.Write()

out_histo.SetDirectory(out_dir)
out_histo.Write()

# save weight counters etc in the top directory in the file
if args.save_weight:
    fout.cd()
    weight_counter.SetName('weight_counter')
    weight_counter.Write()

fout.Write()
fout.Close()

