#ifndef NTUPLEINTERFACENTUPLER_H
#define NTUPLEINTERFACENTUPLER_H

/** the ntupler implementation of the sumup_loop interface

 these functions create the populate the collections of definitions used in sumup_loop
 the types of the collections are defined in the sumup_loop header
 they are basically std::map<string=name of the definition, <whatever defines it, some struct with the function and whatever else>>
 */

#include "UserCode/processing_ntuples/interface/sumup_loop_ntuple.h"
#include "TTree.h"

T_known_defs_procs    create_known_defs_procs_ntupler(void);
T_known_defs_distrs   create_known_defs_distrs_ntupler(void);
T_known_defs_channels create_known_defs_channels_ntupler(void);
T_known_defs_systs    create_known_defs_systs_ntupler(void);

T_known_MC_normalization_per_somename create_known_MC_normalization_per_syst_ntupler(void);
T_known_MC_normalization_per_somename create_known_MC_normalization_per_proc_ntupler(void);
T_known_MC_normalization_per_somename create_known_MC_normalization_per_chan_ntupler(void);


//F_connect_ntuple_interface connect_ntuple_interface_ntupler;
int connect_ntuple_interface_ntupler(TTree*);

//extern Int_t NT_nup;

#endif /* NTUPLEINTERFACENTUPLER_H */
