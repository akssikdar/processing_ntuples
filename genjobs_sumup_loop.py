import argparse
import logging

import re
import glob
from os import listdir, mkdir, makedirs
from os.path import isdir, isfile, join, getmtime

SUMUP_LOOP_COMMAND_TEMPLATE = "{exe} {interface_type} {simulate_data_output} 1 0 {lumi} {systematics} {channels} {processes} {distrs} {{output_file}} {{input_files}}"
# {distrs_dir}/{vNtupler}/{vHists}/{{DSET}}.root
# {ntuples_dir}/{vNtupler}/{{DSET}}/*/*/*/*.root"

'''
each job makes histograms from a chunk of dataset files
and outputs the histograms in 1 file
'''


parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description = "generate job queues for sumup_loop that operate directly on Ntuples, without the proc stage",
    epilog = "Example:\n$ python3 genjobs_sumup_loop.py 94v15 hists_3"
    )

default_dir_queue = './queue_dir/'
default_dir_distrs = './jobsums/distrs/'
default_dir_nt =  '/eos/user/a/asikdar/' # './gstore_outdirs/'

parser.add_argument("vNtupler",    help="Ntupler output version")
parser.add_argument("vHists",      help="Histograms version")

parser.add_argument("--dsets-grep",  type=str, default='.',
    help=f"select only the datasets in the {default_dir_nt}/vNtupler that matches this regexp (default passes all)")

parser.add_argument('-n', '--number-jobs',  type=int, default=5,
    help="number of Ntupler job files processed by 1 sumup_loop job (default 5)")

parser.add_argument("--queue-dir",      type=str, default=default_dir_queue,
        help=f"the directory for storing the generated job queues (default {default_dir_queue})")
parser.add_argument("--distrs-dir",     type=str, default=default_dir_distrs,
        help=f"the directory for storing the generated job queues (default {default_dir_distrs})")
parser.add_argument("--ntuples-dir",    type=str, default=default_dir_nt,
        help=f'the directory with Ntupler outputs (default {default_dir_nt})')

parser.add_argument("--systematics", type=str, default='std', help="the systematics in the produced histograms")
parser.add_argument("--channels",    type=str, default='el_sel,mu_sel,tt_elmu,el_sel_tauSV3,mu_sel_tauSV3', help="the selection channels in the produced histograms")
parser.add_argument("--processes",   type=str, default='std', help="the gen-level processes in the produced MC histograms")
parser.add_argument("--distrs",      type=str, default='Mt_lep_met_c,leading_lep_pt,tau_sv_sign,dilep_mass,met_f', help="distributions to histogram")

parser.add_argument("--exe",            type=str, default='sumup_loop', help="change the executable name if needed")
parser.add_argument("--interface-type", type=str, default='1',          help="old or new structure of the histograms datafile that goes into the higgscombine fit")
parser.add_argument("--simulate-data-output", type=str, default='0',    help="add a dummy data output in case you do not run on data")
parser.add_argument("--lumi",           type=str, default='41300',      help="luminosity factor for the MC")

parser.add_argument("-d", "--debug",    action='store_true', help="DEBUG level of logging")


args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logging.debug("parsed args: %s" % repr(args))

assert isdir(args.queue_dir)
assert isdir(args.ntuples_dir)
assert isdir(args.distrs_dir)

def make_nested_dirs(dir_list):
    full_path = ''
    for dirpath in dir_list:
        full_path += dirpath + '/'
        if not isdir(full_path): mkdir(full_path)
    return full_path

output_dir = make_nested_dirs([args.distrs_dir, args.vNtupler, args.vHists])

args_dict = vars(args)
# vars() returns __dict__ of the object
command_template = SUMUP_LOOP_COMMAND_TEMPLATE.format(**args_dict)
#print(command_template)

# ---------- construct the job commands
# for each dataset
# construct the chunkes of input files
# and create the corresponding job commands
job_commands_per_dset = {}
'''
it contains
{"dset": [(output_name, [input, names, ...]), ...],
 "other_dset": ...}
'''

dset_pattern = re.compile(args.dsets_grep)
dsets_to_process = [d for d in listdir('{ntuples_dir}/{vNtupler}/'.format(**args_dict)) if dset_pattern.match(d)]

def divide_chunks(a_list, n):
    '''divide_chunks(a_list, n) ->[[], []]

    Yield successive n-sized chunks from a_list.
    '''

    # looping till length a_list
    for i in range(0, len(a_list), n):
        yield a_list[i:i + n]

for dset in dsets_to_process:
    dset_dir = '{ntuples_dir}/{vNtupler}/{dset}'.format(dset=dset, **args_dict)

    # make the dset output directory
    output_of_dset = make_nested_dirs([output_dir, dset])

    # chunkes of files & output filename
    all_files = glob.glob(f'{dset_dir}/*/*/*/*.root')
    input_file_chunkes = divide_chunks(all_files, args.number_jobs)

    # save each chunk and its output filename for this dataset
    job_inputs_outputs = []
    for i, chunk in enumerate(input_file_chunkes):
        output_filename = f'{output_of_dset}/{args.number_jobs}_{i}.root'
        job_inputs_outputs.append((output_filename, chunk))

    job_commands_per_dset[dset] = job_inputs_outputs


# ---------- write down job scripts and condor submit files
job_template = """#!/bin/sh
pwd
export X509_USER_PROXY={X509_USER_PROXY}
export SCRAM_ARCH={SCRAM_ARCH}
export BUILD_ARCH={SCRAM_ARCH}
export VO_CMS_SW_DIR={VO_CMS_SW_DIR}
source $VO_CMS_SW_DIR/cmsset_default.sh
export CMS_PATH=$VO_CMS_SW_DIR
cd {project_dir}
cmsenv
cd UserCode/processing_ntuples/
{{job}}
"""

'''eval `scramv1 runtime -sh`
cd -
ulimit -c 0;'''

# make the job shell script template
from os import environ

vars_for_the_job = dict(environ)
# after boot.tcsh everything is in the vars
#project_dir = '/lstore/cms/olek/CMSSW_8_0_26_patch1/src/'
project_dir = vars_for_the_job['CMSSW_BASE'] + '/src/'
#ntupler_proc_dir = 'UserCode/proc/'
ntupler_proc_dir = 'UserCode/processing_ntuples/'
vars_for_the_job.update(project_dir=project_dir)

if 'X509_USER_PROXY' not in vars_for_the_job:
    vars_for_the_job['X509_USER_PROXY'] = ''
if 'VO_CMS_SW_DIR' not in vars_for_the_job:
    vars_for_the_job['VO_CMS_SW_DIR'] = '/cvmfs/cms.cern.ch'

job_template = job_template.format(**vars_for_the_job)


# make the condor sumbition files
condor_subfile_template = '''executable            = {jobsh}
arguments             = 
output                = output/{jobsh_name}.$(ClusterId).$(ProcId).out
error                 = error/{jobsh_name}.$(ClusterId).$(ProcId).err
log                   = log/{jobsh_name}.$(ClusterId).log
+JobFlavour = "longlunch"
queue
'''

batch_systems_submit_commands = {'qsub': "qsub -l h_vmem={mem_size} '{jobsh}'",
                                  'bsub': "bsub -q cmscaf1nh -J {job_name} < '{jobsh}'",
                                  'condor': "condor_submit {jobsh}.sub"}
job_submit_template = batch_systems_submit_commands['condor']

# make the jobs dir
jobs_dir = make_nested_dirs([args.queue_dir, args.vNtupler, args.vHists])
#jobs_dir  = args.queue_dir + '/' + args.vNtupler
#if not isdir(jobs_dir): mkdir(jobs_dir)
#jobs_dir += '/' + args.vHists
#if not isdir(jobs_dir): mkdir(jobs_dir)

# write all the job files
job_filenames = []

# flat list of all job chunks
all_job_chunks = []
for _, job_chunks in job_commands_per_dset.items():
    for a_job in job_chunks:
        all_job_chunks.append(a_job)

for i, a_job in enumerate(all_job_chunks):
    # job script filename
    job_name = '/job_%d' % i
    job_filename = jobs_dir + job_name
    job_filenames.append(job_filename)

    # the final sumup_loop command
    output_file, input_files = a_job
    the_command = command_template.format(output_file=output_file, input_files=' '.join(input_files))

    # write the job script file
    with open(job_filename, 'w') as f:
        f.write(job_template.format(job=the_command))

    # since it is condor, make a .sub file for the job
    with open(job_filename + '.sub', 'w') as f:
        f.write(condor_subfile_template.format(jobsh=job_filename, jobsh_name=job_filename.split('/')[-1]))

#make the queue submition file
submition_file = jobs_dir + '/submit'
with open(submition_file, 'w') as f:
    f.write('\n'.join(job_submit_template.format(jobsh=j_fname, job_name=j_fname.split('/')[-1]) for j_fname in job_filenames) + '\n')

# submition file
logging.info("source %s" % submition_file)

