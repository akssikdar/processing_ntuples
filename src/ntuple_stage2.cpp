
#include "UserCode/processing_ntuples/interface/ntuple_stage2.h"

/* Global interface to the ttree, the name space for all the event-processing fucntions.
 */
#define NTUPLE_INTERFACE_CLASS_DECLARE
#include "stage2_interface.h"

/* --------------------------------------------------------------- */
/* STD DEFS */
//#include "std_defs.h"

/*
 * The distributions:
 * processing functions in the name space of the stage2 interface,
 * definitions of histograms with various ranges.
 */


static double NT_sysweight_NOMINAL_HLT_EL()
	{
	return NT_event_weight*NT_event_weight_PU*NT_event_weight_LEPmuID*NT_event_weight_LEPelID* NT_event_weight_LEPelTRG;
	}

static double NT_sysweight_NOMINAL_HLT_MU()
	{
	return NT_event_weight*NT_event_weight_PU*NT_event_weight_LEPmuID*NT_event_weight_LEPelID* NT_event_weight_LEPmuTRG;
	}

static double NT_sysweight_NOMINAL_HLT_LEP()
	{
	double common = NT_event_weight*NT_event_weight_PU*NT_event_weight_LEPmuID*NT_event_weight_LEPelID;
	if (abs(NT_event_leptons_ids[0]) == 13)
		return  NT_event_weight_LEPmuTRG * common;
	else
		return  NT_event_weight_LEPelTRG * common;
	}

static double NT_sysweight_NOMINAL_HLT_EL_MedTau()
	{
	// old stage2 output, from the 2016 xsection measurement
	//return NT_event_weight*0.95;
	// new, 2017 stage2
	return NT_event_weight*NT_event_weight_PU*NT_event_weight_LEPmuID*NT_event_weight_LEPelID* NT_event_weight_LEPelTRG * NT_event_taus_SF_Medium[0];
	}

static double NT_sysweight_NOMINAL_HLT_MU_MedTau()
	{
	// old stage2 output, from the 2016 xsection measurement
	//return NT_event_weight*0.95;
	return NT_event_weight*NT_event_weight_PU*NT_event_weight_LEPmuID*NT_event_weight_LEPelID* NT_event_weight_LEPmuTRG * NT_event_taus_SF_Medium[0];
	}

static double NT_sysweight_NOMINAL_HLT_LEP_MedTau()
	{
	//double common = NT_event_weight*NT_event_weight_PU*NT_event_weight_LEPmuID*NT_event_weight_LEPelID * NT_event_taus_SF_Medium[0];
	//if (abs(NT_event_leptons_ids[0]) == 13)
	//	return  NT_event_weight_LEPmuTRG * common;
	//else
	//	return  NT_event_weight_LEPelTRG * common;
	double lep_weight = NT_sysweight_NOMINAL_HLT_LEP();
	return lep_weight * NT_event_taus_SF_Medium[0];
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



#define _quick_set_objsys(sysname) m[#sysname] = {sysname, NT_sysweight_NOMINAL}
#define _quick_set_wgtsys(sysname) m[#sysname] = {NOMINAL, NT_sysweight_##sysname}

T_known_defs_systs create_known_defs_systs_stage2()
	{
	map<TString, _S_systematic_definition> m;
	m["NOMINAL"] = {NOMINAL, NT_sysweight_NOMINAL};

	_quick_set_objsys(JERUp);
	_quick_set_objsys(JERDown);
	_quick_set_objsys(JESUp);
	_quick_set_objsys(JESDown);
	_quick_set_objsys(TESUp);
	_quick_set_objsys(TESDown);

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

	return m;
	}



static double NT_distr_nvtx(ObjSystematics sys)
	{
	return NT_nvtx;
	}

static double NT_distr_leading_lep_pt(ObjSystematics sys)
	{
	return NT_event_leptons[0].pt();
	}

static double NT_distr_dilep_mass(ObjSystematics sys)
	{
	if (NT_event_leptons.size()>1)
		return (NT_event_leptons[0] + NT_event_leptons[1]).mass();
	else if (NT_event_taus.size()>0)
		return (NT_event_leptons[0] + NT_event_taus[0]).mass();
	else
		return -111.;
	}

static double NT_distr_tau_pt(ObjSystematics sys)
	{

	// from stage2.py and std_defs.py:
	//'tau_pt':        ({'NOMINAL': lambda ev: ev.event_taus[0].pt()    if len(ev.event_taus) > 0   else -111.},    ('histo-range',  [40,0,200])),
	//'event_taus_TES_up' : 'DoubleVector',
	//'event_taus_TES_down' : 'DoubleVector',
	//p4 = tau[0] * TES_nom
	//event_taus          .push_back(p4)
	//event_taus_TES_up   .push_back(TES_up / TES_nom)
	//event_taus_TES_down .push_back(TES_down / TES_nom)

	if (NT_event_taus.size()==0)
		return -111.;

	double pt = NT_event_taus[0].pt();
	if      (sys == TESUp)   return pt * NT_event_taus_TES_up[0];
	else if (sys == TESDown) return pt * NT_event_taus_TES_down[0];
	else                     return pt;
	}

static double NT_distr_tau_sv_sign(ObjSystematics sys)
	{
	if (NT_event_taus_sv_sign.size()>0)
		return NT_event_taus_sv_sign[0];
	else
		return -111.;
	}

static double NT_distr_sum_cos(ObjSystematics sys)
	{
	if (NT_event_leptons.size() == 0 || NT_event_taus.size() == 0) return -11.;
	double cos_lep_met = TMath::Cos(NT_event_leptons[0].Phi() - NT_event_met.Phi());
	double cos_tau_met = TMath::Cos(NT_event_taus[0]   .Phi() - NT_event_met.Phi());
	return cos_lep_met + cos_tau_met;
	}


static double NT_distr_lj_var(ObjSystematics sys)
	{
	return NT_event_jets_lj_var;
	}

static double NT_distr_lj_var_w_mass(ObjSystematics sys)
	{
	return NT_event_jets_lj_w_mass;
	}

static double NT_distr_lj_var_t_mass(ObjSystematics sys)
	{
	return NT_event_jets_lj_t_mass;
	}

static double NT_distr_Mt_lep_met(ObjSystematics sys)
	{

	if      (sys == NOMINAL) return NT_event_met_lep_mt;
	else if (sys == JERUp)   return NT_event_met_lep_mt_JERUp;
	else if (sys == JERDown) return NT_event_met_lep_mt_JERDown;
	else if (sys == JESUp)   return NT_event_met_lep_mt_JESUp;
	else if (sys == JESDown) return NT_event_met_lep_mt_JESDown;
	else if (sys == TESUp)   return NT_event_met_lep_mt_TESUp;
	else if (sys == TESDown) return NT_event_met_lep_mt_TESDown;

	else return NT_event_met_lep_mt;
	}

static double NT_distr_met(ObjSystematics sys)
	{

	if      (sys == NOMINAL) return NT_event_met.pt();
	else if (sys == JERUp)   return NT_event_met_JERUp.pt();
	else if (sys == JERDown) return NT_event_met_JERDown.pt();
	else if (sys == JESUp)   return NT_event_met_JESUp.pt();
	else if (sys == JESDown) return NT_event_met_JESDown.pt();
	else if (sys == TESUp)   return NT_event_met_TESUp.pt();
	else if (sys == TESDown) return NT_event_met_TESDown.pt();

	else return NT_event_met.pt();
	}



/**
\brief The initialization function for the definitions of the known distributions in the stage2 output ntuples.

\return map<const char*, _TH1D_histo_def>
 */

T_known_defs_distrs create_known_defs_distrs_stage2()
{
	map<TString, _TH1D_histo_def> m;
	_TH1D_histo_range r;
	//r = {.nbins=40, .linear_min=0, .linear_max=200}; m["leading_lep_pt"] = {leading_lep_pt, r};
	// despicable!
	// "sorry, unimplemented: non-trivial designated initializers not supported"

	r = {50,  true,   0, 50};                                                      m["nvtx"] = {NT_distr_nvtx, r};

	r = {40,  true,   0, 200};                                                     m["leading_lep_pt"] = {NT_distr_leading_lep_pt, r};
	r = {40,  true,  30,  40};                                                     m["leading_lep_pt_el_edge35"] = {NT_distr_leading_lep_pt, r};
	r = {40,  true,   0, 200};                                                     m["tau_pt"]         = {NT_distr_tau_pt, r};
	// taus have smaller energy in ttbar, therefore we might want to look at a smaller range
	r = {40,  true,   0, 150};                                                     m["tau_pt_range2"]  = {NT_distr_tau_pt, r};
	r = {21,  true,  -1,  20};                                                     m["tau_sv_sign"]    = {NT_distr_tau_sv_sign, r};

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

static bool NT_channel_mu_sel(ObjSystematics sys)
	{
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
	}

static bool NT_channel_mu_sel_ss(ObjSystematics sys)
	{
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
	}

static bool NT_channel_mu_sel_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_mu_sel(sys);
	return sel ?  NT_event_taus_sv_sign[0] > 3. : false;
	}

static bool NT_channel_mu_sel_ss_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_mu_sel_ss(sys);
	return sel ?  NT_event_taus_sv_sign[0] > 3. : false;
	}

static bool NT_channel_el_sel(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_JESDown;
	else if (sys == TESUp)     relevant_selection_stage = NT_selection_stage_TESUp  ;
	else if (sys == TESDown)   relevant_selection_stage = NT_selection_stage_TESDown;
	else relevant_selection_stage = NT_selection_stage;
	return relevant_selection_stage == 19 || relevant_selection_stage == 17;
	}

static bool NT_channel_el_sel_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_JESDown;
	else if (sys == TESUp)     relevant_selection_stage = NT_selection_stage_TESUp  ;
	else if (sys == TESDown)   relevant_selection_stage = NT_selection_stage_TESDown;
	else relevant_selection_stage = NT_selection_stage;
	return relevant_selection_stage == 18 || relevant_selection_stage == 16;
	}

// old stage2 presel!! from xsec measurement
static bool NT_channel_el_old_presel(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	//if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage;
	//else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_JERUp  ;
	//else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_JERDown;
	//else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_JESUp  ;
	//else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_JESDown;
	//else if (sys == TESUp)     relevant_selection_stage = NT_selection_stage_TESUp  ;
	//else if (sys == TESDown)   relevant_selection_stage = NT_selection_stage_TESDown;
	relevant_selection_stage = NT_selection_stage_presel;
	return (relevant_selection_stage == 19 || relevant_selection_stage == 17);
	}

static bool NT_channel_el_old_presel_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	relevant_selection_stage = NT_selection_stage_presel;
	return (relevant_selection_stage == 18 || relevant_selection_stage == 16); // || relevant_selection_stage == 15);
	}

static bool NT_channel_mu_old_presel(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	relevant_selection_stage = NT_selection_stage_presel;
	//return relevant_selection_stage == 9;
	return (relevant_selection_stage == 9 || relevant_selection_stage == 7);
	}

static bool NT_channel_mu_old_presel_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	relevant_selection_stage = NT_selection_stage_presel;
	return (relevant_selection_stage == 8 || relevant_selection_stage == 6);
	}


static bool NT_channel_el_sel_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_el_sel(sys);
	return sel ?  NT_event_taus_sv_sign[0] > 3. : false;
	}

static bool NT_channel_el_sel_ss_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_el_sel_ss(sys);
	return sel ?  NT_event_taus_sv_sign[0] > 3. : false;
	}

// union os mu_sel and el_sel
static bool NT_channel_lep_sel(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_JESDown;
	else if (sys == TESUp)     relevant_selection_stage = NT_selection_stage_TESUp  ;
	else if (sys == TESDown)   relevant_selection_stage = NT_selection_stage_TESDown;
	else relevant_selection_stage = NT_selection_stage;
	return relevant_selection_stage == 9 || relevant_selection_stage == 7 || relevant_selection_stage == 19 || relevant_selection_stage == 17;
	}

static bool NT_channel_lep_sel_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_JESDown;
	else if (sys == TESUp)     relevant_selection_stage = NT_selection_stage_TESUp  ;
	else if (sys == TESDown)   relevant_selection_stage = NT_selection_stage_TESDown;
	else relevant_selection_stage = NT_selection_stage;
	return relevant_selection_stage == 8 || relevant_selection_stage == 6 || relevant_selection_stage == 18 || relevant_selection_stage == 16;
	}

static bool NT_channel_lep_sel_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_lep_sel(sys);
	return sel ?  NT_event_taus_sv_sign[0] > 3. : false;
	}

static bool NT_channel_lep_sel_ss_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_lep_sel_ss(sys);
	// I use the if expression to be sure the vector NT_event_taus_sv_sign is not empty!
	//return sel && NT_event_taus_sv_sign[0] > 3.;
	return sel ?  NT_event_taus_sv_sign[0] > 3. : false;
	}


static bool NT_channel_tt_elmu(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage_em;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_em_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_em_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_em_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_em_JESDown;
	else relevant_selection_stage = NT_selection_stage_em;
	return relevant_selection_stage > 210 && relevant_selection_stage < 220;
	}

static bool NT_channel_tt_elmu_tight(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage_em;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_em_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_em_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_em_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_em_JESDown;
	else relevant_selection_stage = NT_selection_stage_em;
	return relevant_selection_stage == 215;
	}



static bool NT_channel_dy_mutau(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage_dy;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_dy_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_dy_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_dy_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_dy_JESDown;
	else if (sys == TESUp)     relevant_selection_stage = NT_selection_stage_dy_TESUp  ;
	else if (sys == TESDown)   relevant_selection_stage = NT_selection_stage_dy_TESDown;
	else relevant_selection_stage = NT_selection_stage_dy;

	double mT = NT_distr_Mt_lep_met(sys);

	return mT < 40 && (relevant_selection_stage == 135 || relevant_selection_stage == 134 || relevant_selection_stage == 125 || relevant_selection_stage == 124);
	}

static bool NT_channel_dy_eltau(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage_dy;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_dy_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_dy_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_dy_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_dy_JESDown;
	else if (sys == TESUp)     relevant_selection_stage = NT_selection_stage_dy_TESUp  ;
	else if (sys == TESDown)   relevant_selection_stage = NT_selection_stage_dy_TESDown;
	else relevant_selection_stage = NT_selection_stage_dy;

	double mT = NT_distr_Mt_lep_met(sys);

	return mT < 40 && (relevant_selection_stage == 235 || relevant_selection_stage == 234 || relevant_selection_stage == 225 || relevant_selection_stage == 224);
	}

static bool NT_channel_dy_mutau_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage_dy;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_dy_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_dy_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_dy_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_dy_JESDown;
	else if (sys == TESUp)     relevant_selection_stage = NT_selection_stage_dy_TESUp  ;
	else if (sys == TESDown)   relevant_selection_stage = NT_selection_stage_dy_TESDown;
	else relevant_selection_stage = NT_selection_stage_dy;

	double mT = NT_distr_Mt_lep_met(sys);

	return mT < 40 && (relevant_selection_stage == 133 || relevant_selection_stage == 132 || relevant_selection_stage == 123 || relevant_selection_stage == 122);
	}

static bool NT_channel_dy_eltau_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage_dy;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_dy_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_dy_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_dy_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_dy_JESDown;
	else if (sys == TESUp)     relevant_selection_stage = NT_selection_stage_dy_TESUp  ;
	else if (sys == TESDown)   relevant_selection_stage = NT_selection_stage_dy_TESDown;
	else relevant_selection_stage = NT_selection_stage_dy;

	double mT = NT_distr_Mt_lep_met(sys);

	return mT < 40 && (relevant_selection_stage == 233 || relevant_selection_stage == 232 || relevant_selection_stage == 223 || relevant_selection_stage == 222);
	}

static bool NT_channel_dy_mutau_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_dy_mutau(sys);
	// I use the if expression to be sure the vector NT_event_taus_sv_sign is not empty!
	return sel ?  NT_event_taus_sv_sign[0] > 3. : false;
	}
static bool NT_channel_dy_mutau_ss_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_dy_mutau_ss(sys);
	return sel ?  NT_event_taus_sv_sign[0] > 3. : false;
	}

static bool NT_channel_dy_eltau_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_dy_eltau(sys);
	return sel ?  NT_event_taus_sv_sign[0] > 3. : false;
	}
static bool NT_channel_dy_eltau_ss_tauSV3(ObjSystematics sys)
	{
	bool sel = NT_channel_dy_eltau_ss(sys);
	return sel ?  NT_event_taus_sv_sign[0] > 3. : false;
	}



static bool NT_channel_dy_elmu(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage_dy_elmu;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_dy_elmu_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_dy_elmu_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_dy_elmu_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_dy_elmu_JESDown;
	else relevant_selection_stage = NT_selection_stage_dy_elmu;
	return relevant_selection_stage == 105;
	}

static bool NT_channel_dy_elmu_ss(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage_dy_elmu;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_dy_elmu_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_dy_elmu_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_dy_elmu_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_dy_elmu_JESDown;
	else relevant_selection_stage = NT_selection_stage_dy_elmu;
	return relevant_selection_stage == 103;
	}


static bool NT_channel_dy_mumu(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage_dy_mumu;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_dy_mumu_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_dy_mumu_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_dy_mumu_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_dy_mumu_JESDown;
	else relevant_selection_stage = NT_selection_stage_dy_mumu;
	return relevant_selection_stage == 102 || relevant_selection_stage == 103 || relevant_selection_stage == 105;
	}

static bool NT_channel_dy_elel(ObjSystematics sys)
	{
	int relevant_selection_stage = 0;
	if      (sys == NOMINAL)   relevant_selection_stage = NT_selection_stage_dy_mumu;
	else if (sys == JERUp)     relevant_selection_stage = NT_selection_stage_dy_mumu_JERUp  ;
	else if (sys == JERDown)   relevant_selection_stage = NT_selection_stage_dy_mumu_JERDown;
	else if (sys == JESUp)     relevant_selection_stage = NT_selection_stage_dy_mumu_JESUp  ;
	else if (sys == JESDown)   relevant_selection_stage = NT_selection_stage_dy_mumu_JESDown;
	else relevant_selection_stage = NT_selection_stage_dy_mumu;
	return relevant_selection_stage == 112 || relevant_selection_stage == 113 || relevant_selection_stage == 115;
	}



#define _quick_set_chandef(m, chan_name, sel_weight_func) m[#chan_name] = {NT_channel_ ## chan_name, sel_weight_func}

/** \brief The initialization function for the `bool` functions of the known distributions in the stage2 output ntuples.

`T_known_defs_channels == map<const char*, _F_channel_sel>`

\return T_known_defs_channels
 */

T_known_defs_channels create_known_defs_channels_stage2()
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

	// old stage2 presel-s, from 2016 xsection measurement
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
is done with a simple integer in stage2, I could implement
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

static bool NT_genproc_tt_eltau3ch()
	{
	return NT_gen_proc_id == 42;
	}

// a short-hand macro

#define NT_genproc(procname, procID)         \
static bool NT_genproc_ ##procname(void)            \
	{                                  \
	return NT_gen_proc_id == (procID); \
	}

NT_genproc(tt_eltau1ch, 41)
NT_genproc(tt_mutau3ch, 32)
NT_genproc(tt_mutau1ch, 31)

NT_genproc(tt_ljb        , 24)
NT_genproc(tt_ljw        , 23)
NT_genproc(tt_ljo        , 22)
NT_genproc(tt_ljz        , 21)
NT_genproc(tt_taultauh   , 12)
NT_genproc(tt_taulj      , 11)
NT_genproc(tt_elmu       , 3)
NT_genproc(tt_ltaul      , 2)
NT_genproc(tt_taueltaumu , 1)
//NT_genproc(tt_other      , 0) // no "tt_other"! it is a catchall process, they are handled automatically

NT_genproc(dy_tautau , 1)

NT_genproc(wjets_tauh , 2)
NT_genproc(wjets_taul , 1)

NT_genproc(stop_eltau    , 20)
NT_genproc(stop_mutau    , 10)
NT_genproc(stop_lj    ,  2)
NT_genproc(stop_elmu  ,  1)

static bool NT_genproc_tt_eltau()
	{
	return NT_gen_proc_id > 40 && NT_gen_proc_id < 43;
	}

#define NT_genproc_range(procname, procID_min, procID_max)         \
static bool NT_genproc_ ##procname(void)          \
	{                                  \
	return NT_gen_proc_id > (procID_min) && NT_gen_proc_id < (procID_max); \
	}

NT_genproc_range(tt_mutau, 30, 33)
NT_genproc_range(tt_leptau, 30, 43)

NT_genproc_range(tt_lj, 20, 30)

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


/** \brief The initialization function for the known gen level processes in the stage2 output ntuples.

\return T_known_defs_procs
 */

T_known_defs_procs create_known_defs_procs_stage2()
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

T_known_MC_normalization_per_somename create_known_MC_normalization_per_syst_stage2()
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
//T_known_MC_normalization_per_somename known_normalization_per_syst_stage2 = create_known_MC_normalization_per_syst();
//T_known_MC_normalization_per_somename known_normalization_per_syst_stage2 = create_known_MC_normalization_per_syst_stage2();

T_known_MC_normalization_per_somename create_known_MC_normalization_per_proc_stage2()
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

//T_known_MC_normalization_per_somename known_normalization_per_proc_stage2 = create_known_MC_normalization_per_proc();


T_known_MC_normalization_per_somename create_known_MC_normalization_per_chan_stage2()
	{
	map<TString, double> m;

	return m;
	}

//T_known_MC_normalization_per_somename known_normalization_per_chan_stage2 = create_known_MC_normalization_per_chan_stage2();


int connect_ntuple_interface_stage2(TTree* NT_output_ttree)
	{
	#define OUTNTUPLE NT_output_ttree
	#define NTUPLE_INTERFACE_CONNECT
	#include "stage2_interface.h" // it runs a bunch of branch-connecting commands on TTree* with name OUTNTUPLE

	return 0;
	}

//connect_ntuple_interface_stage2 = &_connect_ntuple_interface_stage2;

