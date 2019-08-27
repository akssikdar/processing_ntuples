from sys import argv
import os
from os.path import isfile
import logging
import threading

from sys import version_info
print version_info

#logging.basicConfig(level=logging.DEBUG)
log_common = logging.getLogger("common")


if __name__ == '__main__':
    #main(argv)
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = "Select the distrs with systematics from processed jobs.",
        #epilog = "Example:\n$ python job_submit.py ttbarleps80_eventSelection jobing/my_runAnalysis_cfg_NEWSUBMIT.templ.py bin/ttbar-leptons-80X/analysis/dsets_testing_noHLT_TTbar.json test/tests/outdir_test_v11_ttbar_v8.40/"
        )
    #def main(input_dir, dtag, outdir, range_min, range_max):

    #parser.add_argument("input_file", help="file with results from job")
    #parser.add_argument("dtag",      help="basically it's the filename with the TTree from jobs")
    parser.add_argument("outdir",    help="where to store the output")
    parser.add_argument("channels",  help="channels of the selection")
    parser.add_argument("-l", "--log-file",  type=str, default='', help="if given the log of the process will go to this file under outdir/log/<log_file>")
    #parser.add_argument("-s", "--range-min", type=int, default=0,    help="number of event to start processing from")
    #parser.add_argument("-e", "--range-max",   type=int, default=None, help="number of event to end processing")
    parser.add_argument("-i", "--input-files", nargs='+', help='files to process (each is run in a thread)')
    parser.add_argument("--old-miniaod-jets",  action='store_true', help="the option to run on pre-v20 incorectly saved jets (initial empty, save in nominal jets)")
    parser.add_argument("--do-W-stitching",    action='store_true', help="turn ON skipping NUP events of inclusive sample")
    parser.add_argument("--all-jets",          action='store_true', help="propagate tau-jet correction too")
    parser.add_argument("--without-bSF",       action='store_true', help="don't apply b tagging SF")
    parser.add_argument("--old-loop",          action='store_true', help="run on old full selection")

    parser.add_argument("--overwrite",      action='store_true', help="overwrite output")
    parser.add_argument("--thread",         action='store_true', help="run stage2 in a separate thread")

    parser.add_argument("--metmuegclean",      type=str, default='true', help="use slimmedMETsMuEGClean MET for data")
    parser.add_argument("--n-recoil-jets",     type=int, help="set recoil jets for W+jets and dy+jets")

    parser.add_argument("--options", type=str, help="options for stage2")

    args = parser.parse_args()

    # configure log and common file for threads
    try:
        os.makedirs(args.outdir + '/logs/')
        
    except OSError as e:
        print e.errno, e.strerror

    if args.log_file:
        logger_file = args.outdir + '/logs/' + args.log_file.split('/')[-1].split('.root')[0] + '.log'
        hdlr = logging.FileHandler(logger_file)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        log_common.addHandler(hdlr)
        log_common.setLevel(logging.DEBUG)

    else:
        log_common.basicConfig(level=logging.DEBUG)

    if args.thread:
        log_common.info('running threads  on %d files' % len(args.input_files))
    else:
        log_common.info('running directly on %d files' % len(args.input_files))


    for input_filename in args.input_files:
        #main(args.input_file, args.outdir, args.range_min, args.range_max)

        # check if output file already exists to not import ROOT
        #input_tfile = TFile(input_filename)
        #tree = input_tfile.Get('ntupler/reduced_ttree')
        #if not range_max: range_max = tree.GetEntries()

        fout_name = input_filename.split('/')[-1].split('.root')[0] + ".root" # no ranges anymore

        if isfile(args.outdir + '/' + fout_name) and not args.overwrite:
            print "output file exists: %s" % (args.outdir + '/' + fout_name)
            continue

        if args.old_loop:
            import full_selection
            from full_selection import main # ROOT stuff is loaded here
            full_selection.OLD_MINIAOD_JETS = args.old_miniaod_jets
            full_selection.W_STITCHING = args.do_W_stitching
            full_selection.ALL_JETS = args.all_jets
            full_selection.ALL_JETS = args.all_jets
            if args.without_bSF:
                full_selection.with_bSF = False

        else:
            import stage2
            from stage2 import main # ROOT stuff is loaded here
            stage2.OLD_MINIAOD_JETS = args.old_miniaod_jets
            stage2.W_STITCHING = args.do_W_stitching
            if args.metmuegclean and args.metmuegclean == 'false':
                stage2.METMuEGClean = not (args.metmuegclean == 'false')
                print 'METMuEGClean', stage2.METMuEGClean
            else:
                print 'no METMuEGClean'
            stage2.ALL_JETS = args.all_jets
            stage2.ALL_JETS = args.all_jets
            if args.without_bSF:
                stage2.with_bSF = False

            if args.n_recoil_jets:
                stage2.N_RECOIL_JETS = args.n_recoil_jets

            if args.options:
              if 'no_prop_tau' in args.options:
                stage2.PROP_TAU = False
                print 'no_prop_tau', stage2.PROP_TAU
              if 'no_prop_jets' in args.options:
                stage2.PROP_JETS = False
                print 'no_prop_jets', stage2.PROP_JETS
              if 'on_prop_lepjets' in args.options:
                stage2.PROP_LEPJET = True
                print 'on_prop_lepjets', stage2.PROP_LEPJET
              if 'no_prop_lepjets' in args.options:
                stage2.PROP_LEPJET = False
                print 'no_prop_lepjets', stage2.PROP_LEPJET

              if 'on_uncor_lepjets' in args.options:
                stage2.PROP_UNCORLEPJET = True
                print 'on_uncor_lepjets', stage2.PROP_UNCORLEPJET

              if 'on_uncor_taujets' in args.options:
                stage2.PROP_UNCORTAUJET = True
                print 'on_uncor_taujets', stage2.PROP_UNCORTAUJET

              if 'on_remove_lepjets' in args.options:
                stage2.REMOVE_LEPJET = True
                print 'on_remove_lepjets', stage2.REMOVE_LEPJET

              if 'no_prop_lepjets_uncluster' in args.options:
                stage2.PROP_LEPJET_UNCLUSTER = False
                print 'no_prop_lepjets_uncluster', stage2.PROP_LEPJET_UNCLUSTER

        if args.thread:
            t = threading.Thread(target=main, args=(input_filename, fout_name, args.outdir, args.channels))
            t.start()
            log_common.info('started thread on %s' % input_filename)
        else:
            log_common.info('running on %s' % input_filename)
            main(input_filename, fout_name, args.outdir, args.channels)


