
#include "UserCode/processing_ntuples/interface/ntuple_ntupler.h"

/* Global interface to the ttree, the name space for all the event-processing fucntions.
 */
#define NTUPLE_INTERFACE_DECLARE_STATIC
#define NTUPLE_INTERFACE_CLASS_DECLARE
#include "ntupler_interface.h"
#undef NTUPLE_INTERFACE_DECLARE_STATIC
#undef NTUPLE_INTERFACE_CLASS_DECLARE

/* --------------------------------------------------------------- */
/* STD DEFS */
//#include "std_defs.h"

/*
 * The distributions:
 * processing functions in the name space of the ntupler interface,
 * definitions of histograms with various ranges.
 */


static double NT_sysweight_NOMINAL_HLT_EL()
	{
	return 1.; // NT_event_weight*NT_event_weight_PU*NT_event_weight_LEPmuID*NT_event_weight_LEPelID* NT_event_weight_LEPelTRG;
	}

static double NT_sysweight_NOMINAL_HLT_MU()
	{
	return 1.; // NT_event_weight*NT_event_weight_PU*NT_event_weight_LEPmuID*NT_event_weight_LEPelID* NT_event_weight_LEPmuTRG;
	}

static double NT_sysweight_NOMINAL_HLT_LEP()
	{
	/* what this does is calculates the weights according to the lepton ID scale factors, and returns the final product
	double common = NT_event_weight*NT_event_weight_PU*NT_event_weight_LEPmuID*NT_event_weight_LEPelID;
	if (abs(NT_event_leptons_ids[0]) == 13)
		return  NT_event_weight_LEPmuTRG * common;
	else
		return  NT_event_weight_LEPelTRG * common;
	*/
	return 1.;
	}

static double NT_sysweight_NOMINAL_HLT_EL_MedTau()
	{
	// old ntupler output, from the 2016 xsection measurement
	//return NT_event_weight*0.95;
	// new, 2017 ntupler
	return 1.; // NT_event_weight*NT_event_weight_PU*NT_event_weight_LEPmuID*NT_event_weight_LEPelID* NT_event_weight_LEPelTRG * NT_event_taus_SF_Medium[0];
	}

static double NT_sysweight_NOMINAL_HLT_MU_MedTau()
	{
	// old ntupler output, from the 2016 xsection measurement
	//return NT_event_weight*0.95;
	return 1.; // NT_event_weight*NT_event_weight_PU*NT_event_weight_LEPmuID*NT_event_weight_LEPelID* NT_event_weight_LEPmuTRG * NT_event_taus_SF_Medium[0];
	}

static double NT_sysweight_NOMINAL_HLT_LEP_MedTau()
	{
	//double common = NT_event_weight*NT_event_weight_PU*NT_event_weight_LEPmuID*NT_event_weight_LEPelID * NT_event_taus_SF_Medium[0];
	//if (abs(NT_event_leptons_ids[0]) == 13)
	//	return  NT_event_weight_LEPmuTRG * common;
	//else
	//	return  NT_event_weight_LEPelTRG * common;
	double lep_weight = NT_sysweight_NOMINAL_HLT_LEP();
	double tau_weight = 1.;
	return lep_weight * tau_weight;
	}

// systematic uncertainties from the nominal weight

static double NT_sysweight_NOMINAL()
	{
	return 1.;
	}

#define NT_sysweight(sysname, weight_expr)   \
static double NT_sysweight_ ##sysname(void)          \
	{                                  \
	return weight_expr; \
	}

/* TODO all these are different in the ntupler -- check stage2.py how they are calculated

// COMMON systematics
NT_sysweight(PUUp,   NT_event_weight_PUUp   / NT_event_weight_PU )
NT_sysweight(PUDown, NT_event_weight_PUDown / NT_event_weight_PU )

NT_sysweight(bSFUp,    (NT_event_weight_bSF > 0.? NT_event_weight_bSFUp   / NT_event_weight_bSF : 0.))
NT_sysweight(bSFDown,  (NT_event_weight_bSF > 0.? NT_event_weight_bSFDown / NT_event_weight_bSF : 0.))

NT_sysweight(LEPelIDUp,    NT_event_weight_LEPelID_Up    / NT_event_weight_LEPelID)
NT_sysweight(LEPelIDDown,  NT_event_weight_LEPelID_Down  / NT_event_weight_LEPelID)
NT_sysweight(LEPelTRGUp,   NT_event_weight_LEPelTRG_Up   / NT_event_weight_LEPelTRG)
NT_sysweight(LEPelTRGDown, NT_event_weight_LEPelTRG_Down / NT_event_weight_LEPelTRG)
NT_sysweight(LEPmuIDUp,    NT_event_weight_LEPmuID_Up    / NT_event_weight_LEPmuID)
NT_sysweight(LEPmuIDDown,  NT_event_weight_LEPmuID_Down  / NT_event_weight_LEPmuID)
NT_sysweight(LEPmuTRGUp,   NT_event_weight_LEPmuTRG_Up   / NT_event_weight_LEPmuTRG)
NT_sysweight(LEPmuTRGDown, NT_event_weight_LEPmuTRG_Down / NT_event_weight_LEPmuTRG)

// Tau systematics

NT_sysweight(TAUIDUp,   (NT_event_taus_SF_Medium_Up   .size()>0 && NT_event_taus_SF_Medium[0] > 0.001) ? NT_event_taus_SF_Medium_Up[0]    / NT_event_taus_SF_Medium[0] : 1.)
NT_sysweight(TAUIDDown, (NT_event_taus_SF_Medium_Down .size()>0 && NT_event_taus_SF_Medium[0] > 0.001) ? NT_event_taus_SF_Medium_Down[0]  / NT_event_taus_SF_Medium[0] : 1.)

// TT_OBJ
NT_sysweight(TOPPTUp   , NT_event_weight_toppt    )
NT_sysweight(TOPPTDown , 1.    )

NT_sysweight(FragUp        , NT_event_weight_FragUp        )
NT_sysweight(FragDown      , NT_event_weight_FragDown      )
NT_sysweight(SemilepBRUp   , NT_event_weight_SemilepBRUp   )
NT_sysweight(SemilepBRDown , NT_event_weight_SemilepBRDown )
NT_sysweight(PetersonUp    , NT_event_weight_PetersonUp    )
NT_sysweight(PetersonDown  , 1.                               )

// TT_HARD
NT_sysweight(MrUp     , NT_event_weight_me_f_rUp )
NT_sysweight(MrDown   , NT_event_weight_me_f_rDn )
NT_sysweight(MfUp     , NT_event_weight_me_fUp_r )
NT_sysweight(MfDown   , NT_event_weight_me_fDn_r )
NT_sysweight(MfrUp    , NT_event_weight_me_frUp  ) 
NT_sysweight(MfrDown  , NT_event_weight_me_frDn  ) 

// TT_ALPHA
NT_sysweight(AlphaSUp     , NT_event_weight_AlphaS_up )
NT_sysweight(AlphaSDown   , NT_event_weight_AlphaS_dn )

// TT_PDF all of them
// maybe a better approach would be to add an index into systematics

NT_sysweight(PDFCT14n1Up     , NT_event_weight_pdf[0] )
NT_sysweight(PDFCT14n2Up     , NT_event_weight_pdf[1] )
NT_sysweight(PDFCT14n3Up     , NT_event_weight_pdf[2] )
NT_sysweight(PDFCT14n4Up     , NT_event_weight_pdf[3] )
NT_sysweight(PDFCT14n5Up     , NT_event_weight_pdf[4] )
NT_sysweight(PDFCT14n6Up     , NT_event_weight_pdf[5] )
NT_sysweight(PDFCT14n7Up     , NT_event_weight_pdf[6] )
NT_sysweight(PDFCT14n8Up     , NT_event_weight_pdf[7] )
NT_sysweight(PDFCT14n9Up     , NT_event_weight_pdf[8] )
NT_sysweight(PDFCT14n10Up    , NT_event_weight_pdf[9] )
NT_sysweight(PDFCT14n11Up    , NT_event_weight_pdf[10])
NT_sysweight(PDFCT14n12Up    , NT_event_weight_pdf[11])
NT_sysweight(PDFCT14n13Up    , NT_event_weight_pdf[12])
NT_sysweight(PDFCT14n14Up    , NT_event_weight_pdf[13])
NT_sysweight(PDFCT14n15Up    , NT_event_weight_pdf[14])
NT_sysweight(PDFCT14n16Up    , NT_event_weight_pdf[15])
NT_sysweight(PDFCT14n17Up    , NT_event_weight_pdf[16])
NT_sysweight(PDFCT14n18Up    , NT_event_weight_pdf[17])
NT_sysweight(PDFCT14n19Up    , NT_event_weight_pdf[18])
NT_sysweight(PDFCT14n20Up    , NT_event_weight_pdf[19])
NT_sysweight(PDFCT14n21Up    , NT_event_weight_pdf[20])
NT_sysweight(PDFCT14n22Up    , NT_event_weight_pdf[21])
NT_sysweight(PDFCT14n23Up    , NT_event_weight_pdf[22])
NT_sysweight(PDFCT14n24Up    , NT_event_weight_pdf[23])
NT_sysweight(PDFCT14n25Up    , NT_event_weight_pdf[24])
NT_sysweight(PDFCT14n26Up    , NT_event_weight_pdf[25])
NT_sysweight(PDFCT14n27Up    , NT_event_weight_pdf[26])
NT_sysweight(PDFCT14n28Up    , NT_event_weight_pdf[27])
NT_sysweight(PDFCT14n29Up    , NT_event_weight_pdf[28])
NT_sysweight(PDFCT14n30Up    , NT_event_weight_pdf[29])
NT_sysweight(PDFCT14n31Up    , NT_event_weight_pdf[30])
NT_sysweight(PDFCT14n32Up    , NT_event_weight_pdf[31])
NT_sysweight(PDFCT14n33Up    , NT_event_weight_pdf[32])
NT_sysweight(PDFCT14n34Up    , NT_event_weight_pdf[33])
NT_sysweight(PDFCT14n35Up    , NT_event_weight_pdf[34])
NT_sysweight(PDFCT14n36Up    , NT_event_weight_pdf[35])
NT_sysweight(PDFCT14n37Up    , NT_event_weight_pdf[36])
NT_sysweight(PDFCT14n38Up    , NT_event_weight_pdf[37])
NT_sysweight(PDFCT14n39Up    , NT_event_weight_pdf[38])
NT_sysweight(PDFCT14n40Up    , NT_event_weight_pdf[39])
NT_sysweight(PDFCT14n41Up    , NT_event_weight_pdf[40])
NT_sysweight(PDFCT14n42Up    , NT_event_weight_pdf[41])
NT_sysweight(PDFCT14n43Up    , NT_event_weight_pdf[42])
NT_sysweight(PDFCT14n44Up    , NT_event_weight_pdf[43])
NT_sysweight(PDFCT14n45Up    , NT_event_weight_pdf[44])
NT_sysweight(PDFCT14n46Up    , NT_event_weight_pdf[45])
NT_sysweight(PDFCT14n47Up    , NT_event_weight_pdf[46])
NT_sysweight(PDFCT14n48Up    , NT_event_weight_pdf[47])
NT_sysweight(PDFCT14n49Up    , NT_event_weight_pdf[48])
NT_sysweight(PDFCT14n50Up    , NT_event_weight_pdf[49])
NT_sysweight(PDFCT14n51Up    , NT_event_weight_pdf[50])
NT_sysweight(PDFCT14n52Up    , NT_event_weight_pdf[51])
NT_sysweight(PDFCT14n53Up    , NT_event_weight_pdf[52])
NT_sysweight(PDFCT14n54Up    , NT_event_weight_pdf[53])
NT_sysweight(PDFCT14n55Up    , NT_event_weight_pdf[54])
NT_sysweight(PDFCT14n56Up    , NT_event_weight_pdf[55])

NT_sysweight(PDFCT14n1Down     , 1.)
NT_sysweight(PDFCT14n2Down     , 1.)
NT_sysweight(PDFCT14n3Down     , 1.)
NT_sysweight(PDFCT14n4Down     , 1.)
NT_sysweight(PDFCT14n5Down     , 1.)
NT_sysweight(PDFCT14n6Down     , 1.)
NT_sysweight(PDFCT14n7Down     , 1.)
NT_sysweight(PDFCT14n8Down     , 1.)
NT_sysweight(PDFCT14n9Down     , 1.)
NT_sysweight(PDFCT14n10Down    , 1.)
NT_sysweight(PDFCT14n11Down    , 1.)
NT_sysweight(PDFCT14n12Down    , 1.)
NT_sysweight(PDFCT14n13Down    , 1.)
NT_sysweight(PDFCT14n14Down    , 1.)
NT_sysweight(PDFCT14n15Down    , 1.)
NT_sysweight(PDFCT14n16Down    , 1.)
NT_sysweight(PDFCT14n17Down    , 1.)
NT_sysweight(PDFCT14n18Down    , 1.)
NT_sysweight(PDFCT14n19Down    , 1.)
NT_sysweight(PDFCT14n20Down    , 1.)
NT_sysweight(PDFCT14n21Down    , 1.)
NT_sysweight(PDFCT14n22Down    , 1.)
NT_sysweight(PDFCT14n23Down    , 1.)
NT_sysweight(PDFCT14n24Down    , 1.)
NT_sysweight(PDFCT14n25Down    , 1.)
NT_sysweight(PDFCT14n26Down    , 1.)
NT_sysweight(PDFCT14n27Down    , 1.)
NT_sysweight(PDFCT14n28Down    , 1.)
NT_sysweight(PDFCT14n29Down    , 1.)
NT_sysweight(PDFCT14n30Down    , 1.)
NT_sysweight(PDFCT14n31Down    , 1.)
NT_sysweight(PDFCT14n32Down    , 1.)
NT_sysweight(PDFCT14n33Down    , 1.)
NT_sysweight(PDFCT14n34Down    , 1.)
NT_sysweight(PDFCT14n35Down    , 1.)
NT_sysweight(PDFCT14n36Down    , 1.)
NT_sysweight(PDFCT14n37Down    , 1.)
NT_sysweight(PDFCT14n38Down    , 1.)
NT_sysweight(PDFCT14n39Down    , 1.)
NT_sysweight(PDFCT14n40Down    , 1.)
NT_sysweight(PDFCT14n41Down    , 1.)
NT_sysweight(PDFCT14n42Down    , 1.)
NT_sysweight(PDFCT14n43Down    , 1.)
NT_sysweight(PDFCT14n44Down    , 1.)
NT_sysweight(PDFCT14n45Down    , 1.)
NT_sysweight(PDFCT14n46Down    , 1.)
NT_sysweight(PDFCT14n47Down    , 1.)
NT_sysweight(PDFCT14n48Down    , 1.)
NT_sysweight(PDFCT14n49Down    , 1.)
NT_sysweight(PDFCT14n50Down    , 1.)
NT_sysweight(PDFCT14n51Down    , 1.)
NT_sysweight(PDFCT14n52Down    , 1.)
NT_sysweight(PDFCT14n53Down    , 1.)
NT_sysweight(PDFCT14n54Down    , 1.)
NT_sysweight(PDFCT14n55Down    , 1.)
NT_sysweight(PDFCT14n56Down    , 1.)

*/


// the systematic definitions:
// a systematic can affect objects in the event, or the event weight
// here the two types of systematics are separated:
// the object systematics pass the systematic name for the objects, but have the NOMINAL event weight
// the weight systematics pass the NOMINAL systematic for the objects, but the weight is there
#define _quick_set_objsys(sysname) m[#sysname] = {sysname, NT_sysweight_NOMINAL}
#define _quick_set_wgtsys(sysname) m[#sysname] = {NOMINAL, NT_sysweight_##sysname}

T_known_defs_systs create_known_defs_systs_ntupler()
	{
	map<TString, _S_systematic_definition> m;
	m["NOMINAL"] = {NOMINAL, NT_sysweight_NOMINAL};

	_quick_set_objsys(JERUp);
	_quick_set_objsys(JERDown);
	_quick_set_objsys(JESUp);
	_quick_set_objsys(JESDown);
	_quick_set_objsys(TESUp);
	_quick_set_objsys(TESDown);

	/* TODO these are not defined above -- copy the definitions from stage2.py
	_quick_set_wgtsys(PUUp);
	_quick_set_wgtsys(PUDown);
	_quick_set_wgtsys(bSFUp);
	_quick_set_wgtsys(bSFDown);
	_quick_set_wgtsys(LEPelIDUp);
	_quick_set_wgtsys(LEPelIDDown);
	_quick_set_wgtsys(LEPelTRGUp);
	_quick_set_wgtsys(LEPelTRGDown);
	_quick_set_wgtsys(LEPmuIDUp);
	_quick_set_wgtsys(LEPmuIDDown);
	_quick_set_wgtsys(LEPmuTRGUp);
	_quick_set_wgtsys(LEPmuTRGDown);

	_quick_set_wgtsys(TAUIDUp);
	_quick_set_wgtsys(TAUIDDown);

	_quick_set_wgtsys(PUUp);
	_quick_set_wgtsys(PUDown);

	_quick_set_wgtsys(TOPPTUp);
	_quick_set_wgtsys(TOPPTDown);
	_quick_set_wgtsys(FragUp);
	_quick_set_wgtsys(FragDown);
	_quick_set_wgtsys(SemilepBRUp);
	_quick_set_wgtsys(SemilepBRDown);
	_quick_set_wgtsys(PetersonUp);
	_quick_set_wgtsys(PetersonDown);

	_quick_set_wgtsys(MrUp     );
	_quick_set_wgtsys(MrDown   );
	_quick_set_wgtsys(MfUp     );
	_quick_set_wgtsys(MfDown   );
	_quick_set_wgtsys(MfrUp    );
	_quick_set_wgtsys(MfrDown  );

	_quick_set_wgtsys(AlphaSUp     );
	_quick_set_wgtsys(AlphaSDown   );

	_quick_set_wgtsys(PDFCT14n1Up     );
	_quick_set_wgtsys(PDFCT14n2Up     );
	_quick_set_wgtsys(PDFCT14n3Up     );
	_quick_set_wgtsys(PDFCT14n4Up     );
	_quick_set_wgtsys(PDFCT14n5Up     );
	_quick_set_wgtsys(PDFCT14n6Up     );
	_quick_set_wgtsys(PDFCT14n7Up     );
	_quick_set_wgtsys(PDFCT14n8Up     );
	_quick_set_wgtsys(PDFCT14n9Up     );
	_quick_set_wgtsys(PDFCT14n10Up    );
	_quick_set_wgtsys(PDFCT14n11Up    );
	_quick_set_wgtsys(PDFCT14n12Up    );
	_quick_set_wgtsys(PDFCT14n13Up    );
	_quick_set_wgtsys(PDFCT14n14Up    );
	_quick_set_wgtsys(PDFCT14n15Up    );
	_quick_set_wgtsys(PDFCT14n16Up    );
	_quick_set_wgtsys(PDFCT14n17Up    );
	_quick_set_wgtsys(PDFCT14n18Up    );
	_quick_set_wgtsys(PDFCT14n19Up    );
	_quick_set_wgtsys(PDFCT14n20Up    );
	_quick_set_wgtsys(PDFCT14n21Up    );
	_quick_set_wgtsys(PDFCT14n22Up    );
	_quick_set_wgtsys(PDFCT14n23Up    );
	_quick_set_wgtsys(PDFCT14n24Up    );
	_quick_set_wgtsys(PDFCT14n25Up    );
	_quick_set_wgtsys(PDFCT14n26Up    );
	_quick_set_wgtsys(PDFCT14n27Up    );
	_quick_set_wgtsys(PDFCT14n28Up    );
	_quick_set_wgtsys(PDFCT14n29Up    );
	_quick_set_wgtsys(PDFCT14n30Up    );
	_quick_set_wgtsys(PDFCT14n31Up    );
	_quick_set_wgtsys(PDFCT14n32Up    );
	_quick_set_wgtsys(PDFCT14n33Up    );
	_quick_set_wgtsys(PDFCT14n34Up    );
	_quick_set_wgtsys(PDFCT14n35Up    );
	_quick_set_wgtsys(PDFCT14n36Up    );
	_quick_set_wgtsys(PDFCT14n37Up    );
	_quick_set_wgtsys(PDFCT14n38Up    );
	_quick_set_wgtsys(PDFCT14n39Up    );
	_quick_set_wgtsys(PDFCT14n40Up    );
	_quick_set_wgtsys(PDFCT14n41Up    );
	_quick_set_wgtsys(PDFCT14n42Up    );
	_quick_set_wgtsys(PDFCT14n43Up    );
	_quick_set_wgtsys(PDFCT14n44Up    );
	_quick_set_wgtsys(PDFCT14n45Up    );
	_quick_set_wgtsys(PDFCT14n46Up    );
	_quick_set_wgtsys(PDFCT14n47Up    );
	_quick_set_wgtsys(PDFCT14n48Up    );
	_quick_set_wgtsys(PDFCT14n49Up    );
	_quick_set_wgtsys(PDFCT14n50Up    );
	_quick_set_wgtsys(PDFCT14n51Up    );
	_quick_set_wgtsys(PDFCT14n52Up    );
	_quick_set_wgtsys(PDFCT14n53Up    );
	_quick_set_wgtsys(PDFCT14n54Up    );
	_quick_set_wgtsys(PDFCT14n55Up    );
	_quick_set_wgtsys(PDFCT14n56Up    );

	_quick_set_wgtsys(PDFCT14n1Down     );
	_quick_set_wgtsys(PDFCT14n2Down     );
	_quick_set_wgtsys(PDFCT14n3Down     );
	_quick_set_wgtsys(PDFCT14n4Down     );
	_quick_set_wgtsys(PDFCT14n5Down     );
	_quick_set_wgtsys(PDFCT14n6Down     );
	_quick_set_wgtsys(PDFCT14n7Down     );
	_quick_set_wgtsys(PDFCT14n8Down     );
	_quick_set_wgtsys(PDFCT14n9Down     );
	_quick_set_wgtsys(PDFCT14n10Down    );
	_quick_set_wgtsys(PDFCT14n11Down    );
	_quick_set_wgtsys(PDFCT14n12Down    );
	_quick_set_wgtsys(PDFCT14n13Down    );
	_quick_set_wgtsys(PDFCT14n14Down    );
	_quick_set_wgtsys(PDFCT14n15Down    );
	_quick_set_wgtsys(PDFCT14n16Down    );
	_quick_set_wgtsys(PDFCT14n17Down    );
	_quick_set_wgtsys(PDFCT14n18Down    );
	_quick_set_wgtsys(PDFCT14n19Down    );
	_quick_set_wgtsys(PDFCT14n20Down    );
	_quick_set_wgtsys(PDFCT14n21Down    );
	_quick_set_wgtsys(PDFCT14n22Down    );
	_quick_set_wgtsys(PDFCT14n23Down    );
	_quick_set_wgtsys(PDFCT14n24Down    );
	_quick_set_wgtsys(PDFCT14n25Down    );
	_quick_set_wgtsys(PDFCT14n26Down    );
	_quick_set_wgtsys(PDFCT14n27Down    );
	_quick_set_wgtsys(PDFCT14n28Down    );
	_quick_set_wgtsys(PDFCT14n29Down    );
	_quick_set_wgtsys(PDFCT14n30Down    );
	_quick_set_wgtsys(PDFCT14n31Down    );
	_quick_set_wgtsys(PDFCT14n32Down    );
	_quick_set_wgtsys(PDFCT14n33Down    );
	_quick_set_wgtsys(PDFCT14n34Down    );
	_quick_set_wgtsys(PDFCT14n35Down    );
	_quick_set_wgtsys(PDFCT14n36Down    );
	_quick_set_wgtsys(PDFCT14n37Down    );
	_quick_set_wgtsys(PDFCT14n38Down    );
	_quick_set_wgtsys(PDFCT14n39Down    );
	_quick_set_wgtsys(PDFCT14n40Down    );
	_quick_set_wgtsys(PDFCT14n41Down    );
	_quick_set_wgtsys(PDFCT14n42Down    );
	_quick_set_wgtsys(PDFCT14n43Down    );
	_quick_set_wgtsys(PDFCT14n44Down    );
	_quick_set_wgtsys(PDFCT14n45Down    );
	_quick_set_wgtsys(PDFCT14n46Down    );
	_quick_set_wgtsys(PDFCT14n47Down    );
	_quick_set_wgtsys(PDFCT14n48Down    );
	_quick_set_wgtsys(PDFCT14n49Down    );
	_quick_set_wgtsys(PDFCT14n50Down    );
	_quick_set_wgtsys(PDFCT14n51Down    );
	_quick_set_wgtsys(PDFCT14n52Down    );
	_quick_set_wgtsys(PDFCT14n53Down    );
	_quick_set_wgtsys(PDFCT14n54Down    );
	_quick_set_wgtsys(PDFCT14n55Down    );
	_quick_set_wgtsys(PDFCT14n56Down    );
	*/

	return m;
	}



static double NT_distr_nvtx(ObjSystematics sys)
	{
	return NT_nvtx;
	}

static double NT_distr_leading_lep_pt(ObjSystematics sys)
	{
	return NT_lep_p4[0].pt();
	}

static double NT_distr_dilep_mass(ObjSystematics sys)
	{
	if (NT_lep_p4.size()>1)
		return (NT_lep_p4[0] + NT_lep_p4[1]).mass();
	else if (NT_tau_p4.size()>0)
		return (NT_lep_p4[0] + NT_tau_p4[0]).mass();
	else
		return -111.;
	}

static double NT_calc_leading_tau_energy_scale_correction(ObjSystematics sys)
	{
	if      (sys == TESUp)   return NT_tau_decayMode[0] == 0 ? 0.995 + 0.012 : (NT_tau_decayMode[0] < 10 ? 1.011 + 0.012 : 1.006 + 0.012);
	else if (sys == TESDown) return NT_tau_decayMode[0] == 0 ? 0.995 - 0.012 : (NT_tau_decayMode[0] < 10 ? 1.011 - 0.012 : 1.006 - 0.012);
	else                     return NT_tau_decayMode[0] == 0 ? 0.995         : (NT_tau_decayMode[0] < 10 ? 1.011         : 1.006        );
	}

static double NT_distr_tau_pt(ObjSystematics sys)
	{

	// from ntupler.py and std_defs.py:
	//'tau_pt':        ({'NOMINAL': lambda ev: ev.event_taus[0].pt()    if len(ev.event_taus) > 0   else -111.},    ('histo-range',  [40,0,200])),
	//'event_taus_TES_up' : 'DoubleVector',
	//'event_taus_TES_down' : 'DoubleVector',
	//p4 = tau[0] * TES_nom
	//event_taus          .push_back(p4)
	//event_taus_TES_up   .push_back(TES_up / TES_nom)
	//event_taus_TES_down .push_back(TES_down / TES_nom)

	if (NT_tau_p4.size()==0)
		return -111.;

	/* from stage2.py
	NT_tau_decayMode[0]
                if tau_DM == 0:
                    TES_factor = 0.995
                    TES_factor_up = 0.995 + 0.012
                    TES_factor_dn = 0.995 - 0.012
                elif tau_DM < 10:
                    TES_factor = 1.011
                    TES_factor_up = 1.011 + 0.012
                    TES_factor_dn = 1.011 - 0.012
                else:
                    TES_factor = 1.006
                    TES_factor_up = 1.006 + 0.012
                    TES_factor_dn = 1.006 - 0.012
	*/
	if (NT_tau_p4[0].pt() > 20 && abs(NT_tau_p4[0].eta())<2.4 )
		{double pt = NT_tau_p4[0].pt();
		return pt * NT_calc_leading_tau_energy_scale_correction(sys);
		} 
	else
		return -111;
	////if      (sys == TESUp)   return pt * NT_event_taus_TES_up[0];
	////else if (sys == TESDown) return pt * NT_event_taus_TES_down[0];
	//if      (sys == TESUp)   return pt * (NT_tau_decayMode[0] == 0 ? 0.995 + 0.012 : (NT_tau_decayMode[0] < 10 ? 1.011 + 0.012 : 1.006 + 0.012));
	//else if (sys == TESDown) return pt * (NT_tau_decayMode[0] == 0 ? 0.995 - 0.012 : (NT_tau_decayMode[0] < 10 ? 1.011 - 0.012 : 1.006 - 0.012));
	//else                     return pt * (NT_tau_decayMode[0] == 0 ? 0.995         : (NT_tau_decayMode[0] < 10 ? 1.011         : 1.006        ));

	}

static double NT_distr_tau3h_pt(ObjSystematics sys)
	{
	if (NT_tau_p4.size()==0)
		return -111.;
	if (NT_tau_decayMode[0]==10 && NT_tau_p4[0].pt() >20) // && NT_tau_deep_IDlev[0] > 1) // interface is not defined for deep tau
	   {
	    double tau3h_pt = NT_tau_p4[0].pt();
	    return tau3h_pt * NT_calc_leading_tau_energy_scale_correction(sys);
	   }
	else 
	    return -111;
	}

static double NT_calc_tau_sv_sign_geom(ObjSystematics sys)
	{
	unsigned int tau_index = 0; // the leading tau
	unsigned int tau_refit_index = NT_tau_refited_index[tau_index];
	bool refitted = tau_refit_index > -1 &&
		(NT_tau_SV_fit_track_OS_matched_track_dR[tau_refit_index] +
		 NT_tau_SV_fit_track_SS1_matched_track_dR[tau_refit_index] +
		 NT_tau_SV_fit_track_SS2_matched_track_dR[tau_refit_index]) < 0.002;
	if (refitted)
                return NT_tau_SV_geom_flightLenSign [tau_refit_index];
	else
		return -111.;
	}

static double NT_distr_tau_sv_sign(ObjSystematics sys)
	{
	return NT_calc_tau_sv_sign_geom(sys);
	}

static double NT_distr_tau_sv_sign_pat(ObjSystematics sys)
	{
	// the refit index is only for the information about the refitted tau SV
	// the PAT data is saved in the original tau index
	unsigned int tau_index = 0; // the leading tau
	unsigned int tau_refit_index = NT_tau_refited_index[0];
	bool refitted = tau_refit_index > -1 &&
		(NT_tau_SV_fit_track_OS_matched_track_dR[tau_refit_index] +
		 NT_tau_SV_fit_track_SS1_matched_track_dR[tau_refit_index] +
		 NT_tau_SV_fit_track_SS2_matched_track_dR[tau_refit_index]) < 0.002;

	// the conditions are kept the same to make a clean comparison
	// but they mostly do not change the content of taus with the decay mode >=10
	if (refitted)
                return NT_tau_flightLengthSignificance[tau_index];
	else
		return -111.;
	}

static double NT_distr_sum_cos(ObjSystematics sys)
	{
	// TODO here we need to propagae the object systematic to MET
	// the problem with met is that even NOMINAL jets can have some corrections to be propagated to MET
	// but supposedly in NanoAOD all corrections are applied and there is no need to propagate more things
	if (NT_lep_p4.size() == 0 || NT_tau_p4.size() == 0) return -11.;
	double cos_lep_met = TMath::Cos(NT_lep_p4[0].Phi() - NT_met_init.Phi());
	double cos_tau_met = TMath::Cos(NT_tau_p4[0].Phi() - NT_met_init.Phi());
	return cos_lep_met + cos_tau_met;
	}

// TODO: these three are long calculations
static double NT_distr_lj_var(ObjSystematics sys)
	{
	return -111.; //NT_event_jets_lj_var;
	}

static double NT_distr_lj_var_w_mass(ObjSystematics sys)
	{
	return -111.; // NT_event_jets_lj_w_mass;
	}

static double NT_distr_lj_var_t_mass(ObjSystematics sys)
	{
	return -111.; // NT_event_jets_lj_t_mass;
	}

static double transverse_mass_pts(double v1_x, double v1_y, double v2_x, double v2_y)
	{
	auto v1v2 = TMath::Sqrt((v1_x*v1_x + v1_y*v1_y)*(v2_x*v2_x + v2_y*v2_y));
	return TMath::Sqrt(2*(v1v2 - (v1_x*v2_x + v1_y*v2_y)));
	}

static double NT_distr_Mt_lep_met(ObjSystematics sys)
	{

	/* in stage2.py
	event_met_lep_mt         [0] = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), proc_met.Px(), proc_met.Py())
	event_met_lep_mt_JERUp   [0] = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), proc_met_JERUp.Px(),   proc_met_JERUp.Py())
	event_met_lep_mt_JERDown [0] = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), proc_met_JERDown.Px(), proc_met_JERDown.Py())
	event_met_lep_mt_JESUp   [0] = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), proc_met_JESUp.Px(),   proc_met_JESUp.Py())
	event_met_lep_mt_JESDown [0] = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), proc_met_JESDown.Px(), proc_met_JESDown.Py())
	event_met_lep_mt_TESUp   [0] = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), proc_met_TESUp.Px(),   proc_met_TESUp.Py())
	event_met_lep_mt_TESDown [0] = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), proc_met_TESDown.Px(), proc_met_TESDown.Py())
	*/

	/*
	if      (sys == NOMINAL) return NT_event_met_lep_mt;
	else if (sys == JERUp)   return NT_event_met_lep_mt_JERUp;
	else if (sys == JERDown) return NT_event_met_lep_mt_JERDown;
	else if (sys == JESUp)   return NT_event_met_lep_mt_JESUp;
	else if (sys == JESDown) return NT_event_met_lep_mt_JESDown;
	else if (sys == TESUp)   return NT_event_met_lep_mt_TESUp;
	else if (sys == TESDown) return NT_event_met_lep_mt_TESDown;

	else return NT_event_met_lep_mt;
	*/

	double mT_init = transverse_mass_pts(NT_lep_p4[0].Px(), NT_lep_p4[0].Py(), NT_met_init.Px(), NT_met_init.Py());
	return mT_init;
	}

static double NT_distr_Mt_el_met(ObjSystematics sys)
	{
	if(NT_lep_p4.size() == 0)
		return -111;
	else if (NT_lep_p4.size()>0 && abs(NT_lep_id[0]) ==11)
		return transverse_mass_pts(NT_lep_p4[0].Px(), NT_lep_p4[0].Py(), NT_met_init.Px(), NT_met_init.Py());
        else if (NT_lep_p4.size()>1 && abs(NT_lep_id[1]) ==11)
     	return transverse_mass_pts(NT_lep_p4[1].Px(), NT_lep_p4[1].Py(), NT_met_init.Px(), NT_met_init.Py());
	else
		return -111.;	
	}

static double NT_distr_Mt_mu_met(ObjSystematics sys)
	{
	if(NT_lep_p4.size() == 0)
		return -111;
	else if (NT_lep_p4.size()>0 && abs(NT_lep_id[0]) ==13)
		return transverse_mass_pts(NT_lep_p4[0].Px(), NT_lep_p4[0].Py(), NT_met_init.Px(), NT_met_init.Py());
        else if (NT_lep_p4.size()>1 && abs(NT_lep_id[1]) ==13)
     	return transverse_mass_pts(NT_lep_p4[1].Px(), NT_lep_p4[1].Py(), NT_met_init.Px(), NT_met_init.Py());
	else
		return -111.;	
	}


static double NT_distr_met(ObjSystematics sys)
	{

	/*
	if      (sys == NOMINAL) return NT_event_met.pt();
	else if (sys == JERUp)   return NT_event_met_JERUp.pt();
	else if (sys == JERDown) return NT_event_met_JERDown.pt();
	else if (sys == JESUp)   return NT_event_met_JESUp.pt();
	else if (sys == JESDown) return NT_event_met_JESDown.pt();
	else if (sys == TESUp)   return NT_event_met_TESUp.pt();
	else if (sys == TESDown) return NT_event_met_TESDown.pt();
	else return NT_event_met.pt();
	*/

	return NT_met_init.Pt();
	}

static double NT_distr_electron_pt(ObjSystematics sys)
        { if(NT_lep_p4.size() == 2)
                if (abs(NT_lep_id[0]) ==11 )    return NT_lep_p4[0].pt();
                else if(abs(NT_lep_id[1]) ==11) return NT_lep_p4[1].pt();
                else    return -111;
        else if(NT_lep_p4.size()==1 && (abs(NT_lep_id[0]) ==11 ||abs( NT_lep_id[1]) ==11) )     return NT_lep_p4[0].pt();
        else
        { return -111;}
        } 

static double NT_distr_muon_pt(ObjSystematics sys)
        { if(NT_lep_p4.size() == 2)
                if (abs(NT_lep_id[0]) ==13 )    return NT_lep_p4[0].pt();
                else if(abs(NT_lep_id[1]) ==13) return NT_lep_p4[1].pt();
                else    return -111;
        else if(NT_lep_p4.size()==1 && (abs(NT_lep_id[0]) ==13 || abs(NT_lep_id[1]) ==13) )       return NT_lep_p4[0].pt();
        else
        { return -111;}
        }
/*
struct lep_id_range 
        { Int_t min;
	  Int_t max;
        };

struct dilep_id_ranges
       {
	struct lep_id_range r1;
	struct lep_id_range r2;
       }

 static bool NT_genproc_tt_mutau3ch()
        {
        auto NT_gen_proc_id = NT_calc_gen_proc_id_tt();
        return NT_gen_proc_id == 32;
        }

 static double NT_distr_mutau3h_taupt(ObjSystematics sys)
  {  if(NT_genproc_tt_mutau3ch())
        return NT_tau_p4[0].pt();
     else
     	return -111;
  }
*/
/**
\brief The initialization function for the definitions of the known distributions in the ntupler output ntuples.

\return map<const char*, _TH1D_histo_def>
 */

T_known_defs_distrs create_known_defs_distrs_ntupler()
{
	map<TString, _TH1D_histo_def> m;
	_TH1D_histo_range r;
	//r = {.nbins=40, .linear_min=0, .linear_max=200}; m["leading_lep_pt"] = {leading_lep_pt, r};
	// despicable!
	// "sorry, unimplemented: non-trivial designated initializers not supported"

	r = {50,  true,   0, 50};                                                      m["nvtx"] = {NT_distr_nvtx, r};

	r = {40,  true,   0, 200};                                                     m["leading_lep_pt"] = {NT_distr_leading_lep_pt, r};
        r = {40,  true,   0, 200};                                                     m["electron_pt"] = {NT_distr_electron_pt, r};
        r = {40,  true,   0, 200};                                                     m["muon_pt"] = {NT_distr_muon_pt, r};
      //  r = {40,  true,   0, 200};                                                     m["mutau1h_pt"] = {NT_distr_mutau1h_taupt, r};
     //   r = {40,  true,   0, 200};                                                     m["mutau3h_pt"] = {NT_distr_mutau3h_taupt, r};
	r = {40,  true,  30,  40};                                                     m["leading_lep_pt_el_edge35"] = {NT_distr_leading_lep_pt, r};
	r = {40,  true,   0, 200};                                                     m["tau_pt"]         = {NT_distr_tau_pt, r};
        r = {40,  true,   0, 200};                                                     m["tau3h_pt"]         = {NT_distr_tau3h_pt, r};
	// taus have smaller energy in ttbar, therefore we might want to look at a smaller range
	r = {40,  true,   0, 150};                                                     m["tau_pt_range2"]   = {NT_distr_tau_pt, r};
	r = {21,  true,  -1,  20};                                                     m["tau_sv_sign"]     = {NT_distr_tau_sv_sign, r};
	r = {21,  true,  -1,  50};                                                     m["tau_sv_sign_pat"] = {NT_distr_tau_sv_sign_pat, r};

	r = {100, true,   0, 400};                                                     m["dilep_mass"]     = {NT_distr_dilep_mass, r};
	r = {40,  true,  80, 100};                                                     m["dilep_mass_dy"]  = {NT_distr_dilep_mass, r};
	r = {40,  true,  20, 120};                                                     m["dilep_mass_dy_tautau"]  = {NT_distr_dilep_mass, r};

	r = {40,  true, -2., 2.};                                                      m["sum_cos"]        = {NT_distr_sum_cos, r};

	static double bins_lj_var[] = {0,15,30,45,60,90,120,170,220,270,400};   r = {(sizeof(bins_lj_var) / sizeof(bins_lj_var[0]))-1, false,-1,  -1, bins_lj_var};   m["lj_var"] = {NT_distr_lj_var, r};
	static double bins_lj_var_w_mass[] = {10,40,65,80,95,120,150,200};      r = {(sizeof(bins_lj_var_w_mass) / sizeof(bins_lj_var_w_mass[0]))-1, false,-1,  -1, bins_lj_var_w_mass};   m["lj_var_w_mass"] = {NT_distr_lj_var_w_mass, r};
	static double bins_lj_var_t_mass[] = {20,100,130,160,180,200,300,400};  r = {(sizeof(bins_lj_var_t_mass) / sizeof(bins_lj_var_t_mass[0]))-1, false,-1,  -1, bins_lj_var_t_mass};   m["lj_var_t_mass"] = {NT_distr_lj_var_t_mass, r};

	//r = {14, false,-1,  -1, .custom_bins=(double[]){0,16,32,44,54,64,74,81,88,95,104,116,132,160,250}}; m["Mt_lep_met_c"]   = {Mt_lep_met,     r};
	//r = {2, false,-1,  -1, .custom_bins=(double[]){{0},{16},{32}}}; m["Mt_lep_met_c"]   = {Mt_lep_met,     r};
	//r = {2, false,-1,  -1, {0.,16.,32.}}; m["Mt_lep_met_c"]   = {Mt_lep_met,     r};
	// it seems gcc on lxplus is buggy
	//static double Mt_lep_met_c_bins[] = {0,16,32,44,54,64};
	//r = {5, false,-1,  -1}; r.custom_bins = Mt_lep_met_c_bins; m["Mt_lep_met_c"]   = {Mt_lep_met,     r};
	// -- ok, this works
	//r = {2, false,-1,  -1, (static double*){0.,16.,32.}}; m["Mt_lep_met_c"]   = {Mt_lep_met,     r};
	//static double Mt_lep_met_c_bins[] = {0,16,32,44,54,64}; r = {5, false,-1,  -1, Mt_lep_met_c_bins}; m["Mt_lep_met_c"]   = {Mt_lep_met,     r};
	static double bins_Mt_lep_met_c[] = {0,16,32,44,54,64,74,81,88,95,104,116,132,160,250}; r = {(sizeof(bins_Mt_lep_met_c) / sizeof(bins_Mt_lep_met_c[0]))-1, false,-1,  -1, bins_Mt_lep_met_c}; m["Mt_lep_met_c"]   = {NT_distr_Mt_lep_met,     r};
	// ok! this needs a wrapper-macro
	//cerr_expr(r.custom_bins[0]);
	//cerr_expr(r.custom_bins[1]);

	r = {20, true,  0, 250};   m["Mt_lep_met_f"]   = {NT_distr_Mt_lep_met,     r};
	r = {25, true,  0, 200};   m["met_f2"]         = {NT_distr_met, r};
	r = {30, true,  0, 300};   m["met_f"]          = {NT_distr_met, r};
        r = {30, true,  0, 300};   m["Mt_el_met"]          = {NT_distr_Mt_el_met, r};
        r = {30, true,  0, 300};   m["Mt_mu_met"]          = {NT_distr_Mt_mu_met, r};
	static double bins_met_c[] = {0,20,40,60,80,100,120,140,200,500}; r = {(sizeof(bins_met_c) / sizeof(bins_met_c[0]))-1, false,  -1, -1, bins_met_c};   m["met_c"]  = {NT_distr_met, r};

	return m;
}


/*
 * The final state channels:
 * boolean functions whether the event passes a selection or no.

old std_defs.py:

'mu_sel':          (lambda sel_stage, ev: (sel_stage==  9 or sel_stage==  7), main_sel_stages),
'mu_sel_ss':       (lambda sel_stage, ev: (sel_stage==  8 or sel_stage==  6), main_sel_stages),
'el_sel':          (lambda sel_stage, ev: (sel_stage== 19 or sel_stage== 17), main_sel_stages),
'el_sel_ss':       (lambda sel_stage, ev: (sel_stage== 18 or sel_stage== 16), main_sel_stages),

'tt_elmu':        (lambda sel_stage, ev: (sel_stage> 200 and sel_stage < 210 and ev.event_leptons[0].pt() > 30. and ev.event_leptons[1].pt() > 30.), {'NOMINAL': lambda ev: ev.selection_stage_em}),
'tt_elmu_tight':  (lambda sel_stage, ev: (sel_stage == 205 and ev.event_leptons[0].pt() > 30. and ev.event_leptons[1].pt() > 30.), {'NOMINAL': lambda ev: ev.selection_stage_em}),
 */

static double b_tag_wp_loose  = 0.1522; // # 0.5426 # 0.460 #
static double b_tag_wp_medium = 0.4941; // # 0.1522 # 0.8484 # 0.8   #
static double b_tag_wp_tight  = 0.8001; // # 0.9535 # 0.935 #

//bool ISO_LEPS    = True
static double JETS_PT_CUT  = 20.; //  21.
static double JETS_ETA_CUT = 2.5; //  21.
static double TAUS_PT_CUT  = 20.; // # 21. # # 20GeV for DY->tautau selection
static unsigned int TAUS_ID_CUT_Tight  = 3; //  # Tight = 4-5, VTight = 5
static unsigned int TAUS_ID_CUT_Medium = 2;
static unsigned int TAUS_ID_CUT_VLoose = 0;
static unsigned int TAUS_ID_CUT = TAUS_ID_CUT_VLoose; // # TAUS_ID_CUT_Medium # Vloose cut for the shape
static bool ONLY_3PI_TAUS = false;
static double SV_SIGN_CUT = 2.5;

static unsigned int NT_calc_b_tagged_njets(ObjSystematics sys)
	{
	// TODO: correct
	unsigned int n_bjets = 0;

        for (int jet_i=0; jet_i < NT_jet_p4.size(); jet_i++)
		{
		double jet_b_discr = NT_jet_b_discr[jet_i];
		double pfid        = NT_jet_PFID   [jet_i];

		bool b_tagged_medium = jet_b_discr > b_tag_wp_medium;
		if (pfid < 1 || abs(NT_jet_p4[jet_i].eta()) > JETS_ETA_CUT || NT_jet_p4[jet_i].pt() < JETS_PT_CUT || !b_tagged_medium) continue;

		n_bjets++;
		}

	return n_bjets;
	}

typedef struct Triggers {
	bool pass_mu;
	bool pass_elmu;
	bool pass_elmu_el;
	bool pass_mumu;
	bool pass_elel;
	bool pass_el;
	bool pass_mu_all;
	bool pass_el_all;} Triggers;

static Triggers NT_calc_triggers(ObjSystematics sys)
	{
	Triggers trigs;

	bool pass_mu_id = abs(NT_leps_ID) == 13 && NT_HLT_mu && NT_lep_matched_HLT[0] && NT_no_iso_veto_leps && abs(NT_lep_dxy[0]) < 0.01 && abs(NT_lep_dz[0]) < 0.02;
	bool pass_el_id = abs(NT_leps_ID) == 11 && (NT_HLT_el || NT_HLT_el_low_pt) && NT_lep_matched_HLT[0] && NT_no_iso_veto_leps;

	bool pass_mu_iso = pass_mu_id && NT_lep_relIso[0] < 0.15  ;
	bool pass_el_iso = pass_el_id && NT_lep_relIso[0] < 0.0588;

	bool pass_mu_kino = pass_mu_id && NT_lep_p4[0].pt() > 30. && abs(NT_lep_p4[0].eta()) < 2.4;
	bool pass_el_kino = pass_el_id && NT_lep_p4[0].pt() > 30. && abs(NT_lep_p4[0].eta()) < 2.4 && (abs(NT_lep_p4[0].eta()) < 1.4442 || abs(NT_lep_p4[0].eta()) > 1.5660);

	trigs.pass_mu = pass_mu_id && pass_mu_kino && pass_mu_iso; // && pass_mu_impact;
	trigs.pass_el = pass_el_id && pass_el_kino && pass_el_iso;

	bool pass_mu_id_all = abs(NT_leps_ID_allIso) == 13 && NT_HLT_mu && NT_lep_alliso_matched_HLT[0] && NT_nleps_veto_mu_all == 0 && NT_nleps_veto_el_all == 0;
	bool pass_el_id_all = abs(NT_leps_ID_allIso) == 11 && NT_HLT_el && NT_lep_alliso_matched_HLT[0] && NT_nleps_veto_el_all == 0 && NT_nleps_veto_mu_all == 0;

	bool pass_mu_kino_all = pass_mu_id_all && NT_lep_alliso_p4[0].pt() > 26. && abs(NT_lep_alliso_p4[0].eta()) < 2.4;
	bool pass_el_kino_all = pass_el_id_all && NT_lep_alliso_p4[0].pt() > 30. && abs(NT_lep_alliso_p4[0].eta()) < 2.4 && (abs(NT_lep_alliso_p4[0].eta()) < 1.4442 || abs(NT_lep_alliso_p4[0].eta()) > 1.5660);

	trigs.pass_mu_all = pass_mu_id_all && pass_mu_kino_all;
	trigs.pass_el_all = pass_el_id_all && pass_el_kino_all;

	bool pass_elmu_id = abs(NT_leps_ID) == 11*13 && NT_no_iso_veto_leps &&
		(NT_lep_p4[0].pt() > 29. && abs(NT_lep_p4[0].eta()) < 2.4) &&
		(NT_lep_p4[1].pt() > 29. && abs(NT_lep_p4[1].eta()) < 2.4);

	bool pass_elmu	= pass_elmu_id && NT_HLT_mu &&
		(abs(NT_lep_id[0]) == 13 ?
			(NT_lep_matched_HLT[0] && abs(NT_lep_dxy[0]) < 0.01 && abs(NT_lep_dz[0]) < 0.02) :
			(NT_lep_matched_HLT[1] && abs(NT_lep_dxy[1]) < 0.01 && abs(NT_lep_dz[1]) < 0.02));

	bool pass_elmu_el = pass_elmu_id && NT_HLT_el &&
		(abs(NT_lep_id[0]) == 11 ? NT_lep_matched_HLT[0] : NT_lep_matched_HLT[1]);

	trigs.pass_elmu    = pass_elmu;
	trigs.pass_elmu_el = pass_elmu_el;

	bool pass_mumu = NT_leps_ID == -13*13 && NT_HLT_mu && (NT_lep_matched_HLT[0] || NT_lep_matched_HLT[1]) && NT_no_iso_veto_leps &&
		(NT_lep_p4[0].pt() > 30 && abs(NT_lep_p4[0].eta()) < 2.4) &&
		(NT_lep_p4[1].pt() > 30 && abs(NT_lep_p4[1].eta()) < 2.4);

	bool pass_elel = NT_leps_ID == -11*11 && NT_HLT_el && (NT_lep_matched_HLT[0] || NT_lep_matched_HLT[1]) && NT_no_iso_veto_leps &&
		(NT_lep_p4[0].pt() > 30 && abs(NT_lep_p4[0].eta()) < 2.4) &&
		(NT_lep_p4[1].pt() > 30 && abs(NT_lep_p4[1].eta()) < 2.4);

	trigs.pass_mumu = pass_mumu;
	trigs.pass_elel = pass_elel;

	return trigs;
	}

static int NT_calc_channel_tt_selection_stages(ObjSystematics sys)
	{
	int channel_stage = 0;

	unsigned int N_jets_b = NT_calc_b_tagged_njets(sys);

	// TODO: triggers!
	//pass_mu, pass_elmu, pass_elmu_el, pass_mumu, pass_elel, pass_el, pass_mu_all, pass_el_all = passed_triggers
	Triggers trigs = NT_calc_triggers(sys);

	bool there_is_lepton = NT_lep_p4.size() == 1;
	bool there_are_taus  = NT_tau_p4.size() > 0;
	bool lep_tau_os = (there_is_lepton && there_are_taus? NT_lep_id[0] * NT_tau_id[0] < 0 : false);

	bool old_jet_sel = N_jets_b > 0 && there_is_lepton;
	bool old_jet_sel_tau_cand	= old_jet_sel && there_are_taus;
	bool old_jet_sel_tau_cand_os    = old_jet_sel_tau_cand && lep_tau_os;

	unsigned int tau_IDlev = (there_are_taus ? NT_tau_IDlev[0] : 0);

	bool pass_Tight_sel        = old_jet_sel    && tau_IDlev > TAUS_ID_CUT_Tight;
	bool pass_Tight_sel_os     = pass_Tight_sel && lep_tau_os;
	bool pass_old_sel	   = old_jet_sel    && tau_IDlev > TAUS_ID_CUT_Medium;
	bool pass_old_sel_os	   = pass_old_sel   && lep_tau_os;
	bool pass_old_selVLoose	   = old_jet_sel    && tau_IDlev > TAUS_ID_CUT_VLoose;
	bool pass_old_selVLoose_os = pass_old_selVLoose && lep_tau_os;

	if   (trigs.pass_mu && pass_Tight_sel_os) {
		channel_stage = 9; }
	else if (trigs.pass_mu && pass_Tight_sel) {
		channel_stage = 8; }
	else if (trigs.pass_mu && pass_old_sel_os) {
		channel_stage = 7; }
	else if (trigs.pass_mu && pass_old_sel) {
		channel_stage = 6; }
	else if (trigs.pass_mu && pass_old_selVLoose_os) {
		channel_stage = 5; }
	else if (trigs.pass_mu && pass_old_selVLoose) {
		channel_stage = 4; }
	else if (trigs.pass_mu && old_jet_sel_tau_cand_os) {
		channel_stage = 3; }
	else if (trigs.pass_mu && old_jet_sel_tau_cand) {
		channel_stage = 2; }
	//else if (trigs.pass_mu && pass_old_presel_os) {
	//	channel_stage = 3; }
	//else if (trigs.pass_mu && pass_old_presel) {
	//	channel_stage = 2; }

	else if (trigs.pass_el && pass_Tight_sel_os) {
		channel_stage = 19; }
	else if (trigs.pass_el && pass_Tight_sel) {
		channel_stage = 18; }
	else if (trigs.pass_el && pass_old_sel_os) {
		channel_stage = 17; }
	else if (trigs.pass_el && pass_old_sel) {
		channel_stage = 16; }
	else if (trigs.pass_el && pass_old_selVLoose_os) {
		channel_stage = 15; }
	else if (trigs.pass_el && pass_old_selVLoose) {
		channel_stage = 14; }
	else if (trigs.pass_el && old_jet_sel_tau_cand_os) {
		channel_stage = 13; }
	else if (trigs.pass_el && old_jet_sel_tau_cand) {
		channel_stage = 12; }
	//else if (trigs.pass_el && pass_old_presel_os) {
	//	channel_stage = 13; }
	//else if (trigs.pass_el && pass_old_presel) {
	//	channel_stage = 12; }

	/*
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_JESDown;
	else if (sys == TESUp)     relevant_selection_stage = NT_selection_stage_TESUp  ;
	else if (sys == TESDown)   relevant_selection_stage = NT_selection_stage_TESDown;
	else relevant_selection_stage = NT_selection_stage;
	return relevant_selection_stage == 9 || relevant_selection_stage == 7;
	*/
	return channel_stage;
	}

static bool NT_channel_mu_sel(ObjSystematics sys)
	{
	int channel_stage = NT_calc_channel_tt_selection_stages(sys);
	return channel_stage == 9 || channel_stage == 7;
	}

static bool NT_channel_mu_sel_ss(ObjSystematics sys)
	{
	/*
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_JESDown;
	else if (sys == TESUp)     relevant_selection_stage = NT_selection_stage_TESUp  ;
	else if (sys == TESDown)   relevant_selection_stage = NT_selection_stage_TESDown;
	else relevant_selection_stage = NT_selection_stage;
	return relevant_selection_stage == 8 || relevant_selection_stage == 6;
	*/

	int channel_stage = NT_calc_channel_tt_selection_stages(sys);
	return channel_stage == 8 || channel_stage == 6;
	}

static bool NT_channel_mu_sel_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_mu_sel(sys);
	return sel ?  NT_calc_tau_sv_sign_geom(sys) > 3. : false;
	}

static bool NT_channel_mu_sel_ss_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_mu_sel_ss(sys);
	return sel ?  NT_calc_tau_sv_sign_geom(sys) > 3. : false;
	}

static bool NT_channel_el_sel(ObjSystematics sys)
	{
	int channel_stage = NT_calc_channel_tt_selection_stages(sys);
	return channel_stage == 19 || channel_stage == 17;
	}

static bool NT_channel_el_sel_ss(ObjSystematics sys)
	{
	int channel_stage = NT_calc_channel_tt_selection_stages(sys);
	return channel_stage == 18 || channel_stage == 16;
	}


static int NT_channel_tt_preselection_stages(ObjSystematics sys)
	{
	int channel_stage = 0;
	Triggers trigs = NT_calc_triggers(sys);
	// TODO: finish copying from stage2.py
	return channel_stage;
	}

// old ntupler presel!! from xsec measurement
static bool NT_channel_el_old_presel(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_channel_tt_preselection_stages(sys);
	return (relevant_selection_stage == 19 || relevant_selection_stage == 17);
	}

static bool NT_channel_el_old_presel_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_channel_tt_preselection_stages(sys);
	return (relevant_selection_stage == 18 || relevant_selection_stage == 16); // || relevant_selection_stage == 15);
	}

static bool NT_channel_mu_old_presel(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_channel_tt_preselection_stages(sys);
	//return relevant_selection_stage == 9;
	return (relevant_selection_stage == 9 || relevant_selection_stage == 7);
	}

static bool NT_channel_mu_old_presel_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_channel_tt_preselection_stages(sys);
	return (relevant_selection_stage == 8 || relevant_selection_stage == 6);
	}


static bool NT_channel_el_sel_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_el_sel(sys);
	return sel ?  NT_calc_tau_sv_sign_geom(sys) > 3. : false;
	}

static bool NT_channel_el_sel_ss_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_el_sel_ss(sys);
	return sel ?  NT_calc_tau_sv_sign_geom(sys) > 3. : false;
	}

// union os mu_sel and el_sel
static bool NT_channel_lep_sel(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_calc_channel_tt_selection_stages(sys);
	return relevant_selection_stage == 9 || relevant_selection_stage == 7 || relevant_selection_stage == 19 || relevant_selection_stage == 17;
	}

static bool NT_channel_lep_sel_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_calc_channel_tt_selection_stages(sys);
	return relevant_selection_stage == 8 || relevant_selection_stage == 6 || relevant_selection_stage == 18 || relevant_selection_stage == 16;
	}

static bool NT_channel_lep_sel_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_lep_sel(sys);
	return sel ?  NT_calc_tau_sv_sign_geom(sys) > 3. : false;
	}

static bool NT_channel_lep_sel_ss_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_lep_sel_ss(sys);
	// I use the if expression to be sure the vector NT_event_taus_sv_sign is not empty!
	//return sel && NT_event_taus_sv_sign[0] > 3.;
	return sel ?  NT_calc_tau_sv_sign_geom(sys) > 3. : false;
	}

static int NT_calc_channel_tt_elmu_selection_stages(ObjSystematics sys)
	{
	int channel_stage = 0;
	Triggers trigs = NT_calc_triggers(sys);
	bool main_tt_elmu_trig = trigs.pass_elmu_el; // pass_elmu or pass_elmu_el

	unsigned int N_jets_b = NT_calc_b_tagged_njets(sys);

	bool pass_elmu_leps    = main_tt_elmu_trig && NT_lep_id.size() == 2;
	bool pass_elmu_leps_os = pass_elmu_leps ? NT_lep_id[0] * NT_lep_id[1] == -11*13 : false;

	bool pass_elmu_leps_jets = pass_elmu_leps; // && N_jets[1] > 1
	bool pass_elmu_leps_jets_bjet = pass_elmu_leps_jets && N_jets_b > 0; // only 1 b jets

	//if   pass_elmu_leps_jets_bjet and pass_elmu_leps_os:
	//	channel_stage = 206
	//elif pass_elmu_leps_jets_bjet:
	//	channel_stage = 205
	//elif pass_elmu_leps_jets:
	//	channel_stage = 204

	if   (pass_elmu_leps_os) {
		channel_stage = 213;

		if (pass_elmu_leps_jets_bjet) {
			channel_stage = 215;
			}
		else if ( pass_elmu_leps_jets) {
			channel_stage = 214;
			}
		}

	else if (pass_elmu_leps) {
		channel_stage = 203;

		if (pass_elmu_leps_jets_bjet) {
			channel_stage = 205;
			}
		else if (pass_elmu_leps_jets) {
			channel_stage = 204;
			}
		}

	else if (main_tt_elmu_trig) {
		channel_stage = 202;
		}

	return channel_stage;
	}


static bool NT_channel_tt_elmu(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_calc_channel_tt_elmu_selection_stages(sys);
	return relevant_selection_stage > 210 && relevant_selection_stage < 220;
	}

static bool NT_channel_tt_elmu_tight(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_calc_channel_tt_elmu_selection_stages(sys);
	return relevant_selection_stage == 215;
	}



static int NT_calc_channel_dy_tautau_selection_stages(ObjSystematics sys)
	{
	int channel_stage = 0;
	Triggers trigs = NT_calc_triggers(sys);

	// muon and any charge tau and no b
	bool there_are_taus  = NT_tau_p4.size() > 0;
	bool there_is_lepton = NT_lep_p4.size() == 1;
	unsigned int N_jets_b = NT_calc_b_tagged_njets(sys);

	bool pass_leptau = there_is_lepton && there_are_taus && N_jets_b == 0;
	bool pass_dy_objects_mu = trigs.pass_mu && pass_leptau;
	bool pass_dy_objects_el = trigs.pass_el && pass_leptau;
	bool pass_objects = pass_leptau; //pass_dy_objects_mu || pass_dy_objects_el;
	if (!pass_objects) {return channel_stage;}

	unsigned int tau_IDlev = (there_are_taus ? NT_tau_IDlev[0] : 0);

	//pass_Tight_sel	 = old_jet_sel	and tau_IDlev > TAUS_ID_CUT_Tight
	//pass_Tight_sel_os  = pass_Tight_sel and leps[4][0] * taus[0][2] < 0
	//pass_old_sel	   = old_jet_sel and tau_IDlev > TAUS_ID_CUT_Medium
	//pass_old_sel_os	= pass_old_sel and leps[4][0] * taus[0][2] < 0
	//pass_old_selVLoose	   = old_jet_sel and tau_IDlev > TAUS_ID_CUT_VLoose
	//pass_old_selVLoose_os	= pass_old_selVLoose and leps[4][0] * taus[0][2] < 0

	//bool opposite_charge = pass_objects ? leps[4][0] * taus[0][2] < 0 : false;
	bool opposite_charge = (pass_objects? NT_lep_id[0] * NT_tau_id[0] < 0 : false);

	auto nom_tau = NT_tau_p4[0] * NT_calc_leading_tau_energy_scale_correction(sys);
	auto pair    = NT_lep_p4[0] + nom_tau;
	auto pair_mass = pair.mass();
	bool pass_dy_mass = 75. < pair_mass && pair_mass < 105.;

	if   (pass_dy_objects_mu && tau_IDlev > TAUS_ID_CUT_Tight && opposite_charge) {
		if (pass_dy_mass) {
			channel_stage = 135;
			}
		else {
			channel_stage = 134;
			}
		}
	else if (pass_dy_objects_mu && tau_IDlev > TAUS_ID_CUT_Tight) {
		if (pass_dy_mass) {
			channel_stage = 133;
			}
		else {
			channel_stage = 132;
			}
		}

	else if (pass_dy_objects_mu && tau_IDlev > TAUS_ID_CUT_Medium && opposite_charge) {
		if (pass_dy_mass) {
			channel_stage = 125;
			}
		else {
			channel_stage = 124;
			}
		}
	else if (pass_dy_objects_mu && tau_IDlev > TAUS_ID_CUT_Medium) {
		if (pass_dy_mass) {
			channel_stage = 123;
			}
		else {
			channel_stage = 122;
			}
		}

	else if (pass_dy_objects_mu && tau_IDlev > TAUS_ID_CUT_VLoose && opposite_charge) {
		if (pass_dy_mass) {
			channel_stage = 115;
			}
		else {
			channel_stage = 114;
			}
		}
	else if (pass_dy_objects_mu && tau_IDlev > TAUS_ID_CUT_VLoose) {
		if (pass_dy_mass) {
			channel_stage = 113;
			}
		else {
			channel_stage = 112;
			}
		}

	else if (pass_dy_objects_mu && opposite_charge) {
		if (pass_dy_mass) {
			channel_stage = 105;
			}
		else {
			channel_stage = 104;
			}
		}
	else if (pass_dy_objects_mu) {
		if (pass_dy_mass) {
			channel_stage = 103;
			}
		else {
			channel_stage = 102;
			}
		}

	else if (pass_dy_objects_el && tau_IDlev > TAUS_ID_CUT_Tight && opposite_charge) {
		if (pass_dy_mass) {
			channel_stage = 235;
			}
		else {
			channel_stage = 234;
			}
		}
	else if (pass_dy_objects_el && tau_IDlev > TAUS_ID_CUT_Tight) {
		if (pass_dy_mass) {
			channel_stage = 233;
			}
		else {
			channel_stage = 232;
			}
		}

	else if (pass_dy_objects_el && tau_IDlev > TAUS_ID_CUT_Medium && opposite_charge) {
		if (pass_dy_mass) {
			channel_stage = 225;
			}
		else {
			channel_stage = 224;
			}
		}
	else if (pass_dy_objects_el && tau_IDlev > TAUS_ID_CUT_Medium) {
		if (pass_dy_mass) {
			channel_stage = 223;
			}
		else {
			channel_stage = 222;
			}
		}

	else if (pass_dy_objects_el && tau_IDlev > TAUS_ID_CUT_VLoose && opposite_charge) {
		if (pass_dy_mass) {
			channel_stage = 215;
			}
		else {
			channel_stage = 214;
			}
		}
	else if (pass_dy_objects_el && tau_IDlev > TAUS_ID_CUT_VLoose) {
		if (pass_dy_mass) {
			channel_stage = 213;
			}
		else {
			channel_stage = 212;
			}
		}

	else if (pass_dy_objects_el && opposite_charge) {
		if (pass_dy_mass) {
			channel_stage = 205;
			}
		else {
			channel_stage = 204;
			}
		}
	else if (pass_dy_objects_el) {
		if (pass_dy_mass) {
			channel_stage = 203;
			}
		else {
			channel_stage = 202;
			}
		}

	return channel_stage;
	}


static bool NT_channel_dy_mutau(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_calc_channel_dy_tautau_selection_stages(sys);
	double mT = NT_distr_Mt_lep_met(sys);
	return mT < 40 && (relevant_selection_stage == 135 || relevant_selection_stage == 134 || relevant_selection_stage == 125 || relevant_selection_stage == 124);
	}

static bool NT_channel_dy_eltau(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_calc_channel_dy_tautau_selection_stages(sys);
	double mT = NT_distr_Mt_lep_met(sys);
	return mT < 40 && (relevant_selection_stage == 235 || relevant_selection_stage == 234 || relevant_selection_stage == 225 || relevant_selection_stage == 224);
	}

static bool NT_channel_dy_mutau_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_calc_channel_dy_tautau_selection_stages(sys);
	double mT = NT_distr_Mt_lep_met(sys);
	return mT < 40 && (relevant_selection_stage == 133 || relevant_selection_stage == 132 || relevant_selection_stage == 123 || relevant_selection_stage == 122);
	}

static bool NT_channel_dy_eltau_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_calc_channel_dy_tautau_selection_stages(sys);
	double mT = NT_distr_Mt_lep_met(sys);
	return mT < 40 && (relevant_selection_stage == 233 || relevant_selection_stage == 232 || relevant_selection_stage == 223 || relevant_selection_stage == 222);
	}

static bool NT_channel_dy_mutau_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_dy_mutau(sys);
	// I use the if expression to be sure the vector NT_event_taus_sv_sign is not empty!
	return sel ?  NT_calc_tau_sv_sign_geom(sys) > 3. : false;
	}
static bool NT_channel_dy_mutau_ss_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_dy_mutau_ss(sys);
	return sel ?  NT_calc_tau_sv_sign_geom(sys) > 3. : false;
	}

static bool NT_channel_dy_eltau_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_dy_eltau(sys);
	return sel ?  NT_calc_tau_sv_sign_geom(sys) > 3. : false;
	}
static bool NT_channel_dy_eltau_ss_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_dy_eltau_ss(sys);
	return sel ?  NT_calc_tau_sv_sign_geom(sys) > 3. : false;
	}



static int NT_calc_channel_dy_elmu_selection_stages(ObjSystematics sys)
	{
	int channel_stage = 0;
	//pass_mu, pass_elmu, pass_elmu_el, pass_mumu, pass_elel, pass_el, pass_mu_all, pass_el_all = passed_triggers
	Triggers trigs = NT_calc_triggers(sys);

	// muon and OS tau and no b
	bool pass_dy_objects_elmu = (trigs.pass_elmu || trigs.pass_elmu_el) && NT_lep_id.size() == 2;
	bool os_leptons = pass_dy_objects_elmu ? NT_lep_id[0] * NT_lep_id[1] < 0 : false;
	unsigned int N_jets_b = NT_calc_b_tagged_njets(sys);
	bool no_b_jets  = N_jets_b == 0;

	//pass_dy_mass = False
	//if pass_dy_objects_mu or pass_dy_objects_el:
	//	pair	= leps[0][0] + leps[0][1]
	//	pair_mass = pair.mass()
	//	pass_dy_mass = 75. < pair_mass < 105.

	if   (pass_dy_objects_elmu && no_b_jets && os_leptons) {
		channel_stage = 105;
		}
	else if (pass_dy_objects_elmu && no_b_jets) {
		channel_stage = 103;
		}
	else if (pass_dy_objects_elmu) {
		channel_stage = 102;
		}

	return channel_stage;
	}


static bool NT_channel_dy_elmu(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_calc_channel_dy_elmu_selection_stages(sys);
	return relevant_selection_stage == 105;
	}

static bool NT_channel_dy_elmu_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_calc_channel_dy_elmu_selection_stages(sys);
	return relevant_selection_stage == 103;
	}


static int NT_calc_channel_dy_mumu_selection_stages(ObjSystematics sys)
	{
	int channel_stage = 0;
	//pass_mu, pass_elmu, pass_elmu_el, pass_mumu, pass_elel, pass_el, pass_mu_all, pass_el_all = passed_triggers
	Triggers trigs = NT_calc_triggers(sys);

	// muon and OS tau and no b
	bool pass_dy_objects_mu = trigs.pass_mumu && NT_lep_id.size() == 2;
	bool pass_dy_objects_el = trigs.pass_elel && NT_lep_id.size() == 2;
	unsigned int N_jets_b = NT_calc_b_tagged_njets(sys);
	bool no_b_jets = N_jets_b == 0;
	bool pass_dy_mass = false;

	if (pass_dy_objects_mu || pass_dy_objects_el)
		{
		auto pair = NT_lep_p4[0] + NT_lep_p4[1];
		auto pair_mass = pair.mass();
		pass_dy_mass = 75. < pair_mass && pair_mass < 105.;
		}

	if   (pass_dy_objects_mu && no_b_jets && pass_dy_mass) {
		channel_stage = 105;
		}
	else if (pass_dy_objects_mu && no_b_jets) {
		channel_stage = 103;
		}
	else if (pass_dy_objects_mu) {
		channel_stage = 102;
		}
	else if (pass_dy_objects_el && no_b_jets && pass_dy_mass) {
		channel_stage = 115;
		}
	else if (pass_dy_objects_el && no_b_jets) {
		channel_stage = 113;
		}
	else if (pass_dy_objects_el) {
		channel_stage = 112;
		}

	return channel_stage;
	}


static bool NT_channel_dy_mumu(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_calc_channel_dy_mumu_selection_stages(sys);
	return relevant_selection_stage == 102 || relevant_selection_stage == 103 || relevant_selection_stage == 105;
	}

static bool NT_channel_dy_elel(ObjSystematics sys)
	{
	int relevant_selection_stage = NT_calc_channel_dy_mumu_selection_stages(sys);
	return relevant_selection_stage == 112 || relevant_selection_stage == 113 || relevant_selection_stage == 115;
	}



#define _quick_set_chandef(m, chan_name, sel_weight_func) m[#chan_name] = {NT_channel_ ## chan_name, sel_weight_func}

/** \brief The initialization function for the `bool` functions of the known distributions in the ntupler output ntuples.

`T_known_defs_channels == map<const char*, _F_channel_sel>`

\return T_known_defs_channels
 */

T_known_defs_channels create_known_defs_channels_ntupler()
{
	//map<TString, _F_channel_sel> m;
	map<TString, _S_chan_def> m;

	//m["el_sel"] = channel_el_sel;
	_quick_set_chandef(m, el_sel   , NT_sysweight_NOMINAL_HLT_EL_MedTau);
	_quick_set_chandef(m, el_sel_ss, NT_sysweight_NOMINAL_HLT_EL_MedTau);
	_quick_set_chandef(m, mu_sel   , NT_sysweight_NOMINAL_HLT_MU_MedTau);
	_quick_set_chandef(m, mu_sel_ss, NT_sysweight_NOMINAL_HLT_MU_MedTau);
	_quick_set_chandef(m, lep_sel      , NT_sysweight_NOMINAL_HLT_LEP_MedTau);
	_quick_set_chandef(m, lep_sel_ss   , NT_sysweight_NOMINAL_HLT_LEP_MedTau);

	_quick_set_chandef(m, el_sel_tauSV3   , NT_sysweight_NOMINAL_HLT_EL_MedTau);
	_quick_set_chandef(m, el_sel_ss_tauSV3, NT_sysweight_NOMINAL_HLT_EL_MedTau);
	_quick_set_chandef(m, mu_sel_tauSV3   , NT_sysweight_NOMINAL_HLT_MU_MedTau);
	_quick_set_chandef(m, mu_sel_ss_tauSV3, NT_sysweight_NOMINAL_HLT_MU_MedTau);
	_quick_set_chandef(m, lep_sel_tauSV3      , NT_sysweight_NOMINAL_HLT_LEP_MedTau);
	_quick_set_chandef(m, lep_sel_ss_tauSV3   , NT_sysweight_NOMINAL_HLT_LEP_MedTau);

	// old ntupler presel-s, from 2016 xsection measurement
	_quick_set_chandef(m, el_old_presel   , NT_sysweight_NOMINAL_HLT_EL_MedTau);
	_quick_set_chandef(m, el_old_presel_ss, NT_sysweight_NOMINAL_HLT_EL_MedTau);
	_quick_set_chandef(m, mu_old_presel   , NT_sysweight_NOMINAL_HLT_MU_MedTau);
	_quick_set_chandef(m, mu_old_presel_ss, NT_sysweight_NOMINAL_HLT_MU_MedTau);

	_quick_set_chandef(m, tt_elmu      , NT_sysweight_NOMINAL_HLT_EL);
	_quick_set_chandef(m, tt_elmu_tight, NT_sysweight_NOMINAL_HLT_EL);

	_quick_set_chandef(m, dy_elmu    , NT_sysweight_NOMINAL_HLT_MU);
	_quick_set_chandef(m, dy_elmu_ss , NT_sysweight_NOMINAL_HLT_MU);

	_quick_set_chandef(m, dy_mutau   , NT_sysweight_NOMINAL_HLT_MU_MedTau);
	_quick_set_chandef(m, dy_mutau_ss, NT_sysweight_NOMINAL_HLT_MU_MedTau);
	_quick_set_chandef(m, dy_eltau   , NT_sysweight_NOMINAL_HLT_EL_MedTau);
	_quick_set_chandef(m, dy_eltau_ss, NT_sysweight_NOMINAL_HLT_EL_MedTau);

	_quick_set_chandef(m, dy_mutau_tauSV3   , NT_sysweight_NOMINAL_HLT_MU_MedTau);
	_quick_set_chandef(m, dy_mutau_ss_tauSV3, NT_sysweight_NOMINAL_HLT_MU_MedTau);
	_quick_set_chandef(m, dy_eltau_tauSV3   , NT_sysweight_NOMINAL_HLT_EL_MedTau);
	_quick_set_chandef(m, dy_eltau_ss_tauSV3, NT_sysweight_NOMINAL_HLT_EL_MedTau);

	_quick_set_chandef(m, dy_mumu    , NT_sysweight_NOMINAL_HLT_MU);
	_quick_set_chandef(m, dy_elel    , NT_sysweight_NOMINAL_HLT_EL);

	return m;
}



/* --------------------------------------------------------------- */


/* --------------------------------------------------------------- */
// DTAGS, dtags, all dtag-related info, x-secs, systematics, gen processes

// (sub-)processes in a dtag are defined by whether gen_proc_id integer falls inside inclusive range of IDs [min_gen_id, max_gen_id]
// a number of standard definitions are given
// so a user can define them per final state channel

/*
In principle, since the definition of a gen-level processes
is done with a simple integer in ntupler, I could implement
definitions of processes with some ranges of gen ID.

typedef struct {
	int min;
	int max;
} proc_ID_range;

But I want to use functions operating in the name space of the TTree interface,
the same way as for the channel definitions.
It would is a much more flexible solution,
it is easily extensible to processing raw ntuples.

However, it requires more typing, therefore I will make some short-hand macro.
*/

/** \brief passes all events, to use in inclusive cases
*/

static bool NT_genproc_inclusive()
	{
	return true;
	}

/** these functions are assigned to specific dtags
    therefore just assume the NT variables relevant to those dtags are there
 */

static int genproc_dy_tautau = 1;
static int genproc_dy_other  = 0;

static int genproc_wjets_tauh = 2;
static int genproc_wjets_taul = 1;
static int genproc_wjets      = 0;

static int genproc_qcd = 0;
static int genproc_data = 0;

static int genproc_stop_el    = 20;
static int genproc_stop_mu    = 10;
static int genproc_stop_lj    = 2;
static int genproc_stop_elmu  = 1;
static int genproc_stop_other = 0;


static int genproc_tt_eltau3ch  = 42;
static int genproc_tt_eltau     = 41;
static int genproc_tt_mutau3ch  = 32;
static int genproc_tt_mutau     = 31;

static int genproc_tt_ljb       = 24;
static int genproc_tt_ljw       = 23;
static int genproc_tt_ljo       = 22;
static int genproc_tt_lj        = 21;
static int genproc_tt_taultauh  = 12;
static int genproc_tt_taulj     = 11;

static int genproc_tt_elmu       = 3;
static int genproc_tt_ltaul      = 2;
static int genproc_tt_taueltaumu = 1;

static int genproc_tt_other = 0;

static int NT_calc_gen_proc_id_tt()
	{
	int t_wid  = abs(NT_gen_t_w_decay_id);
	int tb_wid = abs(NT_gen_tb_w_decay_id);

	if ((t_wid > 15*15 && tb_wid == 13) || (t_wid == 13 && tb_wid > 15*15)) {
		// check if tau decayed in 3 charged particles
		if ((t_wid >= 15*30 && tb_wid == 13) || (t_wid == 13 && tb_wid >= 15*30)) {
			return genproc_tt_mutau3ch;
			}
		else {
			return genproc_tt_mutau;
			}
		}

	else if ((t_wid > 15*15 && tb_wid == 11) || (t_wid == 11 && tb_wid > 15*15)) {
		if ((t_wid >= 15*30 && tb_wid == 11) || (t_wid == 11 && tb_wid >= 15*30)) {
			return genproc_tt_eltau3ch;
			}
		else {
			return genproc_tt_eltau;
			}
		}

	else if (NT_gen_t_w_decay_id * NT_gen_tb_w_decay_id == -13*11) {
		return genproc_tt_elmu;
		}
	//else if (t_wid * tb_wid == 15*13*15*11: # this should w||k, but:
	else if ((t_wid == 15*13 && tb_wid == 15*11) || (t_wid == 15*11 && tb_wid == 15*13)) {
		return genproc_tt_taueltaumu;
		}
	else if ((t_wid  == 13 && tb_wid == 15*11) || (t_wid  == 11 && tb_wid == 15*13) ||
		 (tb_wid == 13 && t_wid  == 15*11) || (tb_wid == 11 &&  t_wid == 15*13)) {
		return genproc_tt_ltaul; // # opposite leptons -- el-taumu etc;
		}
	else if (t_wid * tb_wid == 13 || t_wid * tb_wid == 11) {
		return genproc_tt_lj;
		}
	else if ((t_wid > 15*15 && (tb_wid == 11*15 || tb_wid == 13*15)) ||
		 ((t_wid == 11*15 || t_wid == 13*15) && tb_wid > 15*15)) {
		return genproc_tt_taultauh;
		}
	else if ((t_wid == 1	 && tb_wid == 13*15) ||
		 (t_wid == 13*15 && tb_wid == 1)     ||
		 (t_wid == 1	 && tb_wid == 11*15) ||
		 (t_wid == 11*15 && tb_wid == 1)) {
		return genproc_tt_taulj;
		}
	else {
		return genproc_tt_other;
		};
	}

static int NT_calc_gen_proc_id_dy()
	{
	int lep1_id, lep2_id;

	if (NT_gen_N_zdecays > 0) {
		lep1_id = abs(NT_gen_zdecays_IDs[0]);
		lep2_id = abs(NT_gen_zdecays_IDs[1]);
		}
	else {
		// check prompt leptns
		// if no Z decay the leptons are there
		lep1_id = abs(NT_gen_pythia8_prompt_leptons_IDs[0]);
		lep2_id = abs(NT_gen_pythia8_prompt_leptons_IDs[1]);
		}

	// TODO: actually track tau decays fro DY? -- no need, it's a small background
	if (lep1_id >= 15 && lep2_id >= 15) {
		return genproc_dy_tautau;
		}
	else {
		return genproc_dy_other;
		}
	}

static int NT_calc_gen_proc_id_wjets()
	{
	int lep1_id, lep2_id;

	if (NT_gen_N_wdecays > 0) {
		lep1_id = abs(NT_gen_wdecays_IDs[0]);
		}
	//W does not need these prompt leptons, but I keep them just in case
	else {
		// check prompt leptns
		lep1_id = abs(NT_gen_pythia8_prompt_leptons_IDs[0]);
		}

	if (lep1_id >= 15*15) {
		return genproc_wjets_tauh;
		}
	else if (lep1_id >= 15) // # 15*11 and 15*13
		{
		return genproc_wjets_taul;
		}
	// we use only WToLNu now, W->j does not happen
	//elif lep1_id == 1:
	//	proc = 'wjets_j'
	else {
		return genproc_wjets;
		}
	}

static int NT_calc_gen_proc_id_single_top()
	{

	// basically only difference is eltau/mutau
	//w1_id = abs(NT_gen_wdecays_IDs[0])
	// check the top decay insted
	int w1_id = NT_gen_t_w_decay_id != -111 ? abs(NT_gen_t_w_decay_id) : abs(NT_gen_tb_w_decay_id);
	int w2_id = 1;

	//if (!isSTopTSchannels) {
	if (NT_gen_wdecays_IDs.size() > 0) { // TODO confirm this works
		// in tW there is an additional W produced with top
		w2_id = abs(NT_gen_wdecays_IDs[0]);
		//w2_id = abs(NT_gen_t_w_decay_id) if NT_gen_t_w_decay_id != -111 else abs(NT_gen_tb_w_decay_id)
		}

	// t/s channels emit top && a quark -- top ID + jets
	if ((w1_id > 15*15 && w2_id == 13) || (w1_id == 13 && w2_id > 15*15)) { // # lt
		return genproc_stop_mu;
		}
	else if ((w1_id > 15*15 && w2_id == 11) || (w1_id == 11 && w2_id > 15*15)) { // # lt
		return genproc_stop_el;
		}
	else if ((w1_id == 11 && w2_id == 13) || (w1_id == 13 && w2_id == 11)) { // # is it faster than comparing to product?
		return genproc_stop_elmu;
		}
	else if (w1_id * w2_id == 13 || w1_id * w2_id == 11) { // # lj
		return genproc_stop_lj;
		}
	//else if ((w1_id > 15*15 && (w2_id == 11*15 || w2_id == 13*15)) ||
	//	 ((w1_id == 11*15 || w1_id == 13*15) && w2_id > 15*15)) { // # taul tauh
	//	proc = 'tt_taultauh'
	else {
		return genproc_stop_other;
		}
	}

static bool NT_genproc_tt_eltau3ch()
	{
	auto NT_gen_proc_id = NT_calc_gen_proc_id_tt();
	return NT_gen_proc_id == 42;
	}

// a short-hand macro

#define NT_genproc(procname, calc_func, procID)         \
static bool NT_genproc_ ##procname(void)            \
	{                                  \
	auto NT_gen_proc_id = calc_func(); \
	return NT_gen_proc_id == (procID); \
	}

NT_genproc(tt_eltau1ch, NT_calc_gen_proc_id_tt, 41)
NT_genproc(tt_mutau3ch, NT_calc_gen_proc_id_tt, 32)
NT_genproc(tt_mutau1ch, NT_calc_gen_proc_id_tt, 31)

NT_genproc(tt_ljb        , NT_calc_gen_proc_id_tt, 24)
NT_genproc(tt_ljw        , NT_calc_gen_proc_id_tt, 23)
NT_genproc(tt_ljo        , NT_calc_gen_proc_id_tt, 22)
NT_genproc(tt_ljz        , NT_calc_gen_proc_id_tt, 21)
NT_genproc(tt_taultauh   , NT_calc_gen_proc_id_tt, 12)
NT_genproc(tt_taulj      , NT_calc_gen_proc_id_tt, 11)
NT_genproc(tt_elmu       , NT_calc_gen_proc_id_tt, 3)
NT_genproc(tt_ltaul      , NT_calc_gen_proc_id_tt, 2)
NT_genproc(tt_taueltaumu , NT_calc_gen_proc_id_tt, 1)
//NT_genproc(tt_other      , 0) // no "tt_other"! it is a catchall process, they are handled automatically

NT_genproc(dy_tautau , NT_calc_gen_proc_id_dy, 1)

NT_genproc(wjets_tauh , NT_calc_gen_proc_id_wjets, 2)
NT_genproc(wjets_taul , NT_calc_gen_proc_id_wjets, 1)

NT_genproc(stop_eltau , NT_calc_gen_proc_id_single_top, 20)
NT_genproc(stop_mutau , NT_calc_gen_proc_id_single_top, 10)
NT_genproc(stop_lj    , NT_calc_gen_proc_id_single_top,  2)
NT_genproc(stop_elmu  , NT_calc_gen_proc_id_single_top,  1)

static bool NT_genproc_tt_eltau()
	{
	auto NT_gen_proc_id = NT_calc_gen_proc_id_tt();
	return NT_gen_proc_id > 40 && NT_gen_proc_id < 43;
	}

#define NT_genproc_range_tt(procname, procID_min, procID_max)         \
static bool NT_genproc_ ##procname(void)          \
	{                                  \
	auto NT_gen_proc_id = NT_calc_gen_proc_id_tt(); \
	return (NT_gen_proc_id > (procID_min)) && (NT_gen_proc_id < (procID_max)); \
	}

NT_genproc_range_tt(tt_mutau, 30, 33)
NT_genproc_range_tt(tt_leptau, 30, 43)

NT_genproc_range_tt(tt_lj, 20, 30)

// standard per-channel processes
static vector<TString> _eltau_tt_procs  = {"tt_eltau", "tt_taulj", "tt_lj"};
static vector<TString> _mutau_tt_procs  = {"tt_mutau", "tt_taulj", "tt_lj"};
static vector<TString> _leptau_tt_procs = {"tt_leptau", "tt_taulj", "tt_lj"};
static vector<TString>  _elmu_tt_procs = {"tt_elmu",  "tt_ltaul"};
//vector<TString> _mumu_tt_procs  = {"tt_inclusive"};
//vector<TString> _elel_tt_procs  = {"tt_inclusive"};
// actually empty vectors must work, the catchall process will handle this
static vector<TString> _mumu_tt_procs  = {};
static vector<TString> _elel_tt_procs  = {};

static vector<TString> _leptau_dy_procs = {"dy_tautau"};
static vector<TString>  _incl_dy_procs = {};

static vector<TString> _eltau_stop_procs = {"stop_eltau", "stop_lj"};
static vector<TString> _mutau_stop_procs = {"stop_mutau", "stop_lj"};
static vector<TString>  _elmu_stop_procs = {"stop_elmu"};
static vector<TString>  _mumu_stop_procs = {};
static vector<TString>  _elel_stop_procs = {};

static vector<TString> _eltau_wjets_procs = {"wjets_tauh", "wjets_taul"};
static vector<TString> _mutau_wjets_procs = {"wjets_tauh", "wjets_taul"};
static vector<TString>  _elmu_wjets_procs = {};
static vector<TString>  _mumu_wjets_procs = {};
static vector<TString>  _elel_wjets_procs = {};

static vector<TString>  _any_procs = {};

// ^--- I am not sure this is the best approach to define these standard processes
//      initially I wanted to have a bunch of general sets, not the concrete per-channel ones


/** \brief The initialization function for the known gen level processes in the ntupler output ntuples.

\return T_known_defs_procs
 */

T_known_defs_procs create_known_defs_procs_ntupler()
	{
	T_known_defs_procs m;

	m["tt"] = {
		.catchall_name = "tt_other",
		.all={
			{"tt_eltau3ch" , NT_genproc_tt_eltau3ch},
			{"tt_eltau1ch" , NT_genproc_tt_eltau1ch},
			{"tt_mutau3ch" , NT_genproc_tt_mutau3ch},
			{"tt_mutau1ch" , NT_genproc_tt_mutau1ch},

			{"tt_ljb"        , NT_genproc_tt_ljb        },
			{"tt_ljw"        , NT_genproc_tt_ljw        },
			{"tt_ljo"        , NT_genproc_tt_ljo        },
			{"tt_ljz"        , NT_genproc_tt_ljz        },
			{"tt_taultauh"   , NT_genproc_tt_taultauh   },
			{"tt_taulj"      , NT_genproc_tt_taulj      },
			{"tt_elmu"       , NT_genproc_tt_elmu       },
			{"tt_ltaul"      , NT_genproc_tt_ltaul      },
			{"tt_taueltaumu" , NT_genproc_tt_taueltaumu },
			//{"tt_other"      , NT_genproc_tt_other      },
			},

		.groups={
			{"tt_eltau" , NT_genproc_tt_eltau},
			{"tt_mutau" , NT_genproc_tt_mutau},
			{"tt_leptau" , NT_genproc_tt_leptau},
			{"tt_lj"    , NT_genproc_tt_lj},
			{"tt_inclusive" , NT_genproc_inclusive},
			},

		.channel_standard = {
			{"el_sel",    _eltau_tt_procs},
			{"el_sel_ss", _eltau_tt_procs},
			{"mu_sel",    _mutau_tt_procs},
			{"mu_sel_ss", _mutau_tt_procs},
			{"el_old_presel",    _eltau_tt_procs},
			{"el_old_presel_ss", _eltau_tt_procs},
			{"mu_old_presel",    _mutau_tt_procs},
			{"mu_old_presel_ss", _mutau_tt_procs},

			{"el_sel_tauSV3",    _eltau_tt_procs},
			{"el_sel_ss_tauSV3", _eltau_tt_procs},
			{"mu_sel_tauSV3",    _mutau_tt_procs},
			{"mu_sel_ss_tauSV3", _mutau_tt_procs},

			{"lep_sel",    _leptau_tt_procs},
			{"lep_sel_ss", _leptau_tt_procs},

			{"tt_elmu",       _elmu_tt_procs},
			{"tt_elmu_tight", _elmu_tt_procs},
			{"dy_elmu",       _elmu_tt_procs},
			{"dy_elmu_ss",    _elmu_tt_procs},

			{"dy_mutau",      _mutau_tt_procs},
			{"dy_mutau_ss",   _mutau_tt_procs},
			{"dy_eltau",      _eltau_tt_procs},
			{"dy_eltau_ss",   _eltau_tt_procs},

			{"dy_mutau_tauSV3",      _mutau_tt_procs},
			{"dy_mutau_ss_tauSV3",   _mutau_tt_procs},
			{"dy_eltau_tauSV3",      _eltau_tt_procs},
			{"dy_eltau_ss_tauSV3",   _eltau_tt_procs},

			{"dy_mumu",       _mumu_tt_procs},
			{"dy_elel",       _mumu_tt_procs},

			}
		};

	m["dy"] = {
		.catchall_name = "dy_other", // usually we run only on DYTo2L, so this is the elel and mumu
		.all={
			{"dy_tautau"   , NT_genproc_dy_tautau},
			},

		.groups={},

		.channel_standard = {
			{"el_sel",    _leptau_dy_procs},
			{"el_sel_ss", _leptau_dy_procs},
			{"mu_sel",    _leptau_dy_procs},
			{"mu_sel_ss", _leptau_dy_procs},
			{"el_old_presel",    _leptau_dy_procs},
			{"el_old_presel_ss", _leptau_dy_procs},
			{"mu_old_presel",    _leptau_dy_procs},
			{"mu_old_presel_ss", _leptau_dy_procs},

			{"el_sel_tauSV3",    _leptau_dy_procs},
			{"el_sel_ss_tauSV3", _leptau_dy_procs},
			{"mu_sel_tauSV3",    _leptau_dy_procs},
			{"mu_sel_ss_tauSV3", _leptau_dy_procs},

			{"tt_elmu",       _incl_dy_procs},
			{"tt_elmu_tight", _incl_dy_procs},

			{"dy_mutau",      _leptau_dy_procs},
			{"dy_mutau_ss",   _leptau_dy_procs},
			{"dy_eltau",      _leptau_dy_procs},
			{"dy_eltau_ss",   _leptau_dy_procs},

			{"dy_mutau_tauSV3",      _leptau_dy_procs},
			{"dy_mutau_ss_tauSV3",   _leptau_dy_procs},
			{"dy_eltau_tauSV3",      _leptau_dy_procs},
			{"dy_eltau_ss_tauSV3",   _leptau_dy_procs},

			{"dy_mumu",       _incl_dy_procs},
			{"dy_elel",       _incl_dy_procs},
			{"dy_elmu",       _leptau_dy_procs},
			{"dy_elmu_ss",    _leptau_dy_procs},
			}
		};

	m["stop"] = {
		.catchall_name = "stop_other",
		.all={
			{"stop_eltau"   , NT_genproc_stop_eltau},
			{"stop_mutau"   , NT_genproc_stop_mutau},
			{"stop_lj"   , NT_genproc_stop_lj},
			{"stop_elmu" , NT_genproc_stop_elmu},
			},

		.groups={},

		.channel_standard = {
			{"el_sel",    _eltau_stop_procs},
			{"el_sel_ss", _eltau_stop_procs},
			{"mu_sel",    _mutau_stop_procs},
			{"mu_sel_ss", _mutau_stop_procs},
			{"el_old_presel",    _eltau_stop_procs},
			{"el_old_presel_ss", _eltau_stop_procs},
			{"mu_old_presel",    _mutau_stop_procs},
			{"mu_old_presel_ss", _mutau_stop_procs},

			{"el_sel_tauSV3",    _eltau_stop_procs},
			{"el_sel_ss_tauSV3", _eltau_stop_procs},
			{"mu_sel_tauSV3",    _mutau_stop_procs},
			{"mu_sel_ss_tauSV3", _mutau_stop_procs},

			{"tt_elmu",        _elmu_stop_procs},
			{"tt_elmu_tight",  _elmu_stop_procs},

			{"dy_mutau",      _mutau_stop_procs},
			{"dy_mutau_ss",   _mutau_stop_procs},
			{"dy_eltau",      _eltau_stop_procs},
			{"dy_eltau_ss",   _eltau_stop_procs},

			{"dy_mutau_tauSV3",      _mutau_stop_procs},
			{"dy_mutau_ss_tauSV3",   _mutau_stop_procs},
			{"dy_eltau_tauSV3",      _eltau_stop_procs},
			{"dy_eltau_ss_tauSV3",   _eltau_stop_procs},

			{"dy_mumu",        _mumu_stop_procs},
			{"dy_elel",        _mumu_stop_procs},
			{"dy_elmu",       _elmu_stop_procs},
			{"dy_elmu_ss",    _elmu_stop_procs},
			}
		};

	m["wjets"] = {
		.catchall_name = "wjets_other",
		.all={
			{"wjets_tauh"   , NT_genproc_wjets_tauh},
			{"wjets_taul"   , NT_genproc_wjets_taul},
			},

		.groups={},

		.channel_standard = {
			{"el_sel",    _eltau_wjets_procs},
			{"el_sel_ss", _eltau_wjets_procs},
			{"mu_sel",    _mutau_wjets_procs},
			{"mu_sel_ss", _mutau_wjets_procs},
			{"el_old_presel",    _eltau_wjets_procs},
			{"el_old_presel_ss", _eltau_wjets_procs},
			{"mu_old_presel",    _mutau_wjets_procs},
			{"mu_old_presel_ss", _mutau_wjets_procs},

			{"el_sel_tauSV3",    _eltau_wjets_procs},
			{"el_sel_ss_tauSV3", _eltau_wjets_procs},
			{"mu_sel_tauSV3",    _mutau_wjets_procs},
			{"mu_sel_ss_tauSV3", _mutau_wjets_procs},

			{"tt_elmu",        _elmu_wjets_procs},
			{"tt_elmu_tight",  _elmu_wjets_procs},

			{"dy_mutau",      _mutau_wjets_procs},
			{"dy_mutau_ss",   _mutau_wjets_procs},
			{"dy_eltau",      _eltau_wjets_procs},
			{"dy_eltau_ss",   _eltau_wjets_procs},

			{"dy_mutau_tauSV3",      _mutau_wjets_procs},
			{"dy_mutau_ss_tauSV3",   _mutau_wjets_procs},
			{"dy_eltau_tauSV3",      _eltau_wjets_procs},
			{"dy_eltau_ss_tauSV3",   _eltau_wjets_procs},

			{"dy_mumu",        _mumu_wjets_procs},
			{"dy_elel",        _mumu_wjets_procs},
			{"dy_elmu",       _elmu_wjets_procs},
			{"dy_elmu_ss",    _elmu_wjets_procs},
			}
		};

	m["qcd"] = {
		.catchall_name = "qcd_other",
		.all={},
		.groups={},

		.channel_standard = {
			{"el_sel",    _any_procs},
			{"el_sel_ss", _any_procs},
			{"mu_sel",    _any_procs},
			{"mu_sel_ss", _any_procs},
			{"el_old_presel",    _any_procs},
			{"el_old_presel_ss", _any_procs},
			{"mu_old_presel",    _any_procs},
			{"mu_old_presel_ss", _any_procs},

			{"el_sel_tauSV3",    _any_procs},
			{"el_sel_ss_tauSV3", _any_procs},
			{"mu_sel_tauSV3",    _any_procs},
			{"mu_sel_ss_tauSV3", _any_procs},

			{"tt_elmu",        _any_procs},
			{"tt_elmu_tight",  _any_procs},

			{"dy_mutau",      _any_procs},
			{"dy_mutau_ss",   _any_procs},
			{"dy_eltau",      _any_procs},
			{"dy_eltau_ss",   _any_procs},

			{"dy_mutau_tauSV3",      _any_procs},
			{"dy_mutau_ss_tauSV3",   _any_procs},
			{"dy_eltau_tauSV3",      _any_procs},
			{"dy_eltau_ss_tauSV3",   _any_procs},

			{"dy_mumu",       _any_procs},
			{"dy_elel",       _any_procs},
			{"dy_elmu",       _any_procs},
			{"dy_elmu_ss",    _any_procs},
			}
		};


	m["data"] = {
		.catchall_name = "data", // usually we run only on DYTo2L, so this is the elel and mumu
		.all={},
		.groups={},
		.channel_standard = {
			{"el_sel",    {}},
			{"el_sel_ss", {}},
			{"mu_sel",    {}},
			{"mu_sel_ss", {}},
			{"el_old_presel",    {}},
			{"el_old_presel_ss", {}},
			{"mu_old_presel",    {}},
			{"mu_old_presel_ss", {}},

			{"el_sel_tauSV3",    {}},
			{"el_sel_ss_tauSV3", {}},
			{"mu_sel_tauSV3",    {}},
			{"mu_sel_ss_tauSV3", {}},

			{"tt_elmu",       {}},
			{"tt_elmu_tight", {}},

			{"dy_mutau",      {}},
			{"dy_mutau_ss",   {}},
			{"dy_eltau",      {}},
			{"dy_eltau_ss",   {}},

			{"dy_mutau_tauSV3",      {}},
			{"dy_mutau_ss_tauSV3",   {}},
			{"dy_eltau_tauSV3",      {}},
			{"dy_eltau_ss_tauSV3",   {}},

			{"dy_mumu",       {}},
			{"dy_elel",       {}},
			{"dy_elmu",       {}},
			{"dy_elmu_ss",    {}},
			}
		};





//genproc_tt_ljb       = 24
//genproc_tt_ljw       = 23
//genproc_tt_ljo       = 22
//genproc_tt_lj        = 21
//genproc_tt_taultauh  = 12
//genproc_tt_taulj     = 11
//
//genproc_tt_elmu       = 3
//genproc_tt_ltaul      = 2
//genproc_tt_taueltaumu = 1
//
//genproc_tt_other = 0


	return m;
	}





/* --------------------------------------------------------------- */
// final normalizations

// TODO: these are post-stage2 normalizations? recalculate them

T_known_MC_normalization_per_somename create_known_MC_normalization_per_syst_ntupler()
	{
	map<TString, double> m;

	// TODO: review these, must the NOMINAL normalization be applied to all the others?

	// 2016 corrections
	m["NOMINAL" ] = 1. / 1.01388; // NOMINAL PU factor
	m["PUUp"    ] = 1. / 0.994846;
	m["PUDown"  ] = 1. / 1.03657;

	// tt only!
	m["FragUp"	] = 0.958852; //1.001123,
	m["FragDown"	] = 1.02936;  //0.999304,
	m["SemilepBRUp"	] = 1.002650;
	m["SemilepBRDown"	] = 1.035812;
	m["PetersonUp"	] = 0.990578;

	m["MrUp"	] = 0.896601;
	m["MrDown"	] = 1.114154;
	m["MfUp"	] = 0.980610;
	m["MfDown"	] = 1.025511;
	m["MfrUp"	] = 0.874602;
	m["MfrDown"	] = 1.135832;
	m["AlphaSDown"	] = 1.015573;
	m["AlphaSUp"	] = 0.984924;
	m["PDFCT14n1Up"	] = 0.999214;
	m["PDFCT14n10Up"	] = 0.992985;
	m["PDFCT14n11Up"	] = 1.011667;
	m["PDFCT14n12Up"	] = 0.991012;
	m["PDFCT14n13Up"	] = 1.011832;
	m["PDFCT14n14Up"	] = 0.994285;
	m["PDFCT14n15Up"	] = 1.020625;
	m["PDFCT14n16Up"	] = 0.985324;
	m["PDFCT14n17Up"	] = 0.986681;
	m["PDFCT14n18Up"	] = 1.015958;
	m["PDFCT14n19Up"	] = 0.999024;
	m["PDFCT14n2Up"	] = 0.999610;
	m["PDFCT14n20Up"	] = 1.001383;
	m["PDFCT14n21Up"	] = 1.000811;
	m["PDFCT14n22Up"	] = 0.998574;
	m["PDFCT14n23Up"	] = 1.004126;
	m["PDFCT14n24Up"	] = 0.996106;
	m["PDFCT14n25Up"	] = 1.012630;
	m["PDFCT14n26Up"	] = 0.987756;
	m["PDFCT14n27Up"	] = 1.003978;
	m["PDFCT14n28Up"	] = 0.994568;
	m["PDFCT14n29Up"	] = 1.002681;
	m["PDFCT14n3Up"	] = 0.991550;
	m["PDFCT14n30Up"	] = 0.999111;
	m["PDFCT14n31Up"	] = 1.001791;
	m["PDFCT14n32Up"	] = 0.997694;
	m["PDFCT14n33Up"	] = 0.996328;
	m["PDFCT14n34Up"	] = 1.008113;
	m["PDFCT14n35Up"	] = 0.985943;
	m["PDFCT14n36Up"	] = 1.013638;
	m["PDFCT14n37Up"	] = 0.993136;
	m["PDFCT14n38Up"	] = 1.010604;
	m["PDFCT14n39Up"	] = 0.995664;
	m["PDFCT14n4Up"	] = 0.995349;
	m["PDFCT14n40Up"	] = 1.004863;
	m["PDFCT14n41Up"	] = 0.999538;
	m["PDFCT14n42Up"	] = 1.000247;
	m["PDFCT14n43Up"	] = 0.997833;
	m["PDFCT14n44Up"	] = 1.005385;
	m["PDFCT14n45Up"	] = 1.004722;
	m["PDFCT14n46Up"	] = 1.001524;
	m["PDFCT14n47Up"	] = 0.999380;
	m["PDFCT14n48Up"	] = 0.993950;
	m["PDFCT14n49Up"	] = 0.993164;
	m["PDFCT14n5Up"	] = 0.994886;
	m["PDFCT14n50Up"	] = 1.003200;
	m["PDFCT14n51Up"	] = 1.001966;
	m["PDFCT14n52Up"	] = 1.000614;
	m["PDFCT14n53Up"	] = 0.968178;
	m["PDFCT14n54Up"	] = 1.010604;
	m["PDFCT14n55Up"	] = 0.992717;
	m["PDFCT14n56Up"	] = 1.012645;
	m["PDFCT14n6Up"	] = 1.004233;
	m["PDFCT14n7Up"	] = 1.001432;
	m["PDFCT14n8Up"	] = 0.992782;
	m["PDFCT14n9Up"	] = 1.008439;

	// 2017 from TTTo2L
	m["MU_PU"]     =         0.692955;
	m["MU_PUUp"]   =         0.757326;
	m["MU_PUDown"] =         0.637007;
	m["El_PU"]     =         0.579763;
	m["El_PUUp"]   =         0.627530;
	m["El_PUDown"] =         0.542434;
	// TODO: the same issue with PU, I need to normalize to nominal PU everywhere?
	// for now let's just normalize systematics
	// I use only muon channels now, so:
	m["NOMINAL" ] = 1./0.692955; // NOMINAL PU factor
	m["PUUp"]     = 1./0.757326;
	m["PUDown"]   = 1./0.637007;

	m["TOPPT"] = 1. /             1.000352;
	m["FragUp"] = 1. /             0.912333;
	m["FragDown"] = 1. /             1.067350;
	m["SemilepBRUp"] = 1. /             1.014130;
	m["SemilepBRDown"] = 1. /             1.047939;
	m["PetersonUp"] = 1. /             0.963072;

	m["MrUp"] = 1. /             0.897033;
	m["MrDown"] = 1. /             1.116338;
	m["MfUp"] = 1. /             0.979744;
	m["MfDown"] = 1. /             1.026878;
	m["MfrUp"] = 1. /             0.874539;
	m["MfrDown"] = 1. /             1.140431;

	m["AlphaSDown"] = 1. /            73.388846;
	m["AlphaSUp"] = 1. /            73.434533;
	m["PDFCT14n1"] = 1. /             0.842441;
	m["PDFCT14n10"] = 1. /             1.019382;
	m["PDFCT14n11"] = 1. /             1.017693;
	m["PDFCT14n12"] = 1. /             1.018400;
	m["PDFCT14n13"] = 1. /             1.021125;
	m["PDFCT14n14"] = 1. /             1.019251;
	m["PDFCT14n15"] = 1. /             1.017953;
	m["PDFCT14n16"] = 1. /             1.019955;
	m["PDFCT14n17"] = 1. /             1.017888;
	m["PDFCT14n18"] = 1. /             1.020231;
	m["PDFCT14n19"] = 1. /             1.016634;
	m["PDFCT14n2"] = 1. /             0.867848;
	m["PDFCT14n20"] = 1. /             1.017093;
	m["PDFCT14n21"] = 1. /             1.019368;
	m["PDFCT14n22"] = 1. /             1.019468;
	m["PDFCT14n23"] = 1. /             1.019067;
	m["PDFCT14n24"] = 1. /             1.016827;
	m["PDFCT14n25"] = 1. /             1.019057;
	m["PDFCT14n26"] = 1. /             1.018442;
	m["PDFCT14n27"] = 1. /             1.019834;
	m["PDFCT14n28"] = 1. /             1.018420;
	m["PDFCT14n29"] = 1. /             1.018189;
	m["PDFCT14n3"] = 1. /             0.894395;
	m["PDFCT14n30"] = 1. /             1.018549;
	m["PDFCT14n31"] = 1. /             1.018317;
	m["PDFCT14n32"] = 1. /             1.017693;
	m["PDFCT14n33"] = 1. /             1.017466;
	m["PDFCT14n34"] = 1. /             1.018964;
	m["PDFCT14n35"] = 1. /             1.018410;
	m["PDFCT14n36"] = 1. /             1.019069;
	m["PDFCT14n37"] = 1. /             1.016709;
	m["PDFCT14n38"] = 1. /             1.016373;
	m["PDFCT14n39"] = 1. /             1.022541;
	m["PDFCT14n4"] = 1. /             0.918370;
	m["PDFCT14n40"] = 1. /             1.020639;
	m["PDFCT14n41"] = 1. /             1.018076;
	m["PDFCT14n42"] = 1. /             1.019376;
	m["PDFCT14n43"] = 1. /             1.018341;
	m["PDFCT14n44"] = 1. /             1.019453;
	m["PDFCT14n45"] = 1. /             1.018983;
	m["PDFCT14n46"] = 1. /             1.019039;
	m["PDFCT14n47"] = 1. /             1.018464;
	m["PDFCT14n48"] = 1. /             1.018923;
	m["PDFCT14n49"] = 1. /             1.018704;
	m["PDFCT14n5"] = 1. /             0.958628;
	m["PDFCT14n50"] = 1. /             1.018930;
	m["PDFCT14n51"] = 1. /             1.017098;
	m["PDFCT14n52"] = 1. /             1.017097;
	m["PDFCT14n53"] = 1. /             1.018855;
	m["PDFCT14n54"] = 1. /             1.019012;
	m["PDFCT14n55"] = 1. /             1.019831;
	m["PDFCT14n56"] = 1. /             1.018409;
	m["PDFCT14n6"] = 1. /             0.986781;
	m["PDFCT14n7"] = 1. /             1.024974;
	m["PDFCT14n8"] = 1. /             1.053645;
	m["PDFCT14n9"] = 1. /             1.018451;

	return m;
	}

//map<TString, double> known_normalization_per_syst = create_known_MC_normalization_per_syst();
//T_known_MC_normalization_per_somename known_normalization_per_syst_ntupler = create_known_MC_normalization_per_syst();
//T_known_MC_normalization_per_somename known_normalization_per_syst_ntupler = create_known_MC_normalization_per_syst_ntupler();

T_known_MC_normalization_per_somename create_known_MC_normalization_per_proc_ntupler()
	{
	map<TString, double> m;

	/* NO! tau ID is only applied in channels where a tau was actually required
	double tau_ID_correction = 0.95;
	m["tt_eltau"]    = tau_ID_correction;
	m["tt_mutau"]    = tau_ID_correction;
	m["tt_eltau3ch"] = tau_ID_correction;
	m["tt_mutau3ch"] = tau_ID_correction;
	m["tt_eltau1ch"] = tau_ID_correction;
	m["tt_mutau1ch"] = tau_ID_correction;

	m["tt_taultauh"] = tau_ID_correction;

	m["dy_tautau"] = tau_ID_correction;
	m["s_top_eltau"] = tau_ID_correction;
	m["s_top_mutau"] = tau_ID_correction;
	*/

	return m;
	}

//T_known_MC_normalization_per_somename known_normalization_per_proc_ntupler = create_known_MC_normalization_per_proc();


T_known_MC_normalization_per_somename create_known_MC_normalization_per_chan_ntupler()
	{
	map<TString, double> m;

	return m;
	}

//T_known_MC_normalization_per_somename known_normalization_per_chan_ntupler = create_known_MC_normalization_per_chan_ntupler();


int connect_ntuple_interface_ntupler(TTree* NT_output_ttree)
	{
	#define OUTNTUPLE NT_output_ttree
	#define NTUPLE_INTERFACE_CONNECT
	#include "ntupler_interface.h" // it runs a bunch of branch-connecting commands on TTree* with name OUTNTUPLE

	return 0;
	}

//connect_ntuple_interface_ntupler = &_connect_ntuple_interface_ntupler;

