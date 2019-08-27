import os
from os import environ
from array import array
from collections import OrderedDict, namedtuple, defaultdict
import cProfile
import logging as Logging
import ctypes
from ctypes import CDLL, cdll, c_double, c_int, POINTER
from random import random as u_random

OLD_MINIAOD_JETS = False
DO_W_STITCHING = False
ALL_JETS = False
with_bSF = True

logging = Logging.getLogger("common")

logging.info('importing ROOT')
import ROOT

ROOT.gROOT.Reset()


## maybe roccors are in tt lib now
#print '''loading Rochester Corrections'''
##libpath = "roccor_wrapper_cc"
##libpath = "RoccoR_cc"
#libpath = "RoccoR_cc.so"
###cdll.LoadLibrary( libpath ) # TODO: if error -- break
##roccor_lib = CDLL( libpath )
##roccor_lib.wrapper_kScaleDT.restype         = c_double
##roccor_lib.wrapper_kScaleFromGenMC.restype  = c_double
##roccor_lib.wrapper_kScaleAndSmearMC.restype = c_double
##ROOT.gROOT.ProcessLine(".L RoccoR.cc++")
#ROOT.gSystem.Load(libpath)
## it crashes on exit for some root reason
#print '''Rochester Corrections loaded'''

#ROOT.gSystem.Unload("RoccoR_cc")
#print "test:2", roccors.kScaleDT(1, 40., 0.1, 0.3, 0, 0)

# the lib is needed for BTagCalibrator and Recoil corrections
# TODO: somehow these 2 CMSSW classes should be acceptable from pyROOT on its' own without the whole lib
ROOT.gSystem.Load("libUserCodettbar-leptons-80X.so")

print '''loaded all libraries'''



##ROOT.gSystem.Load("RoccoR_cc")
## -- trying to add it into ttbar lib
##roccors = ROOT.roccor_wrapper # wrapper does not work somehow
#roccors = ROOT.RoccoR("rcdata.2016.v3")
### works as roccors.kScaleDT(1, 40., 0.1, 0.3, 0, 0)
#print "rochcor test:", roccors.kScaleDT(1, 40., 0.1, 0.3, 0, 0)



from ROOT import TFile, TTree, TH1D, TH2D, TLorentzVector, TVector3, gROOT, gSystem, TCanvas, TGraphAsymmErrors, TMath, TString
from ROOT.Math import LorentzVector

# the names for the positions of renorm refact weights
from gen_proc_defs import MUf_nom_MUr_nom  , MUf_up_MUr_nom   , MUf_down_MUr_nom , MUf_nom_MUr_up   , MUf_up_MUr_up    , MUf_down_MUr_up  , MUf_nom_MUr_down , MUf_up_MUr_down  , MUf_down_MUr_down

'''
MUf_nom_MUr_nom    = 0
MUf_up_MUr_nom     = 1
MUf_down_MUr_nom   = 2
MUf_nom_MUr_up     = 3
MUf_up_MUr_up      = 4
MUf_down_MUr_up    = 5
MUf_nom_MUr_down   = 6
MUf_up_MUr_down    = 7
MUf_down_MUr_down  = 8
'''

pileup_ratio_h2 = array('d',
[       0., 5.2880843860098, 1.9057428051882, 0.8279489845062, 1.0183017803649, 0.8886546873859, 0.4586617471559, 0.4516527021066,
 0.6156808676490, 0.1704361822954, 0.3242275168011, 0.5576231467578, 0.6113064296958, 0.6618982312954, 0.7238796620111, 0.7496036493902, 0.7527610638253,
 0.7469665061269, 0.7399984493388, 0.7465103664963, 0.7983735170584, 0.8590931105313, 0.9034039953181, 0.9130886924812, 0.9080208719211, 0.9319379163103,
 0.9829435013036, 1.0322224123557, 1.1140955233618, 1.2058248250755, 1.2824965710179, 1.4313360174361, 1.5303677831147, 1.6810938978350, 1.8448654681967,
 1.9861677547885, 2.1231190233093, 2.2767850875912, 2.3717805455775, 2.4839160504037, 2.5332424087905, 2.4972378057180, 2.5549035019904, 2.5646400146497,
 2.5977594311101, 2.5410596186181, 2.4380019788525, 2.4582931794916, 2.4394333130376, 2.4135104510863, 2.3435484251709, 2.3026709406522, 2.2808207974466,
 2.1519700764652, 2.0425342255892, 1.5440178702333, 0.8925931999325, 0.4286677365298, 0.2057304468250, 0.0757408709610, 0.0356223199915, 0.0133823865731,
 0.0044643816760, 0.0021957442680, 0.0006438366822, 0.0002663753765, 0.0001247116374, 0.0000712745971, 0.0000307860041, 0.0000294100598, 0.0000103247078,
 0.0000055513056, 0.0000033501883, 0.0000035220198, 0.0000009221242])

pileup_ratio_b = array('d',
[       0.,  1.1931990788,  1.1075569611,  1.0661905165,  1.6281619271,  1.5759491716,  1.1654388423,  1.9665149072,  6.4816307673,  4.6824471835,
  3.5057573726,  2.7367422100,  2.0880922033,  1.8309627522,  1.7165427917,  1.6325677435,  1.5679104982,  1.5226132395,  1.4786172115,  1.4187556193,  1.3584199443,
  1.2535044794,  1.1332899913,  0.9984288822,  0.8518945520,  0.7154925510,  0.5827665258,  0.4457781053,  0.3302472894,  0.2310463295,  0.1498402182,  0.0965442096,
  0.0567106928,  0.0327699725,  0.0182363853,  0.0096751297,  0.0050124552,  0.0026185972,  0.0013947431,  0.0008483666,  0.0006315445,  0.0005978998,  0.0007339426,
  0.0010207996,  0.0015749231,  0.0025230767,  0.0042221245,  0.0078659845,  0.0152193676,  0.0308807634,  0.0644886301,  0.1423880343,  0.3304052121,  0.7589089584,
  1.8143503956,  3.5544006370,  5.4397543208,  7.0034023639,  9.0337430924,  8.8675115583, 10.9147825813, 10.4253507840,  8.5070481287,  9.7647211573,  6.3458905766,
  5.5327398483,  5.2282218781,  5.8413138671,  4.8338755929,  8.7575484032,  5.8155542511,  5.9275685169,  6.8122980083, 13.7528845721,  6.9540203430,  ])

pileup_ratio_sum = array('d',
[       0., 2.7084899, 1.2387248, 0.8567540, 1.1319902, 1.0625620, 0.6788884, 0.6404915, 1.5813397, 1.2265823, 1.1225145, 1.1346217, 1.0804378, 1.0719238,
 1.0481945, 1.0210914, 1.0035636, 0.9938051, 0.9824541, 0.9712776, 0.9866336, 0.9979909, 1.0111960, 1.0147509, 1.0078850, 1.0150851, 1.0273812, 1.0179873, 1.0242233,
 1.0233836, 0.9961096, 1.0091713, 0.9729596, 0.9599715, 0.9457656, 0.9168015, 0.8878596, 0.8702436, 0.8374816, 0.8195456, 0.7897366, 0.7430977, 0.7321259, 0.7130387,
 0.7051140, 0.6768290, 0.6399811, 0.6383632, 0.6289537, 0.6205741, 0.6051458, 0.6053456, 0.6291184, 0.6658740, 0.8105650, 0.9697623, 1.1145130, 1.2538530, 1.5301977,
 1.4704201, 1.7955171, 1.7098770, 1.3936616, 1.5989832, 1.0389566, 0.9057558, 0.8558735, 0.9562222, 0.7912980, 1.4335911, 0.9519911, 0.9703263, 1.1151534, 2.2513064,
 1.1383523])



pileup_ratio = array('d', [
0.360609416811339, 0.910848525427002, 1.20629960507795, 0.965997726573782, 1.10708082813183, 1.14843491548622, 0.786526251164482, 0.490577792661333, 0.740680941110478,
0.884048630953726,
0.964813189764159, 1.07045369167689, 1.12497267309738, 1.17367530613108, 1.20239808206413, 1.20815108390021, 1.20049333094509, 1.18284686347315, 1.14408796655615,
1.0962284704313, 1.06549162803223, 1.05151011089581, 1.05159666626121, 1.05064452078328, 1.0491726301522, 1.05772537082991, 1.07279673875566, 1.0837536468865, 1.09536667397119,
1.10934472980173, 1.09375894592864, 1.08263679568271, 1.04289345879947, 0.9851490341672, 0.909983816540809, 0.821346330143864, 0.71704523475871, 0.609800913869359, 0.502935245638477,
0.405579825620816, 0.309696044611377, 0.228191137503131, 0.163380359253309, 0.113368437957202, 0.0772279997453792, 0.0508111733313502, 0.0319007262683943, 0.0200879459309245, 0.0122753366005436,
0.00739933885813127, 0.00437426967257811, 0.00260473545284139, 0.00157047254226743, 0.000969500595715493, 0.000733193118123283, 0.000669817107713128, 0.000728548958604492, 0.000934559691182011, 0.00133719688378802,
0.00186652283903214, 0.00314422244976771, 0.00406954793369611, 0.00467888840511915, 0.00505224284441512, 0.00562827194936864, 0.0055889504870752, 0.00522867039470319, 0.00450752163476433, 0.00395300774604375,
0.00330577167682956, 0.00308353042577215, 0.00277846504893301, 0.00223943190687725, 0.00196650068765464, 0.00184742734258922,])

## recalc from ntuple, basically the same
#pileup_ratio = array('d', [
#0.344887, 0.869219, 1.12271, 0.968119, 1.04695, 1.10773, 0.740941, 0.477038, 0.719406, 0.857546,
#0.938079, 1.04656, 1.09508, 1.14765, 1.17614, 1.18508, 1.17563, 1.16215, 1.12725, 1.08148,
#1.05394, 1.04048, 1.04329, 1.04534, 1.04798, 1.05541, 1.07543, 1.08567, 1.10311, 1.11874,
#1.10373, 1.09798, 1.05651, 1.00496, 0.931962, 0.842275, 0.736296, 0.626743, 0.520142, 0.419807,
#0.323103, 0.239115, 0.170803, 0.119757, 0.0821237, 0.0541623, 0.0338, 0.0215088, 0.0131677, 0.00806879,
#0.00477981, 0.00283188, 0.00173487, 0.00107583, 0.000821263, 0.000757651, 0.000829695, 0.00102146, 0.00152372, 0.00205202,
#0.00372623, 0.00458362, 0.00632652, 0.00643546, 0.00646819, 0.00677855, 0.00618487, 0.00519075, 0.00488287, 0.00433706,
#0.00335919, 0.00359263, 0.00266798, 0.00270629, 0.00261116,])


pileup_ratio_up = array('d', [0.351377216124927, 0.717199649125846, 1.14121536968772, 0.84885826611733, 1.00700929402897, 1.03428595270903, 0.717444379696992, 0.344078389355127, 0.499570875027422,
0.606614916257104, 0.632584599390169, 0.731450949466174, 0.827511723989754, 0.910682115553867, 0.960170981598162, 0.988896170761361, 1.02468865580207, 1.05296667126403, 1.05112033565679,
1.0269129153969, 1.00548641752714, 0.998316130432865, 1.01492587998551, 1.03753749807849, 1.05742218946485, 1.08503978097083, 1.12134132247053, 1.15585339474274, 1.19214399856171,
1.23308400947467, 1.24528804633732, 1.26786364716917, 1.26101551498967, 1.23297806722714, 1.18042533075471, 1.10534683838101, 1.00275591661645, 0.889094305531985, 0.768791254270252,
0.655054015673457, 0.533361034358457, 0.423095146361996, 0.329177839117034, 0.250352385505809, 0.188377378855567, 0.137852651411779, 0.0968577167707531, 0.0686240187247059, 0.0473889635126706,
0.0323695027438475, 0.0216752397914914, 0.0145119352923332, 0.00961177893634792, 0.00615582219138384, 0.00430085627914427, 0.00305735512896403, 0.00223567790438986, 0.00189369737638594, 0.00199585978316291,
0.00236236592656064, 0.00372472999463276, 0.00474687312579969, 0.00549508151576102, 0.00603023110946686, 0.0068545111910253, 0.00695838760530896, 0.00666224781277046, 0.00588243140681038, 0.00528714370892014,
0.00453424615273565, 0.00433985030329723, 0.00401493171035719, 0.00332436608713241, 0.00300063798808221, 0.00289925128977536,])

pileup_ratio_down = array('d', [0.37361294640242, 1.1627791004568, 1.26890787896295, 1.10266790442705, 1.23456697093644, 1.26278991594152, 0.909648777562084, 0.759569490571151, 1.09035651921682,
1.34530547603283, 1.48713160105, 1.52535976889483, 1.49730550773404, 1.49792998045778, 1.49767851097519, 1.44431045398336, 1.3681909492045, 1.29912252494785, 1.2274279217797,
1.16525969099909, 1.12531044676724, 1.09094501417685, 1.06405434433422, 1.03997120824565, 1.0185716022098, 1.00560949501652, 0.997570939806059, 0.985543761409897, 0.972557804582185,
0.957832827239337, 0.9139572640153, 0.872252387173971, 0.808388185417578, 0.733817960498049, 0.650440963845892, 0.561688505024782, 0.466564380334112, 0.374428618658619, 0.28845274688129,
0.214909665968644, 0.149991974352384, 0.100014138338029, 0.0642260884603397, 0.0396553405911344, 0.0238687936736627, 0.0137921542898078, 0.00756854010632403, 0.00415483516246187, 0.00221776872027937,
0.00118249725637452, 0.000641889697310868, 0.000383647166012176, 0.000273637590071334, 0.000242902582071058, 0.000291239677209452, 0.000394091114279828, 0.000542541231466254, 0.000771067920964491, 0.00113596447675107,
0.00158061353194779, 0.00261959852500539, 0.00331800452823827, 0.00372426930370732, 0.00392086545082614, 0.00425479965493548, 0.00411256966391362, 0.00374240422174387, 0.00313603438166934, 0.00267155793176928,
0.00216878198028599, 0.00196249821290853, 0.00171433839159669, 0.00133866519755926, 0.00113810604240254, 0.00103447940224886,])

















pileup_ratio_ele = array('d', [
   0.413231   ,    1.01701    ,    1.19502     ,   0.883906   ,    1.05852    ,    1.11823    ,    0.789439   ,    0.515477   ,    0.81338    ,    0.990148   ,
   1.0919     ,    1.21784    ,    1.28268     ,   1.33936    ,    1.37267    ,    1.38001    ,    1.37224    ,    1.35253    ,    1.30805    ,    1.25303    ,
   1.21761    ,    1.20085    ,    1.1987      ,   1.19257    ,    1.1807     ,    1.17079    ,    1.15238    ,    1.10667    ,    1.03375    ,    0.935086   ,
   0.793376   ,    0.65125    ,    0.502727    ,   0.369298   ,    0.25859    ,    0.173207   ,    0.110361   ,    0.0677957  ,    0.0403186  ,    0.0236369  ,
   0.0133546  ,    0.00746494 ,    0.00417626  ,   0.00233773 ,    0.0013288  ,    0.000757718,    0.000432788,    0.000266239,    0.000177605,    0.000137241,
   0.000125696,    0.000137018,    0.000167806 ,   0.000215108,    0.000313214,    0.000464376,    0.000669855,    0.000981399,    0.00148275 ,    0.00211313 ,
   0.0035872  ,    0.00465614 ,    0.005359    ,   0.00578897 ,    0.00645001 ,    0.00640537 ,    0.00599263 ,    0.00516618 ,    0.00453067 ,    0.00378886 ,
   0.00353415 ,    0.00318451 ,    0.0025667   ,   0.00225388 ,    0.00211741 ,])

pileup_ratio_up_ele = array('d', [
   0.402668    ,   0.803377   ,    1.15963    ,    0.764147   ,    0.966328    ,   0.995159   ,    0.71563    ,    0.354304   ,   0.541943   ,    0.674778   ,
   0.713035    ,   0.830366   ,    0.942616   ,    1.03882    ,    1.09589     ,   1.12909    ,    1.17068    ,    1.20376    ,   1.20191    ,    1.17404    ,
   1.14928     ,   1.14083    ,    1.15906    ,    1.18279    ,    1.20082     ,   1.22277    ,    1.24559    ,    1.25129    ,   1.23607    ,    1.19534    ,
   1.09539     ,   0.978694   ,    0.82546    ,    0.662451   ,    0.50547     ,   0.367764   ,    0.25369    ,    0.168007   ,   0.10706    ,    0.0667404  ,
   0.0397874   ,   0.0233291  ,    0.0136533  ,    0.00799737 ,    0.00476279  ,   0.00284044 ,    0.00167744 ,    0.00103389 ,   0.000648432,    0.000427764,
   0.000303899 ,   0.000247672,    0.000236803,    0.000258026,    0.000345092 ,   0.000494341,    0.000708128,    0.00104444 ,   0.00159927 ,    0.00231779 ,
   0.00400894  ,   0.00530831 ,    0.00623822 ,    0.00688571 ,    0.00784455  ,   0.00797042 ,    0.00763388 ,    0.00674129 ,   0.00605947 ,    0.00519674 ,
   0.00497399  ,   0.00460162 ,    0.00381017 ,    0.00343914 ,    0.00332295  ,])

pileup_ratio_down_ele = array('d', [
   0.428107   ,   1.29388    ,    1.22078   ,    1.02596    ,    1.1769     ,    1.24377    ,    0.921862   ,    0.814769   ,    1.20901   ,    1.51527   ,
   1.68838    ,   1.73792    ,    1.70826   ,    1.70984    ,    1.71038    ,    1.65067    ,    1.56442    ,    1.48535    ,    1.40303   ,    1.33164   ,
   1.28514    ,   1.24342    ,    1.20714   ,    1.16839    ,    1.12262    ,    1.06993    ,    0.999693   ,    0.900043   ,    0.778486  ,    0.644942  ,
   0.497564   ,   0.37052    ,    0.259917  ,    0.174109   ,    0.111585   ,    0.0687061  ,    0.0404941  ,    0.0232033  ,    0.0129877 ,    0.00721863,
   0.00388086 ,   0.00206418 ,    0.00109735,    0.000585006,    0.000321242,    0.000184087,    0.000114353,    8.57172e-5 ,    7.68135e-5,    8.09537e-5,
   9.42381e-5 ,   0.000118387,    0.0001548 ,    0.000202628,    0.000294603,    0.000431519,    0.00061181 ,    0.000878668,    0.00129927,    0.0018102 ,
   0.00300153 ,   0.00380243 ,    0.0042683 ,    0.00449375 ,    0.00487654 ,    0.00471355 ,    0.0042893  ,    0.00359432 ,    0.00306198,    0.00248572,
   0.0022493  ,   0.00196487 ,    0.0015343 ,    0.00130443 ,    0.00118566 ,])















from module_leptons import lepton_muon_SF, lepton_muon_trigger_SF, lepton_electron_SF, lepton_electron_trigger_SF

if with_bSF:
    from support_btagging_sf import calc_btag_sf_weight, bEff_histo_b, bEff_histo_c, bEff_histo_udsg
    from support_btagging_sf import h_control_btag_eff_b, h_control_btag_eff_c, h_control_btag_eff_udsg, h_control_btag_weight_b, h_control_btag_weight_c, h_control_btag_weight_udsg, h_control_btag_weight_notag_b, h_control_btag_weight_notag_c, h_control_btag_weight_notag_udsg

def top_pT_SF(x):
    # the SF function is SF(x)=exp(a+bx)
    # where x is pT of the top quark (at generation?)
    # sqrt(s)         channel             a             b
    # 7 TeV         all combined         0.199         -0.00166
    # 7 TeV         l+jets              0.174         -0.00137
    # 7 TeV         dilepton            0.222         -0.00197
    # 8 TeV         all combined         0.156         -0.00137
    # 8 TeV         l+jets               0.159         -0.00141
    # 8 TeV         dilepton             0.148         -0.00129
    # 13 TeV        all combined        0.0615        -0.0005
    # -- taking all combined 13 TeV
    a = 0.0615
    b = -0.0005
    return TMath.Exp(a + b*x)

def ttbar_pT_SF(t_pt, tbar_pt):
    return TMath.Sqrt(top_pT_SF(t_pt) * top_pT_SF(tbar_pt))

def transverse_mass(v1, v2):
    return TMath.Sqrt(2*v1.pt()*v2.pt()*(1 - TMath.Cos(v1.phi() - v2.phi())))

def transverse_mass_pts(v1_x, v1_y, v2_x, v2_y):
    v1v2 = TMath.Sqrt((v1_x*v1_x + v1_y*v1_y)*(v2_x*v2_x + v2_y*v2_y))
    return TMath.Sqrt(2*(v1v2 - (v1_x*v2_x + v1_y*v2_y)))

def transverse_cos(v1, v2):
    t_cos = (v1.Px()*v2.Px() + v1.Py()*v2.Py()) / TMath.Sqrt((v1.Px()*v1.Px() + v1.Py()*v1.Py())* (v2.Px()*v2.Px() + v2.Py()*v2.Py()))
    return t_cos

def calc_lj_var(ev, light_jets, b_jets, save_all_permutations=False, isMC=False):
    closest_pair_gens = (0, 0)
    closest_b_gen = 0
    if len(b_jets) == 0 or len(light_jets) < 2: return 5000., 5000., 5000., (closest_pair_gens, closest_b_gen), []
    # (not doing it now) loop over light jets -- check their mass
    # loop over light jets, check mass of their pairs to be close to 80
    # find the closest vector
    # then loop over b jets finding the combination with mass closest to 173

    # light jets close to W
    dist_W = 99999.
    ## closest_vector
    #for j, mult in light_jets:
    #    new_dist = abs(j.mass() * mult - 80) # DANGER: the LorentzVector is used, .M() is spacial magnitude
    #    if new_dist < dist_W:
    #        dist_W = new_dist
    #        closest_to_W = j * mult

    # save [(mW, mt)] of all permutations if requested
    all_masses = []

    # pairs of light jets
    light_jet_pairs = []
    for i in range(len(light_jets)):
      for u in range(i):
        ji, multi, _, _, _, _, _ = light_jets[i]
        ju, multu, _, _, _, _, _ = light_jets[u]
        pair = ji * multi + ju * multu
        if save_all_permutations:
            light_jet_pairs.append(pair)
        new_dist = abs(pair.mass() - 80)
        if new_dist < dist_W:
            dist_W = new_dist
            closest_to_W = pair
            if isMC:
                closest_pair_gens = (ev.jet_matching_gen[light_jets[i][6]], ev.jet_matching_gen[light_jets[u][6]])

    # closest to 173
    dist_t = 99999.
    for j, mult, _, _, _, _, jet_index in b_jets:
        b_jet = j * mult
        pair = b_jet + closest_to_W
        if save_all_permutations:
            for cand_W in light_jet_pairs:
                cand_t = cand_W + b_jet
                all_masses.append((cand_W.mass(), cand_t.mass()))
        new_dist = abs(pair.mass() - 173)
        if new_dist < dist_t:
            dist_t = new_dist
            closest_to_t = pair
            if isMC:
                closest_b_gen = ev.jet_matching_gen[jet_index]

    return TMath.Sqrt(dist_W*dist_W + dist_t*dist_t), closest_to_W.mass(), closest_to_t.mass(), (closest_pair_gens, closest_b_gen), all_masses


#def PFTau_FlightLength_significance(TVector3 pv,TMatrixTSym<double> PVcov, TVector3 sv, TMatrixTSym<double> SVcov ){
def PFTau_FlightLength_significance(pv,  PVcov, sv, SVcov):
   run_test = False # option to print contents of some of the structures during calculation

   SVPV = sv - pv
   FD = ROOT.TVectorF()
   FD.ResizeTo(3);
   #FD(0) = SVPV.X();
   #FD(1) = SVPV.Y();
   #FD(2) = SVPV.Z();
   FD.SetElements(array('f', [SVPV.X(), SVPV.Y(), SVPV.Z()]))

   # input covs are
   # ROOT.Math.SMatrix(float, 3, 3, ROOT.Math.MatRepSym(float, 3) )

   #TMatrixT<double> PVcv;
   PVcv = ROOT.TMatrixT(float)()
   PVcv.ResizeTo(3,3);
   #TMatrixT<double> SVcv;
   SVcv = ROOT.TMatrixT(float)()
   SVcv.ResizeTo(3,3);
   #for(int nr =0; nr<PVcov.GetNrows(); nr++){
   #  for(int nc =0; nc<PVcov.GetNcols(); nc++){
   #    PVcv(nr,nc) = PVcov(nr,nc);
   #  }
   #}
   #for(int nr =0; nr<SVcov.GetNrows(); nr++){
   #  for(int nc =0; nc<SVcov.GetNcols(); nc++){
   #    SVcv(nr,nc) = SVcov(nr,nc);
   #  }
   #}
   # assume rows -- first index, coloumns -- second
   for nr in range(3):
      for nc in range(3):
         PVcv[nr][nc] = PVcov(nr, nc)
         SVcv[nr][nc] = SVcov(nr, nc)

   #TMatrixT<double> SVPVMatrix(3,1);
   #SVPVMatrix = ROOT.TMatrixT(float)(3,1) # Error in <operator*=(const TMatrixT &)>: source matrix has wrong shape
   SVPVMatrix = ROOT.TMatrixT(float)(3,3)
   #for(int i=0; i<SVPVMatrix.GetNrows();i++){
   #  SVPVMatrix(i,0)=FD(i);
   #}
   for i in range(SVPVMatrix.GetNrows()):
       SVPVMatrix[i][0] = FD(i)
       SVPVMatrix[i][1] = 0
       SVPVMatrix[i][2] = 0

   #TMatrixT<double> SVPVMatrixT=SVPVMatrix;
   SVPVMatrixT = SVPVMatrix.Clone()
   SVPVMatrixT.T()

   if run_test:
      SVcv.Print()
      PVcv.Print()
   SVcv += PVcv
   PVSVcv = SVcv
   if run_test:
      SVcv.Print()
      PVSVcv.Print()

   if run_test:
       SVPVMatrixT.Print()
       PVSVcv     .Print()
       SVPVMatrix .Print()

   #TMatrixT<double> lambda2 = SVPVMatrixT*(SVcv + PVcv)*SVPVMatrix;
   #lambda2 = SVPVMatrixT*(SVcv + PVcv)*SVPVMatrix
   #lambda2 = SVPVMatrixT*PVSVcv*SVPVMatrix
   # doc says "Compute target = target * source inplace"
   # https://root.cern.ch/doc/v608/classTMatrixT.html
   lambda2 = SVPVMatrixT
   lambda2 *= PVSVcv
   lambda2 *= SVPVMatrix
   if run_test:
       lambda2.Print()

   sigmaabs = TMath.Sqrt(lambda2(0,0))/SVPV.Mag()
   sign = SVPV.Mag()/sigmaabs

   return SVPV.Mag(), sigmaabs, sign


control_counters = TH1D("control_counters", "", 500, 0, 500)

# no data types/protocols in ROOT -- looping has to be done manually
def full_loop(tree, dtag, lumi_bcdef, lumi_gh, logger, channels_to_select):
    '''full_loop(tree, dtag)

    TTree tree
    dtag string
    '''

    ratio_bcdef = lumi_bcdef / (lumi_bcdef + lumi_gh)
    ratio_gh    = lumi_gh / (lumi_bcdef + lumi_gh)

    logger.write('dtag=%s\n' % dtag)
    logger.write('lumi_bcdef=%f lumi_gh=%f\n' % (lumi_bcdef, lumi_gh))

    isMC = 'MC' in dtag
    #save_control = False
    save_weights = True and isMC
    aMCatNLO = 'amcatnlo' in dtag
    isTT = 'TT' in dtag

    # fix the naming in dtag-dset info files
    tt_systematic_datasets = {'fsrup': 'FSRUp', 'fsrdown': 'FSRDown',
        'TuneCUETP8M2T4down': 'TuneCUETP8M2T4Down', 'TuneCUETP8M2T4up': 'TuneCUETP8M2T4Up',
        'isrup': 'ISRUp', 'isrdown': 'ISRDown',
        'hdampUP': 'HDAMPUp', 'hdampDOWN': 'HDAMPDown',
        'GluonMoveCRTune': 'GluonMoveCRTuneUp', 'QCDbasedCRTune': 'QCDbasedCRTuneUp'}

    def which_sys(dtag, systematics=tt_systematic_datasets):
        # if the dtag name is already fixed return it as is
        for sys_name in systematics.values():
            if sys_name in dtag:
                return sys_name
        # else try to translate the old name
        for sys_name in systematics.keys():
            if sys_name in dtag:
                return systematics[sys_name]
        return None

    isTT_systematic = isTT and which_sys(dtag)

    isSTop = 'SingleT' in dtag or 'tchannel' in dtag or 'schannel' in dtag
    isSTopTSchannels = 'tchannel' in dtag or 'schannel' in dtag
    isDY = 'DY' in dtag
    isWJets = 'WJet' in dtag or 'W1Jet' in dtag or 'W2Jet' in dtag or 'W3Jet' in dtag or 'W4Jet' in dtag
    isWJetsInclusive = 'WJet' in dtag
    isQCD = 'QCD' in dtag
    isDibosons = 'WW' in dtag or 'ZZ' in dtag or 'WZ' in dtag

    logger.write(' '.join(name + '=' + str(setting) for name, setting in
        [('isMC', isMC), ('save_weights', save_weights), ('aMCatNLO', aMCatNLO), ('isTT', isTT), ('isTT_systematic', isTT_systematic), ('isSTop', isSTop), ('isSTopTSchannels', isSTopTSchannels), ('isDY', isDY), ('isWJets', isWJets), ('isQCD', isQCD), ('isDibosons', isDibosons)]) + '\n')


    logging.info("load root_funcs")
    ROOT.gROOT.ProcessLine(".L /exper-sw/cmst3/cmssw/users/olek/CMSSW_8_0_26_patch1/src/UserCode/NtuplerAnalyzer/root_funcs.C+") # TODO: change absolute path to relative

    # Recoil corrections
    doRecoilCorrections = isWJets or isDY # TODO: check if it is needed for DY
    if doRecoilCorrections:
        logging.info("will use Recoil Corrections")
        ROOT.gROOT.ProcessLine(".L /exper-sw/cmst3/cmssw/users/olek/CMSSW_8_0_26_patch1/src/UserCode/NtuplerAnalyzer/recoil_corrections.C+") # TODO: change absolute path to relative
        #recoil_corrections_data_file = TString("/HTT-utilities/RecoilCorrections/data/TypeIPFMET_2016BCD.root")
        #recoilPFMetCorrector = ROOT.RecoilCorrector(recoil_corrections_data_file);
        #ROOT.BTagCalibrationReader


    # Z pt mass weight
    # std::string zPtMassWeights_filename = std::string(std::getenv("CMSSW_BASE")) + "/src/UserCode/zpt_weights_2016.root";
    # TFile* zPtMassWeights_file  = TFile::Open(zPtMassWeights_filename.c_str());
    # TH2D*  zPtMassWeights_histo = (TH2D*) zPtMassWeights_file->Get("zptmass_histo");
    # TH2D*  zPtMassWeights_histo_err = (TH2D*) zPtMassWeights_file->Get("zptmass_histo_err");
    # 
    # float zPtMass_weight(float genMass, float genPt)
    #         {
    #         return zPtMassWeights_histo->GetBinContent(zPtMassWeights_histo->GetXaxis()->FindBin(genMass), zPtMassWeights_histo->GetYaxis()->FindBin(genPt));
    #         }

    if isDY:
        logging.info("loading Z pt mass weights")
        zPtMass_filename = environ['CMSSW_BASE'] + '/src/UserCode/zpt_weights_2016.root'
        zPtMassWeights_file  = TFile(zPtMass_filename)
        zPtMassWeights_file.Print()
        zPtMassWeights_histo     = zPtMassWeights_file.Get("zptmass_histo")
        zPtMassWeights_histo_err = zPtMassWeights_file.Get("zptmass_histo_err")

        def zPtMass_weight(genMass, genPt):
            return zPtMassWeights_histo.GetBinContent(zPtMassWeights_histo.GetXaxis().FindBin(genMass), zPtMassWeights_histo.GetYaxis().FindBin(genPt))


    control_hs = OrderedDict([
    ('weight_pu',     TH1D("weight_pu", "", 50, 0, 2)),
    ('weight_pu_el', TH1D("weight_pu_el", "", 50, 0, 2)),
    ('weight_pu_mu', TH1D("weight_pu_mu", "", 50, 0, 2)),

    ('weight_pu_mu_up',     TH1D("weight_pu_up", "", 50, 0, 2)),
    ('weight_pu_mu_dn',     TH1D("weight_pu_dn", "", 50, 0, 2)),
    ('weight_pu_el_up', TH1D("weight_pu_ele_up", "", 50, 0, 2)),
    ('weight_pu_el_dn', TH1D("weight_pu_ele_dn", "", 50, 0, 2)),

    ('weight_pu_sum', TH1D("weight_pu_sum", "", 50, 0, 2)),
    ('weight_pu_b',   TH1D("weight_pu_b", "", 50, 0, 2)),
    ('weight_pu_h2',  TH1D("weight_pu_h2", "", 50, 0, 2)),
    ('weight_top_pt', TH1D("weight_top_pt", "", 50, 0, 2)),

    #('roccor_factor', TH1D("roccor_factor", "", 50, 0, 2)),

    ('weights_gen_weight_too',         TH1D("weights_gen_weight_too",         "", 50, 0, 2)),
    ('weights_gen_weight_norm',        TH1D("weights_gen_weight_norm",        "", 50, 0, 2)),
    ('weights_gen_weight_average',     TH1D("weights_gen_weight_average",     "", 50, 0, 2)),
    ('weights_gen_weight_alphasUp',    TH1D("weights_gen_weight_alphasUp",    "", 50, 0, 2)),
    ('weights_gen_weight_alphasDown',  TH1D("weights_gen_weight_alphasDown",  "", 50, 0, 2)),
    ('weights_gen_weight_centralFrag', TH1D("weights_gen_weight_centralFrag", "", 50, 0, 2)),
    ('weights_gen_weight_Peterson',    TH1D("weights_gen_weight_Peterson",    "", 50, 0, 2)),
    ('weights_gen_weight_FragUp',      TH1D("weights_FragUp",   "", 50, 0, 2)),
    ('weights_gen_weight_FragDown',    TH1D("weights_FragDown", "", 50, 0, 2)),
    ('weights_gen_weight_semilepbrUp',      TH1D("weights_semilepbrUp",   "", 50, 0, 2)),
    ('weights_gen_weight_semilepbrDown',    TH1D("weights_semilepbrDown", "", 50, 0, 2)),

    ('AlphaSUp',       TH1D("weight_AlphaSUp",       "", 50, 0, 2)),
    ('AlphaSDown',     TH1D("weight_AlphaSDown",     "", 50, 0, 2)),
    ('FragUp',         TH1D("weight_FragUp",         "", 50, 0, 2)),
    ('FragDown',       TH1D("weight_FragDown",       "", 50, 0, 2)),
    ('SemilepBRUp',    TH1D("weight_SemilepBRUp",         "", 50, 0, 2)),
    ('SemilepBRDown',  TH1D("weight_SemilepBRDown",       "", 50, 0, 2)),
    ('PetersonUp',     TH1D("weight_PetersonUp",         "", 50, 0, 2)),
    ('PetersonDown',   TH1D("weight_PetersonDown",       "", 50, 0, 2)),
    ('MrUp',      TH1D("weight_MrUp",         "", 50, 0, 2)),
    ('MrDown',    TH1D("weight_MrDown",       "", 50, 0, 2)),
    ('MfUp',      TH1D("weight_MfUp",         "", 50, 0, 2)),
    ('MfDown',    TH1D("weight_MfDown",       "", 50, 0, 2)),
    ('MfrUp',     TH1D("weight_MfrUp",        "", 50, 0, 2)),
    ('MfrDown',   TH1D("weight_MfrDown",      "", 50, 0, 2)),

    ('weights_gen_weight_nom'   , TH1D('weights_gen_weight_nom'  , "", 50, 0, 2)),
    ('weights_gen_weight_f_rUp' , TH1D('weights_gen_weight_f_rUp', "", 50, 0, 2)),
    ('weights_gen_weight_f_rDn' , TH1D('weights_gen_weight_f_rDn', "", 50, 0, 2)),
    ('weights_gen_weight_fUp_r' , TH1D('weights_gen_weight_fUp_r', "", 50, 0, 2)),
    ('weights_gen_weight_fDn_r' , TH1D('weights_gen_weight_fDn_r', "", 50, 0, 2)),
    ('weights_gen_weight_frUp'  , TH1D('weights_gen_weight_frUp' , "", 50, 0, 2)),
    ('weights_gen_weight_frDn'  , TH1D('weights_gen_weight_frDn' , "", 50, 0, 2)),

    ('weight_z_mass_pt', TH1D("weight_z_mass_pt", "", 50, 0, 2)),
    ('weight_bSF',       TH1D("weight_bSF", "", 50, 0, 2)),

    ('weight_mu_trk_bcdef', TH1D("weight_mu_trk_bcdef", "", 50, 0, 2)),
    ('weight_mu_trk_bcdef_vtx', TH1D("weight_mu_trk_bcdef_vtx", "", 50, 0, 2)),
    ('weight_mu_trk_bcdef_vtx_gen', TH1D("weight_mu_trk_bcdef_vtx_gen", "", 50, 0, 2)),
    ('weight_mu_id_bcdef' , TH1D("weight_mu_id_bcdef", "", 50, 0, 2)),
    ('weight_mu_iso_bcdef', TH1D("weight_mu_iso_bcdef", "", 50, 0, 2)),
    ('weight_mu_trg_bcdef', TH1D("weight_mu_trg_bcdef", "", 50, 0, 2)),
    ('weight_mu_all_bcdef', TH1D("weight_mu_all_bcdef", "", 50, 0, 2)),

    ('weight_mu_trk_gh', TH1D("weight_mu_trk_gh", "", 50, 0, 2)),
    ('weight_mu_trk_gh_vtx', TH1D("weight_mu_trk_gh_vtx", "", 50, 0, 2)),
    ('weight_mu_trk_gh_vtx_gen', TH1D("weight_mu_trk_gh_vtx_gen", "", 50, 0, 2)),
    ('weight_mu_id_gh' , TH1D("weight_mu_id_gh", "", 50, 0, 2)),
    ('weight_mu_iso_gh', TH1D("weight_mu_iso_gh", "", 50, 0, 2)),
    ('weight_mu_trg_gh', TH1D("weight_mu_trg_gh", "", 50, 0, 2)),
    ('weight_mu_all_gh', TH1D("weight_mu_all_gh", "", 50, 0, 2)),

    ('weight_mu_bSF', TH1D("weight_mu_bSF", "", 50, 0, 2)),
    ('weight_mu_bSF_up', TH1D("weight_mu_bSF_up", "", 50, 0, 2)),
    ('weight_mu_bSF_down', TH1D("weight_mu_bSF_down", "", 50, 0, 2)),

    ('weight_el_trk', TH1D("weight_el_trk", "", 50, 0, 2)),
    ('weight_el_idd', TH1D("weight_el_idd", "", 50, 0, 2)),
    ('weight_el_trg', TH1D("weight_el_trg", "", 50, 0, 2)),
    ('weight_el_all', TH1D("weight_el_all", "", 50, 0, 2)),

    ('weight_el_bSF', TH1D("weight_el_bSF", "", 50, 0, 2)),
    ('weight_el_bSF_up', TH1D("weight_el_bSF_up", "", 50, 0, 2)),
    ('weight_el_bSF_down', TH1D("weight_el_bSF_down", "", 50, 0, 2)),
    ])

    if isTT:
        control_hs.update({'PDFCT14n%dUp' % i: TH1D("weight_PDFCT14n%dUp" % i, "", 50, 0, 2) for i in range(58) })

    # strange, getting PyROOT_NoneObjects from these after output
    for _, h in control_hs.items():
        h.SetDirectory(0)

    #channels = {'el': ['foo'], 'mu': ['foo'], 'mujets': ['foo'],
    #'mujets_b': ['foo'], 'taumutauh': ['foo'], 'taumutauh_antiMt_pretau_allb': ['foo'], 'taumutauh_antiMt_pretau': ['foo'], 'taumutauh_antiMt': ['foo'], 'taumutauh_antiMt_OS': ['foo']}
    #channels = {'presel': ['foo'], 'el': ['foo'], 'mu': ['foo']}
    # TODO: I actually need:
    #    same set of selections for el and mu
    #    which is preselection (no tau requirement), selection of tau, bins of inside/outside lj and also outside lj 2 or 1 b-tagged jets
    # do simplest, separate things
    #    Data or MC -> process (for whole event)
    #    for each systematic -> list of passed channels
    #    process+passed channel -> processes to store (TODO: or tt_other)
    # again, do simple: for each kind of dtags make {channels: ([procs], default)
    # or use a defaultdict somewhere?
    # --- I'll just do a special care for TT
    # the others have 1 process per whole dtag for now
    # (split DY and single-top later

    tt_el_procs = ['tt_eltau', 'tt_lj', 'tt_taultauh', 'tt_taulj', 'tt_other']
    tt_mu_procs = ['tt_mutau', 'tt_lj', 'tt_taultauh', 'tt_taulj', 'tt_other']

    systematic_names_nominal = ['NOMINAL']

    all_systematic_objects = ('NOMINAL', 'JESUp', 'JESDown', 'JERUp', 'JERDown', 'TauESUp', 'TauESDown', 'bSFUp', 'bSFDown')

    if isMC:
        systematic_names_all = ['NOMINAL',
                'LEPUp'     ,
                'LEPDown'   ,
                'JESUp'     ,
                'JESDown'   ,
                'JERUp'     ,
                'JERDown'   ,
                'TauESUp'   ,
                'TauESDown' ,
                'bSFUp'     ,
                'bSFDown'   ,
                'PUUp'      ,
                'PUDown'    ,
                ]
        systematic_names_pu = ['NOMINAL', 'PUUp', 'PUDown']
        systematic_names_pu_toppt = ['NOMINAL', 'PUUp', 'PUDown']
    else:
        systematic_names_all = ['NOMINAL']
        systematic_names_pu  = ['NOMINAL']
        systematic_names_pu_toppt  = ['NOMINAL']
    systematic_names_toppt = ['NOMINAL']

    systematic_names_all_with_th = systematic_names_all[:]
    systematic_names_th_renorm_refact = ['NOMINAL']
    if isTT:
        systematic_names_all.extend(('TOPPTUp', 'TOPPTDown'))
        systematic_names_toppt = ['NOMINAL', 'TOPPTUp']
        systematic_names_pu_toppt.append('TOPPTUp')

        systematic_names_all_with_th.extend(('TOPPTUp', 'TOPPTDown'))
        systematic_names_all_with_th.extend(('AlphaSUp', 'AlphaSDown', 'FragUp', 'FragDown', 'SemilepBRUp', 'SemilepBRDown', 'PetersonUp', 'PetersonDown'))
        systematic_names_all_with_th.extend(('MrUp', 'MrDown', 'MfUp', 'MfDown', 'MfrUp', 'MfrDown'))
        systematic_names_all_with_th.extend(('PDF_TRIGGER',))

        systematic_names_th_renorm_refact.extend(['MrUp', 'MrDown', 'MfUp', 'MfDown', 'MfrUp', 'MfrDown'])

    if isMC:
        if isTT:
            # TODO: probably can clarify this
            if isTT_systematic:
                systematic_names_toppt    = [isTT_systematic]
                systematic_names_pu_toppt = [isTT_systematic]
                systematic_names_pu       = [isTT_systematic]
                systematic_names_all      = [isTT_systematic]
                systematic_names_nominal  = [isTT_systematic]
                systematic_names_all_with_th = [isTT_systematic]
                systematic_names_th_renorm_refact = [isTT_systematic]

            procs_el     = tt_procs_el     =  (['tt_eltau', 'tt_lj', 'tt_taultauh', 'tt_taulj', 'tt_other'], 'tt_other')
            procs_mu     = tt_procs_mu     =  (['tt_mutau', 'tt_lj', 'tt_taultauh', 'tt_taulj', 'tt_other'], 'tt_other')
            procs_el_3ch = tt_procs_el_3ch =  (['tt_eltau3ch', 'tt_eltau', 'tt_lj', 'tt_taultauh', 'tt_taulj', 'tt_other'], 'tt_other')
            procs_mu_3ch = tt_procs_mu_3ch =  (['tt_mutau3ch', 'tt_mutau', 'tt_lj', 'tt_taultauh', 'tt_taulj', 'tt_other'], 'tt_other')
            procs_el_3ch_fbw = tt_procs_el_3ch_fbw =  (['tt_eltau3ch', 'tt_eltau', 'tt_ljb', 'tt_ljw', 'tt_ljo', 'tt_lj', 'tt_taultauh', 'tt_taulj', 'tt_other'], 'tt_other')
            procs_mu_3ch_fbw = tt_procs_mu_3ch_fbw =  (['tt_mutau3ch', 'tt_mutau', 'tt_ljb', 'tt_ljw', 'tt_ljo', 'tt_lj', 'tt_taultauh', 'tt_taulj', 'tt_other'], 'tt_other')
            #procs_elmu   = tt_procs_elmu   =  (['tt_elmu', 'tt_taueltaumu', 'tt_other'], 'tt_other')
            procs_elmu   = tt_procs_elmu   =  (['tt_elmu', 'tt_ltaul', 'tt_taueltaumu', 'tt_other'], 'tt_other')
            usual_process   = 'tt_other'

        if isWJets:
            wjets_procs = (['wjets', 'wjets_tauh', 'wjets_taul'],  'wjets')
            procs_el_3ch = procs_el = procs_mu_3ch = procs_mu = procs_elmu = procs_mu_3ch_fbw = procs_el_3ch_fbw = wjets_procs
            usual_process = 'wjets'

        if isDY:
            dy_procs = (['dy_tautau', 'dy_other'], 'dy_other')
            procs_el_3ch = procs_el = procs_mu_3ch = procs_mu = procs_elmu = procs_mu_3ch_fbw = procs_el_3ch_fbw = dy_procs
            usual_process = 'dy_other'

        if isSTop:
            s_top_procs_el = (['s_top_eltau', 's_top_lj', 's_top_other'], 's_top_other')
            s_top_procs_mu = (['s_top_mutau', 's_top_lj', 's_top_other'], 's_top_other')
            s_top_procs_elmu = (['s_top_elmu', 's_top_other'], 's_top_other')
            procs_el_3ch = procs_el = procs_el_3ch_fbw = s_top_procs_el
            procs_mu_3ch = procs_mu = procs_mu_3ch_fbw = s_top_procs_mu
            procs_elmu = s_top_procs_elmu
            usual_process = 's_top_other'

        if isQCD:
            qcd_procs = (['qcd'], 'qcd')
            procs_el_3ch = procs_el = procs_mu_3ch = procs_mu = procs_elmu = procs_mu_3ch_fbw = procs_el_3ch_fbw = qcd_procs
            usual_process = 'qcd'

        if isDibosons:
            dibosons_procs = (['dibosons'], 'dibosons')
            procs_el_3ch = procs_el = procs_mu_3ch = procs_mu = procs_elmu = procs_mu_3ch_fbw = procs_el_3ch_fbw = dibosons_procs
            usual_process = 'dibosons'

    else:
        data_procs = (['data'], 'data')
        procs_el_3ch = procs_el = procs_mu_3ch = procs_mu = procs_elmu = procs_mu_3ch_fbw = procs_el_3ch_fbw = data_procs
        usual_process = 'data'

    channels_usual = {'el_presel':      (procs_el_3ch, systematic_names_pu_toppt), #systematic_names_all),
                'el_sel':         (procs_el_3ch, systematic_names_pu_toppt), #systematic_names_all),
                'el_lj':          (procs_el_3ch, systematic_names_all), #systematic_names_all),
                'el_lj_out':      (procs_el_3ch, systematic_names_all), #systematic_names_all),
                #'mu_prepresel':   (procs_mu_3ch, systematic_names_pu_toppt), #systematic_names_all),
                'mu_presel':      (procs_mu_3ch, systematic_names_pu_toppt), #systematic_names_all),
                'mu_sel':         (procs_mu_3ch, systematic_names_pu_toppt), #systematic_names_all),
                'mu_lj':          (procs_mu_3ch, systematic_names_all),
                'mu_lj_out':      (procs_mu_3ch, systematic_names_all),
                'mu_lj_ss':       (procs_mu_3ch, systematic_names_pu_toppt),
                'mu_lj_out_ss':   (procs_mu_3ch, systematic_names_pu_toppt),
                # same sign for some QCD control
                'el_sel_ss':      (procs_el, systematic_names_nominal),
                'mu_sel_ss':      (procs_mu, systematic_names_nominal),
                #'el_presel_ss':   (procs_el, systematic_names_nominal),
                #'mu_presel_ss':   (procs_mu, systematic_names_nominal),
                # with tau POG selection
                #'pog_mu_presel':  (procs_mu, systematic_names_nominal),
                #'pog_mu_pass':    (procs_mu, systematic_names_nominal),
                #'pog_mu_pass_ss': (procs_mu, systematic_names_nominal),
                #'pog_mu_fail':    (procs_mu, systematic_names_nominal),
                # with addition of no DY mass, no match to b-tag (could add a cut on small MT)
                #'adv_el_sel':       (procs_el_3ch, systematic_names_toppt), #systematic_names_pu),
                #'adv_el_sel_Sign4': (procs_el_3ch, systematic_names_toppt), #systematic_names_pu), # this is done with a hack in the following, watch closely

                # in adv selection jets cross-cleaned from tau
                'adv_mu_sel_Tight':          (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_Tight_ss':       (procs_mu_3ch, systematic_names_toppt),

                # preselection with all IDs...
                #'adv_mu_sel_preLoose':       (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_Loose':          (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_Loose_ss':       (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_Loose_lj':       (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_Loose_lj_ss':    (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_Loose_ljout':    (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_Loose_ljout_ss': (procs_mu_3ch, systematic_names_toppt),
                #'sel_mu_min':                (procs_mu,     systematic_names_all),
                #'sel_mu_min_ss':             (procs_mu,     systematic_names_all),
                #'sel_mu_min_lj':             (procs_mu,     systematic_names_all),
                #'sel_mu_min_lj_ss':          (procs_mu,     systematic_names_all),
                #'sel_mu_min_ljout':          (procs_mu,     systematic_names_all),
                #'sel_mu_min_ljout_ss':       (procs_mu,     systematic_names_all),
                # the advanced-advanced selection -- scanning the optimization
                # b-jets are Loose, tau is Medium
                # TODO: I need that uniform selection and distributions for this.....
                #'adv_mu_sel_preLoose2':       (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_LooseM':          (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_LooseM_ss':       (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_LooseM_lj':       (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_LooseM_lj_ss':    (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_LooseM_ljout':    (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_LooseM_ljout_ss': (procs_mu_3ch, systematic_names_toppt),

                # data-driven QCD only on "loose" selections
                'adv_mu_sel_Loose_alliso':          (procs_mu_3ch, systematic_names_toppt),
                'adv_mu_sel_Loose_alliso_ss':       (procs_mu_3ch, systematic_names_toppt),
                #'adv_mu_sel_Loose_alliso_lj':       (procs_mu_3ch, systematic_names_toppt),
                #'adv_mu_sel_Loose_alliso_lj_ss':    (procs_mu_3ch, systematic_names_toppt),
                #'adv_mu_sel_Loose_alliso_ljout':    (procs_mu_3ch, systematic_names_toppt),
                #'adv_mu_sel_Loose_alliso_ljout_ss': (procs_mu_3ch, systematic_names_toppt),
                #'sel_mu_min_alliso':                (procs_mu,     systematic_names_toppt),
                #'sel_mu_min_alliso_ss':             (procs_mu,     systematic_names_toppt),
                #'sel_mu_min_alliso_lj':             (procs_mu,     systematic_names_toppt),
                #'sel_mu_min_alliso_lj_ss':          (procs_mu,     systematic_names_toppt),
                #'sel_mu_min_alliso_ljout':          (procs_mu,     systematic_names_toppt),
                #'sel_mu_min_alliso_ljout_ss':       (procs_mu,     systematic_names_toppt),

                #'sel_mu_min_medtau':  (procs_mu, systematic_names_nominal), #systematic_names_pu_toppt), # minimum selection with Medium taus -- hopefully it will reduce QCD
                # control selections: WJets, DY mumu and tautau, tt elmu
                'ctr_mu_wjet':        (procs_mu, systematic_names_pu),
                #'ctr_mu_wjet_ss':    (procs_mu, systematic_names_nominal),
                #'ctr_mu_wjet_old':   (procs_mu, systematic_names_nominal),
                'ctr_mu_dy_mumu':     (procs_mu, systematic_names_pu),
                #'ctr_mu_dy_mumu_ss':  (procs_mu, systematic_names_nominal),
                'ctr_mu_dy_tt':       (procs_mu, systematic_names_pu),
                'ctr_mu_dy_tt_ss':    (procs_mu, systematic_names_pu),
                #'ctr_mu_dy_SV_tt':    (procs_mu, systematic_names_nominal), #systematic_names_all),
                #'ctr_mu_dy_SV_tt_ss': (procs_mu, systematic_names_nominal), #systematic_names_all),
                'ctr_mu_tt_em':       (procs_elmu, systematic_names_pu_toppt),
                }

    # for the special shape study of backgrounds
    if isWJets or isDY:
        channels_usual.update({
                   'mu_sel_nomet':         (procs_mu, ['NOMINAL']),
                   'mu_sel_onlymet':       (procs_mu, ['NOMINAL']),
                   'mu_sel_nobtag':        (procs_mu, ['NOMINAL']),
                   'mu_sel_onlybtag':      (procs_mu, ['NOMINAL']),
                   'mu_sel_no3jets':       (procs_mu, ['NOMINAL']),
                   'mu_sel_only3jets':     (procs_mu, ['NOMINAL'])
                   })

    channels_mu_only = {
                'mu_presel':      (procs_mu_3ch, systematic_names_nominal),
                'mu_sel':         (procs_mu_3ch, systematic_names_nominal),
                'mu_lj':          (procs_mu_3ch, systematic_names_nominal),
                'mu_lj_out':      (procs_mu_3ch, systematic_names_nominal),
                'mu_lj_ss':       (procs_mu_3ch, systematic_names_nominal),
                'mu_lj_out_ss':   (procs_mu_3ch, systematic_names_nominal),
                }

    # OPTIMIZATION
    # optimization scan over tau and b ID selections in mu-tau
    # tau ID = presel, loose, medium, tight
    # N b jets = 1L0M, 2L0M, 1L1M, 2L1M, 2L2M (2 means 2 or more)
    # = 20 selections
    # jets are cross-dR from tau
    # tau is OS to lep -- in principle need SS for QCD estimation... but works very well now (shape-wise) so skipping it here
    channels_mutau_optimization_scan = {
                'optmu_presel':         (procs_mu, systematic_names_nominal),
                'optmu_presel_ss':      (procs_mu, systematic_names_nominal),

                'optmu_presel_1L0M':      (procs_mu, systematic_names_nominal),
                'optmu_presel_2L0M':      (procs_mu, systematic_names_nominal),
                'optmu_presel_1L1M':      (procs_mu, systematic_names_nominal),
                'optmu_presel_2L1M':      (procs_mu, systematic_names_nominal),
                'optmu_presel_2L2M':      (procs_mu, systematic_names_nominal),

                'optmu_loose_1L0M':      (procs_mu, systematic_names_nominal),
                'optmu_loose_2L0M':      (procs_mu, systematic_names_nominal),
                'optmu_loose_1L1M':      (procs_mu, systematic_names_nominal),
                'optmu_loose_2L1M':      (procs_mu, systematic_names_nominal),
                'optmu_loose_2L2M':      (procs_mu, systematic_names_nominal),

                'optmu_medium_1L0M':      (procs_mu, systematic_names_nominal),
                'optmu_medium_2L0M':      (procs_mu, systematic_names_nominal),
                'optmu_medium_1L1M':      (procs_mu, systematic_names_nominal),
                'optmu_medium_2L1M':      (procs_mu, systematic_names_nominal),
                'optmu_medium_2L2M':      (procs_mu, systematic_names_nominal),

                'optmu_tight_1L0M':      (procs_mu, systematic_names_nominal),
                'optmu_tight_2L0M':      (procs_mu, systematic_names_nominal),
                'optmu_tight_1L1M':      (procs_mu, systematic_names_nominal),
                'optmu_tight_2L1M':      (procs_mu, systematic_names_nominal),
                'optmu_tight_2L2M':      (procs_mu, systematic_names_nominal),

                'optmu_presel_1L0M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_presel_2L0M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_presel_1L1M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_presel_2L1M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_presel_2L2M_ss':      (procs_mu, systematic_names_nominal),

                'optmu_loose_1L0M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_loose_2L0M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_loose_1L1M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_loose_2L1M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_loose_2L2M_ss':      (procs_mu, systematic_names_nominal),

                'optmu_medium_1L0M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_medium_2L0M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_medium_1L1M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_medium_2L1M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_medium_2L2M_ss':      (procs_mu, systematic_names_nominal),

                'optmu_tight_1L0M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_tight_2L0M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_tight_1L1M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_tight_2L1M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_tight_2L2M_ss':      (procs_mu, systematic_names_nominal),
               }

    '''
    optimization shows 2L1M as best choice for ttbar
    Tight tau ID gives about the same as old event yield ratios
    but about x2 more events
       14.5k signal VS 8.6k old signal
       27.4k all events VS 14.7k old events
       of which 8% is QCD, which is due to low pt cuts

    loose and medium WP don't give much more signal:
       18.8k with loose, 16.6k with medium

    but increase various backgrounds:
       50.5k all events with loose, 36.6k with medium

    2M1L has a bit more involved b-tagging correction, which I won't do right now [TODO]

    run a test to show the improved performance in the fit
    use 2L1M+tight for that, for mutau and eltau,
    add 2L1M+tight+pt cuts selection [should reduce QCD without cutting the signal too much]
    just in case add 2L1M+loose/tight for mutau only -- main computation is lj parameter, which is done only for events passing main selection (OS and SS tau)
    hence recomputing should not be that big

    also I need to run WJets and DY controls with PU systematics -- for WJets normalization and QCD OS/SS estimation
    and I need anti-iso region for QCD estimation
    -- I'll add a complete all_iso selection for each target selection,
       hopefully there are not so many anti-iso events (it seems so from the tests)

    thus there are:
        2L1M presel + (loose + medium) + tight * (1+2lj + 1cut) = 7 selections for mu-tau
        2L1M presel + tight * (1+2lj)                    = 4 for el-tau
                                        * 2ss * 2 all iso
                                                         = 44 selections
        WJets * 2ss * 2all iso + DY control              = 5
                                                         = 49 selections

    -- I do * 2ss * 2 all iso where I want to check QCD         (all main selections and WJets for QCD-WJets estimation)
       1 + 2lj only for the target selections for fit -- tight
       also only they will have all systematics (lj bins and all events for fit without lj)
       el has only the target                (for full fit)
       mutau has selection with cuts         (without lj, to see event yield posibilities)
       WJets and DY have PU systematics      (for WJets-DY estimation -- to cover the issue with bend at high Mt)

    I had 42 selections for optimization
    (with nominal only systematics and no all iso)
    let's hope it'll fly

    only tight selections have all systematics
    the rest are nominal,
    except DY and WJets os iso -- with PU Up/Down
    '''

    selection_definitions = {
        'channels_optimized_alliso' : {
                'optmu_alliso_presel_2L1M':         (procs_mu, systematic_names_nominal),
                'optmu_alliso_presel_2L1M_ss':      (procs_mu, systematic_names_nominal),
                #'optmu_alliso_loose_2L1M':          (procs_mu, systematic_names_nominal),
                #'optmu_alliso_loose_2L1M_ss':       (procs_mu, systematic_names_nominal),
                #'optmu_alliso_medium_2L1M':         (procs_mu, systematic_names_nominal),
                #'optmu_alliso_medium_2L1M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_alliso_tight_2L1M_cuts':     (procs_mu, systematic_names_nominal),
                'optmu_alliso_tight_2L1M_cuts_ss':  (procs_mu, systematic_names_nominal),
                'optmu_alliso_tight_2L1M':          (procs_mu, systematic_names_nominal),
                'optmu_alliso_tight_2L1M_ss':       (procs_mu, systematic_names_nominal),
                'optmu_alliso_tight_2L1M_lj':       (procs_mu, systematic_names_nominal),
                'optmu_alliso_tight_2L1M_lj_ss':    (procs_mu, systematic_names_nominal),
                'optmu_alliso_tight_2L1M_ljout':    (procs_mu, systematic_names_nominal),
                'optmu_alliso_tight_2L1M_ljout_ss': (procs_mu, systematic_names_nominal),

                'optel_alliso_presel_2L1M':         (procs_el, systematic_names_nominal),
                'optel_alliso_presel_2L1M_ss':      (procs_el, systematic_names_nominal),
                'optel_alliso_tight_2L1M':          (procs_el, systematic_names_nominal),
                'optel_alliso_tight_2L1M_ss':       (procs_el, systematic_names_nominal),
                'optel_alliso_tight_2L1M_lj':       (procs_el, systematic_names_nominal),
                'optel_alliso_tight_2L1M_lj_ss':    (procs_el, systematic_names_nominal),
                'optel_alliso_tight_2L1M_ljout':    (procs_el, systematic_names_nominal),
                'optel_alliso_tight_2L1M_ljout_ss': (procs_el, systematic_names_nominal),
        },

        'channels_optimized' : {
                'optmu_presel_2L1M':         (procs_mu, systematic_names_nominal),
                'optmu_presel_2L1M_ss':      (procs_mu, systematic_names_nominal),
                #'optmu_loose_2L1M':          (procs_mu, systematic_names_nominal),
                #'optmu_loose_2L1M_ss':       (procs_mu, systematic_names_nominal),
                #'optmu_medium_2L1M':         (procs_mu, systematic_names_nominal),
                #'optmu_medium_2L1M_ss':      (procs_mu, systematic_names_nominal),
                'optmu_tight_2L1M_cuts':     (procs_mu, systematic_names_nominal),
                'optmu_tight_2L1M_cuts_ss':  (procs_mu, systematic_names_nominal),

                'optmu_tight_2L1M':          (procs_mu, systematic_names_all),
                'optmu_tight_2L1M_ss':       (procs_mu, systematic_names_all),
                'optmu_tight_2L1M_lj':       (procs_mu, systematic_names_all),
                'optmu_tight_2L1M_lj_ss':    (procs_mu, systematic_names_all),
                'optmu_tight_2L1M_ljout':    (procs_mu, systematic_names_all),
                'optmu_tight_2L1M_ljout_ss': (procs_mu, systematic_names_all),

                'optmu_loose_2L1M':          (procs_mu, systematic_names_nominal),
                'optmu_loose_2L1M_ss':       (procs_mu, systematic_names_nominal),
                'optmu_loose_2L1M_lj':       (procs_mu, systematic_names_nominal),
                'optmu_loose_2L1M_lj_ss':    (procs_mu, systematic_names_nominal),
                'optmu_loose_2L1M_ljout':    (procs_mu, systematic_names_nominal),
                'optmu_loose_2L1M_ljout_ss': (procs_mu, systematic_names_nominal),

                'optel_presel_2L1M':         (procs_el, systematic_names_nominal),
                'optel_presel_2L1M_ss':      (procs_el, systematic_names_nominal),
                'optel_tight_2L1M':          (procs_el, systematic_names_all),
                'optel_tight_2L1M_ss':       (procs_el, systematic_names_all),
                'optel_tight_2L1M_lj':       (procs_el, systematic_names_all),
                'optel_tight_2L1M_lj_ss':    (procs_el, systematic_names_all),
                'optel_tight_2L1M_ljout':    (procs_el, systematic_names_all),
                'optel_tight_2L1M_ljout_ss': (procs_el, systematic_names_all),

                'ctr_mu_wjet':              (procs_mu, systematic_names_pu),
                'ctr_mu_wjet_ss':           (procs_mu, systematic_names_pu),
                'ctr_alliso_mu_wjet':       (procs_mu, systematic_names_nominal),
                'ctr_alliso_mu_wjet_ss':    (procs_mu, systematic_names_nominal),
                'ctr_mu_dy_mumu':           (procs_mu, systematic_names_pu),

                'ctr_mu_tt_em':             (procs_elmu, systematic_names_pu_toppt),
                'ctr_old_mu_sel':           (procs_mu, systematic_names_nominal),     # testing issue with event yield advantage
                'ctr_old_mu_sel_ss':        (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_lj':        (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_lj_ss':     (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ljout':     (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ljout_ss':  (procs_mu, systematic_names_nominal),
        },

        'channels_optimized_old_full_sys' : {
                'ctr_mu_wjet':              (procs_mu, systematic_names_pu),
                'ctr_mu_wjet_ss':           (procs_mu, systematic_names_pu),
                'ctr_el_wjet':              (procs_el, systematic_names_pu),
                'ctr_el_wjet_ss':           (procs_el, systematic_names_pu),
                'ctr_alliso_mu_wjet':       (procs_mu, systematic_names_nominal),
                'ctr_alliso_mu_wjet_ss':    (procs_mu, systematic_names_nominal),

                'ctr_mu_dy_mumu':           (procs_mu, systematic_names_pu),
                'ctr_mu_dy_elel':           (procs_el, systematic_names_pu),
                #'ctr_mu_tt_em':             (procs_elmu, systematic_names_pu_toppt),
                'ctr_mu_tt_em_close':       (procs_elmu, systematic_names_all_with_th),


                #'ctr_old_mu_presel':        (procs_mu_3ch_fbw, systematic_names_pu_toppt),     # testing issue with event yield advantage
                #'ctr_old_mu_presel_ss':     (procs_mu_3ch_fbw, systematic_names_pu_toppt),

                'ctr_old_mu_presel':        (procs_mu, systematic_names_pu_toppt),     # testing issue with event yield advantage
                'ctr_old_mu_presel_ss':     (procs_mu, systematic_names_pu_toppt),

                #'ctr_old_mu_presel_alliso':        (procs_mu, systematic_names_nominal),
                #'ctr_old_mu_presel_alliso_ss':     (procs_mu, systematic_names_nominal),
                #'ctr_old_el_presel_alliso':        (procs_el, systematic_names_nominal),
                #'ctr_old_el_presel_alliso_ss':     (procs_el, systematic_names_nominal),

                'ctr_old_mu_selVloose_alliso':      (procs_mu, systematic_names_nominal),
                'ctr_old_mu_selVloose_alliso_ss':   (procs_mu, systematic_names_nominal),
                'ctr_old_el_selVloose_alliso':      (procs_el, systematic_names_nominal),
                'ctr_old_el_selVloose_alliso_ss':   (procs_el, systematic_names_nominal),

                # testing issue with event yield advantage
                'ctr_old_mu_selVloose':     (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_ss':  (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel':           (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_ss':        (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_lj':        (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_lj_ss':     (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_ljout':     (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_ljout_ss':  (procs_mu, systematic_names_all_with_th),

                'ctr_old_mu_sel_tauSign3':           (procs_mu_3ch_fbw, systematic_names_nominal),
                'ctr_old_mu_sel_tauSign3_ss':        (procs_mu_3ch_fbw, systematic_names_nominal),

                'ctr_old_el_presel':        (procs_el, systematic_names_pu_toppt),     # testing issue with event yield advantage
                'ctr_old_el_presel_ss':     (procs_el, systematic_names_pu_toppt),
                'ctr_old_el_selVloose':     (procs_el, systematic_names_all_with_th),
                'ctr_old_el_selVloose_ss':  (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel':           (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_ss':        (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_lj':        (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_lj_ss':     (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_ljout':     (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_ljout_ss':  (procs_el, systematic_names_all_with_th),
        },

        'channels_full_sys_electron_selections' : {
                'ctr_el_wjet':              (procs_el, systematic_names_pu),
                'ctr_el_wjet_ss':           (procs_el, systematic_names_pu),
                'ctr_old_el_presel':        (procs_el, systematic_names_pu_toppt),     # testing issue with event yield advantage
                'ctr_old_el_presel_ss':     (procs_el, systematic_names_pu_toppt),
                'ctr_old_el_selVloose':     (procs_el, systematic_names_all_with_th),
                'ctr_old_el_selVloose_ss':  (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel':           (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_ss':        (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_lj':        (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_lj_ss':     (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_ljout':     (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_ljout_ss':  (procs_el, systematic_names_all_with_th),
        },

        'channels_full_sys_muon_selections' : {
                'ctr_mu_wjet':                    (procs_mu, systematic_names_pu),
                'ctr_mu_wjet_ss':                 (procs_mu, systematic_names_pu),
                'ctr_old_mu_presel':              (procs_mu, systematic_names_pu_toppt),     # testing issue with event yield advantage
                'ctr_old_mu_presel_ss':           (procs_mu, systematic_names_pu_toppt),
                'ctr_old_mu_selVloose':           (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_ss':        (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_lj':        (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_lj_ss':     (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_ljout':     (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_ljout_ss':  (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel':                 (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_ss':              (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_lj':              (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_lj_ss':           (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_ljout':           (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_ljout_ss':        (procs_mu, systematic_names_all_with_th),
        },

        'channels_full_sys_muon_sel' : {
                'ctr_old_mu_selVloose':           (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_ss':        (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_lj':        (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_lj_ss':     (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_ljout':     (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_ljout_ss':  (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel':                 (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_ss':              (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_lj':              (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_lj_ss':           (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_ljout':           (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_ljout_ss':        (procs_mu, systematic_names_all_with_th),
        },

        'channels_nom_sys_muon_sel' : {
                'ctr_old_mu_selVloose':           (procs_mu, systematic_names_nominal),
                'ctr_old_mu_selVloose_ss':        (procs_mu, systematic_names_nominal),
                'ctr_old_mu_selVloose_lj':        (procs_mu, systematic_names_nominal),
                'ctr_old_mu_selVloose_lj_ss':     (procs_mu, systematic_names_nominal),
                'ctr_old_mu_selVloose_ljout':     (procs_mu, systematic_names_nominal),
                'ctr_old_mu_selVloose_ljout_ss':  (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel':                 (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ss':              (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_lj':              (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_lj_ss':           (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ljout':           (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ljout_ss':        (procs_mu, systematic_names_nominal),
        },

        'channels_nom_sys_muon_sel_main' : {
                'ctr_old_mu_sel':                 (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ss':              (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_lj':              (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_lj_ss':           (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ljout':           (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ljout_ss':        (procs_mu, systematic_names_nominal),
        },

        'channels_nom_sys_both_sel_main' : {
                'ctr_old_mu_sel':                 (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ss':              (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_lj':              (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_lj_ss':           (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ljout':           (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ljout_ss':        (procs_mu, systematic_names_nominal),
                'ctr_old_el_sel':                 (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_ss':              (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_lj':              (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_lj_ss':           (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_ljout':           (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_ljout_ss':        (procs_el, systematic_names_nominal),
        },

        'channels_full_sys_lep_selections' : {
                #'ctr_el_wjet':              (procs_el, systematic_names_pu),
                #'ctr_el_wjet_ss':           (procs_el, systematic_names_pu),
                #'ctr_old_el_presel':        (procs_el, systematic_names_pu_toppt),     # testing issue with event yield advantage
                #'ctr_old_el_presel_ss':     (procs_el, systematic_names_pu_toppt),
                'ctr_old_el_selVloose':     (procs_el, systematic_names_all_with_th),
                'ctr_old_el_selVloose_ss':  (procs_el, systematic_names_all_with_th),
                'ctr_old_el_selVloose_lj':     (procs_el, systematic_names_all_with_th),
                'ctr_old_el_selVloose_lj_ss':  (procs_el, systematic_names_all_with_th),
                'ctr_old_el_selVloose_ljout':     (procs_el, systematic_names_all_with_th),
                'ctr_old_el_selVloose_ljout_ss':  (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel':           (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_ss':        (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_lj':        (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_lj_ss':     (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_ljout':     (procs_el, systematic_names_all_with_th),
                'ctr_old_el_sel_ljout_ss':  (procs_el, systematic_names_all_with_th),

                #'ctr_mu_wjet':              (procs_mu, systematic_names_pu),
                #'ctr_mu_wjet_ss':           (procs_mu, systematic_names_pu),
                #'ctr_old_mu_presel':        (procs_mu, systematic_names_pu_toppt),     # testing issue with event yield advantage
                #'ctr_old_mu_presel_ss':     (procs_mu, systematic_names_pu_toppt),
                'ctr_old_mu_selVloose':     (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_ss':  (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_lj':        (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_lj_ss':     (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_ljout':     (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_selVloose_ljout_ss':  (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel':           (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_ss':        (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_lj':        (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_lj_ss':     (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_ljout':     (procs_mu, systematic_names_all_with_th),
                'ctr_old_mu_sel_ljout_ss':  (procs_mu, systematic_names_all_with_th),
        },

        'channels_nominal_full_lep_selections' : {
                'ctr_old_el_presel':        (procs_el, systematic_names_nominal),     # testing issue with event yield advantage
                'ctr_old_el_presel_ss':     (procs_el, systematic_names_nominal),
                'ctr_old_el_sel':           (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_ss':        (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_lj':        (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_lj_ss':     (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_ljout':     (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_ljout_ss':  (procs_el, systematic_names_nominal),

                'ctr_old_mu_presel':        (procs_mu, systematic_names_nominal),
                'ctr_old_mu_presel_ss':     (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel':           (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ss':        (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_lj':        (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_lj_ss':     (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ljout':     (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ljout_ss':  (procs_mu, systematic_names_nominal),
        },

        'channels_nominal_full_mu_selections' : {
                'ctr_old_mu_presel':        (procs_mu, systematic_names_nominal),
                'ctr_old_mu_presel_ss':     (procs_mu, systematic_names_nominal),
                'ctr_old_mu_presel2b':      (procs_mu, systematic_names_nominal),
                'ctr_old_mu_presel2b_ss':   (procs_mu, systematic_names_nominal),
                'ctr_old_mu_selVloose':     (procs_mu, systematic_names_nominal),
                'ctr_old_mu_selVloose_ss':  (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel':           (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ss':        (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_lj':        (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_lj_ss':     (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ljout':     (procs_mu, systematic_names_nominal),
                'ctr_old_mu_sel_ljout_ss':  (procs_mu, systematic_names_nominal),
        },

        'channels_nominal_full_el_selections' : {
                'ctr_old_el_presel':        (procs_el, systematic_names_nominal),
                'ctr_old_el_presel_ss':     (procs_el, systematic_names_nominal),
                'ctr_old_el_presel2b':      (procs_el, systematic_names_nominal),
                'ctr_old_el_presel2b_ss':   (procs_el, systematic_names_nominal),
                'ctr_old_el_selVloose':     (procs_el, systematic_names_nominal),
                'ctr_old_el_selVloose_ss':  (procs_el, systematic_names_nominal),
                'ctr_old_el_sel':           (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_ss':        (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_lj':        (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_lj_ss':     (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_ljout':     (procs_el, systematic_names_nominal),
                'ctr_old_el_sel_ljout_ss':  (procs_el, systematic_names_nominal),
        },

        'channels_refact_sys_lep_selections' : {
                #'ctr_el_wjet':              (procs_el, systematic_names_pu),
                #'ctr_el_wjet_ss':           (procs_el, systematic_names_pu),
                #'ctr_old_el_presel':        (procs_el, systematic_names_pu_toppt),     # testing issue with event yield advantage
                #'ctr_old_el_presel_ss':     (procs_el, systematic_names_pu_toppt),
                'ctr_old_el_selVloose':     (procs_el, systematic_names_th_renorm_refact),
                'ctr_old_el_selVloose_ss':  (procs_el, systematic_names_th_renorm_refact),
                'ctr_old_el_selVloose_lj':     (procs_el, systematic_names_th_renorm_refact),
                'ctr_old_el_selVloose_lj_ss':  (procs_el, systematic_names_th_renorm_refact),
                'ctr_old_el_selVloose_ljout':     (procs_el, systematic_names_th_renorm_refact),
                'ctr_old_el_selVloose_ljout_ss':  (procs_el, systematic_names_th_renorm_refact),
                'ctr_old_el_sel':           (procs_el, systematic_names_th_renorm_refact),
                'ctr_old_el_sel_ss':        (procs_el, systematic_names_th_renorm_refact),
                'ctr_old_el_sel_lj':        (procs_el, systematic_names_th_renorm_refact),
                'ctr_old_el_sel_lj_ss':     (procs_el, systematic_names_th_renorm_refact),
                'ctr_old_el_sel_ljout':     (procs_el, systematic_names_th_renorm_refact),
                'ctr_old_el_sel_ljout_ss':  (procs_el, systematic_names_th_renorm_refact),

                #'ctr_mu_wjet':              (procs_mu, systematic_names_pu),
                #'ctr_mu_wjet_ss':           (procs_mu, systematic_names_pu),
                #'ctr_old_mu_presel':        (procs_mu, systematic_names_pu_toppt),     # testing issue with event yield advantage
                #'ctr_old_mu_presel_ss':     (procs_mu, systematic_names_pu_toppt),
                'ctr_old_mu_selVloose':     (procs_mu, systematic_names_th_renorm_refact),
                'ctr_old_mu_selVloose_ss':  (procs_mu, systematic_names_th_renorm_refact),
                'ctr_old_mu_selVloose_lj':        (procs_mu, systematic_names_th_renorm_refact),
                'ctr_old_mu_selVloose_lj_ss':     (procs_mu, systematic_names_th_renorm_refact),
                'ctr_old_mu_selVloose_ljout':     (procs_mu, systematic_names_th_renorm_refact),
                'ctr_old_mu_selVloose_ljout_ss':  (procs_mu, systematic_names_th_renorm_refact),
                'ctr_old_mu_sel':           (procs_mu, systematic_names_th_renorm_refact),
                'ctr_old_mu_sel_ss':        (procs_mu, systematic_names_th_renorm_refact),
                'ctr_old_mu_sel_lj':        (procs_mu, systematic_names_th_renorm_refact),
                'ctr_old_mu_sel_lj_ss':     (procs_mu, systematic_names_th_renorm_refact),
                'ctr_old_mu_sel_ljout':     (procs_mu, systematic_names_th_renorm_refact),
                'ctr_old_mu_sel_ljout_ss':  (procs_mu, systematic_names_th_renorm_refact),
        },

        'channels_control_regions' : {
                'ctr_mu_wjet':              (procs_mu, systematic_names_pu),
                'ctr_mu_wjet_ss':           (procs_mu, systematic_names_pu),
                'ctr_el_wjet':              (procs_el, systematic_names_pu),
                'ctr_el_wjet_ss':           (procs_el, systematic_names_pu),
                'ctr_alliso_mu_wjet':       (procs_mu, systematic_names_nominal),
                'ctr_alliso_mu_wjet_ss':    (procs_mu, systematic_names_nominal),

                'ctr_mu_dy_mumu':           (procs_mu, systematic_names_pu),
                'ctr_mu_dy_elel':           (procs_el, systematic_names_pu),
                'ctr_mu_tt_em':             (procs_elmu, systematic_names_pu_toppt),
                #'ctr_mu_tt_em_close':       (procs_elmu, systematic_names_all_with_th), # for the ratio

                'ctr_old_mu_presel_alliso':        (procs_mu, systematic_names_nominal),
                'ctr_old_mu_presel_alliso_ss':     (procs_mu, systematic_names_nominal),
                'ctr_old_el_presel_alliso':        (procs_el, systematic_names_nominal),
                'ctr_old_el_presel_alliso_ss':     (procs_el, systematic_names_nominal),

                'ctr_old_mu_selVloose_alliso':      (procs_mu, systematic_names_nominal),
                'ctr_old_mu_selVloose_alliso_ss':   (procs_mu, systematic_names_nominal),
                'ctr_old_el_selVloose_alliso':      (procs_el, systematic_names_nominal),
                'ctr_old_el_selVloose_alliso_ss':   (procs_el, systematic_names_nominal),
        },

        'channels_control_regions_wjets' : {
                'ctr_mu_wjet':              (procs_mu, systematic_names_pu),
                'ctr_mu_wjet_ss':           (procs_mu, systematic_names_pu),
                'ctr_el_wjet':              (procs_el, systematic_names_pu),
                'ctr_el_wjet_ss':           (procs_el, systematic_names_pu),
                'ctr_alliso_mu_wjet':       (procs_mu, systematic_names_nominal),
                'ctr_alliso_mu_wjet_ss':    (procs_mu, systematic_names_nominal),
        },

        'channels_presels' : {
                'ctr_old_el_presel':        (procs_el, systematic_names_pu_toppt),     # testing issue with event yield advantage
                'ctr_old_el_presel_ss':     (procs_el, systematic_names_pu_toppt),
                'ctr_old_mu_presel':        (procs_mu, systematic_names_pu_toppt),     # testing issue with event yield advantage
                'ctr_old_mu_presel_ss':     (procs_mu, systematic_names_pu_toppt),
        },

        'channels_control_regions_elmu' : {
                'ctr_mu_tt_em':             (procs_elmu, systematic_names_pu_toppt),
                'ctr_mu_tt_em_close':       (procs_elmu, systematic_names_pu_toppt),
                'ctr_el_tt_em':             (procs_elmu, systematic_names_pu_toppt),
                'ctr_el_tt_em_close':       (procs_elmu, systematic_names_pu_toppt),
        },

        'channels_control_regions_elmu_allsys' : {
                'ctr_mu_tt_em':             (procs_elmu, systematic_names_all_with_th),
                'ctr_mu_tt_em_close':       (procs_elmu, systematic_names_all_with_th),
                'ctr_el_tt_em':             (procs_elmu, systematic_names_all_with_th),
                'ctr_el_tt_em_close':       (procs_elmu, systematic_names_all_with_th),
        },

        'channels_control_regions_dy' : {
                'ctr_mu_dy_mumu':           (procs_mu, systematic_names_pu),
                'ctr_mu_dy_elel':           (procs_el, systematic_names_pu),
        }
    }

    print systematic_names_all_with_th
    print systematic_names_pu_toppt
    print systematic_names_pu
    print systematic_names_nominal

    #channels = channels_mu_only
    #channels = channels_usual
    #channels, with_bSF = channels_mutau_optimization_scan, False
    #selected_channels = channels_optimized_old_full_sys
    #selected_channels = channels_full_sys_electron_selections
    selected_channels = selection_definitions[channels_to_select]

    with_JER   = isMC and True
    with_JES   = isMC and True
    with_TauES = isMC and True

    # find all requested systematics
    requested_systematics  = set()
    requested_objects      = set()
    for k, (ch_name, systematic_names) in selected_channels.items():
      for systematic_name in systematic_names:
        requested_systematics.add(systematic_name)
        if systematic_name in all_systematic_objects:
            requested_objects.add(systematic_name)

    with_bSF_sys = with_bSF and ('bSFUp' in requested_systematics or 'bSFDown' in requested_systematics)
    with_JER_sys = with_JER and ('JERUp' in requested_systematics or 'JERDown' in requested_systematics)
    with_JES_sys = with_JES and ('JESUp' in requested_systematics or 'JESDown' in requested_systematics)
    with_TauES_sys = with_TauES and ('TauESUp' in requested_systematics or 'TauESDown' in requested_systematics)

    with_AlphaS_sys  = True and ('AlphaSUp' in requested_systematics or 'AlphaSDown' in requested_systematics)
    with_Frag_sys    = True and ('FragUp'   in requested_systematics or 'FragDown'   in requested_systematics)
    with_MEscale_sys = True and ('MfUp'     in requested_systematics or 'MfDown'   in requested_systematics)
    with_PDF_sys     = True and ('PDF_TRIGGER'      in requested_systematics)

    #SystematicJets = namedtuple('Jets', 'nom sys_JERUp sys_JERDown sys_JESUp sys_JESDown sys_bUp sys_bDown')
    # all requested jet cuts
    JetBSplit = namedtuple('BJets', 'medium loose rest taumatched lepmatched')
    #JetCutsPerSystematic = namedtuple('Jets', 'lowest cuts old') # TODO add jets loose
    JetCutsPerSystematic = namedtuple('Jets', 'old old_alliso') # TODO add jets loose
    TauCutsPerSystematic = namedtuple('Taus', 'lowest loose cuts old oldVloose presel_alliso presel')
    LeptonSelection = namedtuple('Leptons', 'iso alliso')

    proc = usual_process
    micro_proc = '' # hack for tt_leptau->3ch subchannel of hadronic taus

    #set_bSF_effs_for_dtag(dtag)
    if with_bSF: logger.write(' '.join(str(id(h)) for h in (bEff_histo_b, bEff_histo_c, bEff_histo_udsg)) + '\n')
    #print b_alljet, b_tagged, c_alljet, c_tagged, udsg_alljet, udsg_tagged
    #global bTagging_b_jet_efficiency, bTagging_c_jet_efficiency, bTagging_udsg_jet_efficiency
    #bTagging_b_jet_efficiency = bTagging_X_jet_efficiency(b_alljet, b_tagged)
    #bTagging_c_jet_efficiency = bTagging_X_jet_efficiency(c_alljet, c_tagged)
    #bTagging_udsg_jet_efficiency = bTagging_X_jet_efficiency(udsg_alljet, udsg_tagged)

    # test
    logger.write('%s\n' % '\n'.join('%s_%s_%s' % (chan, proc, sys[0]) for chan, ((procs, _), sys) in selected_channels.items() for proc in procs))

    tau_fakerate_pts  = (ctypes.c_double * 10)(* [20, 30, 40, 50, 70, 90, 120, 150, 200, 300])
    tau_fakerate_pts_n  = 9
    tau_fakerate_etas = (ctypes.c_double * 13)(* [-2.4, -2, -1.6, -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2, 1.6, 2, 2.4])
    tau_fakerate_etas_n = 12
    lep_relIso_el_bins   = (ctypes.c_double * 6)(* [0, 0.059, 0.1, 0.175, 0.3, 0.5])
    lep_relIso_el_bins_n = 5
    lep_relIso_el_bins_ext   = (ctypes.c_double * 8)(* [0, 0.059, 0.1, 0.175, 0.3, 0.5, 2., 4.])
    lep_relIso_el_bins_ext_n = 7
    lep_relIso_bins   = (ctypes.c_double * 7)(* [0, 0.15, 0.25, 0.5, 1., 2., 4.])
    lep_relIso_bins_n = 6
    lep_relIso_bins_ext   = (ctypes.c_double * 9)(* [0, 0.15, 0.25, 0.5, 1., 2., 4., 8., 16.])
    lep_relIso_bins_ext_n = 8

    dijet_trijet_bins_ext = (ctypes.c_double * 8)(* [0, 20., 40., 60., 100., 150., 250., 400.])
    dijet_trijet_bins_ext_n = 7

    dijet_bins_ext  = (ctypes.c_double * 8)(* [10, 40., 65., 80., 95., 120., 150., 200.])
    dijet_bins_ext_n  = 7

    trijet_bins_ext = (ctypes.c_double * 8)(* [20., 100., 125., 150., 175., 200., 300., 400.])
    trijet_bins_ext_n = 7

    # channel -- reco selection
    # proc    -- MC gen info, like inclusive tt VS tt->mutau and others,
    #            choice of subprocesses depends on channel (sadly),
    #            (find most precise subprocess ones, then store accordingly for channels)
    # sys     -- shape systematics

    class ZeroOutDistr:
        def Fill(self, *args):
            pass
        def SetDirectory(self, *args):
            pass
        def Write(self, *args):
            pass
    #zero_out_distr = ZeroOutDistr()

    # helper codes for phi distrs
    pdgId_codes = {11: 'elP_phi', -11: 'elN_phi', 13: 'muP_phi', -13: 'muN_phi'}

    def format_distrs(chan, proc, sys):
        '''
        I don't need all distrs for all systematics, only some

        if distr is not there? -- ok, I'll use defaultdict with the factory for defaults
        it creates the dummies dynamically and runs quickly after that
        '''

        # do simply
        # here all-syst distrs and PDF syst:
        distrs = defaultdict(ZeroOutDistr)
        if 'PDF' in sys:
            distrs.update({
              'Mt_lep_met_f': TH1D('%s_%s_%s_Mt_lep_met_f' % (chan, proc, sys), '', 20, 0, 250),
              #'Mt_lep_met':   TH1D('%s_%s_%s_Mt_lep_met'   % (chan, proc, sys), '', 10, 0, 200),
              })
        else:
            distrs.update({
              'met':          TH1D('%s_%s_%s_met'          % (chan, proc, sys), '', 30, 0, 300),
              'lep_pt':       TH1D('%s_%s_%s_lep_pt'       % (chan, proc, sys), '', 40, 0, 200),
              'Mt_lep_met_f': TH1D('%s_%s_%s_Mt_lep_met_f' % (chan, proc, sys), '', 20, 0, 250),
              'Mt_lep_met':   TH1D('%s_%s_%s_Mt_lep_met'   % (chan, proc, sys), '', 10, 0, 200),
              })

        if 'TOPPT' in sys or 'PU' in sys or sys == 'NOMINAL':
            distrs.update({
            'bMjet_pt':   TH1D('%s_%s_%s_bMjet_pt'   % (chan, proc, sys), '', 30, 0, 300),
            'b1Mjet_pt':  TH1D('%s_%s_%s_b1Mjet_pt'  % (chan, proc, sys), '', 30, 0, 300),
              })

        if 'PU' in sys or sys == 'NOMINAL':
            distrs.update({
              'nvtx':        TH1D('%s_%s_%s_nvtx'       % (chan, proc, sys), '', 50, 0, 50),

             'regMt_tau_pt':   TH1D('%s_%s_%s_regMt_tau_pt'      % (chan, proc, sys), '', 20, 0, 150),
             'regMt_tau_substitution':      TH1D('%s_%s_%s_regMt_tau_substitution'     % (chan, proc, sys), '', 20, 0, 50.),
             'regMt_lep_pt':   TH1D('%s_%s_%s_regMt_lep_pt'      % (chan, proc, sys), '', 20, 0, 250),
             'regMt_lep_eta':  TH1D('%s_%s_%s_regMt_lep_eta'      % (chan, proc, sys), '', 50, -2.5, 2.5),
             'regMt_lep_eta_lowpt':  TH1D('%s_%s_%s_regMt_lep_eta_lowpt' % (chan, proc, sys), '', 50, -2.5, 2.5),
             'regMt_Mt_lowpt':       TH1D('%s_%s_%s_regMt_Mt_lowpt'      % (chan, proc, sys), '', 20, 0, 250),
             'regMt_lep_phi':  TH1D('%s_%s_%s_regMt_lep_phi'      % (chan, proc, sys), '', 66, -3.3, 3.3),
             'regMt_met':      TH1D('%s_%s_%s_regMt_met'      % (chan, proc, sys), '', 20, 0, 250),
             'regMt_met_phi':  TH1D('%s_%s_%s_regMt_met_phi'      % (chan, proc, sys), '', 66, -3.3, 3.3),
             'regMt_met_lep_cos':  TH1D('%s_%s_%s_regMt_met_lep_cos' % (chan, proc, sys), '', 22, -1.1, 1.1),
             'regMt_tau_lep_cos':  TH1D('%s_%s_%s_regMt_tau_lep_cos' % (chan, proc, sys), '', 22, -1.1, 1.1),
             'regMt_tau_jet_scale':  TH1D('%s_%s_%s_regMt_tau_jet_scale' % (chan, proc, sys), '', 22, 0.0, 2.0),
             'regMt_nMbjets':   TH1D('%s_%s_%s_regMt_nMbjets'    % (chan, proc, sys), '', 10, 0, 10),
             'regMt_nLbjets':   TH1D('%s_%s_%s_regMt_nLbjets'    % (chan, proc, sys), '', 10, 0, 10),
             'regMt_nRbjets':   TH1D('%s_%s_%s_regMt_nRbjets'    % (chan, proc, sys), '', 10, 0, 10),
             'regMt_bMjet_pt':  TH1D('%s_%s_%s_regMt_bMjet_pt'   % (chan, proc, sys), '', 30, 0, 300),

             'regMt_lep_pt_eta':   TH2D('%s_%s_%s_regMt_lep_pt_eta'     % (chan, proc, sys), '', 15, 0, 250, 50, -2.5, 2.5),
             'regMt_lep_pt_Mt':    TH2D('%s_%s_%s_regMt_lep_pt_Mt'      % (chan, proc, sys), '', 15, 0, 250, 15, 0, 250),
              })

        # here only obj syst:
        if sys in requested_objects:
          distrs.update({
            ## debuging the cut on MC lep pt from weights at 26 GeV
            #'lep_pt_turn_raw_w_b_trk':          TH1D('%s_%s_%s_lep_pt_turn_raw_w_b_trk'     % (chan, proc, sys), '', 40, 20, 40),
            #'lep_pt_turn_raw_w_b_trk_vtx':      TH1D('%s_%s_%s_lep_pt_turn_raw_w_b_trk_vtx' % (chan, proc, sys), '', 40, 20, 40),
            #'lep_pt_turn_raw_w_b_id':           TH1D('%s_%s_%s_lep_pt_turn_raw_w_b_id'      % (chan, proc, sys), '', 40, 20, 40),
            #'lep_pt_turn_raw_w_b_iso':          TH1D('%s_%s_%s_lep_pt_turn_raw_w_b_iso'     % (chan, proc, sys), '', 40, 20, 40),
            #'lep_pt_turn_raw_w_b_trk_vtxgen':   TH1D('%s_%s_%s_lep_pt_turn_raw_w_b_trk_vtxgen' % (chan, proc, sys), '', 40, 20, 40),
            #'lep_pt_turn_raw_w_b_trg':          TH1D('%s_%s_%s_lep_pt_turn_raw_w_b_trg'     % (chan, proc, sys), '', 40, 20, 40), # <--- this one is 0
            ## debugging cut at 120 GeV
            ## the new defaults for id and iso were erroneous
            #'lep_pt_raw_w_b_trk':          TH1D('%s_%s_%s_lep_pt_raw_w_b_trk'     % (chan, proc, sys), '', 40, 20, 200),
            #'lep_pt_raw_w_b_trk_vtx':      TH1D('%s_%s_%s_lep_pt_raw_w_b_trk_vtx' % (chan, proc, sys), '', 40, 20, 200),
            #'lep_pt_raw_w_b_id':           TH1D('%s_%s_%s_lep_pt_raw_w_b_id'      % (chan, proc, sys), '', 40, 20, 200),
            #'lep_pt_raw_w_b_iso':          TH1D('%s_%s_%s_lep_pt_raw_w_b_iso'     % (chan, proc, sys), '', 40, 20, 200),
            #'lep_pt_raw_w_b_trk_vtxgen':   TH1D('%s_%s_%s_lep_pt_raw_w_b_trk_vtxgen' % (chan, proc, sys), '', 40, 20, 200),
            #'lep_pt_raw_w_b_trg':          TH1D('%s_%s_%s_lep_pt_raw_w_b_trg'     % (chan, proc, sys), '', 40, 20, 200), # <--- this one is 0

            'lep_eta':    TH1D('%s_%s_%s_lep_eta'    % (chan, proc, sys), '', 50, -2.5, 2.5),
            'tau_pt':     TH1D('%s_%s_%s_tau_pt'     % (chan, proc, sys), '', 30, 0, 150),
            'tau_eta':    TH1D('%s_%s_%s_tau_eta'    % (chan, proc, sys), '', 50, -2.5, 2.5),

            'Rjet_pt':    TH1D('%s_%s_%s_Rjet_pt'    % (chan, proc, sys), '', 30, 0, 300),
            'Rjet_eta':   TH1D('%s_%s_%s_Rjet_eta'   % (chan, proc, sys), '', 50, -2.5, 2.5),
            'LRjet_pt':   TH1D('%s_%s_%s_LRjet_pt'   % (chan, proc, sys), '', 30, 0, 300),
            'LRjet_eta':  TH1D('%s_%s_%s_LRjet_eta'  % (chan, proc, sys), '', 50, -2.5, 2.5),
            #'bMjet_pt':   TH1D('%s_%s_%s_bMjet_pt'   % (chan, proc, sys), '', 30, 0, 300),
            'bMjet_eta':  TH1D('%s_%s_%s_bMjet_eta'  % (chan, proc, sys), '', 50, -2.5, 2.5),
            'bLjet_pt':   TH1D('%s_%s_%s_bLjet_pt'   % (chan, proc, sys), '', 30, 0, 300),
            'bLjet_eta':  TH1D('%s_%s_%s_bLjet_eta'  % (chan, proc, sys), '', 20, -2.5, 2.5),
            'bL2jet_pt':  TH1D('%s_%s_%s_bL2jet_pt'  % (chan, proc, sys), '', 30, 0, 300),
            'bL2jet_eta': TH1D('%s_%s_%s_bL2jet_eta' % (chan, proc, sys), '', 20, -2.5, 2.5),
            'bMjet0_pt':  TH1D('%s_%s_%s_bMjet0_pt'   % (chan, proc, sys), '', 30, 0, 300),
            'bMjet1_pt':  TH1D('%s_%s_%s_bMjet1_pt'   % (chan, proc, sys), '', 30, 0, 300),
            'bMjet1_eta': TH1D('%s_%s_%s_bMjet1_eta'  % (chan, proc, sys), '', 50, -2.5, 2.5),
            'bMjet0_hadronFlavour':   TH1D('%s_%s_%s_bMjet0_hadronFlavour'   % (chan, proc, sys), '', 20, -10, 10),
            'bMjet1_hadronFlavour':   TH1D('%s_%s_%s_bMjet1_hadronFlavour'   % (chan, proc, sys), '', 20, -10, 10),
            'bMjet2_hadronFlavour':   TH1D('%s_%s_%s_bMjet2_hadronFlavour'   % (chan, proc, sys), '', 20, -10, 10),

            ## OPTIMIZATION
            ## control the b-jet categories
            ## tau-b-jet categories
            ## tau index in tau arrays (should always be 0)
            #'opt_bjet_categories':      TH1D('%s_%s_%s_opt_bjet_categories'     % (chan, proc, sys), '', 5, 0., 5.),
            ##'opt_tau_categories':       TH1D('%s_%s_%s_opt_tau_categories'      % (chan, proc, sys), '', 5, 0., 5.),
            #'opt_tau_bjet_categories':  TH1D('%s_%s_%s_opt_tau_bjet_categories' % (chan, proc, sys), '', 4*5, 0., 4*5.),
            #'opt_bjet_categories_incl':      TH1D('%s_%s_%s_opt_bjet_categories_incl'     % (chan, proc, sys), '', 5, 0., 5.),
            #'opt_tau_bjet_categories_incl':  TH1D('%s_%s_%s_opt_tau_bjet_categories_incl' % (chan, proc, sys), '', 4*5, 0., 4*5.),
            #'opt_tau_index_loose':      TH1D('%s_%s_%s_opt_tau_index_loose'     % (chan, proc, sys), '', 10, 0., 10.),
            #'opt_tau_index_medium':     TH1D('%s_%s_%s_opt_tau_index_medium'    % (chan, proc, sys), '', 10, 0., 10.),
            #'opt_tau_index_tight':      TH1D('%s_%s_%s_opt_tau_index_tight'     % (chan, proc, sys), '', 10, 0., 10.),
            #'opt_lep_tau_pt':           TH2D('%s_%s_%s_opt_lep_tau_pt'          % (chan, proc, sys), '', 20, 0, 200, 30, 0, 300),
            #'opt_lep_bjet_pt':          TH2D('%s_%s_%s_opt_lep_bjet_pt'         % (chan, proc, sys), '', 20, 0, 200, 30, 0, 300),
            #'opt_bjet_bjet2_pt':        TH2D('%s_%s_%s_opt_bjet_bjet2_pt'       % (chan, proc, sys), '', 20, 0, 250, 20, 0, 250),
            #'opt_n_presel_tau':  TH1D('%s_%s_%s_opt_n_presel_tau'    % (chan, proc, sys), '', 5, 0., 5.),
            #'opt_n_loose_tau':   TH1D('%s_%s_%s_opt_n_loose_tau'     % (chan, proc, sys), '', 5, 0., 5.),
            #'opt_n_medium_tau':  TH1D('%s_%s_%s_opt_n_medium_tau'    % (chan, proc, sys), '', 5, 0., 5.),
            #'opt_n_tight_tau':   TH1D('%s_%s_%s_opt_n_tight_tau'     % (chan, proc, sys), '', 5, 0., 5.),
            #'opt_n_loose_bjet':  TH1D('%s_%s_%s_opt_n_loose_bjet'    % (chan, proc, sys), '', 5, 0., 5.),
            #'opt_n_medium_bjet': TH1D('%s_%s_%s_opt_n_medium_bjet'   % (chan, proc, sys), '', 5, 0., 5.),

            ## for tt->elmu FAKERATES
            #'all_jet_pt':     TH1D('%s_%s_%s_all_jet_pt'     % (chan, proc, sys), '', tau_fakerate_pts_n, tau_fakerate_pts),
            #'all_jet_eta':    TH1D('%s_%s_%s_all_jet_eta'    % (chan, proc, sys), '', tau_fakerate_etas_n, tau_fakerate_etas),
            #'candidate_tau_jet_pt':  TH1D('%s_%s_%s_candidate_tau_jet_pt'  % (chan, proc, sys), '', tau_fakerate_pts_n, tau_fakerate_pts),
            #'candidate_tau_jet_eta': TH1D('%s_%s_%s_candidate_tau_jet_eta' % (chan, proc, sys), '', tau_fakerate_etas_n, tau_fakerate_etas),
            #'vloose_tau_jet_pt':  TH1D('%s_%s_%s_vloose_tau_jet_pt'  % (chan, proc, sys), '', tau_fakerate_pts_n, tau_fakerate_pts),
            #'vloose_tau_jet_eta': TH1D('%s_%s_%s_vloose_tau_jet_eta' % (chan, proc, sys), '', tau_fakerate_etas_n, tau_fakerate_etas),
            #'loose_tau_jet_pt':   TH1D('%s_%s_%s_loose_tau_jet_pt'   % (chan, proc, sys), '', tau_fakerate_pts_n, tau_fakerate_pts),
            #'loose_tau_jet_eta':  TH1D('%s_%s_%s_loose_tau_jet_eta'  % (chan, proc, sys), '', tau_fakerate_etas_n, tau_fakerate_etas),
            #'medium_tau_jet_pt':  TH1D('%s_%s_%s_medium_tau_jet_pt'  % (chan, proc, sys), '', tau_fakerate_pts_n, tau_fakerate_pts),
            #'medium_tau_jet_eta': TH1D('%s_%s_%s_medium_tau_jet_eta' % (chan, proc, sys), '', tau_fakerate_etas_n, tau_fakerate_etas),
            #'tight_tau_jet_pt':   TH1D('%s_%s_%s_tight_tau_jet_pt'   % (chan, proc, sys), '', tau_fakerate_pts_n, tau_fakerate_pts),
            #'tight_tau_jet_eta':  TH1D('%s_%s_%s_tight_tau_jet_eta'  % (chan, proc, sys), '', tau_fakerate_etas_n, tau_fakerate_etas),
            #'vtight_tau_jet_pt':  TH1D('%s_%s_%s_vtight_tau_jet_pt'  % (chan, proc, sys), '', tau_fakerate_pts_n, tau_fakerate_pts),
            #'vtight_tau_jet_eta': TH1D('%s_%s_%s_vtight_tau_jet_eta' % (chan, proc, sys), '', tau_fakerate_etas_n, tau_fakerate_etas),
            'Mt_tau_met':         TH1D('%s_%s_%s_Mt_tau_met'     % (chan, proc, sys), '', 20, 0, 200),
            'Mt_tau_met_lep':     TH2D('%s_%s_%s_Mt_tau_met_lep' % (chan, proc, sys), '', 20, 0, 300, 20, 0, 300),

            # for dileptons, it is practically the same as lep+tau, but for simplicity keeping them separate
            'M_lep_lep':   TH1D('%s_%s_%s_M_lep_lep'  % (chan, proc, sys), '', 20, 0, 250),
            'M_lep_tau':   TH1D('%s_%s_%s_M_lep_tau'  % (chan, proc, sys), '', 20, 0, 200),
            })

        # and only nominals
        if sys == 'NOMINAL':
           distrs.update({
             'Mt_tau_lep':  TH1D('%s_%s_%s_Mt_tau_lep' % (chan, proc, sys), '', 20, 0, 300),
              'yield':      TH1D('%s_%s_%s_yield' % (chan, proc, sys), '', 3, 0, 3),

             'bMjet_pt_nocor':     TH1D('%s_%s_%s_bMjet_pt_nocor'   % (chan, proc, sys), '', 30, 0, 300),
             # control the tau/jet prop to met
             'met_prop_taus':      TH2D('%s_%s_%s_met_prop_taus'  % (chan, proc, sys), '', 20, 0, 300, 20, -5., 5.),
             'met_prop_jets':      TH2D('%s_%s_%s_met_prop_jets'  % (chan, proc, sys), '', 20, 0, 300, 20, -5., 5.),
             'init_met':           TH1D('%s_%s_%s_init_met'   % (chan, proc, sys), '', 30, 0, 300),
             'corr_met':           TH1D('%s_%s_%s_corr_met'   % (chan, proc, sys), '', 30, 0, 300),
             'met_objects':        TH1D('%s_%s_%s_met_objects'% (chan, proc, sys), '', 30, 0, 300),
             'met_lep_phi':        TH1D('%s_%s_%s_met_lep_phi'% (chan, proc, sys), '', 30, -3.2, 3.2),
             'met_phi_met_pt':     TH2D('%s_%s_%s_met_phi_met_pt'% (chan, proc, sys), '', 30, -3.2, 3.2, 25, 0, 250),
             'met_pt_smallphi':    TH1D('%s_%s_%s_met_pt_smallphi'   % (chan, proc, sys), '', 30, 0, 300),
             'met_pt_largephi':    TH1D('%s_%s_%s_met_pt_largephi'   % (chan, proc, sys), '', 30, 0, 300),
             'met_lep_cos':        TH1D('%s_%s_%s_met_lep_cos'% (chan, proc, sys), '', 44, -1.1, 1.1),
             'rev_met_lep_cos':    TH1D('%s_%s_%s_rev_met_lep_cos'% (chan, proc, sys), '', 44, -1.1, 1.1),
             'allobj_lep_cos':     TH1D('%s_%s_%s_allobj_lep_cos'    % (chan, proc, sys), '', 44, -1.1, 1.1),
             'allobj_met_lep_cos': TH1D('%s_%s_%s_allobj_met_lep_cos'% (chan, proc, sys), '', 44, -1.1, 1.1),
             'Mt_lep_allobj_met':  TH1D('%s_%s_%s_Mt_lep_allobj_met' % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_allobj':      TH1D('%s_%s_%s_Mt_lep_allobj'     % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_rev_met':     TH1D('%s_%s_%s_Mt_lep_rev_met'    % (chan, proc, sys), '', 20, 0, 250),
             'lep1_phi':           TH1D('%s_%s_%s_lep1_phi'   % (chan, proc, sys), '', 30, -3.2, 3.2),
             'lep2_phi':           TH1D('%s_%s_%s_lep2_phi'   % (chan, proc, sys), '', 30, -3.2, 3.2), # tau in lep-tau channels
             'lep1_eta':           TH1D('%s_%s_%s_lep1_eta'   % (chan, proc, sys), '', 50, -2.5, 2.5),
             'lep2_eta':           TH1D('%s_%s_%s_lep2_eta'   % (chan, proc, sys), '', 50, -2.5, 2.5), # tau in lep-tau channels
             'met_phi':            TH1D('%s_%s_%s_met_phi'    % (chan, proc, sys), '', 30, -3.2, 3.2),
             'rev_met_phi':        TH1D('%s_%s_%s_rev_met_phi'    % (chan, proc, sys), '', 30, -3.2, 3.2),
             'allobj_phi':         TH1D('%s_%s_%s_allobj_phi'   % (chan, proc, sys), '', 30, -3.2, 3.2),
             'met_lep_phis':       TH2D('%s_%s_%s_met_lep_phis' % (chan, proc, sys), '', 30, -3.2, 3.2, 30, -3.2, 3.2),
             'met_allobj_met_phis':TH2D('%s_%s_%s_met_allobj_met_phis' % (chan, proc, sys), '', 30, -3.2, 3.2, 30, -3.2, 3.2),
             'met_allobj_phis':    TH2D('%s_%s_%s_met_allobj_phis'     % (chan, proc, sys), '', 30, -3.2, 3.2, 30, -3.2, 3.2),
             'met_allobj_met_pts': TH2D('%s_%s_%s_met_allobj_met_pts'  % (chan, proc, sys), '', 20, 0., 200., 20, 0., 200.),
             'elP_phi':            TH1D('%s_%s_%s_elP_phi'   % (chan, proc, sys), '', 30, -3.2, 3.2),
             'muP_phi':            TH1D('%s_%s_%s_muP_phi'   % (chan, proc, sys), '', 30, -3.2, 3.2),
             'elN_phi':            TH1D('%s_%s_%s_elN_phi'   % (chan, proc, sys), '', 30, -3.2, 3.2),
             'muN_phi':            TH1D('%s_%s_%s_muN_phi'   % (chan, proc, sys), '', 30, -3.2, 3.2),
             'tau_phi':            TH1D('%s_%s_%s_tau_phi'   % (chan, proc, sys), '', 30, -3.2, 3.2),
             'met_cancelation':    TH1D('%s_%s_%s_met_cancelation'% (chan, proc, sys), '', 30, 0, 300),
             'met_cancelation_xy': TH2D('%s_%s_%s_met_cancelation_xy'% (chan, proc, sys), '', 20, -100, 100, 20, -100, 100),
             'met_cancelation_x_met_x': TH2D('%s_%s_%s_met_cancelation_x_met_x'% (chan, proc, sys), '', 20, -100, 100, 20, -100, 100),
             'met_cancelation_y_met_y': TH2D('%s_%s_%s_met_cancelation_y_met_y'% (chan, proc, sys), '', 20, -100, 100, 20, -100, 100),
             'met_x': TH1D('%s_%s_%s_met_x' % (chan, proc, sys), '', 20, -100, 100),
             'met_y': TH1D('%s_%s_%s_met_y' % (chan, proc, sys), '', 20, -100, 100),
             'allobj_x': TH1D('%s_%s_%s_allobj_x' % (chan, proc, sys), '', 20, -100, 100),
             'allobj_y': TH1D('%s_%s_%s_allobj_y' % (chan, proc, sys), '', 20, -100, 100),
             'Mt_lep_met_init_f':  TH1D('%s_%s_%s_Mt_lep_met_init_f' % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_corr_f':  TH1D('%s_%s_%s_Mt_lep_met_corr_f' % (chan, proc, sys), '', 20, 0, 250),
             'all_sum_control':       TH1D('%s_%s_%s_all_sum_control'      % (chan, proc, sys), '', 50, 0, 200),
             'all_sum_control_init':  TH1D('%s_%s_%s_all_sum_control_init' % (chan, proc, sys), '', 50, 0, 200),
             'tau_cor_control':       TH1D('%s_%s_%s_tau_cor_control'      % (chan, proc, sys), '', 20, 0, 5),
             'tau_substitution':      TH1D('%s_%s_%s_tau_substitution'     % (chan, proc, sys), '', 20, 0, 50.),
             'lep_pt_turn':TH1D('%s_%s_%s_lep_pt_turn'% (chan, proc, sys), '', 270, 23, 50),
             'lep_pt_turn_raw':TH1D('%s_%s_%s_lep_pt_turn_raw' % (chan, proc, sys), '', 40, 20, 40),

             'Mt_lep_met_shifted': TH1D('%s_%s_%s_Mt_lep_met_shifted'    % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_sublep':  TH1D('%s_%s_%s_Mt_lep_met_sublep'     % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_30GeV':   TH1D('%s_%s_%s_Mt_lep_met_30GeV'      % (chan, proc, sys), '', 20, 0, 250),

             """
             'regMt_lep_pt_puM'    :  TH1D('%s_%s_%s_regMt_lep_pt_puM'      % (chan, proc, sys), '', 20,    0, 250),
             'regMt_lep_pt_puE'    :  TH1D('%s_%s_%s_regMt_lep_pt_puE'      % (chan, proc, sys), '', 20,    0, 250),
             'regMt_lep_pt_puM_up' :  TH1D('%s_%s_%s_regMt_lep_pt_puM_up'   % (chan, proc, sys), '', 20,    0, 250),
             'regMt_lep_pt_puE_up' :  TH1D('%s_%s_%s_regMt_lep_pt_puE_up'   % (chan, proc, sys), '', 20,    0, 250),
             'regMt_lep_pt_puM_dn' :  TH1D('%s_%s_%s_regMt_lep_pt_puM_dn'   % (chan, proc, sys), '', 20,    0, 250),
             'regMt_lep_pt_puE_dn' :  TH1D('%s_%s_%s_regMt_lep_pt_puE_dn'   % (chan, proc, sys), '', 20,    0, 250),

             'regMt_lep_pt_init':   TH1D('%s_%s_%s_regMt_lep_pt_init'      % (chan, proc, sys), '', 20,    0, 250),
             'regMt_lep_pt_rocc':   TH1D('%s_%s_%s_regMt_lep_pt_rocc'      % (chan, proc, sys), '', 20,    0, 250),
             'regMt_lep_eta_init':  TH1D('%s_%s_%s_regMt_lep_eta_init'     % (chan, proc, sys), '', 50, -2.5, 2.5),
             'regMt_lep_phi_init':  TH1D('%s_%s_%s_regMt_lep_phi_init'     % (chan, proc, sys), '', 66, -3.3, 3.3),
             'regMt_lep_eta_rocc':  TH1D('%s_%s_%s_regMt_lep_eta_rocc'     % (chan, proc, sys), '', 50, -2.5, 2.5),
             'regMt_lep_phi_rocc':  TH1D('%s_%s_%s_regMt_lep_phi_rocc'     % (chan, proc, sys), '', 66, -3.3, 3.3),
             'regMt_rocc':          TH1D('%s_%s_%s_regMt_rocc'     % (chan, proc, sys), '', 50, 0.0, 2.0),
             # compare to Mt_lep_met_f_init
             'Mt_lep_met_f_rocc':   TH1D('%s_%s_%s_Mt_lep_met_f_rocc'      % (chan, proc, sys), '', 20, 0, 250),
             """

             'b_discr_rest':  TH1D('%s_%s_%s_b_discr_rest'  % (chan, proc, sys), '', 30, 0., 1.),
             'b_discr_med':   TH1D('%s_%s_%s_b_discr_med'   % (chan, proc, sys), '', 30, 0., 1.),
             'b_discr_loose': TH1D('%s_%s_%s_b_discr_loose' % (chan, proc, sys), '', 30, 0., 1.),
             'b_discr_LR':    TH1D('%s_%s_%s_b_discr_LR' % (chan, proc, sys), '', 30, 0., 1.),
             'n_bMjets_hadronFlavour': TH2D('%s_%s_%s_n_bMjets_hadronFlavour'    % (chan, proc, sys), '', 10, 0, 10, 10, 0, 10),

             'tau_jetmatched':         TH1D('%s_%s_%s_tau_jetmatched'    % (chan, proc, sys), '', 3, -1, 2),
             'tau_jetmatched_VS_eta':  TH2D('%s_%s_%s_tau_jetmatched_VS_eta'    % (chan, proc, sys), '', 3, -1, 2, 50, -2.5, 2.5),

             # jet flavours exist only for mc
             # do them up to 30 -- check overflows if there are many
             'jet_flavours_hadron': TH1D('%s_%s_%s_jet_flavours_hadron' % (chan, proc, sys), '', 35, -5, 30),
             'jet_flavours_parton': TH1D('%s_%s_%s_jet_flavours_parton' % (chan, proc, sys), '', 35, -5, 30),
             'lep_genmatch':        TH1D('%s_%s_%s_lep_genmatch'        % (chan, proc, sys), '', 20, -10, 10),
             'tau_genmatch_p':      TH1D('%s_%s_%s_tau_genmatch_p'        % (chan, proc, sys), '', 20, -10, 10),
             'tau_genmatch_n':      TH1D('%s_%s_%s_tau_genmatch_n'        % (chan, proc, sys), '', 20, -10, 10),
             'jet_genmatch':        TH1D('%s_%s_%s_jet_genmatch'        % (chan, proc, sys), '', 20, -10, 10),
             'jet_genmatch_Mb':     TH1D('%s_%s_%s_jet_genmatch_Mb'     % (chan, proc, sys), '', 20, -10, 10),
             'jet_genmatch_Lb':     TH1D('%s_%s_%s_jet_genmatch_Lb'     % (chan, proc, sys), '', 20, -10, 10),
             'jet_genmatch_R':      TH1D('%s_%s_%s_jet_genmatch_R'      % (chan, proc, sys), '', 20, -10, 10),
             'jet_bID_lev':         TH1D('%s_%s_%s_jet_bID_lev'         % (chan, proc, sys), '', 5, 0, 5),

             # parameters of tau
             'tau_ref_Sign': TH1D('%s_%s_%s_tau_ref_Sign'% (chan, proc, sys), '', 44, -1, 10),
             'tau_ref_Leng': TH1D('%s_%s_%s_tau_ref_Leng'% (chan, proc, sys), '', 44, -0.001, 0.01),
             'tau_pat_Sign': TH1D('%s_%s_%s_tau_pat_Sign'% (chan, proc, sys), '', 50, -10, 40),
             'tau_pat_Leng': TH1D('%s_%s_%s_tau_pat_Leng'% (chan, proc, sys), '', 44, -0.01, 0.1),
             'tau_SV_sign':  TH1D('%s_%s_%s_tau_SV_sign'% (chan, proc, sys), '', 50, -5, 20),
             'tau_SV_leng':  TH1D('%s_%s_%s_tau_SV_leng'% (chan, proc, sys), '', 21, -0.1, 1.),
             'tau_jet_bdiscr': TH1D('%s_%s_%s_tau_jet_bdiscr'  % (chan, proc, sys), '', 20, -0.1, 1.1),
             # Dalitz parameters of the tau
             'tau_dalitzes': TH2D('%s_%s_%s_tau_dalitzes' % (chan, proc, sys), '', 20, 0, 2., 20, 0., 2.),
             # correlations to other physical parameters (usually only sign-b and len-energy work)
             'tau_pat_sign_bdiscr':TH2D('%s_%s_%s_tau_pat_sign_bdiscr' % (chan, proc, sys), '', 41, -1, 40, 20, 0., 1.),
             'tau_ref_sign_bdiscr':TH2D('%s_%s_%s_tau_ref_sign_bdiscr' % (chan, proc, sys), '', 44, -1, 10, 20, 0., 1.),
             'tau_sign_bdiscr':TH2D('%s_%s_%s_tau_sign_bdiscr' % (chan, proc, sys), '', 21, -1, 20, 20, 0., 1.),
             'tau_leng_bdiscr':TH2D('%s_%s_%s_tau_leng_bdiscr' % (chan, proc, sys), '', 21, -0.1, 1., 20, 0., 1.),
             'tau_sign_energy':TH2D('%s_%s_%s_tau_sign_energy' % (chan, proc, sys), '', 21, -1,  20., 20, 20., 150.),
             'tau_leng_energy':TH2D('%s_%s_%s_tau_leng_energy' % (chan, proc, sys), '', 21, -0.1, 1., 20, 20., 150.),
             'tau_pat_leng_energy':TH2D('%s_%s_%s_tau_pat_leng_energy' % (chan, proc, sys), '', 44, -0.01,  0.1,  20, 20., 150.),
             'tau_ref_leng_energy':TH2D('%s_%s_%s_tau_ref_leng_energy' % (chan, proc, sys), '', 44, -0.001, 0.01, 20, 20., 150.),
             #'nvtx':        TH1D('%s_%s_%s_nvtx'       % (chan, proc, sys), '', 50, 0, 50),
             'nvtx_raw':    TH1D('%s_%s_%s_nvtx_raw'   % (chan, proc, sys), '', 50, 0, 50),
             'nvtx_gen':    TH1D('%s_%s_%s_nvtx_gen'   % (chan, proc, sys), '', 100, 0, 100),
             # TODO: add rho to ntuples
             'rho':         TH1D('%s_%s_%s_rho'        % (chan, proc, sys), '', 50, 0, 50),

             'njets_event': TH1D('%s_%s_%s_njets_event'% (chan, proc, sys), '', 15, 0, 15),
             'njets':       TH1D('%s_%s_%s_njets'      % (chan, proc, sys), '', 10, 0, 10),
             'njets_all':   TH1D('%s_%s_%s_njets_all'      % (chan, proc, sys), '', 10, 0, 10),
             'nRjets':      TH1D('%s_%s_%s_nRjets'     % (chan, proc, sys), '', 10, 0, 10),
             'nMbjets':     TH1D('%s_%s_%s_nMbjets'    % (chan, proc, sys), '', 5, 0, 5),
             'nLbjets':     TH1D('%s_%s_%s_nLbjets'    % (chan, proc, sys), '', 5, 0, 5),
             'nTBjets':     TH1D('%s_%s_%s_nTBjets'    % (chan, proc, sys), '', 5, 0, 5),
             'nTRjets':     TH1D('%s_%s_%s_nTRjets'    % (chan, proc, sys), '', 5, 0, 5),

             'njets_cats':  TH1D('%s_%s_%s_njets_cats' % (chan, proc, sys), '', 45, 0, 45),
             'ntaus':       TH1D('%s_%s_%s_ntaus'      % (chan, proc, sys), '', 5, 0, 5),

             'met_nRjets':  TH2D('%s_%s_%s_met_nRjets'        % (chan, proc, sys), '', 30, 0, 300, 10, 0, 10),

             # control of tt channels
             #'genproc_id':        TH2D('%s_%s_%s_genproc_id'        % (chan, proc, sys), '', 9, 0, 9, 9, 0, 9),

             #'dijet_mass':  TH1D('%s_%s_%s_dijet_mass'  % (chan, proc, sys), '', 20, 0, 200),
             #'trijet_mass': TH1D('%s_%s_%s_trijet_mass' % (chan, proc, sys), '', 20, 0, 400),
             'dijet_mass':  TH1D('%s_%s_%s_dijet_mass'  % (chan, proc, sys), '', dijet_bins_ext_n, dijet_bins_ext),
             'trijet_mass': TH1D('%s_%s_%s_trijet_mass' % (chan, proc, sys), '', trijet_bins_ext_n, trijet_bins_ext),
             '2D_dijet_trijet':     TH2D('%s_%s_%s_2D_dijet_trijet'     % (chan, proc, sys), '', 20, 0, 200, 20, 0, 300),
             '2D_dijet_trijet_all': TH2D('%s_%s_%s_2D_dijet_trijet_all' % (chan, proc, sys), '', 20, 0, 200, 20, 0, 300),
             #'dijet_trijet_mass':   TH1D('%s_%s_%s_dijet_trijet_mass' % (chan, proc, sys), '', 20, 0, 400),
             'input_has':              TH1D('%s_%s_%s_input_has'       % (chan, proc, sys), '', 7, 0, 7),
             'combination_has':        TH1D('%s_%s_%s_combination_has' % (chan, proc, sys), '', 7, 0, 7),
             'combination_input_have': TH2D('%s_%s_%s_combination_input_have' % (chan, proc, sys), '', 8, 0, 8, 7, 0, 7),
             'lj_gens':             TH1D('%s_%s_%s_lj_gens' % (chan, proc, sys), '', 15, 0, 15),
             'lj_gens_b_gen':       TH1D('%s_%s_%s_lj_gens_b_gen' % (chan, proc, sys), '', 20, -10, 10),
             'lj_gens_w1_gen':      TH1D('%s_%s_%s_lj_gens_w1_gen' % (chan, proc, sys), '', 20, -10, 10),
             'lj_gens_w2_gen':      TH1D('%s_%s_%s_lj_gens_w2_gen' % (chan, proc, sys), '', 20, -10, 10),
             'dijet_trijet_mass':   TH1D('%s_%s_%s_dijet_trijet_mass' % (chan, proc, sys), '', dijet_trijet_bins_ext_n, dijet_trijet_bins_ext),
             'dijet_trijet_mass_N_permutations':        TH1D('%s_%s_%s_dijet_trijet_mass_N_permutations'         % (chan, proc, sys), '', 50, 0, 50),
             'dijet_trijet_mass_N_permutations_passed': TH1D('%s_%s_%s_dijet_trijet_mass_N_permutations_passed'  % (chan, proc, sys), '', 50, 0, 50),
             'dijet_trijet_mass_N_permutations_passed_b1': TH1D('%s_%s_%s_dijet_trijet_mass_N_permutations_passed_b1'  % (chan, proc, sys), '', 50, 0, 50),
             'dijet_trijet_mass_N_permutations_passed_bM': TH1D('%s_%s_%s_dijet_trijet_mass_N_permutations_passed_bM'  % (chan, proc, sys), '', 50, 0, 50),
             'dijet_trijet_mass_vs_permutations':  TH2D('%s_%s_%s_dijet_trijet_mass_vs_permutations' % (chan, proc, sys), '', 20, 0, 400, 50, 0, 50),


             # mass between tau and all non-b jets (to catch the c-jets from W)
             'M_tau_nonb':       TH1D('%s_%s_%s_M_tau_nonb'       % (chan, proc, sys), '', 19, 10, 200),
             'M_tau_nonb_min':   TH1D('%s_%s_%s_M_tau_nonb_min'   % (chan, proc, sys), '', 19, 10, 200),
             'M_tau_nonb_Wdist': TH1D('%s_%s_%s_M_tau_nonb_Wdist' % (chan, proc, sys), '', 19, 10, 200),

             # PU tests
             'lep_pt_pu_sum':     TH1D('%s_%s_%s_lep_pt_pu_sum'     % (chan, proc, sys), '', 20, 0, 200),
             'lep_pt_pu_b'  :     TH1D('%s_%s_%s_lep_pt_pu_b'       % (chan, proc, sys), '', 20, 0, 200),
             'lep_pt_pu_h2' :     TH1D('%s_%s_%s_lep_pt_pu_h2'      % (chan, proc, sys), '', 20, 0, 200),
             'met_pu_sum'   :     TH1D('%s_%s_%s_met_pu_sum'      % (chan, proc, sys), '', 20, 0, 200),
             'met_pu_b'     :     TH1D('%s_%s_%s_met_pu_b'        % (chan, proc, sys), '', 20, 0, 200),
             'met_pu_h2'    :     TH1D('%s_%s_%s_met_pu_h2'       % (chan, proc, sys), '', 20, 0, 200),
             'Mt_lep_met_f_pu_sum':     TH1D('%s_%s_%s_Mt_lep_met_f_pu_sum'       % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_pu_b'  :     TH1D('%s_%s_%s_Mt_lep_met_f_pu_b'       % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_pu_h2' :     TH1D('%s_%s_%s_Mt_lep_met_f_pu_h2'       % (chan, proc, sys), '', 20, 0, 250),
             # control distrs for effect of different weights
             'Mt_lep_met_f_init':       TH1D('%s_%s_%s_Mt_lep_met_f_init'       % (chan, proc, sys), '', 20, 0, 250),
             'nvtx_init':               TH1D('%s_%s_%s_nvtx_init'               % (chan, proc, sys), '', 50, 0, 50),
             #sys_weight = weight * weight_bSF * weight_PU * weight_top_pt
             'nvtx_w_trk_b':            TH1D('%s_%s_%s_nvtx_w_trk_b'            % (chan, proc, sys), '', 50, 0, 50),
             'nvtx_w_trk_h':            TH1D('%s_%s_%s_nvtx_w_trk_h'            % (chan, proc, sys), '', 50, 0, 50),
             'Mt_lep_met_f_w_in':       TH1D('%s_%s_%s_Mt_lep_met_f_w_in'       % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_mu_trk_b': TH1D('%s_%s_%s_Mt_lep_met_f_w_mu_trk_b' % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_mu_trk_h': TH1D('%s_%s_%s_Mt_lep_met_f_w_mu_trk_h' % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_pu':       TH1D('%s_%s_%s_Mt_lep_met_f_w_pu'       % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_pu_sum':   TH1D('%s_%s_%s_Mt_lep_met_f_w_pu_sum'   % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_pu_mu':    TH1D('%s_%s_%s_Mt_lep_met_f_w_pu_mu'    % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_pu_el':    TH1D('%s_%s_%s_Mt_lep_met_f_w_pu_el'    % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_pu_mu_dn': TH1D('%s_%s_%s_Mt_lep_met_f_w_pu_mu_dn' % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_pu_el_dn': TH1D('%s_%s_%s_Mt_lep_met_f_w_pu_el_dn' % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_pu_mu_up': TH1D('%s_%s_%s_Mt_lep_met_f_w_pu_mu_up' % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_pu_el_up': TH1D('%s_%s_%s_Mt_lep_met_f_w_pu_el_up' % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_bf':       TH1D('%s_%s_%s_Mt_lep_met_f_w_bf'       % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_bf_min':   TH1D('%s_%s_%s_Mt_lep_met_f_w_bf_min'   % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_f_w_tp':       TH1D('%s_%s_%s_Mt_lep_met_f_w_tp'       % (chan, proc, sys), '', 20, 0, 250),

             #'bdiscr_max':       TH1D('%s_%s_%s_b_discr_max'      % (chan, proc, sys), '', 30, 0, 300),
             #'dphi_lep_met': TH1D('%s_%s_%s_dphi_lep_met' % (chan, proc, sys), '', 20, -3.2, 3.2),
             #'cos_dphi_lep_met': TH1D('%s_%s_%s_cos_dphi_lep_met' % (chan, proc, sys), '', 20, -1.1, 1.1),
             # relIso for the QCD anti-iso region
             'lep_relIso_el':       TH1D('%s_%s_%s_lep_relIso_el'     % (chan, proc, sys), '', lep_relIso_el_bins_n,     lep_relIso_el_bins),
             'lep_relIso_el_ext':   TH1D('%s_%s_%s_lep_relIso_el_ext' % (chan, proc, sys), '', lep_relIso_el_bins_ext_n, lep_relIso_el_bins_ext),
             'lep_relIso':          TH1D('%s_%s_%s_lep_relIso'     % (chan, proc, sys), '', lep_relIso_bins_n,     lep_relIso_bins),
             'lep_relIso_ext':      TH1D('%s_%s_%s_lep_relIso_ext' % (chan, proc, sys), '', lep_relIso_bins_ext_n, lep_relIso_bins_ext),
             'lep_relIso_precise':  TH1D('%s_%s_%s_lep_relIso_precise' % (chan, proc, sys), '', 300, 0., 0.3), # around the cut of 0.125-0.15
             #'Mt_lep_met_f_mth':   TH1D('%s_%s_%s_Mt_lep_met_f_mth'   % (chan, proc, sys), '', 20, 0, 250),
             #'Mt_lep_met_f_cos':   TH1D('%s_%s_%s_Mt_lep_met_f_cos'   % (chan, proc, sys), '', 20, 0, 250),
             #'Mt_lep_met_f_cos_c': TH1D('%s_%s_%s_Mt_lep_met_f_cos_c' % (chan, proc, sys), '', 20, 0, 250),
             #'Mt_lep_met_f_c':     TH1D('%s_%s_%s_Mt_lep_met_f_c'     % (chan, proc, sys), '', 20, 0, 250),
             #'Mt_lep_met_f_test':  TH1D('%s_%s_%s_Mt_lep_met_f_test'  % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_zero':           TH1D('%s_%s_%s_Mt_lep_met_zero'       % (chan, proc, sys), '', 20, 0, 20),
             'Mt_lep_met_METfilters':     TH1D('%s_%s_%s_Mt_lep_met_METfilters' % (chan, proc, sys), '', 20, 0, 20),

             'met_VS_Mt_lep_met_f':       TH2D('%s_%s_%s_met_VS_Mt_lep_met_f'   % (chan, proc, sys), '', 15, 0, 300, 10, 0, 250),
             'Mt_lep_met_t1':             TH1D('%s_%s_%s_Mt_lep_met_t1'         % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_t2':             TH1D('%s_%s_%s_Mt_lep_met_t2'         % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_t3':             TH1D('%s_%s_%s_Mt_lep_met_t3'         % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_t4':             TH1D('%s_%s_%s_Mt_lep_met_t4'         % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_t5':             TH1D('%s_%s_%s_Mt_lep_met_t5'         % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_t6':             TH1D('%s_%s_%s_Mt_lep_met_t6'         % (chan, proc, sys), '', 20, 0, 250),
             # Mt per different n jets
             'Mt_lep_met_lessjets':       TH1D('%s_%s_%s_Mt_lep_met_lessjets'   % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_0L2M':           TH1D('%s_%s_%s_Mt_lep_met_0L2M'       % (chan, proc, sys), '', 20, 0, 250),
             'Mt_lep_met_0L2Mnot':        TH1D('%s_%s_%s_Mt_lep_met_0L2Mnot'    % (chan, proc, sys), '', 20, 0, 250),
             'met_0L2M':           TH1D('%s_%s_%s_met_0L2M'          % (chan, proc, sys), '', 30, 0, 300),
             'met_0L2Mnot':        TH1D('%s_%s_%s_met_0L2Mnot'       % (chan, proc, sys), '', 30, 0, 300),
             'met_lessjets':       TH1D('%s_%s_%s_met_lessjets'      % (chan, proc, sys), '', 30, 0, 300),
             'met_lessjets_init':  TH1D('%s_%s_%s_met_lessjets_init' % (chan, proc, sys), '', 30, 0, 300),

             'Mt_lep_met_f_VS_nvtx':      TH2D('%s_%s_%s_Mt_lep_met_f_VS_nvtx'  % (chan, proc, sys), '', 20, 0, 250, 50, 0, 50),
             'Mt_lep_met_f_VS_nvtx_gen':  TH2D('%s_%s_%s_Mt_lep_met_f_VS_nvtx_gen' % (chan, proc, sys), '', 20, 0, 250, 50, 0, 50),

             'control_init_weight': TH1D('%s_%s_%s_control_init_weight' % (chan, proc, sys), '', 150, 0., 1.5),
             'control_bSF_weight':  TH1D('%s_%s_%s_control_bSF_weight'  % (chan, proc, sys), '', 150, 0., 1.5),
             'control_bSF_weight_applied':  TH1D('%s_%s_%s_control_bSF_weight_applied'  % (chan, proc, sys), '', 150, 0., 1.5),
             'control_PU_weight':   TH1D('%s_%s_%s_control_PU_weight'   % (chan, proc, sys), '', 150, 0., 1.5),
             'control_th_weight':   TH1D('%s_%s_%s_control_th_weight'   % (chan, proc, sys), '', 150, 0., 1.5),
             'control_top_weight':  TH1D('%s_%s_%s_control_top_weight'  % (chan, proc, sys), '', 150, 0., 1.5),
             'control_rec_weight':  TH1D('%s_%s_%s_control_rec_weight'  % (chan, proc, sys), '', 150, 0., 1.5),
             })

        return (chan, proc, sys), distrs

    print "to systs"
    out_hs = OrderedDict([format_distrs(chan, proc, sys)
         for chan, ((procs, _), systs) in selected_channels.items() for proc in procs for sys in systs if sys != 'PDF_TRIGGER'])

    print "passed non-PDF systs"
    # add pdf uncertainties where requiested
    def pdf_sys_name_up(number):
        return 'PDFCT14n%dUp' % i
    def pdf_sys_name_down(number):
        return 'PDFCT14n%dDown' % i

    if with_PDF_sys:
        #pdf_sys_names_Up   = ['PDFCT14n%dUp'   % i for i in range(1,57)]
        #pdf_sys_names_Down = ['PDFCT14n%dDown' % i for i in range(1,57)]
        print "making PDF systs"
        for chan, ((procs, _), systs) in selected_channels.items():
          for proc in procs:
            for sys in systs:
                if sys != 'PDF_TRIGGER':
                    continue
                # create PDF-varied target histograms
                # for 56 CT14 (not nominal) members
                for i in range(1,57):
                    out_hs.update(OrderedDict([format_distrs(chan, proc, sys_name) for sys_name in ('PDFCT14n%dUp' % i, 'PDFCT14n%dDown' % i)]))
    print "passed PDF systs"

    # strange, getting PyROOT_NoneObjects from these after output
    for _, histos in out_hs.items():
        for h in histos.values():
            h.SetDirectory(0)

    '''
    for d, histos in out_hs.items():
        for name, histo in histos.items():
            print(d, name)
            histo.Print()
    '''

    logger.write("N entries: %d\n" % tree.GetEntries())
    #if not range_max or range_max > tree.GetEntries():
        #range_mas = tree.GetEntries()

    profile = cProfile.Profile()
    profile.enable()
    #for iev in range(range_min, range_max): # root sucks
    for iev, ev in enumerate(tree):
        '''
        HLT_el && abs(leps_ID) == 11 && abs(lep0_p4.eta()) < 2.4 && lep0_dxy <0.01 && lep0_dz<0.02 && njets > 2 && met_corrected.pt() > 40 && nbjets > 0
        '''

        '''
        scheme:

        dtag -> process [subprocesses]
        for event:
            for each SYS -> jet_pts, tau_pts, weight
                which (reco) [channels] it passes
                find (gen) subprocess <------! different subprocess def-s for diff channels
                record distr-s for each
        '''

        #if iev > 10000: break
        control_counters.Fill(0)

        # NUP stitching for WJets
        if isWJetsInclusive and DO_W_STITCHING:
            if ev.gen_NUP > 5: continue

        #if iev <  range_min: continue
        #if iev >= 10: break
        #ev = tree.GetEntry(iev)

        '''
        # plug roccor right here
        #roccor_factor = 1.
        for i in range(len(ev.lep_id)):
            if abs(ev.lep_id[i]) == 13:
                #Q = c_int(ev.lep_id > 0)
                #pt = c_double(ev.lep_p4[i].pt())
                #eta = c_double(ev.lep_p4[i].eta())
                #phi = c_double(ev.lep_p4[i].phi())
                ##nl = c_int(ev.lep_N_trackerLayersWithMeasurement[i])
                #nl = c_int(14)
                #genPt = pt
                #u1 = c_double(0.5)
                #u2 = c_double(0.5)
                #s = c_int(0)
                #m = c_int(0)

                #
                Q = int(ev.lep_id > 0)
                pt  = ev.lep_p4[i].pt()
                eta = ev.lep_p4[i].eta()
                phi = ev.lep_p4[i].phi()
                #nl = ev.lep_N_trackerLayersWithMeasurement[i]
                nl = 12 # average in data and mc
                genPt = pt # TODO add this
                u1 = u_random() #0.5
                u2 = u_random() #0.5
                s = 0
                m = 0

                #if isMC and ev.lep_matching_gen[i]:
                #    #roccor_factor = roccors.wrapper_kScaleFromGenMC(Q, pt, eta, phi, nl, genPt, u1, s, m)
                #    roccor_factor = roccors.kScaleFromGenMC(Q, pt, eta, phi, nl, genPt, u1, s, m)
                #elif isMC and not ev.lep_matching_gen[i]:
                #    #roccor_factor = roccors.wrapper_kScaleAndSmearMC(Q, pt, eta, phi, nl, u1, u2, s, m)
                #    roccor_factor = roccors.kScaleAndSmearMC(Q, pt, eta, phi, nl, u1, u2, s, m)
                #else:
                #    #roccor_factor = roccors.wrapper_kScaleDT(Q, pt, eta, phi, s, m)
                #    roccor_factor = roccors.kScaleDT(Q, pt, eta, phi, s, m)

                ##ev.lep_p4[i] *= roccor_factor
                #control_hs['roccor_factor'].Fill(roccor_factor)
        '''

        if not isMC:
            if not (ev.pass_basic_METfilters and ev.METfilterbadChCand and ev.METfilterbadPFMuon):
                continue

        # the lepton requirements for all 1-lepton channels:
        # do relIso on 1/8 = 0.125, and "all iso" for QCD anti-iso factor

        # I'll make the iso distribution and get the factor over whole range
        pass_mu_id = abs(ev.leps_ID) == 13 and ev.HLT_mu and ev.lep_matched_HLT[0] and ev.no_iso_veto_leps
        pass_el_id = abs(ev.leps_ID) == 11 and ev.HLT_el and ev.lep_matched_HLT[0] and ev.no_iso_veto_leps

        if abs(ev.leps_ID) == 13:    control_counters.Fill(1)
        if abs(ev.leps_ID) == 13 and ev.HLT_mu:  control_counters.Fill(2)
        if abs(ev.leps_ID) == 13 and ev.HLT_mu and ev.lep_matched_HLT[0]:  control_counters.Fill(3)
        if abs(ev.leps_ID) == 13 and ev.HLT_mu and ev.lep_matched_HLT[0] and ev.no_iso_veto_leps:  control_counters.Fill(4)

        if abs(ev.leps_ID) == 11:    control_counters.Fill(6)
        if abs(ev.leps_ID) == 11 and ev.HLT_el:  control_counters.Fill(7)
        if abs(ev.leps_ID) == 11 and ev.HLT_el and ev.lep_matched_HLT[0]:  control_counters.Fill(8)
        if abs(ev.leps_ID) == 11 and ev.HLT_el and ev.lep_matched_HLT[0] and ev.no_iso_veto_leps:  control_counters.Fill(9)

        # impacts are embedded into ID procedure, no need to repeate them here, TODO: re-check
        # for mu suggested dB is 5mm dz and 2mm dxy
        # for el suggested dB 0.02 cm
        #pass_mu_impact = ev.lep_dz[0] < 0.5 and ev.lep_dxy[0] < 0.2
        #pass_el_impact = ev.lep_dB[0] < 0.02

        # for el the suggested relIso 0.0588 for barrel, 0.0571 for endcaps
        # data shows it does not matter
        pass_mu_iso = pass_mu_id and ev.lep_relIso[0] < 0.15  
        pass_el_iso = pass_el_id and ev.lep_relIso[0] < 0.0588

        # 1GeV above HLT pt
        # ele eta gap
        # suggested minimal offline
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideMuonIdRun2#2016_Data
        # pt > 25, eta < 2.4
        pass_mu_kino = pass_mu_id and ev.lep_p4[0].pt() > 26. and abs(ev.lep_p4[0].eta()) < 2.4
        #pass_mu_kino = pass_mu_id and ev.lep_p4[0].pt() * roccor_factor > 26. and abs(ev.lep_p4[0].eta()) < 2.4
        pass_el_kino = pass_el_id and ev.lep_p4[0].pt() > 30. and abs(ev.lep_p4[0].eta()) < 2.4 and (abs(ev.lep_p4[0].eta()) < 1.4442 or abs(ev.lep_p4[0].eta()) > 1.5660)

        # (did) for optimization testing minimum pt cut --- review it after test results
        #    -- significant discrepancy at lowest lep pt bin -> UP 1 GeV from HLT and added a detailed distr of the trun on curve
        #    -- it seems the discrepancy were comming from trigger SF going down to 26 only -- fixed that, testing now

        pass_mu     = pass_mu_id and pass_mu_kino and pass_mu_iso # and pass_mu_impact
        pass_el     = pass_el_id and pass_el_kino and pass_el_iso

        if pass_el_id:    control_counters.Fill(11)
        if pass_el_iso:   control_counters.Fill(12)
        if pass_el_kino:  control_counters.Fill(13)
        if pass_el:       control_counters.Fill(14)

        if pass_mu_id:    control_counters.Fill(16)
        if pass_mu_iso:   control_counters.Fill(17)
        if pass_mu_kino:  control_counters.Fill(18)
        if pass_mu:       control_counters.Fill(19)

        # do this in place for the required selection
        #pass_mu_cuts = pass_mu and ev.lep_p4[0].pt() > 25. # so, it's smaller than the old cut 27 GeV

        #pass_mu_all = pass_mu_id_kino and ev.lep_relIso[0] >= 0.125

        pass_mu_id_all = abs(ev.leps_ID_allIso) == 13 and ev.HLT_mu and ev.lep_alliso_matched_HLT[0] and ev.nleps_veto_mu_all == 0 and ev.nleps_veto_el_all == 0
        pass_el_id_all = abs(ev.leps_ID_allIso) == 11 and ev.HLT_el and ev.lep_alliso_matched_HLT[0] and ev.nleps_veto_el_all == 0 and ev.nleps_veto_mu_all == 0

        pass_mu_kino_all = pass_mu_id_all and ev.lep_alliso_p4[0].pt() > 26. and abs(ev.lep_alliso_p4[0].eta()) < 2.4
        pass_el_kino_all = pass_el_id_all and ev.lep_alliso_p4[0].pt() > 30. and abs(ev.lep_alliso_p4[0].eta()) < 2.4 and (abs(ev.lep_alliso_p4[0].eta()) < 1.4442 or abs(ev.lep_alliso_p4[0].eta()) > 1.5660)

        pass_mu_all = pass_mu_id_all and pass_mu_kino_all
        pass_el_all = pass_el_id_all and pass_el_kino_all

        #pass_mu = pass_mu_id_kino and ev.lep_relIso[0] < 0.125
        #pass_el_all = pass_el_id and ev.lep_p4[0].pt() > 27. and abs(ev.lep_p4[0].eta()) < 2.4
        #pass_el     = pass_el_id and ev.lep_p4[0].pt() > 27. and abs(ev.lep_p4[0].eta()) < 2.4 and ev.lep_relIso[0] < 0.125

        # TODO: need to check the trigger SF-s then......
        # for now I'm just trying to get rid of el-mu mix in MC
        #pass_elmu = ev.leps_ID == -11*13 and ev.HLT_mu and not ev.HLT_el and ev.no_iso_veto_leps and \
        pass_elmu_id = ev.leps_ID == -11*13 and ev.HLT_mu and ev.lep_matched_HLT[0] and ev.no_iso_veto_leps and \
            (ev.lep_p4[0].pt() > 30 and abs(ev.lep_p4[0].eta()) < 2.4) and \
            (ev.lep_p4[1].pt() > 30 and abs(ev.lep_p4[1].eta()) < 2.4)

        #   (ev.lep_matched_HLT[0] if abs(ev.lep_id[0]) == 13 else ev.lep_matched_HLT[1]) and \

        #pass_elmu = pass_elmu_id and ((ev.lep_relIso[0] < 0.15 and ev.lep_relIso[1] < 0.0588) if abs(ev.lep_id[0]) == 13 else (ev.lep_relIso[1] < 0.15 and ev.lep_relIso[0] < 0.0588))

        # these are done in NT
        pass_elmu = pass_elmu_id
        # both HLTs
        #pass_elmu = pass_elmu_id and ev.lep_matched_HLT[0] and ev.HLT_el and ev.lep_matched_HLT[1]

        pass_elmu_el = ev.leps_ID == -11*13 and ev.HLT_el and ev.no_iso_veto_leps and \
            (ev.lep_matched_HLT[0] if abs(ev.lep_id[0]) == 11 else ev.lep_matched_HLT[1]) and \
            (ev.lep_p4[0].pt() > 30 and abs(ev.lep_p4[0].eta()) < 2.4) and \
            (ev.lep_p4[1].pt() > 30 and abs(ev.lep_p4[1].eta()) < 2.4)

        pass_mumu = ev.leps_ID == -13*13 and (ev.HLT_mu) and (ev.lep_matched_HLT[0] or ev.lep_matched_HLT[1]) and ev.no_iso_veto_leps and \
            (ev.lep_p4[0].pt() > 30 and abs(ev.lep_p4[0].eta()) < 2.4) and \
            (ev.lep_p4[1].pt() > 30 and abs(ev.lep_p4[1].eta()) < 2.4)

        pass_elel = ev.leps_ID == -11*11 and (ev.HLT_el) and (ev.lep_matched_HLT[0] or ev.lep_matched_HLT[1]) and ev.no_iso_veto_leps and \
            (ev.lep_p4[0].pt() > 30 and abs(ev.lep_p4[0].eta()) < 2.4) and \
            (ev.lep_p4[1].pt() > 30 and abs(ev.lep_p4[1].eta()) < 2.4)

        pass_mumu_ss = ev.leps_ID == 13*13 and (ev.HLT_mu) and (ev.lep_matched_HLT[0] or ev.lep_matched_HLT[1]) and ev.no_iso_veto_leps and \
            (ev.lep_p4[0].pt() > 30 and abs(ev.lep_p4[0].eta()) < 2.4) and \
            (ev.lep_p4[1].pt() > 30 and abs(ev.lep_p4[1].eta()) < 2.4)

        if pass_elmu:    control_counters.Fill(21)
        if pass_mumu:    control_counters.Fill(22)
        if pass_elel:    control_counters.Fill(23)
        if pass_el_all:  control_counters.Fill(24)
        if pass_mu_all:  control_counters.Fill(25)

        # minimum possible pt threshold -- 24 GeV, = to HLT and recorded in Ntupler
        pass_mu_id_iso = pass_mu_id and pass_mu_iso
        pass_min_mu     = pass_mu_id_iso and abs(ev.lep_p4[0].eta()) < 2.4 and ev.lep_relIso[0] < 0.125
        pass_min_mu_all = pass_mu_id_iso and abs(ev.lep_p4[0].eta()) < 2.4 and ev.lep_relIso[0] >= 0.125

        # 1-lep channels, 2mu DY and el-mu ttbar, and anti-iso
        #if not (pass_min_mu or pass_min_mu_all or pass_mu_all or pass_mu or pass_el_all or pass_el or pass_mumu or pass_mumu_ss or pass_elmu): continue
        #passes = pass_min_mu or pass_min_mu_all or pass_mu_all or pass_mu or pass_el or pass_mumu or pass_mumu_ss or pass_elmu or pass_mu_id_iso
        # OPTIMIZATION tests are done only on pass_mu
        #passes_optimized = pass_mu_all or pass_el_all or pass_mumu or pass_elmu
        passes_optimized = pass_mu or pass_el or pass_mumu or pass_elmu or pass_mu_all or pass_el_all or pass_elel
        event_passes = pass_mu or pass_el # pass_elmu # or pass_elmu_el # pass_mumu or pass_elel # pass_el # or pass_elmu_el # pass_mu or pass_el # passes_optimized #

        if pass_elmu or pass_elmu_el or pass_mumu or pass_elel:
            # check dR of leptons
            tlep0_p4 = TLorentzVector(ev.lep_p4[0].X(), ev.lep_p4[0].Y(), ev.lep_p4[0].Z(), ev.lep_p4[0].T())
            tlep1_p4 = TLorentzVector(ev.lep_p4[1].X(), ev.lep_p4[1].Y(), ev.lep_p4[1].Z(), ev.lep_p4[1].T())
            if not tlep0_p4.DeltaR(tlep1_p4) > 0.3:
                continue

        if not event_passes: continue
        control_counters.Fill(51)

        pass_mus = pass_mu_all or pass_mu or pass_elmu or pass_mumu # or pass_mumu_ss
        # also at least some kind of tau in single-el:
        #if (pass_mu or pass_el) and (not ev.tau_p4.size() > 0): continue # this is the only thing reduces computing
        passed_ele_event = pass_el or pass_el_all or pass_elel or pass_elmu_el

        micro_proc = ''

        # expensive calls and they don't depend on systematics now
        if doRecoilCorrections:
            #def transverse_mass_pts(v1_x, v1_y, v2_x, v2_y):
            #met_x = ev.pfmetcorr_ex
            #met_y = ev.pfmetcorr_ey
            # no, recalculated them

            met_x = ROOT.met_pt_recoilcor_x(
                #ev.met_corrected.Px(),
                #ev.met_corrected.Py(),
                # RECORRECTED
                ev.met_init.Px(), # uncorrected type I pf met px (float)
                ev.met_init.Py(), # uncorrected type I pf met py (float)
                ev.gen_genPx, # generator Z/W/Higgs px (float)
                ev.gen_genPy, # generator Z/W/Higgs py (float)
                ev.gen_visPx, # generator visible Z/W/Higgs px (float)
                ev.gen_visPy, # generator visible Z/W/Higgs py (float)
                0  # max recoil (I checked that -- plot in scrap/recoil-corrections-study)
                #ev.nalljets  # number of jets (hadronic jet multiplicity) (int) <-- they use jets with pt>30... here it's the same, only pt requirement (20), no eta or PF ID
                )

            met_y = ROOT.met_pt_recoilcor_y(
                #ev.met_corrected.Px(),
                #ev.met_corrected.Py(),
                ev.met_init.Px(), # uncorrected type I pf met px (float)
                ev.met_init.Py(), # uncorrected type I pf met py (float)
                ev.gen_genPx, # generator Z/W/Higgs px (float)
                ev.gen_genPy, # generator Z/W/Higgs py (float)
                ev.gen_visPx, # generator visible Z/W/Higgs px (float)
                ev.gen_visPy, # generator visible Z/W/Higgs py (float)
                0
                #ev.nalljets  # number of jets (hadronic jet multiplicity) (int) <-- they use jets with pt>30... here it's the same, only pt requirement (20), no eta or PF ID
                )

            #Mt_lep_met_c   = ROOT.MTlep_met_pt_recoilcor(ev.lep_p4[0].Px(), ev.lep_p4[0].Py(), ev.met_corrected.Px(), ev.met_corrected.Py(), ev.gen_genPx, ev.gen_genPy, ev.gen_visPx, ev.gen_visPy, 0)
            #Mt_lep_met = transverse_mass_pts(ev.lep_p4[0].Px(), ev.lep_p4[0].Py(), ev.pfmetcorr_ex, ev.pfmetcorr_ey)
            #Mt_tau_met_nominal = transverse_mass_pts(ev.tau_p4[0].Px(), ev.tau_p4[0].Py(), ev.pfmetcorr_ex, ev.pfmetcorr_ey)
            # TODO: tau is corrected with systematic ES

        elif not isMC:
            met_x = ev.met_slimmedMETsMuEGClean.Px()
            met_y = ev.met_slimmedMETsMuEGClean.Py()
        # to test: is it = met_init

        else:
            #met_x = ev.met_corrected.Px()
            #met_y = ev.met_corrected.Py()
            # RECORRECTED
            # use miniaod met and jets, reapply corrections of the passed jets to met
            met_x = ev.met_init.Px()
            met_y = ev.met_init.Py()
            # NOMINAL NTUPLE CORRECTED
            #met_x = ev.met_corrected.Px()
            #met_y = ev.met_corrected.Py()

            #Mt_lep_met_c   = ROOT.MTlep_c(ev.lep_p4[0].Px(), ev.lep_p4[0].Py(), ev.met_corrected.Px(), ev.met_corrected.Py())
            #Mt_lep_met_test = transverse_mass_pts(ev.lep_p4[0].Px(), ev.lep_p4[0].Py(), met_x, met_y)
            #Mt_lep_met = transverse_mass(ev.lep_p4[0], ev.met_corrected)
            #Mt_tau_met = transverse_mass(ev.tau_p4[0], ev.met_corrected)
            #Mt_tau_met_nominal = transverse_mass_pts(ev.tau_p4[0].Px(), ev.tau_p4[0].Py(), ev.met_corrected.Px(), ev.met_corrected.Py())
        # also
        #Mt_lep_met_d = (ev.lep_p4[0] + ev.met_corrected).Mt()

        proc_met         = LorentzVector('ROOT::Math::PxPyPzE4D<double>')(met_x, met_y, 0., 0.)
        proc_met_JERUp   = LorentzVector('ROOT::Math::PxPyPzE4D<double>')(met_x, met_y, 0., 0.)
        proc_met_JERDown = LorentzVector('ROOT::Math::PxPyPzE4D<double>')(met_x, met_y, 0., 0.)
        proc_met_JESUp   = LorentzVector('ROOT::Math::PxPyPzE4D<double>')(met_x, met_y, 0., 0.)
        proc_met_JESDown = LorentzVector('ROOT::Math::PxPyPzE4D<double>')(met_x, met_y, 0., 0.)
        proc_met_lepsub  = LorentzVector('ROOT::Math::PxPyPzE4D<double>')(met_x, met_y, 0., 0.)

        # from PU tests, leaving it here for now
        if not isMC:
            weight_pu_sum = 1.
            weight_pu_b = 1.
            weight_pu_h2 = 1.

        weight = 1. # common weight of event (1. for data)
        weight_pu = 1.
        #weights_th = namedtuple('th_weights', 'AlphaSUp AlphaSDown FragUp FragDown')
        #weights_th = (1., 1., 1., 1.)
        weights_gen_weight_alphas = (1., 1.)
        weights_Frag   = (1., 1.)
        weights_gen_weight_centralFrag   = 1.
        if isMC:
            try:
                weight_pu_el    = pileup_ratio_ele     [ev.nvtx_gen]
                weight_pu_el_up = pileup_ratio_up_ele  [ev.nvtx_gen]
                weight_pu_el_dn = pileup_ratio_down_ele[ev.nvtx_gen]
                weight_pu_mu    = pileup_ratio[ev.nvtx_gen]
                weight_pu_mu_up = pileup_ratio_up[ev.nvtx_gen]
                weight_pu_mu_dn = pileup_ratio_down[ev.nvtx_gen]
                if passed_ele_event:
                    weight_pu    = weight_pu_el   
                    weight_pu_up = weight_pu_el_up
                    weight_pu_dn = weight_pu_el_dn
                    control_hs['weight_pu_el']   .Fill(weight_pu)
                    control_hs['weight_pu_el_up'].Fill(weight_pu_up)
                    control_hs['weight_pu_el_dn'].Fill(weight_pu_dn)
                else:
                    weight_pu    = weight_pu_mu   
                    weight_pu_up = weight_pu_mu_up
                    weight_pu_dn = weight_pu_mu_dn
                    control_hs['weight_pu_mu']   .Fill(weight_pu)
                    control_hs['weight_pu_mu_up'].Fill(weight_pu_up)
                    control_hs['weight_pu_mu_dn'].Fill(weight_pu_dn)
                # and the new PU-s
                weight_pu_sum  = pileup_ratio_sum[ev.nvtx_gen]
                weight_pu_b    = pileup_ratio_b[ev.nvtx_gen]
                weight_pu_h2   = pileup_ratio_h2[ev.nvtx_gen]
                control_hs['weight_pu_sum'] .Fill(weight_pu_sum)
                control_hs['weight_pu_b']   .Fill(weight_pu_b)
                control_hs['weight_pu_h2']  .Fill(weight_pu_h2)
            except:
                #print i, ev.nvtx
                continue

            if aMCatNLO and ev.aMCatNLO_weight < 0:
                weight *= -1

            weight_z_mass_pt = 1.
            if isDY:
                # float zPtMass_weight(float genMass, float genPt)
                weight_z_mass_pt *= zPtMass_weight(ev.genMass, ev.genPt)
                weight *= weight_z_mass_pt
                # DY has this trick, which I had to solve cleanly in ntuples
                # but I just dumped all info downstream..
                # it might have actual Z particle in decay chain
                # or not (and no gamma too) -- then you judge from "prompt" leptons
                # the mutually exclusive case never appears
                if ev.gen_N_zdecays > 0:
                    lep1_id = abs(ev.gen_zdecays_IDs[0])
                    lep2_id = abs(ev.gen_zdecays_IDs[1])
                else:
                    # check prompt leptns
                    # if no Z decay the leptons are there
                    lep1_id = abs(ev.gen_pythia8_prompt_leptons_IDs[0])
                    lep2_id = abs(ev.gen_pythia8_prompt_leptons_IDs[1])
                # TODO: actually track tau decays fro DY? -- no need, it's a small background
                if lep1_id >= 15 and lep2_id >= 15:
                    proc = 'dy_tautau'
                else:
                    proc = 'dy_other'

            if isWJets:
                if ev.gen_N_wdecays > 0:
                    lep1_id = abs(ev.gen_wdecays_IDs[0])
                #W does not need these prompt leptons, but I keep them just in case
                else:
                    # check prompt leptns
                    lep1_id = abs(ev.gen_pythia8_prompt_leptons_IDs[0])
                if lep1_id >= 15*15:
                    proc = 'wjets_tauh'
                elif lep1_id >= 15: # 15*11 and 15*13
                    proc = 'wjets_taul'
                # we use only WToLNu now, W->j does not happen
                #elif lep1_id == 1:
                #    proc = 'wjets_j'
                else:
                    proc = 'wjets'

            weight_top_pt = 1.
            # "Only top quarks in SM ttbar events must be reweighted, not single tops or tops from BSM production mechanisms."
            # https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopPtReweighting
            if isTT:
                # th weights if needed
                if with_AlphaS_sys:
                    #weights_gen_weight_norm = ev.gen_weight_norm
                    # weight_norm = 1 always
                    weights_gen_weight_alphas = (ev.gen_weight_alphas_1, ev.gen_weight_alphas_2)
                    # norm to average
                    #weights_gen_weight_norm = (weights_gen_weight_alphas[0] + weights_gen_weight_alphas[1]) / 2
                    weights_gen_weight_norm = ev.gen_weights_pdf_hessians[0]
                    # norm is the nominal PDF
                    if 0. <= weights_gen_weight_norm < 0.00001:
                        weights_gen_weight_norm = 0.00001
                    elif 0. > weights_gen_weight_norm > -0.00001:
                        weights_gen_weight_norm = -0.00001

                    #control_hs['weights_gen_weight_norm']   .Fill(ev.gen_weight_too)
                    control_hs['weights_gen_weight_too']        .Fill(ev.gen_weight_too)
                    control_hs['weights_gen_weight_norm']       .Fill(ev.gen_weight_norm)
                    control_hs['weights_gen_weight_average']    .Fill(weights_gen_weight_norm)
                    control_hs['weights_gen_weight_alphasUp']   .Fill(weights_gen_weight_alphas[0])
                    control_hs['weights_gen_weight_alphasDown'] .Fill(weights_gen_weight_alphas[1])

                    weights_gen_weight_alphas_up = weights_gen_weight_alphas[0] / weights_gen_weight_norm
                    weights_gen_weight_alphas_dn = weights_gen_weight_alphas[1] / weights_gen_weight_norm

                    # sane high weight in tt->taumu tauh as in pdfs
                    if weights_gen_weight_alphas_up > 2.:
                        weights_gen_weight_alphas_up = 1.
                    if weights_gen_weight_alphas_dn > 2.:
                        weights_gen_weight_alphas_dn = 1.

                if with_Frag_sys:
                    weights_gen_weight_centralFrag = ev.gen_weight_centralFrag if ev.gen_weight_centralFrag > 0. else 0.00001
                    weights_gen_weight_Frag = (ev.gen_weight_FragUp, ev.gen_weight_FragDown)
                    weights_gen_weight_semilepbr = (ev.gen_weight_semilepbrUp, ev.gen_weight_semilepbrDown)
                    weights_gen_weight_Peterson = ev.gen_weight_PetersonFrag
                    # sub to this naming in the following ntuple runs:
                    #weights_gen_weight_Frag = (ev.gen_weight_FragUp, ev.gen_weight_FragDown)
                    control_hs['weights_gen_weight_centralFrag']   .Fill(weights_gen_weight_centralFrag)
                    control_hs['weights_gen_weight_FragUp']   .Fill(weights_gen_weight_Frag[0])
                    control_hs['weights_gen_weight_FragDown'] .Fill(weights_gen_weight_Frag[1])
                    control_hs['weights_gen_weight_Peterson'] .Fill(weights_gen_weight_Peterson)
                    control_hs['weights_gen_weight_semilepbrUp']   .Fill(weights_gen_weight_semilepbr[0])
                    control_hs['weights_gen_weight_semilepbrDown'] .Fill(weights_gen_weight_semilepbr[1])

                if with_MEscale_sys:
                    """ these are calculated "with respect to the sum of nominal weights":
                      > Depending on the case, one may want to normalize the per-event weights
                      > to the sum of weights corresponding to the default scale choice...
                        i.e. they are not per-event normalized to the nominal weight
                        but they are normalized afterwards to the overall weight, i.e. to the average of the nominal
                    """
                    weights_gen_weight_nom   = ev.gen_weights_renorm_fact[MUf_nom_MUr_nom] if ev.gen_weights_renorm_fact[MUf_nom_MUr_nom] > 0. else 0.00001
                    weights_gen_weight_f_rUp = ev.gen_weights_renorm_fact[MUf_nom_MUr_up]
                    weights_gen_weight_f_rDn = ev.gen_weights_renorm_fact[MUf_nom_MUr_down]
                    weights_gen_weight_fUp_r = ev.gen_weights_renorm_fact[MUf_up_MUr_nom]
                    weights_gen_weight_fDn_r = ev.gen_weights_renorm_fact[MUf_down_MUr_nom]
                    weights_gen_weight_frUp  = ev.gen_weights_renorm_fact[MUf_up_MUr_up]
                    weights_gen_weight_frDn  = ev.gen_weights_renorm_fact[MUf_down_MUr_down]

                    # sub to this naming in the following ntuple runs:
                    #weights_gen_weight_Frag = (ev.gen_weight_FragUp, ev.gen_weight_FragDown)
                    control_hs['weights_gen_weight_nom']   .Fill(weights_gen_weight_nom  )
                    control_hs['weights_gen_weight_f_rUp'] .Fill(weights_gen_weight_f_rUp)
                    control_hs['weights_gen_weight_f_rDn'] .Fill(weights_gen_weight_f_rDn)
                    control_hs['weights_gen_weight_fUp_r'] .Fill(weights_gen_weight_fUp_r)
                    control_hs['weights_gen_weight_fDn_r'] .Fill(weights_gen_weight_fDn_r)
                    control_hs['weights_gen_weight_frUp']  .Fill(weights_gen_weight_frUp )
                    control_hs['weights_gen_weight_frDn']  .Fill(weights_gen_weight_frDn )

                weight_top_pt = ttbar_pT_SF(ev.gen_t_pt, ev.gen_tb_pt)
                #weight *= weight_top_pt # to sys
                control_hs['weight_top_pt']   .Fill(weight_top_pt)
                # basically only difference is eltau/mutau
                t_wid  = abs(ev.gen_t_w_decay_id)
                tb_wid = abs(ev.gen_tb_w_decay_id)
                ## save detailed proc control for elmu "other" contribution
                #tt_ids = [0, 0]
                #tt_id1 = 0
                #for i, t_w_id in enumerate((t_wid, tb_wid)):
                #    if t_w_id == 1:
                #        tt_ids[i] = 1
                #    elif t_w_id == 11:
                #        tt_ids[i] = 2
                #    elif t_w_id == 13:
                #        tt_ids[i] = 3
                #    elif t_w_id == 15*11:
                #        tt_ids[i] = 4
                #    elif t_w_id == 15*13:
                #        tt_ids[i] = 5
                #    elif 15*15 < t_w_id < 15*30:
                #        tt_ids[i] = 6
                #    elif t_w_id >= 15*30:
                #        tt_ids[i] = 7
                #    else:
                #        tt_ids[i] = 8

                if (t_wid > 15*15 and tb_wid == 13) or (t_wid == 13 and tb_wid > 15*15): # lt
                    proc = 'tt_mutau'
                    # check if tau decayed in 3 charged particles
                    if (t_wid >= 15*30 and tb_wid == 13) or (t_wid == 13 and tb_wid >= 15*30): # lt
                        micro_proc = 'tt_mutau3ch'
                elif (t_wid > 15*15 and tb_wid == 11) or (t_wid == 11 and tb_wid > 15*15): # lt
                    proc = 'tt_eltau'
                    if (t_wid >= 15*30 and tb_wid == 11) or (t_wid == 11 and tb_wid >= 15*30): # lt
                        micro_proc = 'tt_eltau3ch'
                elif ev.gen_t_w_decay_id * ev.gen_tb_w_decay_id == -13*11:
                    proc = 'tt_elmu'
                #elif t_wid * tb_wid == 15*13*15*11: # this should work, but:
                elif (t_wid == 15*13 and tb_wid == 15*11) or (t_wid == 15*11 and tb_wid == 15*13):
                    proc = 'tt_taueltaumu'
                elif (t_wid  == 13 and tb_wid == 15*11) or (t_wid  == 11 and tb_wid == 15*13) or \
                     (tb_wid == 13 and t_wid  == 15*11) or (tb_wid == 11 and  t_wid == 15*13):
                    proc = 'tt_ltaul' # opposite leptons -- el-taumu etc
                elif t_wid * tb_wid == 13 or t_wid * tb_wid == 11: # lj
                    proc = 'tt_lj'
                elif (t_wid > 15*15 and (tb_wid == 11*15 or tb_wid == 13*15)) or \
                     ((t_wid == 11*15 or t_wid == 13*15) and tb_wid > 15*15): # taul tauh
                    proc = 'tt_taultauh'
                elif (t_wid == 1     and tb_wid == 13*15) or \
                     (t_wid == 13*15 and tb_wid == 1)     or \
                     (t_wid == 1     and tb_wid == 11*15) or \
                     (t_wid == 11*15 and tb_wid == 1):
                    proc = 'tt_taulj'
                    #proc = 'tt_tauelj'
                else:
                    proc = 'tt_other'

            if isSTop:
                # basically only difference is eltau/mutau
                #w1_id = abs(ev.gen_wdecays_IDs[0])
                # check the top decay insted
                w1_id = abs(ev.gen_t_w_decay_id) if ev.gen_t_w_decay_id != -111 else abs(ev.gen_tb_w_decay_id)
                w2_id = 1
                if not isSTopTSchannels:
                    # in tW there is an additional W produced with top
                    w2_id = abs(ev.gen_wdecays_IDs[0])
                    #w2_id = abs(ev.gen_t_w_decay_id) if ev.gen_t_w_decay_id != -111 else abs(ev.gen_tb_w_decay_id)
                # t/s channels emit top and a quark -- top ID + jets
                if (w1_id > 15*15 and w2_id == 13) or (w1_id == 13 and w2_id > 15*15): # lt
                    proc = 's_top_mutau'
                elif (w1_id > 15*15 and w2_id == 11) or (w1_id == 11 and w2_id > 15*15): # lt
                    proc = 's_top_eltau'
                elif (w1_id == 11 and w2_id == 13) or (w1_id == 13 and w2_id == 11): # is it faster than comparing to product?
                    proc = 's_top_elmu'
                elif w1_id * w2_id == 13 or w1_id * w2_id == 11: # lj
                    proc = 's_top_lj'
                #elif (w1_id > 15*15 and (w2_id == 11*15 or w2_id == 13*15)) or
                #     ((w1_id == 11*15 or w1_id == 13*15) and w2_id > 15*15): # taul tauh
                #    proc = 'tt_taultauh'
                else:
                    proc = 's_top_other'

            if isMC and (pass_mu_all or pass_mu or pass_mumu or pass_mumu_ss):
                #mu_sfs = lepton_muon_SF(abs(ev.lep_p4[0].eta()), ev.lep_p4[0].pt()) # old
                # 0, 1, 2 -- trk
                # 3, 4    -- id, iso
                if pass_mu_all and not (pass_mu or pass_mumu or pass_mumu_ss):
                    mu_sfs_b, mu_sfs_h = lepton_muon_SF(abs(ev.lep_alliso_p4[0].eta()), ev.lep_alliso_p4[0].pt(), ev.nvtx, ev.nvtx_gen)
                    (mu_trg_sf_b, trg_b_unc), (mu_trg_sf_h, trg_h_unc) = lepton_muon_trigger_SF(abs(ev.lep_alliso_p4[0].eta()), ev.lep_alliso_p4[0].pt())
                else:
                    mu_sfs_b, mu_sfs_h = lepton_muon_SF(abs(ev.lep_p4[0].eta()), ev.lep_p4[0].pt(), ev.nvtx, ev.nvtx_gen) # running tracking SF on reco nvtx and output on nvtx_gen for control
                    (mu_trg_sf_b, trg_b_unc), (mu_trg_sf_h, trg_h_unc) = lepton_muon_trigger_SF(abs(ev.lep_p4[0].eta()), ev.lep_p4[0].pt())
                # bcdef gh eras
                #weight *= ratio_bcdef * mu_trg_sf[0] * mu_sfs_b[0] * mu_sfs_b[1] * mu_sfs_b[2] * mu_sfs_b[3] + ratio_gh * mu_trg_sf[1] * mu_sfs_h[0] * mu_sfs_h[1] * mu_sfs_h[2] * mu_sfs_h[3]
                # with gen_nvtx for tracking eff
                mu_b_trk = mu_sfs_b[0] * mu_sfs_b[1]
                mu_h_trk = mu_sfs_h[0] * mu_sfs_h[1]
                weight_lep_Up   = weight * (ratio_bcdef * (mu_trg_sf_b + trg_b_unc) * mu_b_trk * (mu_sfs_b[3][0] + mu_sfs_b[3][1]) * (mu_sfs_b[4][0] + mu_sfs_b[4][1]) + \
                                               ratio_gh * (mu_trg_sf_h + trg_h_unc) * mu_h_trk * (mu_sfs_h[3][0] + mu_sfs_h[3][1]) * (mu_sfs_h[4][0] + mu_sfs_h[4][1]))
                weight_lep_Down = weight * (ratio_bcdef * (mu_trg_sf_b - trg_b_unc) * mu_b_trk * (mu_sfs_b[3][0] - mu_sfs_b[3][1]) * (mu_sfs_b[4][0] - mu_sfs_b[4][1]) + \
                                               ratio_gh * (mu_trg_sf_h - trg_h_unc) * mu_h_trk * (mu_sfs_h[3][0] - mu_sfs_h[3][1]) * (mu_sfs_h[4][0] - mu_sfs_h[4][1]))

                # test how much lepton SFs affect
                weight *= ratio_bcdef * mu_trg_sf_b * mu_b_trk * mu_sfs_b[3][0] * mu_sfs_b[4][0] + \
                             ratio_gh * mu_trg_sf_h * mu_h_trk * mu_sfs_h[3][0] * mu_sfs_h[4][0]

            if isMC and pass_elmu:
                # find which lepton is mu and which is el
                mu_n, el_n = (0, 1) if abs(ev.lep_id[0]) == 13 else (1, 0)
                mu_sfs_b, mu_sfs_h     = lepton_muon_SF(abs(ev.lep_p4[mu_n].eta()), ev.lep_p4[mu_n].pt(), ev.nvtx, ev.nvtx_gen)
                (mu_trg_sf_b, trg_b_unc), (mu_trg_sf_h, trg_h_unc) = lepton_muon_trigger_SF(abs(ev.lep_p4[mu_n].eta()), ev.lep_p4[mu_n].pt())
                el_sfs_reco, el_sfs_id = lepton_electron_SF(abs(ev.lep_p4[el_n].eta()), ev.lep_p4[el_n].pt())
                #el_trg_sf              = lepton_electron_trigger_SF(abs(ev.lep_p4[el_n].eta()), ev.lep_p4[el_n].pt())
                #weight_lep_Up   *= weight * (el_trg_sf[0] + el_trg_sf[1]) * (el_sfs_reco[0] + el_sfs_reco[1]) * (el_sfs_id[0] + el_sfs_id[1])
                #weight_lep_Down *= weight * (el_trg_sf[0] - el_trg_sf[1]) * (el_sfs_reco[0] - el_sfs_reco[1]) * (el_sfs_id[0] - el_sfs_id[1])
                #weight *= el_trg_sf[0] * el_sfs_reco[0] * el_sfs_id[0]
                # w.o. el trig
                mu_b_trk = mu_sfs_b[0] * mu_sfs_b[1]
                mu_h_trk = mu_sfs_h[0] * mu_sfs_h[1]

                weight_lep_Up   = weight * (ratio_bcdef * (mu_trg_sf_b + trg_b_unc) * mu_b_trk * (mu_sfs_b[3][0] + mu_sfs_b[3][1]) * (mu_sfs_b[4][0] + mu_sfs_b[4][1]) + \
                                               ratio_gh * (mu_trg_sf_h + trg_h_unc) * mu_h_trk * (mu_sfs_h[3][0] + mu_sfs_h[3][1]) * (mu_sfs_h[4][0] + mu_sfs_h[4][1]))
                weight_lep_Down = weight * (ratio_bcdef * (mu_trg_sf_b - trg_b_unc) * mu_b_trk * (mu_sfs_b[3][0] - mu_sfs_b[3][1]) * (mu_sfs_b[4][0] - mu_sfs_b[4][1]) + \
                                               ratio_gh * (mu_trg_sf_h - trg_h_unc) * mu_h_trk * (mu_sfs_h[3][0] - mu_sfs_h[3][1]) * (mu_sfs_h[4][0] - mu_sfs_h[4][1]))

                weight_lep_Up   *= (el_sfs_reco[0] + el_sfs_reco[1]) * (el_sfs_id[0] + el_sfs_id[1])
                weight_lep_Down *= (el_sfs_reco[0] - el_sfs_reco[1]) * (el_sfs_id[0] - el_sfs_id[1])

                weight *= el_sfs_reco[0] * el_sfs_id[0]

                weight *= ratio_bcdef * mu_trg_sf_b * mu_b_trk * mu_sfs_b[3][0] * mu_sfs_b[4][0] + \
                          ratio_gh    * mu_trg_sf_h * mu_h_trk * mu_sfs_h[3][0] * mu_sfs_h[4][0]

            # FIXME: this thing might interfere with muonic elmu! run separately or fix
            if False and isMC and pass_elmu_el:
                # find which lepton is mu and which is el
                mu_n, el_n = (0, 1) if abs(ev.lep_id[0]) == 13 else (1, 0)
                mu_sfs_b, mu_sfs_h     = lepton_muon_SF(abs(ev.lep_p4[mu_n].eta()), ev.lep_p4[mu_n].pt(), ev.nvtx, ev.nvtx_gen)
                #(mu_trg_sf_b, trg_b_unc), (mu_trg_sf_h, trg_h_unc) = lepton_muon_trigger_SF(abs(ev.lep_p4[mu_n].eta()), ev.lep_p4[mu_n].pt())
                el_sfs_reco, el_sfs_id = lepton_electron_SF(abs(ev.lep_p4[el_n].eta()), ev.lep_p4[el_n].pt())
                el_trg_sf              = lepton_electron_trigger_SF(abs(ev.lep_p4[el_n].eta()), ev.lep_p4[el_n].pt())
                #weight_lep_Up   *= weight * (el_trg_sf[0] + el_trg_sf[1]) * (el_sfs_reco[0] + el_sfs_reco[1]) * (el_sfs_id[0] + el_sfs_id[1])
                #weight_lep_Down *= weight * (el_trg_sf[0] - el_trg_sf[1]) * (el_sfs_reco[0] - el_sfs_reco[1]) * (el_sfs_id[0] - el_sfs_id[1])
                #weight *= el_trg_sf[0] * el_sfs_reco[0] * el_sfs_id[0]

                # w.o. mu trig
                mu_b_trk = mu_sfs_b[0] * mu_sfs_b[1]
                mu_h_trk = mu_sfs_h[0] * mu_sfs_h[1]

                weight_lep_Up   = weight * (ratio_bcdef * mu_b_trk * (mu_sfs_b[3][0] + mu_sfs_b[3][1]) * (mu_sfs_b[4][0] + mu_sfs_b[4][1]) + \
                                               ratio_gh * mu_h_trk * (mu_sfs_h[3][0] + mu_sfs_h[3][1]) * (mu_sfs_h[4][0] + mu_sfs_h[4][1]))
                weight_lep_Down = weight * (ratio_bcdef * mu_b_trk * (mu_sfs_b[3][0] - mu_sfs_b[3][1]) * (mu_sfs_b[4][0] - mu_sfs_b[4][1]) + \
                                               ratio_gh * mu_h_trk * (mu_sfs_h[3][0] - mu_sfs_h[3][1]) * (mu_sfs_h[4][0] - mu_sfs_h[4][1]))

                weight_lep_Up   *= (el_trg_sf[0] + el_trg_sf[1]) * (el_sfs_reco[0] + el_sfs_reco[1]) * (el_sfs_id[0] + el_sfs_id[1])
                weight_lep_Down *= (el_trg_sf[0] - el_trg_sf[1]) * (el_sfs_reco[0] - el_sfs_reco[1]) * (el_sfs_id[0] - el_sfs_id[1])

                #weight *= el_trg_sf[0] * el_sfs_reco[0] * el_sfs_id[0]

                #weight *= ratio_bcdef * mu_b_trk * mu_sfs_b[3][0] * mu_sfs_b[4][0] + \
                #          ratio_gh    * mu_h_trk * mu_sfs_h[3][0] * mu_sfs_h[4][0]



            if isMC and (pass_el_all or pass_el or pass_elel):
                if pass_el_all and not (pass_el or pass_elel):
                    el_sfs_reco, el_sfs_id = lepton_electron_SF(abs(ev.lep_alliso_p4[0].eta()), ev.lep_alliso_p4[0].pt())
                    el_trg_sf = lepton_electron_trigger_SF(abs(ev.lep_alliso_p4[0].eta()), ev.lep_alliso_p4[0].pt())
                else:
                    el_sfs_reco, el_sfs_id = lepton_electron_SF(abs(ev.lep_p4[0].eta()), ev.lep_p4[0].pt())
                    el_trg_sf = lepton_electron_trigger_SF(abs(ev.lep_p4[0].eta()), ev.lep_p4[0].pt())
                # on 0 position is the value, on 1 is uncertainty
                weight_lep_Up   = weight * (el_trg_sf[0] + el_trg_sf[1]) * (el_sfs_reco[0] + el_sfs_reco[1]) * (el_sfs_id[0] + el_sfs_id[1])
                weight_lep_Down = weight * (el_trg_sf[0] - el_trg_sf[1]) * (el_sfs_reco[0] - el_sfs_reco[1]) * (el_sfs_id[0] - el_sfs_id[1])

                # test how much leptons SFs affect
                weight *= el_trg_sf[0] * el_sfs_reco[0] * el_sfs_id[0]

        control_counters.Fill(52)

        # -------------------- LEPTONS
        leps = LeptonSelection(iso=(ev.lep_p4, ev.lep_relIso, ev.lep_matching_gen, ev.lep_matching_gen_dR, ev.lep_id), alliso=(ev.lep_alliso_p4, ev.lep_alliso_relIso, ev.lep_alliso_matching_gen, ev.lep_alliso_matching_gen_dR, ev.lep_alliso_id))
        #leps = LeptonSelection(iso=(ev.lep_p4, ev.lep_relIso, ev.lep_matching_gen, ev.lep_matching_gen_dR, ev.lep_id), alliso=(ev.lep_p4, ev.lep_relIso, ev.lep_matching_gen, ev.lep_matching_gen_dR, ev.lep_id))

        # -------------------- TAUS

        # tau pt-s
        # ES correction
        # modes have different correction but the same uncertainty = +- 1.2% = 0.012
        # uncertainties are not correlated, but I'll do correlated UP/DOWN -- all modes UP or all modes DOWN
        #tau_pts_corrected = []
        #tau_pts_corrected_up = []
        #tau_pts_corrected_down = []
        #Mt_tau_met_nominal, Mt_tau_met_up, Mt_tau_met_down = None, None, None
        Mt_tau_met_nominal, Mt_tau_met_up, Mt_tau_met_down = 0, 0, 0

        # so, actually what I need from taus is
        # whether there is a medium tau with pt 30, eta 2.4
        # and if it is OS with the lepton
        # usually it is the tau on first position (0)
        # should I really loop?

        # each selection requires only 1 ID level of tau:
        # lowest and cuts -- tight
        # old -- medium
        # I also need preselection for WJets SS and preselection SS (for QCD)
        taus_nom    = TauCutsPerSystematic(lowest=[], loose=[], cuts=[], old=[], oldVloose=[], presel_alliso=[], presel=[])
        taus_ESUp   = TauCutsPerSystematic(lowest=[], loose=[], cuts=[], old=[], oldVloose=[], presel_alliso=[], presel=[])
        taus_ESDown = TauCutsPerSystematic(lowest=[], loose=[], cuts=[], old=[], oldVloose=[], presel_alliso=[], presel=[])

        # each tau is
        # p4, ES factor (ID lev is per collection), pdg ID (for OS, SS)

        """
        tausP_nom    = TauCutsPerSystematic(lowest=[], cuts=[], old=[])
        tausL_nom    = TauCutsPerSystematic(lowest=[], cuts=[], old=[])
        tausM_nom    = TauCutsPerSystematic(lowest=[], cuts=[], old=[])
        tausT_nom    = TauCutsPerSystematic(lowest=[], cuts=[], old=[])

        tausP_ESUp   = TauCutsPerSystematic(lowest=[], cuts=[], old=[])
        tausL_ESUp   = TauCutsPerSystematic(lowest=[], cuts=[], old=[])
        tausM_ESUp   = TauCutsPerSystematic(lowest=[], cuts=[], old=[])
        tausT_ESUp   = TauCutsPerSystematic(lowest=[], cuts=[], old=[])

        tausP_ESDown = TauCutsPerSystematic(lowest=[], cuts=[], old=[])
        tausL_ESDown = TauCutsPerSystematic(lowest=[], cuts=[], old=[])
        tausM_ESDown = TauCutsPerSystematic(lowest=[], cuts=[], old=[])
        tausT_ESDown = TauCutsPerSystematic(lowest=[], cuts=[], old=[])
        """

        """
        # p4 momenta of taus and the Energy Scale factor
        taus_nominal_min = []
        taus_nominal = []
        taus_es_up   = []
        taus_es_down = []

        # OPTIMIZATION
        # I assume tau is usually only 1 in the event
        # to control it I can:
        #   keep a counter of N loow, medium and tight taus, but I'll use only the first tau
        #   or
        #   return list of taus with their IDlev... -- for each ES variation pssing the pt cut
        #   ..also my ES variations are for Medium WP only?
        #     and I don't really need it for optimization tests....
        taus_all_foropt = []
        """

        # only top pt tau is treated but that's fine
        '''IDlev
        1 VLoose
        2 Loose
        3 Medium
        4 Tight
        5 VTight
        '''

        #tlep_p4 = TLorentzVector(ev.lep_p4[0].X(), ev.lep_p4[0].Y(), ev.lep_p4[0].Z(), ev.lep_p4[0].T())
        #if ev.tau_p4.size() > 0 and ev.tau_IDlev[0] > 1 and abs(ev.tau_p4[0].eta()) < 2.4:
        for i, (p4, tau_ID, tau_DM, tau_pdgID) in enumerate(zip(ev.tau_p4, ev.tau_IDlev, ev.tau_decayMode, ev.tau_id)):
            # discard taus if they match to lepton
            # TODO: turn it on in next NT
            #if ev.tau_matching_lep[i]:
            #    continue
            # the original index i is needed for the match to refitted values

            if abs(p4.eta()) > 2.4: continue
            # it should work like Python does and not copy these objects! (cast)
            #p4, DM, IDlev = ev.tau_p4[0], ev.tau_decayMode[0], ev.tau_IDlev[0]
            #if IDlev < 3 or abs(p4.eta()) < 2.4: continue # only Medium taus

            ## check dR to lepton
            # it's done in Ntupler -- not needed here
            #ttau_p4 = TLorentzVector(tau_p4.X(), tau_p4.Y(), tau_p4.Z(), tau_p4.T())
            #if not tlep_p4.DeltaR(ttau_p4) > 0.3:
            #    continue

            tau_pt = p4.pt()
            TES_factor = 1. # this factor exists for nominal taus

            pt_cut_cuts = 22.
            pt_cut_old  = 30.

            jetmatched = ev.tau_dR_matched_jet[i] # > -1

            match_lep        = ev.tau_matching_lep[i]
            match_lep_alliso = ev.tau_matching_allIso_lep[i]

            #if tau_pt < 20.: continue # no need to check -- it's default in ntupler

            # MC corrections
            if isMC: # and with_TauES_sys:
                if tau_DM == 0:
                    factor = 0.995
                    factor_up   = 0.995 + 0.012
                    factor_down = 0.995 - 0.012
                elif tau_DM < 10:
                    factor = 1.011
                    factor_up   = 1.011 + 0.012
                    factor_down = 1.011 - 0.012
                else:
                    factor = 1.006
                    factor_up   = 1.006 + 0.012
                    factor_down = 1.006 - 0.012
                tau_pt_up   = tau_pt * factor_up
                tau_pt_down = tau_pt * factor_down
                TES_factor  = factor
                tau_pt     *= factor

            # I store only 1 ID per selection
            # tight for lowest and cuts
            # medium for old
            # presel for presel

            # nominals
            if tau_pt > 20.:
                if not match_lep:
                    taus_nom               .presel.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                if not match_lep_alliso:
                    taus_nom               .presel_alliso.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                #if tau_ID > 1: tausL_nom.lowest.append((p4, TES_factor))
                #if tau_ID > 2: tausM_nom.lowest.append((p4, TES_factor))
                if tau_ID > 1 and not match_lep: taus_nom.loose.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                if tau_ID > 2 and not match_lep: taus_nom.lowest.append((p4, TES_factor, tau_pdgID, i, jetmatched))
            #if tau_pt > pt_cut_cuts and not match_lep:
            #    if tau_ID > 3: taus_nom.cuts.append((p4, TES_factor, tau_pdgID, i, jetmatched))
            if tau_pt > pt_cut_old:
                if tau_ID > 0 and not match_lep: taus_nom.oldVloose .append((p4, TES_factor, tau_pdgID, i, jetmatched))
                if tau_ID > 2 and not match_lep: taus_nom.old .append((p4, TES_factor, tau_pdgID, i, jetmatched))

            # TES
            if isMC and with_TauES_sys:

                TES_factor = factor_up
                if tau_pt_up > 20.:
                    if not match_lep:
                        taus_ESUp               .presel.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                    if not match_lep_alliso:
                        taus_ESUp               .presel_alliso.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                    if tau_ID > 1 and not match_lep: taus_ESUp.loose.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                    if tau_ID > 2 and not match_lep: taus_ESUp.lowest.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                #if tau_pt_up > pt_cut_cuts and not match_lep:
                #    if tau_ID > 3: taus_ESUp.cuts.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                if tau_pt_up > pt_cut_old:
                    if tau_ID > 0 and not match_lep: taus_ESUp.oldVloose.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                    if tau_ID > 2 and not match_lep: taus_ESUp.old.append((p4, TES_factor, tau_pdgID, i, jetmatched))

                TES_factor = factor_down
                if tau_pt_down > 20.:
                    if not match_lep:
                        taus_ESDown               .presel.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                    if not match_lep_alliso:
                        taus_ESDown               .presel_alliso.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                    if tau_ID > 1 and not match_lep: taus_ESDown.loose.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                    if tau_ID > 2 and not match_lep: taus_ESDown.lowest.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                #if tau_pt_down > pt_cut_cuts and not match_lep:
                #    if tau_ID > 3: taus_ESDown.cuts.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                if tau_pt_down > pt_cut_old:
                    if tau_ID > 0 and not match_lep: taus_ESDown.oldVloose.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                    if tau_ID > 2 and not match_lep: taus_ESDown.old.append((p4, TES_factor, tau_pdgID, i, jetmatched))

            """
            usual_pt_cut = 20. # TODO: cut for optimization study, review it after results
            if not isMC:
                if tau_pt > usual_pt_cut:
                    taus_all_foropt.append((tau_p4, 1., tau_ID, tau_pdgID))
                    if tau_ID > 2:
                        taus_nominal.append((tau_p4, 1.))
                if tau_pt > 20. and tau_ID > 1: # Loose taus
                    taus_nominal_min.append((tau_p4, 1.))
            else:

                # only nominal for min taus
                if tau_p4 * factor > usual_pt_cut:
                    taus_all_foropt.append((tau_p4, factor, tau_ID, tau_pdgID))
                    if tau_ID > 1:
                        taus_nominal_min.append((tau_p4, factor))

                ## calculate it later, inplace of record
                #if not Mt_tau_met_nominal:
                #    Mt_tau_met_nominal = transverse_mass_pts(ev.tau_p4[0].Px()*factor, ev.tau_p4[0].Py()*factor, met_x, met_y)
                #has_tau_es_up   = (ev.tau_p4[0].pt() * factor_up  ) > 30
                #has_tau_es_down = (ev.tau_p4[0].pt() * factor_down) > 30
                if tau_ID > 2:
                    if tau_pt * factor > usual_pt_cut:
                        taus_nominal.append((tau_p4, factor))
                    if tau_pt * factor_up > usual_pt_cut:
                        taus_es_up.append((tau_p4, factor_up))
                    if tau_pt * factor_down > usual_pt_cut:
                        taus_es_down.append((tau_p4, factor_down))
                #if not Mt_tau_met_up:
                #    Mt_tau_met_up   = transverse_mass_pts(ev.tau_p4[0].Px()*factor_up, ev.tau_p4[0].Py()*factor_up, met_x, met_y)
                #    Mt_tau_met_down = transverse_mass_pts(ev.tau_p4[0].Px()*factor_down, ev.tau_p4[0].Py()*factor_down, met_x, met_y)

        # OPTIMIZATION
        taus_all_foropt.sort(key=lambda tau: tau[2], reverse=True) # sort by IDlev
        n_presel_taus = n_loose_taus = n_medium_taus = n_tight_taus = 0
        n_presel_tau_i = n_loose_tau_i = n_medium_tau_i = n_tight_tau_i = -1
        n_presel_tau_pdg = n_loose_tau_pdg = n_medium_tau_pdg = n_tight_tau_pdg = 0
        for i, (_, _, IDlev, pdgID) in enumerate(taus_all_foropt):
            n_presel_taus += 1
            if i == 0:
                n_presel_tau_i = 0
                n_presel_tau_pdg = pdgID
            if IDlev > 3:
                n_loose_taus  += 1
                n_medium_taus += 1
                n_tight_taus  += 1
            elif IDlev == 3:
                n_loose_taus  += 1
                n_medium_taus += 1
            elif IDlev == 2:
                n_loose_taus  += 1

            # damn, I also need tau pdg ID for OS to lepton...
            # and I want to know the tau index in the tau list -- is it always the 0 tau which is picked up?
            if n_loose_taus == 1:
                n_loose_tau_i = i
                n_loose_tau_pdg = pdgID
            if n_medium_taus == 1:
                n_medium_tau_i = i
                n_medium_tau_pdg = pdgID
            if n_tight_taus == 1:
                n_tight_tau_i = i
                n_tight_tau_pdg = pdgID
            """


        # sort by pt
        taus_nom    .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
        taus_nom    .loose .sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
        #taus_nom    .cuts  .sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
        taus_nom    .old   .sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
        taus_nom    .presel.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)

        # TES
        if isMC and with_TauES_sys:
            taus_ESUp   .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
            taus_ESDown .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
            taus_ESUp   .loose .sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
            taus_ESDown .loose .sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
            #taus_ESUp   .cuts  .sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
            #taus_ESDown .cuts  .sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
            taus_ESUp   .old   .sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
            taus_ESDown .old   .sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
            taus_ESUp   .presel.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
            taus_ESDown .presel.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)

        #has_medium_tau = any(IDlev > 2 and p4.pt() > 30 for IDlev, p4 in zip(ev.tau_IDlev, ev.tau_p4))
        #has_medium_tau = ev.tau_IDlev.size() > 0 and ev.tau_IDlev[0] > 2 and ev.tau_p4[0].pt() > 30
        #has_medium_tau = bool(tau_pts_corrected)
        #TODO: propagate TES to MET?


        # ---------- JETS

        # jets save (p4, factor) and (..., dR_far_of_tau) for adv selection -- counting tau-cleaned jets for Loose2
        # TODO: add jet b-discr or b-ID, also consider adding dR to tau (to which tau? loose? medium? save the ID of dR-ed tau?)

        """
        all_jets_b_discrs = []
        lead_jet_b_discr = -1.

        # OPTIMIZATION
        # similar procedure for bjets as in tau
        bjets_all_foropt = []
        """

        ##SystematicJets = namedtuple('Jets', 'nom sys_JERUp sys_JERDown sys_JESUp sys_JESDown sys_bUp sys_bDown')
        #jets_all_optimized          = SystematicJets('nom'=[], sys_JERUp=[], sys_JERDown=[], sys_JESUp=[], sys_JESDown=[], sys_bUp=[], sys_bDown=[])
        #jets_all_optimized_cuts     = SystematicJets('nom'=[], sys_JERUp=[], sys_JERDown=[], sys_JESUp=[], sys_JESDown=[], sys_bUp=[], sys_bDown=[])
        #jets_all_optimized_old_cuts = SystematicJets('nom'=[], sys_JERUp=[], sys_JERDown=[], sys_JESUp=[], sys_JESDown=[], sys_bUp=[], sys_bDown=[])
        ## each systematic is a list of jets with
        ## p4, energy factor, b SF weight, b ID level

        #JetCutsPerSystematic = namedtuple('Jets', 'lowest cuts old')
        # collection holds jet info per 1 systematic
        # for each of the requested cuts
        # -- so that I still can loop over systematics
        #    and keep it extendable
        # each jet collection holds:
        #    p4, energy factor, b SF weight, b ID level

        # each selection needs b-jets (loose and medium) and other jets
        # -- for lj calculations and b-jet control
        # taumatched jets are needed jor lj too
        # they are split in b and non-b jets according to the selection
        '''
        jets_nom     = JetCutsPerSystematic(lowest=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])),
                                              cuts=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])),
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])))
        jets_JERUp   = JetCutsPerSystematic(lowest=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])),
                                              cuts=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])),
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])))
        jets_JERDown = JetCutsPerSystematic(lowest=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])),
                                              cuts=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])), 
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])))
        jets_JESUp   = JetCutsPerSystematic(lowest=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])),
                                              cuts=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])), 
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])))
        jets_JESDown = JetCutsPerSystematic(lowest=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])),
                                              cuts=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])), 
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])))
        jets_bUp     = JetCutsPerSystematic(lowest=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])),
                                              cuts=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])), 
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])))
        jets_bDown   = JetCutsPerSystematic(lowest=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])),
                                              cuts=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])), 
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], [])))
        # maybe it's worthwhile to make a custom object with propper defaults and fancy initialization without code
        '''

        jets_nom     = JetCutsPerSystematic(
                                        old_alliso=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]),
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]))
        jets_JERUp   = JetCutsPerSystematic(
                                        old_alliso=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]),
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]))
        jets_JERDown = JetCutsPerSystematic(
                                        old_alliso=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]),
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]))
        jets_JESUp   = JetCutsPerSystematic(
                                        old_alliso=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]),
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]))
        jets_JESDown = JetCutsPerSystematic(
                                        old_alliso=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]),
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]))
        jets_bUp     = JetCutsPerSystematic(
                                        old_alliso=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]),
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]))
        jets_bDown   = JetCutsPerSystematic(
                                        old_alliso=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]),
                                               old=JetBSplit(medium=[], loose=[], rest=[], taumatched=([], []), lepmatched=[]))
        # maybe it's worthwhile to make a custom object with propper defaults and fancy initialization without code


        #bjetsL_nom     = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsL_JERUp   = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsL_JERDown = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsL_JESUp   = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsL_JESDown = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsL_bUp     = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsL_bDown   = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsM_nom     = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsM_JERUp   = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsM_JERDown = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsM_JESUp   = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsM_JESDown = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsM_bUp     = JetCutsPerSystematic(lowest=[], cuts=[], old=[])
        #bjetsM_bDown   = JetCutsPerSystematic(lowest=[], cuts=[], old=[])

        # I forgot about the needed b-jet splitting (for lj and easy 1M, 2L1M selections)
        # and it got out of hand
        # I don't want to use dict-s of strings for performance sake
        # and trying to operate on direct pointers with named tuples (hopefully that's how it is implemented TODO check speed)
        # macro would be nice here
        # TODO is there another way?

        if len(ev.jet_b_discr) > 0:
            lead_jet_b_discr = ev.jet_b_discr[0]

        b_tag_wp_loose  = 0.460
        b_tag_wp_medium = 0.8484 #0.8 #
        b_tag_wp_tight  = 0.935
        b_tag_wp = b_tag_wp_medium

        tau_dR_jet_min = 0.4 # ak4 jets

        """
        # lists of "light jets", not passing b-tag
        jets_nominal = [] # nominal jet pts
        jets_jer_up, jets_jer_down = [], []
        jets_jes_up, jets_jes_down = [], []
        # lists of "heavy jets", passing b-tag
        jets_b_nominal = [] # nominal jet pts
        jets_b_jer_up, jets_b_jer_down = [], []
        jets_b_jes_up, jets_b_jes_down = [], []

        #has_2_loose_bjets
        jets_b_nominal_loose = [] # nominal jet pts
        jets_b_nominal_tight = [] # nominal jet pts
        jets_not_loose_b = [] # nominal jet pts
        jets_not_tight_b = [] # nominal jet pts

        #nbjets_nominal = 0
        #nbjets_jer_up, nbjets_jer_down = 0, 0
        #nbjets_jes_up, nbjets_jes_down = 0, 0

        weight_bSF = 1.
        weight_bSF_up, weight_bSF_down = 1., 1.
        weight_bSF_jer_up, weight_bSF_jer_down = 1., 1.
        weight_bSF_jes_up, weight_bSF_jes_down = 1., 1.

        jets_nominal_min = [] # nominal jet pts
        jets_b_nominal_min = [] # nominal jet pts
        weight_bSF_min = 1.

        ## for tt->elmu FAKERATES [TODO: add this as some ifs]
        #all_jets_for_fakes = []
        """

        # these collections should be cross-cleaned from loose+ tau
        #if taus_nominal_min:
        #    tau_p4 = taus_nominal_min[0][0]
        #    ttau_p4 = TLorentzVector(tau_p4.X(), tau_p4.Y(), tau_p4.Z(), tau_p4.T())
        # I'll do cross-clean with nominal loose taus
        #tausL_nom    = TauCutsPerSystematic(lowest=[], cuts=[], old=[])
        # of lowest cuts? -- no, of the same as in the selection
        #                 -- and this again messes up the code.......

        taus_nom_TLorentz    = TauCutsPerSystematic(lowest=[], loose=[], cuts=[], old=[], oldVloose=[], presel=[], presel_alliso=[]) # presel won't be needed
        # presel should also be cleaned of the tau -- of the one I do SS with
        # in fact the cross-cleaning should be done only from the used tau
        # I can sort the taus by pt and use the first one

        # just lists of tlorentz vectors
        # in lowest and cuts we use tight tau
        # -- using only the first tau in the list -- the target one!
        for tau_p4, _, _, _, _ in taus_nom.lowest[:1]:
            taus_nom_TLorentz.lowest.append(TLorentzVector(tau_p4.X(), tau_p4.Y(), tau_p4.Z(), tau_p4.T()))
        # TODO: loose taus for 2L1M + loose tau selection -- I'll do it quickly here, re-using the lowest jets (with tight tau)
        #for tau_p4, _, _ in taus_nom.loose[:1]:
            #taus_nom_TLorentz.loose.append(TLorentzVector(tau_p4.X(), tau_p4.Y(), tau_p4.Z(), tau_p4.T()))
        #for tau_p4, _, _, _, _ in taus_nom.cuts[:1]:
        #    taus_nom_TLorentz.cuts.append(TLorentzVector(tau_p4.X(), tau_p4.Y(), tau_p4.Z(), tau_p4.T()))
        # in old we use medium tau
        for tau_p4, _, _, _, _ in taus_nom.old[:1]:
            taus_nom_TLorentz.old.append(TLorentzVector(tau_p4.X(), tau_p4.Y(), tau_p4.Z(), tau_p4.T()))
        #for tau_p4, _, _, _, _ in taus_nom.oldVloose[:1]:
        #    taus_nom_TLorentz.oldVloose.append(TLorentzVector(tau_p4.X(), tau_p4.Y(), tau_p4.Z(), tau_p4.T()))
        # in principle I should also change TES -- but this effect is very second order

        # loose and tight b jet collections are cross cleaned from loose zero tau
        # only 1 jet is taken out
        tau_match_lowest, tau_match_cuts, tau_match_old = False, False, False

        # transition to v20-v21
        #miniaod_jets = ev.jet_p4 if OLD_MINIAOD_JETS else ev.jet_initial_p4

        # MC jets are corrected for JER, which is propagated to met
        #jet_cor

        sub_lep = True
        for i in xrange(ev.jet_p4.size()):
            # discard jets if they match to lepton
            # TODO: turn it on in next NT
            #if ev.jet_matching_lep[i]:
            #    continue

            #pfid, p4 = ev.jet_PFID[i], ev.jet_p4[i]
            # RECORRECTED jets
            #p4 = ev.jet_uncorrected_p4[i]
            # jet_p4 is fully corrected online
            # and whole correction is propagated to corrected met
            # as I did before I use the subset of passed jets, and propagate only their correction to met
            # TODO: add comparison to using all-corrected jets
            #p4 = ev.jet_initial_p4[i]
            #p4 = miniaod_jets[i]

            # nominally corrected jets in NTuple (v28 data and all previous for MC)
            #p4 = ev.jet_p4[i]

            # the default miniaod objects
            p4 = ev.jet_initial_p4[i]
            #p4 = ev.jet_uncorrected_p4[i]

            pfid = ev.jet_PFID[i]

            # actually the jet_p4 is the slimmed jet
            # -- works for slimmed met, which is met_init
            # met_x = ev.met_init.Px()

            # to apply JES I need uncorrected jet and to propagate it to MET I need the uncorrection factor included
            # = main thing is to start from the same point

            # but now I need full factor for MC
            if pfid < 1 or abs(p4.eta()) > 2.5: continue # Loose PFID and eta

            jet_b_discr = ev.jet_b_discr[i]
            #all_jets_b_discrs.append(jet_b_discr)

            match_lep        = ev.jet_matching_lep[i]
            match_lep_alliso = ev.jet_matching_allIso_lep[i]

            # jet energy scale factor = JES factor * JER
            # But the JES is re-correction
            # Thus also * UncorFactor
            en_factor = 1.

            #jes_factor = ev.jet_jes_recorrection[i] # ALREADY APPLIED IN NTUPLER
            #en_factor *= jes_factor
            # the idea is to match these jets with the full_corr met

            HF = -1
            PF = -1
            jet_index = i
            #genmatch = 0
            if isMC:
                # ALREADY APPLIED
                #jes_uncorFactor = ev.jet_uncorrected_jecFactor[i]
                #en_factor *= jer_factor * jes_uncorFactor

                # jer factor is needed for the syst variation
                jer_factor = ev.jet_jer_factor[i]
                # and let's try the new prescription: miniaod objects + jer
                en_factor *= jer_factor
                # this jer is calculated on top of recorected jes, let's hope it's fine
                # (mostly depends on eta, dependence on pt is small)
                # and the jes variation (jes_shift used in the following)
                # is calculated in the recorrection procedure
                # -- let's hope it is also adequate
                HF = ev.jet_hadronFlavour[i]
                PF = ev.jet_partonFlavour[i]

                # this check is done online with dR 0.4
                #if ev.jet_matching_gen_dR[i] < 0.3:
                    #genmatch = ev.jet_matching_gen[i]

            # propagate the correction to met
            proc_met -= p4 * (en_factor - 1.)

            if sub_lep and match_lep:
                # sub jet by lep
                # works only for 1 lepton
                #proc_met_lepsub -= ev.lep_p4[0] - p4
                proc_met_lepsub += p4
                sub_lep = False
            else:
                proc_met_lepsub -= p4 * (en_factor - 1.)

            # and with systematic variations
            if isMC and with_JER_sys:
                #jer_factor, up, down = ev.jet_jer_factor[i], ev.jet_jer_factor_up[i], ev.jet_jer_factor_down[i]
                jer_up, jer_down = ev.jet_jer_factor_up[i], ev.jet_jer_factor_down[i]
                proc_met_JERUp   -= p4 * (jer_up - 1.)
                proc_met_JERDown -= p4 * (jer_down - 1.)

            if isMC and with_JES_sys:
                #jes_shift = ev.jet_jes_correction_relShift[i]
                jes_shift = ev.jet_jes_uncertainty[i]
                proc_met_JESUp   -= p4 * (en_factor*(1 + jes_shift) - 1.)
                proc_met_JESDown -= p4 * (en_factor*(1 - jes_shift) - 1.)


            jet_pt  = p4.pt() * en_factor
            jet_eta = p4.eta()

            #if p4.pt() > 30: # nominal jet
            # TODO: for optimization tests I reduced the cut, review it with the test results
            if jet_pt > 20: # nominal jet
                tj_p4 = TLorentzVector(p4.X(), p4.Y(), p4.Z(), p4.T())
                #for ttau_p4 in taus_nom_TLorentz.lowest:
                #    if tj_p4.DeltaR(ttau_p4) < 0.3:
                #        tau_match_lowest = True
                #        break

                #for ttau_p4 in taus_nom_TLorentz.cuts:
                #    if tj_p4.DeltaR(ttau_p4) < 0.3:
                #        tau_match_cuts = True
                #        break

                #for ttau_p4 in taus_nom_TLorentz.old:
                #    if tj_p4.DeltaR(ttau_p4) < 0.3:
                #        tau_match_old = True
                #        break

                jet_tau_match_lowest = jet_tau_match_cuts = jet_tau_match_old = False
                #if not tau_match_lowest: # the tau did'nt remove a jet yet
                #    tau_match_lowest = jet_tau_match_lowest = any(tj_p4.DeltaR(ttau_p4) < tau_dR_jet_min for ttau_p4 in taus_nom_TLorentz.lowest)
                #if not tau_match_cuts:
                #    tau_match_cuts   = jet_tau_match_cuts   = any(tj_p4.DeltaR(ttau_p4) < tau_dR_jet_min for ttau_p4 in taus_nom_TLorentz.cuts)
                if not tau_match_old:
                    tau_match_old    = jet_tau_match_old    = any(tj_p4.DeltaR(ttau_p4) < tau_dR_jet_min for ttau_p4 in taus_nom_TLorentz.old)

                #if jet_tau_match_lowest and jet_tau_match_cuts and jet_tau_match_old:
                #    continue

                # jet passed ID, eta, lowest pt threshold and doesn't match to a Loose tau
                # now find its' systematic corrections and save
                flavId = ev.jet_hadronFlavour[i]
                b_tagged = b_tagged_medium = jet_b_discr > b_tag_wp_medium
                b_tagged_loose = jet_b_discr > b_tag_wp_loose
                b_tagged_tight = jet_b_discr > b_tag_wp_tight

                bID_lev = sum((b_tagged_loose, b_tagged_medium, b_tagged_tight))

                # jet at given systematic and selection is defined by p4, energy factor, bSF weight and b ID lev
                # JER and JES are already nominally corrected -- only Up/Down are needed
                jet_factor_JERUp = 1.
                jet_factor_JESUp = 1.
                jet_factor_JERDown = 1.
                jet_factor_JESDown = 1.
                # b SF needs to be calculated
                jet_weight_bSF_nom = 1.     # there might be several schemes for b SF weights
                jet_weight_bSFUp   = 1.
                jet_weight_bSFDown = 1.

                # so, for nominal jets I just need to check is bSF needs to be calculated and add it if so

                if isMC:
                    if with_bSF:
                        # for now I calculate only the old b SF scheme with only medium b WP
                        # TODO: add the 2L1M b SF scheme
                        jet_weight_bSF_nom, _, _ = calc_btag_sf_weight(b_tagged_medium, flavId, jet_pt, jet_eta)
                        if with_bSF_sys:
                            # again only old scheme
                            jet_weight_bSFUp  , _, _ = calc_btag_sf_weight(b_tagged, flavId, jet_pt, jet_eta, "up")
                            jet_weight_bSFDown, _, _ = calc_btag_sf_weight(b_tagged, flavId, jet_pt, jet_eta, "down")

                    if with_JER_sys:
                        #jer_factor, up, down = ev.jet_jer_factor[i], ev.jet_jer_factor_up[i], ev.jet_jer_factor_down[i]
                        up, down = ev.jet_jer_factor_up[i], ev.jet_jer_factor_down[i]
                        jet_factor_JERUp   = (up   / jer_factor) if jer_factor > 0 else 0
                        jet_factor_JERDown = (down / jer_factor) if jer_factor > 0 else 0

                        jet_pt_jer_up   = jet_pt * jet_factor_JERUp
                        jet_pt_jer_down = jet_pt * jet_factor_JERDown

                    if with_JES_sys:
                        #jes_shift = ev.jet_jes_correction_relShift[i]
                        jes_shift = ev.jet_jes_uncertainty[i]
                        jet_factor_JESUp   = 1 + jes_shift
                        jet_factor_JESDown = 1 - jes_shift

                        jet_pt_jes_up   = jet_pt * jet_factor_JESUp
                        jet_pt_jes_down = jet_pt * jet_factor_JESDown

                '''
                # I'll do this per selection cut, since I tau-match
                if not jet_tau_match_lowest:
                    # jet is p4, jet energy factor (which is 1 for nominal), b SF factor and bID lev
                    # the jet energy factor was corrected in ntuple but what's with MET?
                    # met comes from met_x = ev.met_corrected.Px()
                    # which:
                    #     LorentzVector MET_corrected = NT_met_init - full_jet_corr; // checked: this is really negligible correction
                    #     const pat::MET& MET = metsHandle_slimmedMETs->front();
                    #     NT_met_slimmedMets = MET.p4();
                    #     NT_met_init = MET.p4();
                    # and full cor is:
                    #     full_jet_corr += jet.p4() - jet_initial_p4; // initial jet + this difference = corrected jet
                    # MET init + jet init = MET cor + jet cor
                    # but these jets are from loop over all jets with Loose ID and pt cut at 20
                    # -- all eta pass

                    # jets are corrected with:
                    # jet.setP4(jet.p4()*jer_factor); // same as scaleEnergy in the Jet POG example
                    # but JES correction was not applied as in:
                    #//jet.setP4(rawJet*jes_correction);
                    # -- I rely on the correction in miniaod and put the JES shift on top of it
                    # I wanted to compare the miniaod jets with re-corrected ones but didn't do it
                    # and I save it in
                    # NT_jet_jes_recorrection.push_back(jes_correction);

                    # if I re-correct JES:
                    # - take rawJet
                    # - *jes_cor*jes_factor
                    # - compare to usual jet? save full correction?
                    # -- the easiest is to save rawJet() lists with the propper jes*jer factors for MC
                    #    the MET propagation will work on its own in the following
                    # RECORRECTED jets

                    # there is also this crap
                    # float jecFactor = jet.jecFactor("Uncorrected") ;
                    # which should be the same the other way

                    # AND a question for $100: is slimmed_met calculated with Uncorrected jets or default miniaod jets?
                    # what exactly should I propagate to met?
                    # -- let's try this and that separately? some control distrs?
                    # I saved the met with JER propagated from miniaod jet, not jes and jer from uncor jet...
                    # the initial met is in
                    # met_init
                    # and there is also uncorrected -- but that's only for latest data
                    # it's late, trying init met and re-correction from raw jets

                    # turns out:
                    # jet_p4 = slimmed jets, not the JER_corrected ones!
                    # hence use jet_p4 * UncorFactor * jes * jer

                    # nominals
                    if b_tagged_medium:
                        jets_nom.lowest.medium.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                        if with_bSF_sys:
                            jets_bUp  .lowest.medium.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                            jets_bDown.lowest.medium.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > 20.: jets_JERUp  .lowest.medium.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > 20.: jets_JERDown.lowest.medium.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > 20.: jets_JESUp  .lowest.medium.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > 20.: jets_JESDown.lowest.medium.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    elif b_tagged_loose:
                        jets_nom.lowest.loose.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                        if with_bSF_sys:
                            jets_bUp  .lowest.loose.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                            jets_bDown.lowest.loose.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > 20.: jets_JERUp  .lowest.loose.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > 20.: jets_JERDown.lowest.loose.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > 20.: jets_JESUp  .lowest.loose.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > 20.: jets_JESDown.lowest.loose.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    else:
                        jets_nom.lowest.rest.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                        if with_bSF_sys:
                            jets_bUp  .lowest.rest.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                            jets_bDown.lowest.rest.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > 20.: jets_JERUp  .lowest.rest.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > 20.: jets_JERDown.lowest.rest.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > 20.: jets_JESUp  .lowest.rest.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > 20.: jets_JESDown.lowest.rest.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                else:
                    # this is the lowest selection, loose b-jets count
                    if b_tagged_loose:
                        jets_nom.lowest.taumatched[0].append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                        if with_bSF_sys:
                            jets_bUp  .lowest.taumatched[0].append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                            jets_bDown.lowest.taumatched[0].append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > 20.: jets_JERUp  .lowest.taumatched[0].append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > 20.: jets_JERDown.lowest.taumatched[0].append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > 20.: jets_JESUp  .lowest.taumatched[0].append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > 20.: jets_JESDown.lowest.taumatched[0].append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    else:
                        jets_nom.lowest.taumatched[1].append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                        if with_bSF_sys:
                            jets_bUp  .lowest.taumatched[1].append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                            jets_bDown.lowest.taumatched[1].append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > 20.: jets_JERUp  .lowest.taumatched[1].append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > 20.: jets_JERDown.lowest.taumatched[1].append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > 20.: jets_JESUp  .lowest.taumatched[1].append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > 20.: jets_JESDown.lowest.taumatched[1].append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                '''

                '''
                pt_cut = 22.
                if not jet_tau_match_cuts:
                    # the same, but the cuts and lowest -> cuts
                    # nominals
                    if b_tagged_medium:
                        if jet_pt > pt_cut:
                            jets_nom.cuts.medium.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .cuts.medium.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.cuts.medium.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .cuts.medium.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.cuts.medium.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .cuts.medium.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.cuts.medium.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    elif b_tagged_loose:
                        if jet_pt > pt_cut:
                            jets_nom.cuts.loose.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .cuts.loose.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.cuts.loose.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .cuts.loose.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.cuts.loose.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .cuts.loose.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.cuts.loose.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    else:
                        if jet_pt > pt_cut:
                            jets_nom.cuts.rest.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .cuts.rest.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.cuts.rest.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .cuts.rest.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.cuts.rest.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .cuts.rest.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.cuts.rest.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                else:
                    # this is the cuts selection, same as lowest but with pt cuts, loose b-jets count
                    if b_tagged_loose:
                        if jet_pt > pt_cut:
                            jets_nom.cuts.taumatched[0].append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .cuts.taumatched[0].append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.cuts.taumatched[0].append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .cuts.taumatched[0].append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.cuts.taumatched[0].append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .cuts.taumatched[0].append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.cuts.taumatched[0].append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    else:
                        if jet_pt > pt_cut:
                            jets_nom.cuts.taumatched[1].append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .cuts.taumatched[1].append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.cuts.taumatched[1].append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .cuts.taumatched[1].append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.cuts.taumatched[1].append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .cuts.taumatched[1].append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.cuts.taumatched[1].append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                '''


                pt_cut = 30.
                # match lep
                if not match_lep:
                  # match tau
                  if not jet_tau_match_old:
                    # the same, but the cuts and lowest -> cuts
                    # nominals
                    # match b-tag
                    if b_tagged_medium:
                        # pass pt cuts
                        if jet_pt > pt_cut:
                            jets_nom.old.medium.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .old.medium.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.old.medium.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .old.medium.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.old.medium.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .old.medium.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.old.medium.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    elif b_tagged_loose:
                        if jet_pt > pt_cut:
                            jets_nom.old.loose.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .old.loose.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.old.loose.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .old.loose.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.old.loose.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .old.loose.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.old.loose.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    else:
                        if jet_pt > pt_cut:
                            jets_nom.old.rest.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .old.rest.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.old.rest.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .old.rest.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.old.rest.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .old.rest.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.old.rest.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                  else:
                    # this is the old selection, the medium b jets count
                    if b_tagged_medium:
                        if jet_pt > pt_cut:
                            jets_nom.old.taumatched[0].append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .old.taumatched[0].append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.old.taumatched[0].append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .old.taumatched[0].append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.old.taumatched[0].append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .old.taumatched[0].append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.old.taumatched[0].append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    else:
                        if jet_pt > pt_cut:
                            jets_nom.old.taumatched[1].append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .old.taumatched[1].append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.old.taumatched[1].append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .old.taumatched[1].append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.old.taumatched[1].append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .old.taumatched[1].append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.old.taumatched[1].append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                else:
                    # matched lep
                    if jet_pt > pt_cut:
                        jets_nom.old.lepmatched.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                        # TODO: notice, the b weights of these jets are not considered
                        #if with_bSF_sys:
                        #    jets_bUp  .old.lepmatched.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                        #    jets_bDown.old.lepmatched.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                    if with_JER_sys:
                        if jet_pt_jer_up   > pt_cut: jets_JERUp  .old.lepmatched.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                        if jet_pt_jer_down > pt_cut: jets_JERDown.old.lepmatched.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    if with_JES_sys:
                        if jet_pt_jes_up   > pt_cut: jets_JESUp  .old.lepmatched.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                        if jet_pt_jes_down > pt_cut: jets_JESDown.old.lepmatched.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))


                # old alliso jets are considered only for alliso preselection
                # where taus are never considered
                # therefore no dR to taus
                pt_cut = 30.
                if not match_lep_alliso:
                    # the same, but the cuts and lowest -> cuts
                    # nominals
                    if b_tagged_medium:
                        if jet_pt > pt_cut:
                            jets_nom.old_alliso.medium.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .old_alliso.medium.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.old_alliso.medium.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .old_alliso.medium.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.old_alliso.medium.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .old_alliso.medium.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.old_alliso.medium.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    elif b_tagged_loose:
                        if jet_pt > pt_cut:
                            jets_nom.old_alliso.loose.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .old_alliso.loose.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.old_alliso.loose.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .old_alliso.loose.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.old_alliso.loose.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .old_alliso.loose.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.old_alliso.loose.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    else:
                        if jet_pt > pt_cut:
                            jets_nom.old_alliso.rest.append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .old_alliso.rest.append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.old_alliso.rest.append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .old_alliso.rest.append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.old_alliso.rest.append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .old_alliso.rest.append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.old_alliso.rest.append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                # alliso is only used in presel, no taumatch checks here
                '''
                else:
                    # this is the old selection, the medium b jets count
                    if b_tagged_medium:
                        if jet_pt > pt_cut:
                            jets_nom.old_alliso.taumatched[0].append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .old_alliso.taumatched[0].append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.old_alliso.taumatched[0].append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .old_alliso.taumatched[0].append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.old_alliso.taumatched[0].append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .old_alliso.taumatched[0].append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.old_alliso.taumatched[0].append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                    else:
                        if jet_pt > pt_cut:
                            jets_nom.old_alliso.taumatched[1].append((p4, en_factor, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if with_bSF_sys:
                                jets_bUp  .old_alliso.taumatched[1].append((p4, en_factor, jet_weight_bSFUp,   jet_b_discr, HF, PF, jet_index))
                                jets_bDown.old_alliso.taumatched[1].append((p4, en_factor, jet_weight_bSFDown, jet_b_discr, HF, PF, jet_index))

                        if with_JER_sys:
                            if jet_pt_jer_up   > pt_cut: jets_JERUp  .old_alliso.taumatched[1].append((p4, en_factor * jet_factor_JERUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jer_down > pt_cut: jets_JERDown.old_alliso.taumatched[1].append((p4, en_factor * jet_factor_JERDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))

                        if with_JES_sys:
                            if jet_pt_jes_up   > pt_cut: jets_JESUp  .old_alliso.taumatched[1].append((p4, en_factor * jet_factor_JESUp,   jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                            if jet_pt_jes_down > pt_cut: jets_JESDown.old_alliso.taumatched[1].append((p4, en_factor * jet_factor_JESDown, jet_weight_bSF_nom, jet_b_discr, HF, PF, jet_index))
                '''







                # just commenting the old jet procedure,
                # this one seems cleaner in every way
                """
                # OPTIMIZATION
                # so, these are jets, passing pt, eta, ID and cross-dR from tau
                # I set jet correction multiplier = 1
                # and set b tag IDlev

                # jet corrections for MC

                bjets_all_foropt.append((p4, 1, b_tagged_loose + b_tagged_medium + b_tagged_tight))

                if b_tagged_loose: # no SF and so on
                    jets_b_nominal_loose.append((p4, 1))
                else:
                    jets_not_loose_b.append((p4, 1))
                if b_tagged_tight:
                    jets_b_nominal_tight.append((p4, 1))
                else:
                    jets_not_tight_b.append((p4, 1))

                if b_tagged:
                    #nbjets_nominal += 1
                    jets_b_nominal.append((p4, 1))
                else:
                    jets_nominal.append((p4, 1))
                if isMC and with_bSF: # do the SF weights
                    weight_bSF      *= calc_btag_sf_weight(b_tagged, flavId, p4.pt(), p4.eta())
                    if with_bSF_sys:
                        weight_bSF_up   *= calc_btag_sf_weight(b_tagged, flavId, p4.pt(), p4.eta(), "up")
                        weight_bSF_down *= calc_btag_sf_weight(b_tagged, flavId, p4.pt(), p4.eta(), "down")

                ## also save "minimal" jets -- with minimal pt threshold
                ## make them only at NOMINAL systematics for now
                #if p4.pt() > 20: # nominal jet
                #if abs(p4.eta()) < 2.3: # for FAKERATES
                #    all_jets_for_fakes.append(p4) # nominal corrections already applied in ntupler
                if b_tagged:
                    #nbjets_nominal += 1
                    jets_b_nominal_min.append((p4, 1))
                else:
                    jets_nominal_min.append((p4, 1))
                if isMC and with_bSF: # do the SF weights
                    weight_bSF_min  *= calc_btag_sf_weight(b_tagged, flavId, p4.pt(), p4.eta())
                    #weight_bSF_up   *= calc_btag_sf_weight(b_tagged, flavId, p4.pt(), p4.eta(), "up")
                    #weight_bSF_down *= calc_btag_sf_weight(b_tagged, flavId, p4.pt(), p4.eta(), "down")
                """

            # TODO: probably these weights are better to be computed at channel recording?
            #    -- the point is that a channel might not require a systematic
            #       but at the same time it is easier and cleaner to compute systematics per jet
            #       probably the only reasonable improvement would be to add a check and _store_ systematic only if required for this cut
            #       not sure if it is significant
            #       thus leaving it as is now -- systematics per event, loop over them and channels do discard
            #       the systematics change only the edge-of-cut events thus there should be few of them and optimization gains are small
            #       the only waste is the channel logic is checked for each systematic -- TODO: is it significant?

            """
            if isMC:
                # vary the jets with systematics, save b-tagged and other
                factor, up, down = ev.jet_jer_factor[i], ev.jet_jer_factor_up[i], ev.jet_jer_factor_down[i]
                #jes_shift = ev.jet_jes_correction_relShift[i]
                jes_shift = ev.jet_jes_uncertainty[i]
                # 
                mult = (up/factor) if factor > 0 else 0
                if p4.pt() * mult > 30: # jer up
                    if b_tagged:
                        #nbjets_jer_up += 1
                        jets_b_jer_up.append((p4, mult))
                    else:
                        jets_jer_up.append((p4, mult))
                    if isMC and with_bSF:
                        weight_bSF_jer_up *= calc_btag_sf_weight(b_tagged, flavId, p4.pt() * mult, p4.eta())

                mult = (down/factor) if factor > 0 else 0
                if p4.pt() * mult > 30: # jer down
                    if b_tagged:
                        #nbjets_jer_down += 1
                        jets_b_jer_down.append((p4, mult))
                    else:
                        jets_jer_down.append((p4, mult))
                    if isMC and with_bSF:
                        weight_bSF_jer_down *= calc_btag_sf_weight(b_tagged, flavId, p4.pt() * mult, p4.eta())

                mult = 1 + jes_shift
                if p4.pt() * mult > 30: # jer up
                    if b_tagged:
                        #nbjets_jes_up += 1
                        jets_b_jes_up.append((p4, mult))
                    else:
                        jets_jes_up.append((p4, mult))
                    if isMC and with_bSF:
                        weight_bSF_jes_up *= calc_btag_sf_weight(b_tagged, flavId, p4.pt() * mult, p4.eta())

                mult = 1 - jes_shift
                if p4.pt() * mult > 30: # jer down
                    if b_tagged:
                        #nbjets_jes_down += 1
                        jets_b_jes_down.append((p4, mult))
                    else:
                        jets_jes_down.append((p4, mult))
                    if isMC and with_bSF:
                        weight_bSF_jes_down *= calc_btag_sf_weight(b_tagged, flavId, p4.pt() * mult, p4.eta())
            """

            # save jets and factors for lj_var
            # count b jets
            # how to calc b SF weight? <---- just calc them, only for nominal jets
            #

        """
        # OPTIMIZATION
        bjets_all_foropt.sort(key=lambda bjet: bjet[2], reverse=True) # sort by IDlev
        bjets_cuts_loose  = []
        bjets_cuts_medium = []
        jets_cuts = []
        bjets_old_cuts = []
        jets_old_cuts = []

        #n_loose_bjets = n_medium_bjets = 0
        for p4, _, IDlev in bjets_all_foropt:
            #if IDlev > 1:
            #    n_loose_bjets  += 1
            #    n_medium_bjets += 1
            #elif IDlev == 1:
            #    n_loose_bjets  += 1

            #
            if p4.pt() > 25.:
                if IDlev == 1:
                    bjets_cuts_loose.append(p4)
                elif IDlev > 1:
                    bjets_cuts_medium.append(p4)
                else:
                    jets_cuts.append(p4)

            if p4.pt() > 30.:
                if IDlev > 1:
                    bjets_old_cuts.append(p4)
                elif IDlev < 1:
                    jets_old_cuts.append(p4)
        """

        # sort jets by pt
        # mainly to record various "leading blah jet"
        # TODO: not sure if it is worthwhile -- shouldn't all this be already sorted in ntupler?

        """ trying without sort
        jets_nom .lowest.rest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
        jets_nom   .cuts.rest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
        jets_nom    .old.rest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)

        jets_nom .lowest.loose.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
        jets_nom   .cuts.loose.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
        jets_nom    .old.loose.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)

        jets_nom .lowest.medium.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
        jets_nom   .cuts.medium.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
        jets_nom    .old.medium.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)

        if isMC:
            if with_bSF_sys:
                jets_bUp   .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bUp     .cuts.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bUp      .old.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bDown .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bDown   .cuts.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bDown    .old.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)

                jets_bUp   .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bUp     .cuts.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bUp      .old.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bDown .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bDown   .cuts.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bDown    .old.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)

                jets_bUp   .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bUp     .cuts.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bUp      .old.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bDown .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bDown   .cuts.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_bDown    .old.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)

            if with_JER_sys:
                jets_JERUp   .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_JERUp     .cuts.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_JERUp      .old.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_JERDown .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_JERDown   .cuts.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_JERDown    .old.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)

            if with_JES_sys:
                jets_JESUp   .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_JESUp     .cuts.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_JESUp      .old.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_JESDown .lowest.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_JESDown   .cuts.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
                jets_JESDown    .old.sort(key=lambda it: it[1]*it[0].pt(), reverse=True)
        """ # trying without sort

        #has_medium_tau = any(IDlev > 2 and p4.pt() > 30 for IDlev, p4 in zip(ev.tau_IDlev, ev.tau_p4))
        #has_medium_tau = ev.tau_IDlev.size() > 0 and ev.tau_IDlev[0] > 2 and ev.tau_p4[0].pt() > 30
        #has_medium_tau = bool(tau_pts_corrected)
        #TODO: propagate TES to MET?

        '''
        # for tau FAKERATES
        # loop over all jets and taus
        # matching them in dR
        # and if matched adding into according collection
        tau_jets_candidates = []
        tau_jets_vloose = []
        tau_jets_loose  = []
        tau_jets_medium = []
        tau_jets_tight  = []
        tau_jets_vtight = []
        for jet_p4 in all_jets_for_fakes:
            for tau_cand_p4, cand_IDlev in zip(ev.tau_p4, ev.tau_IDlev):
                #if tau_cand_p4.eta() < 2.3 and tau_cand_p4.pt() > 20: was done in ntupler
                tj_p4   = TLorentzVector(jet_p4.X(), jet_p4.Y(), jet_p4.Z(), jet_p4.T())
                ttau_p4 = TLorentzVector(tau_cand_p4.X(), tau_cand_p4.Y(), tau_cand_p4.Z(), tau_cand_p4.T())
                if tj_p4.DeltaR(ttau_p4) < 0.3:
                    # add the jet p4 into collection according to IDlev
                    #Int_t IDlev = 0;
                    #if (tau.tauID(tau_VTight_ID)) IDlev = 5;
                    #else if (tau.tauID(tau_Tight_ID))  IDlev = 4;
                    #else if (tau.tauID(tau_Medium_ID)) IDlev = 3;
                    #else if (tau.tauID(tau_Loose_ID))  IDlev = 2;
                    #else if (tau.tauID(tau_VLoose_ID)) IDlev = 1;
                    tau_jets_candidates.append(jet_p4)
                    if cand_IDlev > 0:
                        if cand_IDlev == 1:
                            tau_jets_vloose.append(jet_p4)
                        elif cand_IDlev == 2:
                            tau_jets_vloose.append(jet_p4)
                            tau_jets_loose .append(jet_p4)
                        elif cand_IDlev == 3:
                            tau_jets_vloose.append(jet_p4)
                            tau_jets_loose .append(jet_p4)
                            tau_jets_medium.append(jet_p4)
                        elif cand_IDlev == 4:
                            tau_jets_vloose.append(jet_p4)
                            tau_jets_loose .append(jet_p4)
                            tau_jets_medium.append(jet_p4)
                            tau_jets_tight .append(jet_p4)
                        elif cand_IDlev == 5:
                            tau_jets_vloose.append(jet_p4)
                            tau_jets_loose .append(jet_p4)
                            tau_jets_medium.append(jet_p4)
                            tau_jets_tight .append(jet_p4)
                            tau_jets_vtight.append(jet_p4)
        '''



        # shape systematics are:
        # corrected jet pts and tau pts
        # weight variations
        #nominal systematics
        # jet pts, tau pts, b weight (=1 for data), pu weight (=1 for data)

        syst_weights_nominal = [weight, weight_pu, 1., 1.]
        syst_weights = {} # {'NOMINAL': syst_weights_nominal}
        # data and tt systematic datasets have all nominal systematic variations -- they are a systematic themselves
        if isTT_systematic:
            syst_objects = {isTT_systematic: [jets_nom, taus_nom, proc_met]}
        elif not isMC:
            syst_objects = {'NOMINAL': [jets_nom, taus_nom, proc_met]}
        elif isMC:
            syst_objects = {'NOMINAL'  : [jets_nom,     taus_nom,    proc_met    ],
                           'JESUp'     : [jets_JESUp,   taus_nom,    proc_met_JESUp   ],
                           'JESDown'   : [jets_JESDown, taus_nom,    proc_met_JESDown ],
                           'JERUp'     : [jets_JERUp,   taus_nom,    proc_met_JERUp   ],
                           'JERDown'   : [jets_JERDown, taus_nom,    proc_met_JERDown ],
                           'TauESUp'   : [jets_nom,     taus_ESUp  , proc_met ],
                           'TauESDown' : [jets_nom,     taus_ESDown, proc_met ],
                           'bSFUp'     : [jets_bUp,     taus_nom,    proc_met ],
                           'bSFDown'   : [jets_bDown,   taus_nom,    proc_met ],
                           }
            syst_weights.update({
                           'LEPUp'     : [weight_lep_Up,   weight_pu,    1, 1.],
                           'LEPDown'   : [weight_lep_Down, weight_pu,    1, 1.],
                           'PUUp'      : [weight,          weight_pu_up, 1, 1.],
                           'PUDown'    : [weight,          weight_pu_dn, 1, 1.],
                           })

            if isTT:
                syst_weights['TOPPTUp']    = [weight, weight_pu, weight_top_pt, 1.]
                syst_weights['TOPPTDown']  = [weight, weight_pu, 1.,            1.]
                if with_AlphaS_sys:
                    syst_weights['AlphaSUp']   = [weight, weight_pu, 1.,  weights_gen_weight_alphas_up]
                    syst_weights['AlphaSDown'] = [weight, weight_pu, 1.,  weights_gen_weight_alphas_dn]
                if with_Frag_sys:
                    syst_weights['FragUp']        = [weight, weight_pu, 1.,  weights_gen_weight_Frag[0] / weights_gen_weight_centralFrag]
                    syst_weights['FragDown']      = [weight, weight_pu, 1.,  weights_gen_weight_Frag[1] / weights_gen_weight_centralFrag]
                    syst_weights['SemilepBRUp']   = [weight, weight_pu, 1.,  weights_gen_weight_semilepbr[0] / weights_gen_weight_centralFrag]
                    syst_weights['SemilepBRDown'] = [weight, weight_pu, 1.,  weights_gen_weight_semilepbr[1] / weights_gen_weight_centralFrag]
                    syst_weights['PetersonUp']    = [weight, weight_pu, 1.,  weights_gen_weight_Peterson / weights_gen_weight_centralFrag]
                    syst_weights['PetersonDown']  = [weight, weight_pu, 1.,  1.]
                if with_MEscale_sys:
                    syst_weights['MrUp']    = [weight, weight_pu, 1., weights_gen_weight_f_rUp]
                    syst_weights['MrDown']  = [weight, weight_pu, 1., weights_gen_weight_f_rDn]
                    syst_weights['MfUp']    = [weight, weight_pu, 1., weights_gen_weight_fUp_r]
                    syst_weights['MfDown']  = [weight, weight_pu, 1., weights_gen_weight_fDn_r]
                    syst_weights['MfrUp']   = [weight, weight_pu, 1., weights_gen_weight_frUp ]
                    syst_weights['MfrDown'] = [weight, weight_pu, 1., weights_gen_weight_frDn ]
                # and PDFs

        # remove not requested syst_objects to reduce the loop:
        for name, _ in syst_objects.items():
            if name not in requested_systematics:
                syst_objects.pop(name)
        # same for weights
        for name, _ in syst_weights.items():
            if name not in requested_systematics:
                syst_weights.pop(name)

        #print syst_objects.keys()
        #print syst_weights.keys()

        # SYSTEMATIC LOOP, RECORD
        # for each systematic
        # pass one of the reco selections
        # check the subprocess
        # store distr

        control_counters.Fill(53)

        for sys_i, (sys_name, (jets, taus, proc_met)) in enumerate(syst_objects.items()):
            #control_counters.Fill(4 + sys_i)
            '''
            1) for each variation of objects check if which channels pass
            2) then in the recording make a special section to fill histos with systematic weights
            3) for the rest use only the nominal weights

            from the object I only need the weight of bSF?
            routine to record a histo with all sys weights?
            and to create that histo with all sys weights?
            -- already the histos are created only for certain systs
            '''
            # -- I miss the bSF weight
            # TODO: in principle it should be added according to the b-s used in the selection and passed down to the channel
            #       notice the b SF are calculated in old scheme, for medium jets only
            #       so for now I'll use this weight everywhere
            weight_bSF = 1.
            #sys_weight_min = weight * weight_bSF_min * weight_PU * weight_top_pt
            # pass reco selections

            # all the channel selections follow
            passed_channels = []

            if sys_i == 0:
                control_counters.Fill(100)

            if pass_mu:
                control_counters.Fill(101)

            if pass_el:
                control_counters.Fill(102)

            if pass_elmu:
                control_counters.Fill(103)

            if pass_elmu_el:
                control_counters.Fill(104)

            if pass_mu_all:
                control_counters.Fill(105)

            if pass_el_all:
                control_counters.Fill(106)

            #has_lowest_2L1M = len(jets.lowest.medium) > 0 and (len(jets.lowest.medium) + len(jets.lowest.loose)) > 1 

            weight_bSF_lowest = 1.
            # p4, energy factor, b SF weight, ID lev
            #for _, _, jet_weight, _, _, _, _ in jets.lowest.medium + jets.lowest.loose + jets.lowest.rest:
            #    weight_bSF_lowest *= jet_weight

            weight_bSF_old = 1.
            for _, _, jet_weight, _, _, _, _ in jets.old.medium + jets.old.loose + jets.old.rest:
                weight_bSF_old *= jet_weight

            weight_bSF_old_alliso = 1.
            for _, _, jet_weight, _, _, _, _ in jets.old_alliso.medium + jets.old_alliso.loose + jets.old_alliso.rest:
                weight_bSF_old_alliso *= jet_weight

            has_tight_lowest_taus = len(taus.lowest) > 0
            has_loose_lowest_taus = len(taus.loose) > 0

            #old_jet_sel = (len(jets.old.medium) + len(jets.old.taumatched[0])) > 0 and (len(jets.old.taumatched[0]) + len(jets.old.taumatched[1]) + len(jets.old.medium) + len(jets.old.loose) + len(jets.old.rest)) > 2
            # separate b and tau tags
            old_jet_sel = len(jets.old.medium) > 0 and (len(jets.old.taumatched[0]) + len(jets.old.taumatched[1]) + len(jets.old.medium) + len(jets.old.loose) + len(jets.old.rest)) > 2

            pass_2b = len(jets.old.medium) > 1

            old_jet_sel_alliso = len(jets.old_alliso.medium) > 0 and (len(jets.old_alliso.taumatched[0]) + len(jets.old_alliso.taumatched[1]) + len(jets.old_alliso.medium) + len(jets.old_alliso.loose) + len(jets.old_alliso.rest)) > 2

            if old_jet_sel:
                control_counters.Fill(111)

            if len(taus.old) > 0:
                control_counters.Fill(112)

            if pass_mu and old_jet_sel:
                control_counters.Fill(203)

            if pass_el and old_jet_sel:
                control_counters.Fill(303)

            if pass_mu and old_jet_sel and len(taus.old) > 0:
                control_counters.Fill(304)

            if pass_el and old_jet_sel and len(taus.old) > 0:
                control_counters.Fill(304)

            # 3 jets (2b and 1 tau) and 1 b-tagged
            # TODO: compare with previous result with only 2 jets and 1 b-tagged -- check njets distrs
            pass_old_mu_sel = pass_mu and old_jet_sel and len(taus.old) > 0 # and no met cut
            pass_old_el_sel = pass_el and old_jet_sel and len(taus.old) > 0 # and no met cut

            pass_old_mu_sel_Vloose = pass_mu and old_jet_sel and len(taus.oldVloose) > 0 # and no met cut
            pass_old_el_sel_Vloose = pass_el and old_jet_sel and len(taus.oldVloose) > 0 # and no met cut

            pass_old_mu_presel = pass_mu and old_jet_sel and len(taus.presel) > 0
            pass_old_el_presel = pass_el and old_jet_sel and len(taus.presel) > 0
            pass_old_lep_presel = pass_old_mu_presel or pass_old_el_presel

            # alliso
            pass_old_mu_presel_alliso = pass_mu_all and old_jet_sel_alliso and len(taus.presel_alliso) > 0
            pass_old_el_presel_alliso = pass_el_all and old_jet_sel_alliso and len(taus.presel_alliso) > 0

            pass_old_mu_sel_Vloose_alliso = pass_mu_all and old_jet_sel_alliso and len(taus.oldVloose) > 0
            pass_old_el_sel_Vloose_alliso = pass_el_all and old_jet_sel_alliso and len(taus.oldVloose) > 0

            pass_elmu_close = pass_elmu and (len(jets.old.medium) + len(jets.old.taumatched[0])) > 0 and (len(jets.old.taumatched[0]) + len(jets.old.taumatched[1]) + len(jets.old.medium) + len(jets.old.loose) + len(jets.old.rest)) > 1

            pass_elmu_el_close = pass_elmu_el and (len(jets.old.medium) + len(jets.old.taumatched[0])) > 0 and (len(jets.old.taumatched[0]) + len(jets.old.taumatched[1]) + len(jets.old.medium) + len(jets.old.loose) + len(jets.old.rest)) > 1

            #requires_lj = pass_elmu_close or pass_old_lep_presel or pass_old_mu_sel or pass_old_el_sel or ((pass_el_all or pass_mu_all) and has_lowest_2L1M and (has_tight_lowest_taus or has_loose_lowest_taus))
            requires_lj = pass_elmu_close or pass_old_lep_presel or pass_old_mu_sel or pass_old_el_sel # or ((pass_el_all or pass_mu_all) and has_lowest_2L1M and (has_tight_lowest_taus or has_loose_lowest_taus))
            if requires_lj:
                # all jets, without regard to tau in the event go into the calculation
                # (taumatched jets go too)
                with_all_permutation_masses = True
                # order: not-b-taged, b-taged
                # only medium b-tags p8 p9
                b_cand_jets     = jets.old.medium + jets.old.taumatched[0]
                light_cand_jets = jets.old.rest + jets.old.loose + jets.old.taumatched[1]
                lj_var, w_mass, t_mass, lj_gens, all_masses = calc_lj_var(ev, light_cand_jets, b_cand_jets, with_all_permutation_masses, isMC)
                # medium and loose b-tags
                # but tau-matches are done to Medium b!
                #lj_var, w_mass, t_mass, lj_gens, all_masses = calc_lj_var(ev, jets.old.rest + jets.old.taumatched[1], jets.old.medium + jets.old.loose + jets.old.taumatched[0], with_all_permutation_masses, isMC)
                n_bjets_used_in_lj = len(b_cand_jets)
                lj_cut = 60.
                large_lj = lj_var > lj_cut

                # for tt_lj MC truth find the jets in these groups
                if (abs(ev.gen_t_w_decay_id) == 13 or abs(ev.gen_t_w_decay_id) == 11) and abs(ev.gen_tb_w_decay_id) == 1:
                    # in tb the jets' genmatches are -6 (b) and -5 (w)
                    propper_b = -6
                    propper_w = -5
                elif abs(ev.gen_t_w_decay_id) == 1 and (abs(ev.gen_tb_w_decay_id) == 13 or abs(ev.gen_tb_w_decay_id) == 11):
                    propper_b = 6
                    propper_w = 5
                else:
                    propper_b = 0
                    propper_w = 0

                jets_input_has = 0
                #3*(lj_b_gen == propper_b) + (lj_w1_gen == propper_w) + (lj_w2_gen == propper_w)
                #closest_pair_gens = (ev.jet_matching_gen[light_jets[i][6]], ev.jet_matching_gen[light_jets[u][6]])
                if propper_b:
                    for b_cand in b_cand_jets:
                        if b_cand[6] == propper_b:
                            jets_input_has += 3
                            break

                    found_light = False
                    for cand in light_cand_jets:
                        if cand[6] == propper_w:
                            jets_input_has += 1
                            if found_light: break
                            found_light = True


            tauSign3 = False
            if len(taus.old) > 0:
                # tau original index
                # taus_nom.old .append((p4, TES_factor, tau_pdgID, i))
                if ev.tau_refited_index[taus.old[0][3]] >= 0:
                    tauSign3 = ev.tau_SV_geom_flightLenSign[ev.tau_refited_index[taus.old[0][3]]] > 3.

            '''
                'optel_presel_2L1M':
                'optel_tight_2L1M':
                'optel_tight_2L1M_lj':
                'optel_tight_2L1M_ljout':

            all iso, ss
            '''

            # I sorted all tau by pt -- and take the first one always

            ''' the selections for optimization
            if pass_el and has_lowest_2L1M and len(taus.presel) > 0:
                presel_os = taus.presel[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_lowest
                sel_jets = jets.lowest
                sel_taus = taus.presel

                if presel_os:
                    passed_channels.append(('optel_presel_2L1M', sel_b_weight, sel_jets, sel_taus))
                else:
                    passed_channels.append(('optel_presel_2L1M_ss', sel_b_weight, sel_jets, sel_taus))

                if has_tight_lowest_taus: # these are tight taus
                    lowest_os = taus.lowest[0][2] * ev.lep_id[0] < 0
                    sel_taus = taus.lowest
                    if lowest_os:
                        passed_channels.append(('optel_tight_2L1M', sel_b_weight, sel_jets, sel_taus))
                        if large_lj:
                            passed_channels.append(('optel_tight_2L1M_ljout', sel_b_weight, sel_jets, sel_taus))
                        else:
                            passed_channels.append(('optel_tight_2L1M_lj', sel_b_weight, sel_jets, sel_taus))
                    else:
                        passed_channels.append(('optel_tight_2L1M_ss', sel_b_weight, sel_jets, sel_taus))
                        if large_lj:
                            passed_channels.append(('optel_tight_2L1M_ljout_ss', sel_b_weight, sel_jets, sel_taus))
                        else:
                            passed_channels.append(('optel_tight_2L1M_lj_ss', sel_b_weight, sel_jets, sel_taus))

            if pass_el_all and has_lowest_2L1M and len(taus.presel) > 0:
                # for all iso don't add passed channel
                # just save the relIso and ?
                # -- whatever.. just save everything too
                presel_os = taus.presel[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_lowest
                sel_jets = jets.lowest
                sel_taus = taus.presel

                if presel_os:
                    passed_channels.append(('optel_alliso_presel_2L1M', sel_b_weight, sel_jets, sel_taus))
                else:
                    passed_channels.append(('optel_alliso_presel_2L1M_ss', sel_b_weight, sel_jets, sel_taus))

                if has_tight_lowest_taus: # these are tight taus
                    lowest_os = taus.lowest[0][2] * ev.lep_id[0] < 0
                    sel_taus = taus.lowest
                    if lowest_os:
                        passed_channels.append(('optel_alliso_tight_2L1M', sel_b_weight, sel_jets, sel_taus))
                        if large_lj:
                            passed_channels.append(('optel_alliso_tight_2L1M_ljout', sel_b_weight, sel_jets, sel_taus))
                        else:
                            passed_channels.append(('optel_alliso_tight_2L1M_lj', sel_b_weight, sel_jets, sel_taus))
                    else:
                        passed_channels.append(('optel_alliso_tight_2L1M_ss', sel_b_weight, sel_jets, sel_taus))
                        if large_lj:
                            passed_channels.append(('optel_alliso_tight_2L1M_ljout_ss', sel_b_weight, sel_jets, sel_taus))
                        else:
                            passed_channels.append(('optel_alliso_tight_2L1M_lj_ss', sel_b_weight, sel_jets, sel_taus))


            #if pass_mu and pass_single_lep_presel:
            #    passed_channels.append('mu_presel')

            # for mu I also have cuts selection
            has_cuts_2L1M = len(jets.cuts.medium) > 0 and (len(jets.cuts.medium) + len(jets.cuts.loose)) > 1 
            has_tight_cuts_taus = len(taus.cuts) > 0

            if pass_mu and has_lowest_2L1M and len(taus.presel) > 0:
                presel_os = taus.presel[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_lowest
                sel_jets = jets.lowest
                sel_taus = taus.presel

                if presel_os:
                    passed_channels.append(('optmu_presel_2L1M', sel_b_weight, sel_jets, sel_taus))
                else:
                    passed_channels.append(('optmu_presel_2L1M_ss', sel_b_weight, sel_jets, sel_taus))

                if has_tight_lowest_taus: # these are tight taus
                    lowest_os = taus.lowest[0][2] * ev.lep_id[0] < 0
                    sel_taus = taus.lowest
                    if lowest_os:
                        passed_channels.append(('optmu_tight_2L1M', sel_b_weight, sel_jets, sel_taus))
                        if large_lj:
                            passed_channels.append(('optmu_tight_2L1M_ljout', sel_b_weight, sel_jets, sel_taus))
                        else:
                            passed_channels.append(('optmu_tight_2L1M_lj', sel_b_weight, sel_jets, sel_taus))
                    else:
                        passed_channels.append(('optmu_tight_2L1M_ss', sel_b_weight, sel_jets, sel_taus))
                        if large_lj:
                            passed_channels.append(('optmu_tight_2L1M_ljout_ss', sel_b_weight, sel_jets, sel_taus))
                        else:
                            passed_channels.append(('optmu_tight_2L1M_lj_ss', sel_b_weight, sel_jets, sel_taus))

                # cuts selection
                if has_tight_cuts_taus and has_cuts_2L1M: # these are tight taus
                    cuts_os = taus.cuts[0][2] * ev.lep_id[0] < 0
                    sel_taus = taus.cuts
                    if cuts_os:
                        passed_channels.append(('optmu_tight_2L1M_cuts', sel_b_weight, sel_jets, sel_taus))
                    else:
                        passed_channels.append(('optmu_tight_2L1M_cuts_ss', sel_b_weight, sel_jets, sel_taus))

                if has_loose_lowest_taus: # these are loose taus with lowest cuts
                    lep_os = taus.loose[0][2] * ev.lep_id[0] < 0
                    sel_taus = taus.loose
                    if lep_os:
                        passed_channels.append(('optmu_loose_2L1M', sel_b_weight, sel_jets, sel_taus))
                        if large_lj:
                            passed_channels.append(('optmu_loose_2L1M_ljout', sel_b_weight, sel_jets, sel_taus))
                        else:
                            passed_channels.append(('optmu_loose_2L1M_lj', sel_b_weight, sel_jets, sel_taus))
                    else:
                        passed_channels.append(('optmu_loose_2L1M_ss', sel_b_weight, sel_jets, sel_taus))
                        if large_lj:
                            passed_channels.append(('optmu_loose_2L1M_ljout_ss', sel_b_weight, sel_jets, sel_taus))
                        else:
                            passed_channels.append(('optmu_loose_2L1M_lj_ss', sel_b_weight, sel_jets, sel_taus))

            # whatever just save all
            if pass_mu_all and has_lowest_2L1M and len(taus.presel) > 0:
                presel_os = taus.presel[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_lowest
                sel_jets = jets.lowest
                sel_taus = taus.presel

                if presel_os:
                    passed_channels.append(('optmu_alliso_presel_2L1M', sel_b_weight, sel_jets, sel_taus))
                else:
                    passed_channels.append(('optmu_alliso_presel_2L1M_ss', sel_b_weight, sel_jets, sel_taus))

                if has_tight_lowest_taus: # these are tight taus
                    lowest_os = taus.lowest[0][2] * ev.lep_id[0] < 0
                    sel_taus = taus.lowest
                    if lowest_os:
                        passed_channels.append(('optmu_alliso_tight_2L1M', sel_b_weight, sel_jets, sel_taus))
                        if large_lj:
                            passed_channels.append(('optmu_alliso_tight_2L1M_ljout', sel_b_weight, sel_jets, sel_taus))
                        else:
                            passed_channels.append(('optmu_alliso_tight_2L1M_lj', sel_b_weight, sel_jets, sel_taus))
                    else:
                        passed_channels.append(('optmu_alliso_tight_2L1M_ss', sel_b_weight, sel_jets, sel_taus))
                        if large_lj:
                            passed_channels.append(('optmu_alliso_tight_2L1M_ljout_ss', sel_b_weight, sel_jets, sel_taus))
                        else:
                            passed_channels.append(('optmu_alliso_tight_2L1M_lj_ss', sel_b_weight, sel_jets, sel_taus))

                # cuts selection
                if has_tight_cuts_taus and has_cuts_2L1M: # these are tight taus
                    cuts_os = taus.cuts[0][2] * ev.lep_id[0] < 0
                    sel_taus = taus.cuts
                    if cuts_os:
                        passed_channels.append(('optmu_alliso_tight_2L1M_cuts', sel_b_weight, sel_jets, sel_taus))
                    else:
                        passed_channels.append(('optmu_alliso_tight_2L1M_cuts_ss', sel_b_weight, sel_jets, sel_taus))
            '''

            # wjets, dy mumu, tt elmu, old mu_sel

            """
                'ctr_mu_wjet':              (procs_mu, systematic_names_pu),
                'ctr_mu_wjet_ss':           (procs_mu, systematic_names_pu),
                'ctr_alliso_mu_wjet':       (procs_mu, systematic_names_pu),
                'ctr_alliso_mu_wjet_ss':    (procs_mu, systematic_names_pu),
                'ctr_mu_dy_mumu':           (procs_mu, systematic_names_pu),

                'ctr_tt_elmu':              (procs_elmu, systematic_names_nominal),
                'ctr_old_mu_sel':           (procs_mu, systematic_names_nominal),     # testing issue with event yield advantage
            """

            if pass_mumu:
                passed_channels.append(('ctr_mu_dy_mumu', False, leps.iso, jets.old, taus.presel))
            if pass_elel:
                passed_channels.append(('ctr_mu_dy_elel', False, leps.iso, jets.old, taus.presel))
            if pass_elmu:
                passed_channels.append(('ctr_mu_tt_em', False, leps.iso, jets.old, taus.presel))
                # elmu selection with almost main jet requirements
                #old_jet_sel = len(jets.old.medium) > 0 and (len(jets.old.medium) + len(jets.old.loose) + len(jets.old.rest)) > 2
                # at least 2 jets (3-1 for missing tau jet) and 1 b-tagged
                # the selection should be close to lep+tau but there is another lepton instead of tau
                #if len(jets.old.medium) > 0 and (len(jets.old.medium) + len(jets.old.loose) + len(jets.old.rest)) > 1:
                if pass_elmu_close:
                    passed_channels.append(('ctr_mu_tt_em_close', 1., leps.iso, jets.old, taus.old))

            if pass_elmu_el:
                passed_channels.append(('ctr_el_tt_em', False, leps.iso, jets.old, taus.presel))
                if pass_elmu_el_close:
                    passed_channels.append(('ctr_el_tt_em_close', 1., leps.iso, jets.old, taus.old))

            #if pass_mu and nbjets == 0 and (Mt_lep_met > 50 or met_pt > 40): # skipped lep+tau mass -- hopefuly DY will be small (-- it became larger than tt)
            #    passed_channels.append('ctr_mu_wjet')
            #if pass_mu_all and len(jets.old.medium) == 0 and (Mt_lep_met > 50 or met_pt > 40) and taus.presel:
            if pass_mu_all and len(jets.old_alliso.medium) == 0 and taus.presel_alliso:
                presel_os = taus.presel_alliso[0][2] * ev.lep_alliso_id[0] < 0
                sel_b_weight = weight_bSF_lowest
                if presel_os:
                    passed_channels.append(('ctr_alliso_mu_wjet', sel_b_weight, leps.alliso, jets.old_alliso, taus.presel_alliso))
                else:
                    passed_channels.append(('ctr_alliso_mu_wjet_ss', sel_b_weight, leps.alliso, jets.old_alliso, taus.presel_alliso))

            if pass_mu and len(jets.old.medium) == 0 and taus.presel:
                presel_os = taus.presel[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_lowest
                if presel_os:
                    passed_channels.append(('ctr_mu_wjet', sel_b_weight, leps.iso, jets.old, taus.presel))
                else:
                    passed_channels.append(('ctr_mu_wjet_ss', sel_b_weight, leps.iso, jets.old, taus.presel))

            if pass_el and len(jets.old.medium) == 0 and taus.presel:
                presel_os = taus.presel[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_lowest

                if presel_os:
                    passed_channels.append(('ctr_el_wjet', sel_b_weight, leps.iso, jets.old, taus.presel))
                else:
                    passed_channels.append(('ctr_el_wjet_ss', sel_b_weight, leps.iso, jets.old, taus.presel))


            if pass_old_mu_presel:
                presel_os = taus.presel[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_old
                if presel_os:
                    passed_channels.append(('ctr_old_mu_presel', sel_b_weight, leps.iso, jets.old, taus.presel))
                else:
                    passed_channels.append(('ctr_old_mu_presel_ss', sel_b_weight, leps.iso, jets.old, taus.presel))

            if pass_old_mu_presel and pass_2b:
                presel_os = taus.presel[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_old
                if presel_os:
                    passed_channels.append(('ctr_old_mu_presel2b', sel_b_weight, leps.iso, jets.old, taus.presel))
                else:
                    passed_channels.append(('ctr_old_mu_presel2b_ss', sel_b_weight, leps.iso, jets.old, taus.presel))

            if pass_old_el_presel and pass_2b:
                presel_os = taus.presel[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_old
                if presel_os:
                    passed_channels.append(('ctr_old_el_presel2b', sel_b_weight, leps.iso, jets.old, taus.presel))
                else:
                    passed_channels.append(('ctr_old_el_presel2b_ss', sel_b_weight, leps.iso, jets.old, taus.presel))

            # presel alliso
            if pass_old_mu_presel_alliso:
                presel_os = taus.presel_alliso[0][2] * ev.lep_alliso_id[0] < 0
                sel_b_weight = weight_bSF_old_alliso
                if presel_os:
                    passed_channels.append(('ctr_old_mu_presel_alliso', sel_b_weight, leps.alliso, jets.old_alliso, taus.presel_alliso))
                else:
                    passed_channels.append(('ctr_old_mu_presel_alliso_ss', sel_b_weight, leps.alliso, jets.old_alliso, taus.presel_alliso))

            if pass_old_el_presel_alliso:
                presel_os = taus.presel_alliso[0][2] * ev.lep_alliso_id[0] < 0
                sel_b_weight = weight_bSF_old_alliso
                if presel_os:
                    passed_channels.append(('ctr_old_el_presel_alliso', sel_b_weight, leps.alliso, jets.old_alliso, taus.presel_alliso))
                else:
                    passed_channels.append(('ctr_old_el_presel_alliso_ss', sel_b_weight, leps.alliso, jets.old_alliso, taus.presel_alliso))

            # VLoose alliso
            if pass_old_mu_sel_Vloose_alliso:
                presel_os = taus.oldVloose[0][2] * ev.lep_alliso_id[0] < 0
                sel_b_weight = weight_bSF_old_alliso
                if presel_os:
                    passed_channels.append(('ctr_old_mu_selVloose_alliso', sel_b_weight, leps.alliso, jets.old_alliso, taus.oldVloose))
                else:
                    passed_channels.append(('ctr_old_mu_selVloose_alliso_ss', sel_b_weight, leps.alliso, jets.old_alliso, taus.oldVloose))

            if pass_old_el_sel_Vloose_alliso:
                presel_os = taus.oldVloose[0][2] * ev.lep_alliso_id[0] < 0
                sel_b_weight = weight_bSF_old_alliso
                if presel_os:
                    passed_channels.append(('ctr_old_el_selVloose_alliso', sel_b_weight, leps.alliso, jets.old_alliso, taus.oldVloose))
                else:
                    passed_channels.append(('ctr_old_el_selVloose_alliso_ss', sel_b_weight, leps.alliso, jets.old_alliso, taus.oldVloose))

            #pass_single_lep_presel = large_met and has_3jets and has_bjets and (pass_el or pass_mu) #and os_lep_med_tau
            #pass_single_lep_sel = pass_single_lep_presel and os_lep_med_tau
            #if pass_mu and old_jet_sel and met_pt > 40 and len(taus.old) > 0:
            if pass_old_mu_sel:
                # actually I should add ev.lep_p4[0].pt() > 27
                old_os = taus.old[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_old
                if old_os:
                    passed_channels.append(('ctr_old_mu_sel', sel_b_weight, leps.iso, jets.old, taus.old))
                    if large_lj:
                        passed_channels.append(('ctr_old_mu_sel_ljout', sel_b_weight, leps.iso, jets.old, taus.old))
                    else:
                        passed_channels.append(('ctr_old_mu_sel_lj', sel_b_weight, leps.iso, jets.old, taus.old))
                else:
                    passed_channels.append(('ctr_old_mu_sel_ss', sel_b_weight, leps.iso, jets.old, taus.old))
                    if large_lj:
                        passed_channels.append(('ctr_old_mu_sel_ljout_ss', sel_b_weight, leps.iso, jets.old, taus.old))
                    else:
                        passed_channels.append(('ctr_old_mu_sel_lj_ss', sel_b_weight, leps.iso, jets.old, taus.old))

            if pass_old_mu_sel_Vloose:
                # actually I should add ev.lep_p4[0].pt() > 27
                old_os = taus.oldVloose[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_old
                if old_os:
                    passed_channels.append(('ctr_old_mu_selVloose', sel_b_weight, leps.iso, jets.old, taus.oldVloose))
                    if large_lj:
                        passed_channels.append(('ctr_old_mu_selVloose_ljout', sel_b_weight, leps.iso, jets.old, taus.oldVloose))
                    else:
                        passed_channels.append(('ctr_old_mu_selVloose_lj', sel_b_weight, leps.iso, jets.old, taus.oldVloose))
                else:
                    passed_channels.append(('ctr_old_mu_selVloose_ss', sel_b_weight, leps.iso, jets.old, taus.oldVloose))
                    if large_lj:
                        passed_channels.append(('ctr_old_mu_selVloose_ljout_ss', sel_b_weight, leps.iso, jets.old, taus.oldVloose))
                    else:
                        passed_channels.append(('ctr_old_mu_selVloose_lj_ss', sel_b_weight, leps.iso, jets.old, taus.oldVloose))

            if pass_old_el_sel_Vloose:
                # actually I should add ev.lep_p4[0].pt() > 27
                old_os = taus.oldVloose[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_old
                if old_os:
                    passed_channels.append(('ctr_old_el_selVloose', sel_b_weight, leps.iso, jets.old, taus.oldVloose))
                    if large_lj:
                        passed_channels.append(('ctr_old_el_selVloose_ljout', sel_b_weight, leps.iso, jets.old, taus.oldVloose))
                    else:
                        passed_channels.append(('ctr_old_el_selVloose_lj', sel_b_weight, leps.iso, jets.old, taus.oldVloose))
                else:
                    passed_channels.append(('ctr_old_el_selVloose_ss', sel_b_weight, leps.iso, jets.old, taus.oldVloose))
                    if large_lj:
                        passed_channels.append(('ctr_old_el_selVloose_ljout_ss', sel_b_weight, leps.iso, jets.old, taus.oldVloose))
                    else:
                        passed_channels.append(('ctr_old_el_selVloose_lj_ss', sel_b_weight, leps.iso, jets.old, taus.oldVloose))

            if pass_old_mu_sel and tauSign3:
                old_os = taus.old[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_old
                if old_os:
                    passed_channels.append(('ctr_old_mu_sel_tauSign3',    sel_b_weight, leps.iso, jets.old, taus.old))
                else:
                    passed_channels.append(('ctr_old_mu_sel_tauSign3_ss', sel_b_weight, leps.iso, jets.old, taus.old))

            if pass_old_el_presel:
                presel_os = taus.presel[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_old
                if presel_os:
                    passed_channels.append(('ctr_old_el_presel', sel_b_weight, leps.iso, jets.old, taus.presel))
                else:
                    passed_channels.append(('ctr_old_el_presel_ss', sel_b_weight, leps.iso, jets.old, taus.presel))

            if pass_old_el_sel:
                # actually I should add ev.lep_p4[0].pt() > 27
                old_os = taus.old[0][2] * ev.lep_id[0] < 0
                sel_b_weight = weight_bSF_old
                if old_os:
                    passed_channels.append(('ctr_old_el_sel', sel_b_weight, leps.iso, jets.old, taus.old))
                    if large_lj:
                        passed_channels.append(('ctr_old_el_sel_ljout', sel_b_weight, leps.iso, jets.old, taus.old))
                    else:
                        passed_channels.append(('ctr_old_el_sel_lj', sel_b_weight, leps.iso, jets.old, taus.old))
                else:
                    passed_channels.append(('ctr_old_el_sel_ss', sel_b_weight, leps.iso, jets.old, taus.old))
                    if large_lj:
                        passed_channels.append(('ctr_old_el_sel_ljout_ss', sel_b_weight, leps.iso, jets.old, taus.old))
                    else:
                        passed_channels.append(('ctr_old_el_sel_lj_ss', sel_b_weight, leps.iso, jets.old, taus.old))

            for chan_i, (chan, apply_bSF, sel_leps, sel_jets, sel_taus) in enumerate((ch for ch in passed_channels if ch[0] in selected_channels)):
                # check for default proc
                #if chan not in channels:
                    #continue
                #control_counters.Fill(50 + 20*sys_i + 2*chan_i)

                ## some channels have micro_proc (tt->lep+tau->3charged)
                ##if chan in ('adv_el_sel', 'adv_mu_sel', 'adv_el_sel_Sign4', 'adv_mu_sel_Sign4') and micro_proc:
                #if chan in ('adv_mu_sel_Loose', 'adv_mu_sel_Loose_ss', 'adv_mu_sel_Loose_lj', 'adv_mu_sel_Loose_lj_ss', 'adv_mu_sel_Tight', 'adv_mu_sel_Tight_ss',
                #   'mu_presel', 'mu_sel', 'mu_lj', 'mu_lj_out', 'mu_lj_ss', 'mu_lj_out_ss', 'el_presel', 'el_sel', 'el_lj', 'el_lj_out') and micro_proc:
                #    proc = micro_proc

                (procs, default_proc), channel_systs = selected_channels[chan]
                if micro_proc in procs:
                    record_proc = micro_proc
                elif proc in procs:
                    record_proc = proc
                else:
                    record_proc = default_proc
                # the idea is:
                # proc and micro_proc are from MC info, from gen level
                # micro_proc is optional
                # record_proc can depend on reco level info

                # also if there are taus and it's tt_lj than try to specify the origin of the fake
                # if it is required by the procs
                if isTT and proc == 'tt_lj' and 'tt_ljb' in procs and sel_taus:

                    '''
                    # the 0 tau is used
                    # sadly root...
                    # I have to convert ALL lorentzvectors to TLorentzVectors to have convenient dR
                    tau_p4 = TLorentzVector(sel_taus[0][0].X(), sel_taus[0][0].Y(), sel_taus[0][0].Z(), sel_taus[0][0].T())
                    # all gen products are in
                    # gen_t_w1_final_p4s gen_t_w2_final_p4s gen_tb_w1_final_p4s gen_tb_w2_final_p4s
                    # gen_t_b_final_p4s gen_tb_b_final_p4s
                    # but neutrinos are also there the ID to check:
                    # gen_t_w1_final_pdgIds etc
                    gen_match_cut = 0.4
                    matched_w = False
                    for w_prod, w_prod_ID in zip(ev.gen_t_w1_final_p4s, ev.gen_t_w1_final_pdgIds) + zip(ev.gen_t_w2_final_p4s, ev.gen_t_w2_final_pdgIds) + \
                                             zip(ev.gen_tb_w1_final_p4s, ev.gen_tb_w1_final_pdgIds) + zip(ev.gen_tb_w2_final_p4s, ev.gen_tb_w2_final_pdgIds):
                        if abs(w_prod_ID) in (12, 14, 16):
                            continue
                        w_prod_p4 = TLorentzVector(w_prod.X(), w_prod.Y(), w_prod.Z(), w_prod.T())
                        if w_prod_p4.DeltaR(tau_p4) < gen_match_cut:
                            matched_w = True
                            break

                    matched_b = False
                    for b_prod, b_prod_ID in zip(ev.gen_t_b_final_p4s, ev.gen_t_b_final_pdgIds) + zip(ev.gen_tb_b_final_p4s, ev.gen_tb_b_final_pdgIds):
                        if abs(b_prod_ID) in (12, 14, 16):
                            continue
                        b_prod_p4 = TLorentzVector(b_prod.X(), b_prod.Y(), b_prod.Z(), b_prod.T())
                        if b_prod_p4.DeltaR(tau_p4) < gen_match_cut:
                            matched_b = True
                            break
                    '''
                    # the same using genmatch info
                    tau_index = sel_taus[0][3]
                    gen_dR = ev.tau_matching_gen_dR[tau_index]
                    gen_id = ev.tau_matching_gen[tau_index]

                    matched_w = gen_dR < 0.3 and abs(gen_id) == 5
                    matched_b = gen_dR < 0.3 and abs(gen_id) == 6

                    if matched_w and matched_b:
                        record_proc = 'tt_ljo'
                    elif matched_w:
                        record_proc = 'tt_ljw'
                    elif matched_b:
                        record_proc = 'tt_ljb'

                # some channels might not have only inclusive processes or minimal systematics
                if (chan, record_proc, sys_name) not in out_hs:
                    continue # it doesn't change amount of computing, systematics are calculated per each event if at all requested
                    # but they are stored per channel and per histogram

                weight_bSF = weight_bSF_to_apply = 1.
                # consider tau-matched jets too as in:
                #old_jet_sel = (len(jets.old.medium) + len(jets.old.taumatched[0])) > 0 and (len(jets.old.taumatched[0]) + len(jets.old.taumatched[1]) + len(jets.old.medium) + len(jets.old.loose) + len(jets.old.rest)) > 2
                # -- TODO: by the way this is a weird part for b-tagging -- are there studies of b-taging for true taus?
                for _, _, jet_weight, _, _, _, _ in sel_jets.medium + sel_jets.loose + sel_jets.rest + sel_jets.taumatched[0] + sel_jets.taumatched[1]:
                    weight_bSF *= jet_weight
                if apply_bSF:
                    weight_bSF_to_apply = weight_bSF

                #leps = LeptonSelection(iso=(ev.lep_p4, ev.lep_relIso, ev.lep_matching_gen, ev.lep_matching_gen_dR), alliso=(ev.lep_alliso_p4, ev.lep_alliso_relIso, ev.lep_alliso_matching_gen, ev.lep_alliso_matching_gen_dR))
                lep_p4, lep_relIso, lep_matching_gen, lep_matching_gen_dR, lep_id = sel_leps

                #if roccor_factor != 1.:
                #    lep_p4[0] *= roccor_factor
                #    #lep_p4[0].SetPt(lep_p4.pt() * roccor_factor) # works only for 0
                #    proc_met -= lep_p4[0] * (roccor_factor - 1.)
                #    #met_x -=
                #    #met_x -=  * (en_factor - 1.)

                #control_counters.Fill(50 + 20*sys_i + 2*chan_i + 1)

                #record_weight = sys_weight if chan not in ('sel_mu_min', 'sel_mu_min_ss', 'sel_mu_min_medtau') else sys_weight_min

                # nominal systematics
                weight_init, weight_PU, weight_top_pt, weight_th = syst_weights_nominal
                nom_sys_weight            = weight_init * weight_th * weight_PU * weight_top_pt
                nom_sys_weight_without_PU = weight_init * weight_th * weight_top_pt # for PU tests

                record_weight = nom_sys_weight * weight_bSF_to_apply


                # propagation of corrections to met

                met_x_prop_taus = proc_met.Px() #met_x
                met_y_prop_taus = proc_met.Py() #met_y

                met_x_prop_jets = proc_met.Px() # met_x
                met_y_prop_jets = proc_met.Py() # met_y

                met_x_prop = proc_met.Px() # met_x
                met_y_prop = proc_met.Py() # met_y

                # visible particles + met sum control
                sum_jets_corr_X = 0.
                sum_jets_corr_Y = 0.
                sum_jets_init_X = 0.
                sum_jets_init_Y = 0.
                #
                sum_tau_corr_X = 0.
                sum_tau_corr_Y = 0.
                sum_tau_init_X = 0.
                sum_tau_init_Y = 0.

                sum_tau_corr_pt = 0.
                substitution_pt = 0.

                # PROPAGATE tau and jet systematic variations to met
                # 
                # taus = [(p4, TES_factor, tau_pdgID)]
                # nominal taus do have a factor
                if isMC and sel_taus: # and 'TauES' in sys_name:
                    #try:
                    sum_tau_init = sel_taus[0][0]
                    sum_tau_corr = sel_taus[0][0] * sel_taus[0][1]
                    tau_cor = sel_taus[0][0] * (1. - sel_taus[0][1])
                    for tau in sel_taus[1:]:
                        tau_cor += tau[0] * (1. - tau[1])
                        sum_tau_init += tau[0]
                        sum_tau_corr += tau[0] * tau[1]

                    sum_tau_corr_X = sum_tau_corr.Px()
                    sum_tau_corr_Y = sum_tau_corr.Py()
                    sum_tau_init_X = sum_tau_init.Px()
                    sum_tau_init_Y = sum_tau_init.Py()

                    sum_tau_corr_pt = tau_cor.pt()

                    #except IndexError:
                    #    print len(sel_taus), type(sel_taus)
                    #    print sel_taus
                    #    print len(sel_taus[0])
                    #    raise IndexError
                    met_x_prop_taus += tau_cor.X()
                    met_y_prop_taus += tau_cor.Y()
                    met_x_prop += tau_cor.X()
                    met_y_prop += tau_cor.Y()

                ### and substitute the jet->tau in met p7 p9 -> 1) v25 p2_tt_jtau, 2) v25 p2_jes_recor
                ## this works very strangely: data is shifted to high Mt?
                ## but the study of jet/tau pt shows approximatly the same values in both MC and Data
                if sel_taus and sel_taus[0][4] > -1:
                    # only first tau is taken
                    tau_index = sel_taus[0][3]
                    the_tau_p4 = sel_taus[0][0] * sel_taus[0][1]
                    tau_jet_index   = sel_taus[0][4]

                    # substitute the nominal jet
                    jer_factor = ev.jet_jer_factor[tau_jet_index] if isMC else 1.
                    #jes_factor = ev.jet_jes_recorrection[tau_jet_index]
                    #jes_uncorFactor = ev.jet_uncorrected_jecFactor[tau_jet_index]
                    en_factor = jer_factor # * jes_factor * jes_uncorFactor
                    the_jet_p4 = ev.jet_initial_p4[tau_jet_index] * en_factor #miniaod_jets[tau_jet_index]
                    #substitution = the_tau_p4 - the_jet_p4
                    # + what is to remove from met
                    # - what is to include in met
                    substitution = the_jet_p4 - the_tau_p4
                    substitution_pt = substitution.pt()
                    #met_x_prop += substitution.X()
                    #met_y_prop += substitution.Y()

                # PROPAGATE jet correcions
                all_sel_jets = sel_jets.medium + sel_jets.loose + sel_jets.rest
                all_sel_jets_taumatched = sel_jets.medium + sel_jets.loose + sel_jets.rest + sel_jets.taumatched[0] + sel_jets.taumatched[1]
                jets_to_prop_met = sel_jets.medium + sel_jets.loose + sel_jets.rest + sel_jets.taumatched[0] + sel_jets.taumatched[1] + sel_jets.lepmatched if ALL_JETS else all_sel_jets
                # propagate above
                ## propagation of corrections of all jets
                ## nominal jets have JER factor
                #if isMC and jets_to_prop_met: # and ('JES' in sys_name or 'JER' in sys_name):
                #    #try:
                #    sum_jets_init = jets_to_prop_met[0][0]
                #    sum_jets_corr = jets_to_prop_met[0][0] * jets_to_prop_met[0][1]
                #    jet_cor       = jets_to_prop_met[0][0] * (1. - jets_to_prop_met[0][1])
                #    #for jet in all_sel_jets[1:] + sel_jets.taumatched[0] + sel_jets.taumatched[1]:
                #    for jet in jets_to_prop_met[1:]:
                #        jet_cor += jet[0] * (1. - jet[1])
                #        sum_jets_init += jet[0]
                #        sum_jets_corr += jet[0] * jet[1]

                #    sum_jets_corr_X = sum_jets_corr.Px()
                #    sum_jets_corr_Y = sum_jets_corr.Py()
                #    sum_jets_init_X = sum_jets_init.Px()
                #    sum_jets_init_Y = sum_jets_init.Py()

                #    met_x_prop_jets += jet_cor.X()
                #    met_y_prop_jets += jet_cor.Y()
                #    met_x_prop += jet_cor.X()
                #    met_y_prop += jet_cor.Y()
                #    # met prop = met nom + nom - factor
                #    # met prop + factor = met nom + nom

                # control over "objects' met"
                #all_sel_objects = LorentzVector(lep_p4[0].X(), lep_p4[0].Y(), lep_p4[0].Z(), lep_p4[0].T())
                #ROOT.Math.LorentzVector('ROOT::Math::PxPyPzE4D<double>')(100.,0.,1.,200.)
                all_sel_objects = LorentzVector('ROOT::Math::PxPyPzE4D<double>')(0.,0.,0.,0.)
                for lep in lep_p4:
                    all_sel_objects += lep
                for tau in sel_taus:
                    all_sel_objects += tau[0] * tau[1]
                for jet in all_sel_jets:
                    all_sel_objects += jet[0] * jet[1]

                Mt_lep_met_init = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), ev.met_init.Px(), ev.met_init.Py())
                # at NOMINAL these two should be the same
                # only systematic variations differ
                Mt_lep_met         = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), met_x_prop, met_y_prop)
                if isMC:
                    Mt_lep_met_shifted = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), met_x_prop + 7.2, met_y_prop + 1.4)
                else:
                     Mt_lep_met_shifted = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), met_x_prop, met_y_prop)
                Mt_lep_met_corr    = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), ev.met_corrected.Px(), ev.met_corrected.Py())
                # test on Mt fluctuation in mu_sel
                #if Mt_lep_met < 1.:
                #    continue
                Mt_lep_met_sublep = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), proc_met_lepsub.Px(), proc_met_lepsub.Py())

                met_pt = TMath.Sqrt(met_x_prop*met_x_prop + met_y_prop*met_y_prop)
                met_pt_taus = TMath.Sqrt(met_x_prop_taus*met_x_prop_taus + met_y_prop_taus*met_y_prop_taus)
                met_pt_jets = TMath.Sqrt(met_x_prop_jets*met_x_prop_jets + met_y_prop_jets*met_y_prop_jets)
                met_pt_init = proc_met.pt() # TMath.Sqrt(met_x*met_x + met_y*met_y)

                met_cancellation_x = met_x_prop + all_sel_objects.Px()
                met_cancellation_y = met_y_prop + all_sel_objects.Py()
                met_cancelation = TMath.Sqrt(met_cancellation_x*met_cancellation_x + met_cancellation_y*met_cancellation_y)

                # SPECIAL block for weight-based systematics:
                # in NOMINAL objects
                # check which syst_weights are requested for the channel
                if sys_name == 'NOMINAL':
                    for weight_sys_name in channel_systs: # these are all systematics
                        if weight_sys_name == 'PDF_TRIGGER':
                            # get the pdfs..
                            #pdf_w = 1.
                            # they don't clarify how to deal with nominal PDF weight
                            # (subtract or divide? both should be very equal actually)
                            # but since they say "calculate 57 xsecs as if you do it with dif PDF weight"
                            # I'll divide -- as if it's normalized and stuff
                            # how does it go into the fit? where is Up and Down? as in
                            # in their formula there is no up-down for a particular K pdf parameter..
                            # there are differences of final values...
                            # out_hs.update(OrderedDict([format_distrs(chan, proc, sys_name) for sys_name in ('PDFCT14n%dUp' % i, 'PDFCT14n%dDown' % i)]))
                            for i in range(1,57):
                                pdf_w = ev.gen_weights_pdf_hessians[i] / weights_gen_weight_norm
                                # 1 event in muon selection has a number of PDF sets far above nominal value, weighted at 18 and more
                                # row 92098 in
                                # /gstore/t3cms/store/user/otoldaie/v23/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/Ntupler_v23_MC2016_Summer16_TTJets_powheg/180317_001114/0000/MC2016_Summer16_TTJets_powheg_91.root
                                # for PDF n2 (one of the problematic ones) there are 2 more events with pdf weight more than 2
                                # the rest (far larger majority) are below
                                if pdf_w > 2.:
                                    pdf_w = 1.
                                pdf_sys_name = pdf_sys_name_up(i) #pdf_sys_names_Up[i-1]
                                control_hs[pdf_sys_name].Fill(pdf_w)
                                out_hs[(chan, record_proc, pdf_sys_name)]['Mt_lep_met_f'] .Fill(Mt_lep_met, record_weight * pdf_w)
                                pdf_sys_name = pdf_sys_name_down(i) #pdf_sys_names_Down[i-1] # down is nominal
                                out_hs[(chan, record_proc, pdf_sys_name)]['Mt_lep_met_f'] .Fill(Mt_lep_met, record_weight)
                            continue

                        # must by a systematic weight, not syst of objects
                        if not weight_sys_name in syst_weights:
                            continue
                        sys_weight, sys_weight_PU, sys_weight_top_pt, sys_weight_th = syst_weights[weight_sys_name]
                        if weight_sys_name in control_hs:
                            control_hs[weight_sys_name].Fill(sys_weight_th)

                        sys_weight       *= sys_weight_th * sys_weight_PU * sys_weight_top_pt
                        record_weight_sys = sys_weight * weight_bSF_to_apply
                        out_hs[(chan, record_proc, weight_sys_name)]['Mt_lep_met_f'] .Fill(Mt_lep_met,     record_weight_sys)
                        out_hs[(chan, record_proc, weight_sys_name)]['Mt_lep_met']   .Fill(Mt_lep_met,     record_weight_sys)
                        out_hs[(chan, record_proc, weight_sys_name)]['met']          .Fill(met_pt,         record_weight_sys)
                        out_hs[(chan, record_proc, weight_sys_name)]['lep_pt']       .Fill(lep_p4[0].pt(), record_weight_sys)
                        if sel_jets.medium:
                            bMjet0_pt = sel_jets.medium[0][0].pt() * sel_jets.medium[0][1]
                            out_hs[(chan, record_proc, weight_sys_name)]['bMjet_pt']  .Fill(bMjet0_pt,  record_weight_sys)
                            if len(sel_jets.medium) == 1: # only 1 tagged jet in event
                                out_hs[(chan, record_proc, weight_sys_name)]['b1Mjet_pt']  .Fill(bMjet0_pt,  record_weight_sys)

                        if sys_name == 'PUUp' or sys_name == 'PUDown':
                            out_hs[(chan, record_proc, sys_name)]['nvtx']     .Fill(ev.nvtx, record_weight_sys)

                n_rest_jets   = len(sel_jets.rest) #  + len(sel_jets.taumatched[1])
                #n_medium_jets = len(sel_jets.medium)
                n_medium_jets = len(sel_jets.medium) # + len(sel_jets.taumatched[0])
                n_loose_jets  = len(sel_jets.loose)
                n_hadrFlavour5 = 0
                for jet in sel_jets.rest + sel_jets.medium + sel_jets.loose:
                    if abs(jet[4]) == 5:
                        n_hadrFlavour5 += 1

                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f'] .Fill(Mt_lep_met,     record_weight)
                if lep_p4[0].pt() > 30:
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_30GeV']  .Fill(Mt_lep_met,     record_weight)
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_sublep']  .Fill(Mt_lep_met_sublep,     record_weight)
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_shifted'] .Fill(Mt_lep_met_shifted,     record_weight)
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met']   .Fill(Mt_lep_met,     record_weight)
                out_hs[(chan, record_proc, sys_name)]['met']          .Fill(met_pt,         record_weight)
                out_hs[(chan, record_proc, sys_name)]['lep_pt']       .Fill(lep_p4[0].pt(), record_weight)
                out_hs[(chan, record_proc, sys_name)]['yield']        .Fill(1, record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_objects']  .Fill(all_sel_objects.pt(), record_weight)
                out_hs[(chan, record_proc, sys_name)]['allobj_phi']   .Fill(all_sel_objects.Phi(), record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_cancelation']  .Fill(met_cancelation, record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_cancelation_xy']  .Fill(met_cancellation_x, met_cancellation_y, record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_cancelation_x_met_x']  .Fill(met_cancellation_x, met_x_prop, record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_cancelation_y_met_y']  .Fill(met_cancellation_y, met_y_prop, record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_lep_phi']  .Fill((proc_met - lep_p4[0]).Phi(), record_weight)

                out_hs[(chan, record_proc, sys_name)]['met_phi_met_pt']  .Fill(proc_met.Phi(), proc_met.pt(), record_weight)
                if abs(proc_met.Phi()) < 1.5:
                    out_hs[(chan, record_proc, sys_name)]['met_pt_smallphi']  .Fill(proc_met.pt(), record_weight)
                else:
                    out_hs[(chan, record_proc, sys_name)]['met_pt_largephi']  .Fill(proc_met.pt(), record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_x']     .Fill(met_x_prop, record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_y']     .Fill(met_y_prop, record_weight)
                out_hs[(chan, record_proc, sys_name)]['allobj_x']  .Fill(all_sel_objects.Px(), record_weight)
                out_hs[(chan, record_proc, sys_name)]['allobj_y']  .Fill(all_sel_objects.Py(), record_weight)

                met_lep_cos = transverse_cos(proc_met, lep_p4[0])
                if isMC:
                    rev_met_lep_cos = transverse_cos(-proc_met, lep_p4[0])
                    rev_met_phi = (-proc_met.Phi())
                else:
                    rev_met_phi = (proc_met.Phi())
                    rev_met_lep_cos = transverse_cos(proc_met, lep_p4[0])
                all_obj_met = -all_sel_objects
                allobj_met_lep_cos = transverse_cos(all_obj_met, lep_p4[0])
                allobj_lep_cos = transverse_cos(all_sel_objects, lep_p4[0])
                out_hs[(chan, record_proc, sys_name)]['met_lep_cos']     .Fill(met_lep_cos, record_weight)
                out_hs[(chan, record_proc, sys_name)]['rev_met_lep_cos']     .Fill(rev_met_lep_cos, record_weight)
                out_hs[(chan, record_proc, sys_name)]['allobj_met_lep_cos']  .Fill(allobj_met_lep_cos, record_weight)
                out_hs[(chan, record_proc, sys_name)]['allobj_lep_cos']  .Fill(allobj_lep_cos, record_weight)
                Mt_lep_allobj_met  = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), all_obj_met.Px(), all_obj_met.Py())
                Mt_lep_allobj      = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), all_sel_objects.Px(), all_sel_objects.Py())
                if isMC:
                    Mt_lep_rev_met     = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), -proc_met.Px(), -proc_met.Py())
                else:
                    Mt_lep_rev_met     = transverse_mass_pts(lep_p4[0].Px(), lep_p4[0].Py(), proc_met.Px(), proc_met.Py())
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_allobj_met'] .Fill(Mt_lep_allobj_met, record_weight)
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_allobj']     .Fill(Mt_lep_allobj,     record_weight)
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_rev_met']    .Fill(Mt_lep_rev_met,    record_weight)

                #out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_rocc']    .Fill(Mt_lep_met,   roccor_factor)

                if sel_taus:
                    corrected_tau = sel_taus[0][0] * sel_taus[0][1]

                    tau_pt     = corrected_tau.pt()
                    tau_eta    = corrected_tau.eta()
                    tau_energy = corrected_tau.energy()

                if Mt_lep_met > 120. and Mt_lep_met < 200.:
                    if sel_taus:
                        out_hs[(chan, record_proc, sys_name)]['regMt_tau_pt']  .Fill(tau_pt,  record_weight)
                        out_hs[(chan, record_proc, sys_name)]['regMt_tau_substitution']  .Fill(substitution_pt,  record_weight)
                        tau_lep_cos = transverse_cos(sel_taus[0][0], lep_p4[0])
                        out_hs[(chan, record_proc, sys_name)]['regMt_tau_lep_cos'] .Fill(tau_lep_cos,    record_weight)
                        #if tau_ID > 3 and not match_lep: taus_ESDown.old.append((p4, TES_factor, tau_pdgID, i, jetmatched))
                        jetmatched_i = sel_taus[0][4]
                        out_hs[(chan, record_proc, sys_name)]['regMt_tau_jet_scale'] .Fill(tau_energy/ev.jet_p4[jetmatched_i].energy(),    record_weight)
                    out_hs[(chan, record_proc, sys_name)]['regMt_lep_pt']      .Fill(lep_p4[0].pt(),  record_weight)
                    out_hs[(chan, record_proc, sys_name)]['regMt_lep_eta']     .Fill(lep_p4[0].eta(), record_weight)
                    out_hs[(chan, record_proc, sys_name)]['regMt_lep_pt_eta']  .Fill(lep_p4[0].pt(), lep_p4[0].eta(), record_weight)
                    out_hs[(chan, record_proc, sys_name)]['regMt_lep_pt_Mt']   .Fill(lep_p4[0].pt(), Mt_lep_met, record_weight)
                    if lep_p4[0].pt() < 50.:
                        out_hs[(chan, record_proc, sys_name)]['regMt_lep_eta_lowpt'] .Fill(lep_p4[0].eta(), record_weight)
                        out_hs[(chan, record_proc, sys_name)]['regMt_Mt_lowpt']      .Fill(Mt_lep_met, record_weight)
                    out_hs[(chan, record_proc, sys_name)]['regMt_lep_phi']     .Fill(lep_p4[0].phi(), record_weight)
                    out_hs[(chan, record_proc, sys_name)]['regMt_met']         .Fill(met_pt,         record_weight)
                    out_hs[(chan, record_proc, sys_name)]['regMt_met_phi']     .Fill(proc_met.phi(), record_weight)
                    out_hs[(chan, record_proc, sys_name)]['regMt_met_lep_cos'] .Fill(met_lep_cos,    record_weight)
                    out_hs[(chan, record_proc, sys_name)]['regMt_lep_pt_init'] .Fill(lep_p4[0].pt())
                    #out_hs[(chan, record_proc, sys_name)]['regMt_lep_pt_rocc'] .Fill(lep_p4[0].pt(), roccor_factor)
                    #if isMC:
                    #    out_hs[(chan, record_proc, sys_name)]['regMt_lep_pt_puM']    .Fill(lep_p4[0].pt(), weight_pu_mu)
                    #    out_hs[(chan, record_proc, sys_name)]['regMt_lep_pt_puE']    .Fill(lep_p4[0].pt(), weight_pu_el)
                    #    out_hs[(chan, record_proc, sys_name)]['regMt_lep_pt_puM_up'] .Fill(lep_p4[0].pt(), weight_pu_mu_up)
                    #    out_hs[(chan, record_proc, sys_name)]['regMt_lep_pt_puE_up'] .Fill(lep_p4[0].pt(), weight_pu_el_up)
                    #    out_hs[(chan, record_proc, sys_name)]['regMt_lep_pt_puM_dn'] .Fill(lep_p4[0].pt(), weight_pu_mu_dn)
                    #    out_hs[(chan, record_proc, sys_name)]['regMt_lep_pt_puE_dn'] .Fill(lep_p4[0].pt(), weight_pu_el_dn)
                    #out_hs[(chan, record_proc, sys_name)]['regMt_lep_eta_init'].Fill(lep_p4[0].eta())
                    #out_hs[(chan, record_proc, sys_name)]['regMt_lep_eta_rocc'].Fill(lep_p4[0].eta(), roccor_factor)
                    #out_hs[(chan, record_proc, sys_name)]['regMt_lep_phi_init'].Fill(lep_p4[0].phi())
                    #out_hs[(chan, record_proc, sys_name)]['regMt_lep_phi_rocc'].Fill(lep_p4[0].phi(), roccor_factor)
                    #out_hs[(chan, record_proc, sys_name)]['regMt_rocc']        .Fill(roccor_factor)
                    out_hs[(chan, record_proc, sys_name)]['regMt_nMbjets'] .Fill(n_medium_jets,  record_weight)
                    out_hs[(chan, record_proc, sys_name)]['regMt_nLbjets'] .Fill(n_loose_jets,   record_weight)
                    out_hs[(chan, record_proc, sys_name)]['regMt_nRbjets'] .Fill(n_rest_jets,    record_weight)
                    if sel_jets.medium:
                        out_hs[(chan, record_proc, sys_name)]['regMt_bMjet_pt'].Fill(sel_jets.medium[0][0].pt() * sel_jets.medium[0][1], record_weight)

                # 2D distrs
                out_hs[(chan, record_proc, sys_name)]['met_lep_phis']        .Fill(proc_met.Phi(), lep_p4[0].Phi(), record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_allobj_met_phis'] .Fill(proc_met.Phi(), all_obj_met.Phi(), record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_allobj_met_pts']  .Fill(proc_met.pt(),  all_obj_met.pt(), record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_allobj_phis']     .Fill(proc_met.Phi(), all_sel_objects.Phi(), record_weight)

                out_hs[(chan, record_proc, sys_name)]['lep1_phi']      .Fill(lep_p4[0].phi(), record_weight)
                out_hs[(chan, record_proc, sys_name)]['lep1_eta']      .Fill(lep_p4[0].eta(), record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_phi']       .Fill(proc_met.phi(), record_weight)
                out_hs[(chan, record_proc, sys_name)]['rev_met_phi']   .Fill(rev_met_phi, record_weight)

                if len(lep_p4)>1:
                    out_hs[(chan, record_proc, sys_name)]['lep2_phi']  .Fill(lep_p4[1].phi(), record_weight)
                    out_hs[(chan, record_proc, sys_name)]['lep2_eta']  .Fill(lep_p4[1].eta(), record_weight)
                elif sel_taus:
		    out_hs[(chan, record_proc, sys_name)]['lep2_eta'] .Fill(sel_taus[0][0].eta(), record_weight)
                    out_hs[(chan, record_proc, sys_name)]['lep2_phi'] .Fill(sel_taus[0][0].phi(), record_weight)
                    out_hs[(chan, record_proc, sys_name)]['tau_phi']  .Fill(sel_taus[0][0].phi(), record_weight)

                for i, pdgId in enumerate(lep_id[:2]):
                    out_hs[(chan, record_proc, sys_name)][pdgId_codes[pdgId]]  .Fill(lep_p4[i].phi(), record_weight)

                # all sum kind of should find:
                # - which level of jet/met correction is the true "synchronized" one (just technical stuff)
                #   it should be around 0, but might show a not-canceled part
                #   1) if met-jets-etc are syncronized than the peak, around zero or not, should not change after correction propagation
                #   2) a not-canceled part might correspond to weak objects in event (they should cancel, since homogeneous)
                #      or maybe the weird -jet+tau effect
                #   3) anyway it is not a problem if Data and MC agree
                #      this sum is just a measure of not-canceled part calculated at some level of corrections before my processing
                #      plus the possible -jet+tau effect
                #      Data-MC should agree at any correction of my processing
                #      (unless -jet+tau gets into it?)
                # - but also it includes -jet+tau and probably will show this discrepancy
                #   hopefully the discrepancy is the same for data and mc
                # - to separate it I need the tau-matched jet
                #   but
                #       + what if tau is not matched to any jet?

                all_sum_control_X = lep_p4[0].Px() + met_x_prop + sum_jets_corr_X + sum_tau_corr_X
                all_sum_control_Y = lep_p4[0].Py() + met_y_prop + sum_jets_corr_Y + sum_tau_corr_Y
                all_sum_control_pt = TMath.Sqrt(all_sum_control_X*all_sum_control_X + all_sum_control_Y*all_sum_control_Y)

                all_sum_control_init_X = lep_p4[0].Px() + met_x + sum_jets_init_X + sum_tau_init_X
                all_sum_control_init_Y = lep_p4[0].Py() + met_y + sum_jets_init_Y + sum_tau_init_Y
                all_sum_control_init_pt = TMath.Sqrt(all_sum_control_init_X*all_sum_control_init_X + all_sum_control_init_Y*all_sum_control_init_Y)

                #all_sum_control_jets_X = lep_p4.X() + met_x_prop_jets + sum_jets_corr.X() + sum_tau_init.X()
                #all_sum_control_jets_Y = lep_p4.Y() + met_y_prop_jets + sum_jets_corr.Y() + sum_tau_init.Y()
                #all_sum_control_jets_pt = TMath.Sqrt(all_sum_control_init_X*all_sum_control_init_X + all_sum_control_init_Y*all_sum_control_init_Y)

                '''
                # tt->elmu FAKERATES
                fakerate_working_points = [(all_jets_for_fakes, 'all_jet'), (tau_jets_candidates, 'candidate_tau_jet'),
                    (tau_jets_vloose, 'vloose_tau_jet'), (tau_jets_loose , 'loose_tau_jet'),
                    (tau_jets_medium, 'medium_tau_jet'), (tau_jets_tight , 'tight_tau_jet'), (tau_jets_vtight, 'vtight_tau_jet')]
                for jet_p4_s, wp_name in fakerate_working_points:
                    for jet_p4 in jet_p4_s:
                        out_hs[(chan, record_proc, sys_name)][wp_name + '_pt']  .Fill(jet_p4.pt() , record_weight)
                        out_hs[(chan, record_proc, sys_name)][wp_name + '_eta'] .Fill(jet_p4.eta(), record_weight)
                '''

                out_hs[(chan, record_proc, sys_name)]['met_prop_taus'].Fill(met_pt_init, met_pt_taus - met_pt_init, record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_prop_jets'].Fill(met_pt_init, met_pt_jets - met_pt_init, record_weight)
                out_hs[(chan, record_proc, sys_name)]['corr_met'].Fill(ev.met_corrected.pt(), record_weight) # for control
                out_hs[(chan, record_proc, sys_name)]['init_met'].Fill(ev.met_init.pt(),      record_weight) # for control
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_init_f'] .Fill(Mt_lep_met_init,     record_weight)
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_corr_f'] .Fill(Mt_lep_met_corr,     record_weight)
                out_hs[(chan, record_proc, sys_name)]['all_sum_control']     .Fill(all_sum_control_pt, record_weight) # for control
                out_hs[(chan, record_proc, sys_name)]['tau_cor_control']     .Fill(sum_tau_corr_pt, record_weight)
                out_hs[(chan, record_proc, sys_name)]['tau_substitution']    .Fill(substitution_pt, record_weight)
                out_hs[(chan, record_proc, sys_name)]['all_sum_control_init'].Fill(all_sum_control_init_pt, record_weight)
                out_hs[(chan, record_proc, sys_name)]['lep_eta'] .Fill(lep_p4[0].eta(), record_weight)
                out_hs[(chan, record_proc, sys_name)]['lep_pt_turn'].Fill(lep_p4[0].pt(),  record_weight)
                out_hs[(chan, record_proc, sys_name)]['lep_pt_turn_raw'].Fill(lep_p4[0].pt())

                ### debuging the cut of lep_pt at 26 for all MC -- it is in one of the weights
                ## -- found the weight from trigger cut at 26 -- somehow the histo of SF for trigger 24 starts at 26
                ##    extended the SFs to pt outside the histo
                ##   [need to check the source for new histos?]
                ## now, debuggin the cut at 120 GeV
                ## -- the defaults for iso and id were erroneous
                #if pass_mu:
                #    ##out_hs[(chan, record_proc, sys_name)]['lep_pt_turn_raw'].Fill(lep_p4[0].pt())
                #    #out_hs[(chan, record_proc, sys_name)]['lep_pt_turn_raw_w_b_trk']    .Fill(lep_p4[0].pt(), mu_sfs_b[0])
                #    #out_hs[(chan, record_proc, sys_name)]['lep_pt_turn_raw_w_b_trk_vtx'].Fill(lep_p4[0].pt(), mu_sfs_b[1])
                #    #out_hs[(chan, record_proc, sys_name)]['lep_pt_turn_raw_w_b_id']     .Fill(lep_p4[0].pt(), mu_sfs_b[2])
                #    #out_hs[(chan, record_proc, sys_name)]['lep_pt_turn_raw_w_b_iso']    .Fill(lep_p4[0].pt(), mu_sfs_b[3])
                #    #out_hs[(chan, record_proc, sys_name)]['lep_pt_turn_raw_w_b_trk_vtxgen'].Fill(lep_p4[0].pt(), mu_sfs_b[4])
                #    #out_hs[(chan, record_proc, sys_name)]['lep_pt_turn_raw_w_b_trg']    .Fill(lep_p4[0].pt(), mu_trg_sf[0]) # <--- this one is 0
                #    ##control_hs['weight_mu_trg_bcdef'].Fill(mu_trg_sf[0])
                #    ##control_hs['weight_mu_all_bcdef'].Fill(mu_trg_sf[0] * mu_sfs_b[0] * mu_sfs_b[1] * mu_sfs_b[2] * mu_sfs_b[3])
                #    out_hs[(chan, record_proc, sys_name)]['lep_pt_raw_w_b_trk']         .Fill(lep_p4[0].pt(), mu_sfs_b[0])
                #    out_hs[(chan, record_proc, sys_name)]['lep_pt_raw_w_b_trk_vtx']     .Fill(lep_p4[0].pt(), mu_sfs_b[1])
                #    out_hs[(chan, record_proc, sys_name)]['lep_pt_raw_w_b_id']          .Fill(lep_p4[0].pt(), mu_sfs_b[2])
                #    out_hs[(chan, record_proc, sys_name)]['lep_pt_raw_w_b_iso']         .Fill(lep_p4[0].pt(), mu_sfs_b[3])
                #    out_hs[(chan, record_proc, sys_name)]['lep_pt_raw_w_b_trk_vtxgen']  .Fill(lep_p4[0].pt(), mu_sfs_b[4])
                #    out_hs[(chan, record_proc, sys_name)]['lep_pt_raw_w_b_trg']         .Fill(lep_p4[0].pt(), mu_trg_sf[0]) # <--- this one is 0

                # OPTIMIZATION controls
                """
                out_hs[(chan, record_proc, sys_name)]['opt_bjet_categories']     .Fill(opt_bjet_category, record_weight)

                out_hs[(chan, record_proc, sys_name)]['opt_n_presel_tau']        .Fill(n_presel_taus, record_weight)
                out_hs[(chan, record_proc, sys_name)]['opt_n_loose_tau']         .Fill(n_loose_taus, record_weight)
                out_hs[(chan, record_proc, sys_name)]['opt_n_medium_tau']        .Fill(n_medium_taus, record_weight)
                out_hs[(chan, record_proc, sys_name)]['opt_n_tight_tau']         .Fill(n_tight_taus, record_weight)
                out_hs[(chan, record_proc, sys_name)]['opt_n_loose_bjet']        .Fill(n_loose_bjets, record_weight)
                out_hs[(chan, record_proc, sys_name)]['opt_n_medium_bjet']       .Fill(n_medium_bjets, record_weight)

                out_hs[(chan, record_proc, sys_name)]['opt_tau_bjet_categories'] .Fill(opt_tau_bjet_category, record_weight)

                # inclusive categories show the flow of events through cuts,
                # not the distribution of events among the selections
                for b_cat, b_pass in enumerate((pass_b_1L0M, pass_b_1L1M, pass_b_2L0M, pass_b_2L1M, pass_b_2L2M)):
                    if b_pass:
                        out_hs[(chan, record_proc, sys_name)]['opt_bjet_categories_incl']     .Fill(b_cat, record_weight)
                for tau_cat, tau_pass in enumerate((pass_tau_presel or pass_tau_ss_presel, pass_tau_loose or pass_tau_ss_loose, pass_tau_medium or pass_tau_ss_medium, pass_tau_tight or pass_tau_ss_tight)):
                    for b_cat, b_pass in enumerate((pass_b_1L0M, pass_b_1L1M, pass_b_2L0M, pass_b_2L1M, pass_b_2L2M)):
                        if tau_pass and b_pass:
                            catn = tau_cat*5 + b_cat
                            out_hs[(chan, record_proc, sys_name)]['opt_tau_bjet_categories_incl'] .Fill(catn, record_weight)

                out_hs[(chan, record_proc, sys_name)]['opt_tau_index_loose']     .Fill(n_loose_tau_i  , record_weight)
                out_hs[(chan, record_proc, sys_name)]['opt_tau_index_medium']    .Fill(n_medium_tau_i , record_weight)
                out_hs[(chan, record_proc, sys_name)]['opt_tau_index_tight']     .Fill(n_tight_tau_i  , record_weight)
                """

                # for anti-iso and overall
                out_hs[(chan, record_proc, sys_name)]['lep_relIso_el']      .Fill(lep_relIso[0],  record_weight)
                out_hs[(chan, record_proc, sys_name)]['lep_relIso_el_ext']  .Fill(lep_relIso[0],  record_weight)
                out_hs[(chan, record_proc, sys_name)]['lep_relIso']         .Fill(lep_relIso[0],  record_weight)
                out_hs[(chan, record_proc, sys_name)]['lep_relIso_ext']     .Fill(lep_relIso[0],  record_weight)
                out_hs[(chan, record_proc, sys_name)]['lep_relIso_precise'] .Fill(lep_relIso[0],  record_weight)

                # not tagged jets
                if sel_jets.rest:
                    out_hs[(chan, record_proc, sys_name)]['Rjet_pt']  .Fill(sel_jets.rest[0][0].pt() * sel_jets.rest[0][1],  record_weight)
                    out_hs[(chan, record_proc, sys_name)]['Rjet_eta'] .Fill(sel_jets.rest[0][0].eta(), record_weight)
                    out_hs[(chan, record_proc, sys_name)]['b_discr_rest'] .Fill(sel_jets.rest[0][3], record_weight)

                # not Medium tagged leading jet
                if sel_jets.rest or sel_jets.loose:
                    jet_l_pt = jet_r_pt = 0.
                    if sel_jets.rest:
                        jet_r_pt = sel_jets.rest[0][0].pt() * sel_jets.rest[0][1]
                    if sel_jets.loose:
                        jet_l_pt = sel_jets.loose[0][0].pt() * sel_jets.loose[0][1]
                    if jet_r_pt > jet_l_pt:
                        out_hs[(chan, record_proc, sys_name)]['LRjet_pt']  .Fill(sel_jets.rest[0][0].pt() * sel_jets.rest[0][1],  record_weight)
                        out_hs[(chan, record_proc, sys_name)]['LRjet_eta'] .Fill(sel_jets.rest[0][0].eta(), record_weight)
                        out_hs[(chan, record_proc, sys_name)]['b_discr_LR'] .Fill(sel_jets.rest[0][3], record_weight)
                    else:
                        out_hs[(chan, record_proc, sys_name)]['LRjet_pt']  .Fill(sel_jets.loose[0][0].pt() * sel_jets.loose[0][1],  record_weight)
                        out_hs[(chan, record_proc, sys_name)]['LRjet_eta'] .Fill(sel_jets.loose[0][0].eta(), record_weight)
                        out_hs[(chan, record_proc, sys_name)]['b_discr_LR'] .Fill(sel_jets.loose[0][3], record_weight)

                if sel_jets.medium:
                    bMjet0_pt = sel_jets.medium[0][0].pt() * sel_jets.medium[0][1]
                    out_hs[(chan, record_proc, sys_name)]['bMjet_pt']  .Fill(bMjet0_pt,  record_weight)
                    out_hs[(chan, record_proc, sys_name)]['bMjet_pt_nocor']  .Fill(sel_jets.medium[0][0].pt(),  record_weight)
                    if len(sel_jets.medium) == 1: # only 1 tagged jet in event
                        out_hs[(chan, record_proc, sys_name)]['b1Mjet_pt']  .Fill(bMjet0_pt,  record_weight)
                    # tested the sort in the following -- it doesn't matter
                    ## just to make sure the jets are sorted in both MC and Data
                    #if len(sel_jets.medium) > 1 and sel_jets.medium[1][0].pt() * sel_jets.medium[1][1] > bMjet0_pt:
                    #    out_hs[(chan, record_proc, sys_name)]['bMjet_pt']  .Fill(sel_jets.medium[1][0].pt() * sel_jets.medium[1][1],  record_weight)
                    #    out_hs[(chan, record_proc, sys_name)]['bMjet_eta'] .Fill(sel_jets.medium[1][0].eta(), record_weight)
                    #else:
                    #    out_hs[(chan, record_proc, sys_name)]['bMjet_eta'] .Fill(sel_jets.medium[0][0].eta(), record_weight)
                    #    out_hs[(chan, record_proc, sys_name)]['bMjet_pt']  .Fill(bMjet0_pt,  record_weight)
                    out_hs[(chan, record_proc, sys_name)]['b_discr_med'] .Fill(sel_jets.medium[0][3], record_weight)

                    out_hs[(chan, record_proc, sys_name)]['n_bMjets_hadronFlavour']  .Fill(n_medium_jets, n_hadrFlavour5,  record_weight)

                    out_hs[(chan, record_proc, sys_name)]['bMjet0_hadronFlavour']  .Fill(sel_jets.medium[0][4],  record_weight)
                    out_hs[(chan, record_proc, sys_name)]['bMjet0_pt']  .Fill(sel_jets.medium[0][0].pt() * sel_jets.medium[0][1],  record_weight)
                    if len(sel_jets.medium) > 1:
                        out_hs[(chan, record_proc, sys_name)]['bMjet1_hadronFlavour']  .Fill(sel_jets.medium[1][4],  record_weight)
                        out_hs[(chan, record_proc, sys_name)]['bMjet1_pt']  .Fill(sel_jets.medium[1][0].pt() * sel_jets.medium[1][1],  record_weight)
                        out_hs[(chan, record_proc, sys_name)]['bMjet1_eta'] .Fill(sel_jets.medium[1][0].eta(),  record_weight)
                    if len(sel_jets.medium) > 2:
                        out_hs[(chan, record_proc, sys_name)]['bMjet2_hadronFlavour']  .Fill(sel_jets.medium[2][4],  record_weight)
                    if len(sel_jets.medium) > 3:
                        out_hs[(chan, record_proc, sys_name)]['bMjet3_hadronFlavour']  .Fill(sel_jets.medium[3][4],  record_weight)

                if sel_jets.loose:
                    out_hs[(chan, record_proc, sys_name)]['bLjet_pt']  .Fill(sel_jets.loose[0][0].pt() * sel_jets.loose[0][1],  record_weight)
                    out_hs[(chan, record_proc, sys_name)]['bLjet_eta'] .Fill(sel_jets.loose[0][0].eta(), record_weight)
                    out_hs[(chan, record_proc, sys_name)]['b_discr_loose'] .Fill(sel_jets.loose[0][3], record_weight)

                if len(sel_jets.loose) > 1:
                    out_hs[(chan, record_proc, sys_name)]['bL2jet_pt']  .Fill(sel_jets.loose[1][0].pt() * sel_jets.loose[1][1],  record_weight)
                    out_hs[(chan, record_proc, sys_name)]['bL2jet_eta'] .Fill(sel_jets.loose[1][0].eta(), record_weight)

                ## tagged jets
                #if jets_b:
                #    out_hs[(chan, record_proc, sys_name)]['bjet_pt']  .Fill(jets_b[0][0].pt() * jets_b[0][1],  record_weight)
                #    out_hs[(chan, record_proc, sys_name)]['bjet_eta'] .Fill(jets_b[0][0].eta(), record_weight)
                #    if len(jets_b)>1:
                #        out_hs[(chan, record_proc, sys_name)]['bjet2_pt']  .Fill(jets_b[1][0].pt() * jets_b[1][1],  record_weight)
                #        out_hs[(chan, record_proc, sys_name)]['bjet2_eta']  .Fill(jets_b[1][0].eta() * jets_b[1][1],  record_weight)

                """
                # tagged jets OPTIMIZATION
                if bjets_all_foropt:
                    out_hs[(chan, record_proc, sys_name)]['bjet_pt']  .Fill(bjets_all_foropt[0][0].pt() * bjets_all_foropt[0][1],  record_weight)
                    out_hs[(chan, record_proc, sys_name)]['bjet_eta'] .Fill(bjets_all_foropt[0][0].eta(), record_weight)
                    out_hs[(chan, record_proc, sys_name)]['opt_lep_bjet_pt']  .Fill(lep_p4[0].pt(), bjets_all_foropt[0][0].pt() * bjets_all_foropt[0][1],  record_weight)
                    if len(bjets_all_foropt)>1:
                        out_hs[(chan, record_proc, sys_name)]['bjet2_pt']  .Fill(bjets_all_foropt[1][0].pt() * bjets_all_foropt[1][1],  record_weight)
                        out_hs[(chan, record_proc, sys_name)]['bjet2_eta'] .Fill(bjets_all_foropt[1][0].eta(),  record_weight)
                        out_hs[(chan, record_proc, sys_name)]['opt_bjet_bjet2_pt']  .Fill(bjets_all_foropt[0][0].pt() * bjets_all_foropt[0][1], bjets_all_foropt[1][0].pt() * bjets_all_foropt[1][1],  record_weight)

                # b-discr control
                out_hs[(chan, record_proc, sys_name)]['b_discr_lead_jet']  .Fill(lead_jet_b_discr,  record_weight)
                for discr in all_jets_b_discrs:
                    out_hs[(chan, record_proc, sys_name)]['b_discr_all_jets']  .Fill(discr,  record_weight)
                """

                #out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_c']    .Fill(Mt_lep_met_c, record_weight)
                #out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_test'] .Fill(Mt_lep_met_test, record_weight)
                #out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_cos']  .Fill(Mt_lep_met_cos, record_weight)
                #out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_cos_c'].Fill(Mt_lep_met_cos_c, record_weight)
                #out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_mth']  .Fill(Mt_lep_met_mth, record_weight)
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_zero']     .Fill(Mt_lep_met, record_weight)
                out_hs[(chan, record_proc, sys_name)]['met_VS_Mt_lep_met_f'] .Fill(met_pt, Mt_lep_met, record_weight)
                if not ev.pass_basic_METfilters:
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_METfilters'].Fill(Mt_lep_met, record_weight)
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_VS_nvtx']      .Fill(Mt_lep_met, ev.nvtx, 1.)
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_VS_nvtx_gen']      .Fill(Mt_lep_met, ev.nvtx_gen, 1.)
                # controls for effect from weights
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_init']      .Fill(Mt_lep_met)
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_in']      .Fill(Mt_lep_met, weight_init)

                if isMC and pass_mus:
                    if pass_mus:
                        out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_mu_trk_b'].Fill(Mt_lep_met, mu_sfs_b[1])
                        out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_mu_trk_h'].Fill(Mt_lep_met, mu_sfs_h[1])
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_bf']       .Fill(Mt_lep_met, weight_bSF_to_apply)
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_pu']       .Fill(Mt_lep_met, weight_PU)
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_pu_sum']   .Fill(Mt_lep_met, weight_pu_sum)
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_pu_mu']    .Fill(Mt_lep_met, weight_pu_mu)
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_pu_el']    .Fill(Mt_lep_met, weight_pu_el)
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_pu_mu_dn'] .Fill(Mt_lep_met, weight_pu_mu_dn)
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_pu_el_dn'] .Fill(Mt_lep_met, weight_pu_el_dn)
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_pu_mu_up'] .Fill(Mt_lep_met, weight_pu_mu_up)
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_pu_el_up'] .Fill(Mt_lep_met, weight_pu_el_up)
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_w_tp']       .Fill(Mt_lep_met, weight_top_pt)
                    #out_hs[(chan, record_proc, sys_name)]['Mt_lep_met']    .Fill(Mt_lep_met, record_weight)
                    #out_hs[(chan, record_proc, sys_name)]['dphi_lep_met']     .Fill(dphi_lep_met, record_weight)
                    #out_hs[(chan, record_proc, sys_name)]['cos_dphi_lep_met'] .Fill(cos_dphi_lep_met, record_weight)

                # checking the effect of mu trk SF
                out_hs[(chan, record_proc, sys_name)]['nvtx_init']      .Fill(ev.nvtx)
                if isMC and pass_mus:
                    out_hs[(chan, record_proc, sys_name)]['nvtx_w_trk_b']     .Fill(ev.nvtx, mu_sfs_b[1])
                    out_hs[(chan, record_proc, sys_name)]['nvtx_w_trk_h']     .Fill(ev.nvtx, mu_sfs_h[1])

                # for PU tests
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_pu_sum']    .Fill(Mt_lep_met, nom_sys_weight_without_PU * weight_pu_sum)
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_pu_b'  ]    .Fill(Mt_lep_met, nom_sys_weight_without_PU * weight_pu_b  )
                out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_f_pu_h2' ]    .Fill(Mt_lep_met, nom_sys_weight_without_PU * weight_pu_h2 )
                out_hs[(chan, record_proc, sys_name)]['met_pu_sum'].Fill(met_pt, nom_sys_weight_without_PU * weight_pu_sum)
                out_hs[(chan, record_proc, sys_name)]['met_pu_b'  ].Fill(met_pt, nom_sys_weight_without_PU * weight_pu_b  )
                out_hs[(chan, record_proc, sys_name)]['met_pu_h2' ].Fill(met_pt, nom_sys_weight_without_PU * weight_pu_h2 )
                out_hs[(chan, record_proc, sys_name)]['lep_pt_pu_sum']  .Fill(lep_p4[0].pt(),  nom_sys_weight_without_PU * weight_pu_sum)
                out_hs[(chan, record_proc, sys_name)]['lep_pt_pu_b'  ]  .Fill(lep_p4[0].pt(),  nom_sys_weight_without_PU * weight_pu_b  )
                out_hs[(chan, record_proc, sys_name)]['lep_pt_pu_h2' ]  .Fill(lep_p4[0].pt(),  nom_sys_weight_without_PU * weight_pu_h2 )

                if len(lep_p4)>1:
                    lep_lep = lep_p4[0] + lep_p4[1]
                    lep_lep_mass = lep_lep.mass()
                    out_hs[(chan, record_proc, sys_name)]['M_lep_lep']  .Fill(lep_lep_mass, record_weight)

                """
                # taus OPTIMIZATION
                if taus_all_foropt:
                    # again assuming the 0 tau is the one
                    # -- check the tau indexes to be sure
                    out_hs[(chan, record_proc, sys_name)]['tau_pt']  .Fill(taus_all_foropt[0][0].pt() * taus_all_foropt[0][1],  record_weight)
                    out_hs[(chan, record_proc, sys_name)]['tau_eta'] .Fill(taus_all_foropt[0][0].eta(), record_weight)
                    out_hs[(chan, record_proc, sys_name)]['opt_lep_tau_pt']  .Fill(lep_p4[0].pt(), taus_all_foropt[0][0].pt() * taus_all_foropt[0][1],  record_weight)
                """

                # test the Mt shape deviation on njets in event:
                # small amount of jets (tau selection) -> large deviation, due to correction
                if len(all_sel_jets) < 4:
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_lessjets'] .Fill(Mt_lep_met,   record_weight)
                    out_hs[(chan, record_proc, sys_name)]['met_lessjets']        .Fill(met_pt,     record_weight)
                    out_hs[(chan, record_proc, sys_name)]['met_lessjets_init']   .Fill(met_pt_init,     record_weight)

                # most deviation was found for 0 loose 2 medium b jets in tau selections
                # is it connected with Mt?
                if len(sel_jets.loose) == 0 and len(sel_jets.medium) == 2:
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_0L2M'] .Fill(Mt_lep_met, record_weight)
                    out_hs[(chan, record_proc, sys_name)]['met_0L2M']        .Fill(met_pt,     record_weight)
                else:
                    out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_0L2Mnot'] .Fill(Mt_lep_met, record_weight)
                    out_hs[(chan, record_proc, sys_name)]['met_0L2Mnot']        .Fill(met_pt,     record_weight)


                if sel_taus: #has_medium_tau:
                #if len(ev.tau_p4) > 0:
                    #lep_tau = lep_p4[0] + taus[0][0] # done above
                    #out_hs[(chan, record_proc, sys_name)]['M_lep_tau']  .Fill(lep_tau.mass(), record_weight)
                    #corrected_tau = sel_taus[0][0] * sel_taus[0][1]

                    #tau_pt     = corrected_tau.pt()
                    #tau_eta    = corrected_tau.eta()
                    #tau_energy = corrected_tau.energy()

                    # TODO: not fully corrected met
                    Mt_tau_met = transverse_mass(corrected_tau, ev.met_corrected)
                    lep_tau = lep_p4[0] + corrected_tau
                    lep_tau_mass = lep_tau.mass()

                    # testing dependency of Mt shape on tau pt (has to be none)
                    if tau_pt < 30:
                        out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_t1']      .Fill(Mt_lep_met, record_weight)
                    elif tau_pt < 40:
                        out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_t2']      .Fill(Mt_lep_met, record_weight)
                    elif tau_pt < 50:
                        out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_t3']      .Fill(Mt_lep_met, record_weight)
                    elif tau_pt < 70:
                        out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_t4']      .Fill(Mt_lep_met, record_weight)
                    elif tau_pt < 90:
                        out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_t5']      .Fill(Mt_lep_met, record_weight)
                    else:
                        out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_t6']      .Fill(Mt_lep_met, record_weight)

                    out_hs[(chan, record_proc, sys_name)]['M_lep_tau']  .Fill(lep_tau_mass, record_weight)
                    out_hs[(chan, record_proc, sys_name)]['Mt_tau_met'] .Fill(Mt_tau_met, record_weight)
                    out_hs[(chan, record_proc, sys_name)]['Mt_tau_met_lep'] .Fill(Mt_tau_met, Mt_lep_met, record_weight)

                    # TODO: this calculation is saved only for NOMINAL syst, in principle it should not be done in other cases then
                    Mt_tau_lep = transverse_mass(corrected_tau, lep_p4[0])
                    out_hs[(chan, record_proc, sys_name)]['Mt_tau_lep'] .Fill(Mt_tau_lep, record_weight)

                    # mass between tau and all non-b jets (to catch the c-jets from W)
                    # sel_jets.rest
                    # jets.lowest.rest + jets.lowest.taumatched[1]
                    M_tau_nonb_min = 1000.
                    M_tau_nonb_Wdist = 1000.
                    for a_jet in sel_jets.rest: # + sel_jets.taumatched[ -- assume the pair won't be tau matched
                        mass_j_tau = (a_jet[0] * a_jet[1] + corrected_tau).mass()
                        if mass_j_tau < M_tau_nonb_min:
                            M_tau_nonb_min = mass_j_tau
                        W_dist = abs(mass_j_tau - 80.)
                        if W_dist < M_tau_nonb_Wdist:
                            M_tau_nonb_Wdist = W_dist
                        out_hs[(chan, record_proc, sys_name)]['M_tau_nonb'] .Fill(mass_j_tau, record_weight)

                    out_hs[(chan, record_proc, sys_name)]['M_tau_nonb_min']   .Fill(M_tau_nonb_min, record_weight)
                    out_hs[(chan, record_proc, sys_name)]['M_tau_nonb_Wdist'] .Fill(M_tau_nonb_Wdist, record_weight)

                    out_hs[(chan, record_proc, sys_name)]['tau_pt']  .Fill(corrected_tau.pt(),  record_weight)
                    out_hs[(chan, record_proc, sys_name)]['tau_eta'] .Fill(corrected_tau.eta(), record_weight)

                    out_hs[(chan, record_proc, sys_name)]['tau_jetmatched']        .Fill(sel_taus[0][4] > -1, record_weight)
                    out_hs[(chan, record_proc, sys_name)]['tau_jetmatched_VS_eta'] .Fill(sel_taus[0][4] > -1, corrected_tau.eta(), record_weight)

                    # don't do these in OPTIMIZATION
                    ##out_hs[(chan, record_proc, sys_name)]['tau_pat_Sign']  .Fill(zero_tau_pat_Sign,  record_weight)
                    ## we only work with 0th tau (highest pt)
                    tau_index = sel_taus[0][3]
                    tau_refit_index = ev.tau_refited_index[tau_index] # tau id in the original vector
                    # require refit and dR quality of refit
                    refitted = tau_refit_index > -1 and ev.tau_SV_fit_track_OS_matched_track_dR[tau_refit_index] + ev.tau_SV_fit_track_SS1_matched_track_dR[tau_refit_index] + ev.tau_SV_fit_track_SS2_matched_track_dR[tau_refit_index] < 0.002
                    if refitted:
                        tau_SV_sign    = ev.tau_SV_geom_flightLenSign [tau_refit_index]
                        tau_SV_leng    = ev.tau_SV_geom_flightLen     [tau_refit_index]
                        out_hs[(chan, record_proc, sys_name)]['tau_SV_sign'] .Fill(tau_SV_sign, record_weight)
                        out_hs[(chan, record_proc, sys_name)]['tau_SV_leng'] .Fill(tau_SV_leng, record_weight)
                        tau_pat_sign    = ev.tau_flightLengthSignificance[tau_index]
                        tau_pat_leng    = ev.tau_flightLength[tau_index]
                        out_hs[(chan, record_proc, sys_name)]['tau_pat_Sign'] .Fill(tau_pat_sign, record_weight)
                        out_hs[(chan, record_proc, sys_name)]['tau_pat_Leng'] .Fill(tau_pat_leng, record_weight)
                        out_hs[(chan, record_proc, sys_name)]['tau_sign_energy'].Fill(tau_SV_sign, tau_energy, record_weight)
                        out_hs[(chan, record_proc, sys_name)]['tau_leng_energy'].Fill(tau_SV_leng, tau_energy, record_weight)
                        out_hs[(chan, record_proc, sys_name)]['tau_pat_leng_energy'].Fill(tau_pat_leng, tau_energy, record_weight)

                        # dalitz parameters
                        try:
                            m1 = (ev.tau_SV_fit_track_OS_p4[tau_refit_index] + ev.tau_SV_fit_track_SS1_p4[tau_refit_index]).mass()
                            m2 = (ev.tau_SV_fit_track_OS_p4[tau_refit_index] + ev.tau_SV_fit_track_SS2_p4[tau_refit_index]).mass()
                            out_hs[(chan, record_proc, sys_name)]['tau_dalitzes'].Fill(m1, m2, record_weight)
                        except IndexError:
                            logger.write("IndexError  : %d, (%d, %d, %d, %d)" % (tau_refit_index, ev.tau_SV_fit_track_OS_p4.size(), ev.tau_SV_fit_track_SS1_p4.size(), ev.tau_SV_fit_track_SS2_p4.size(), ev.tau_p4.size()))
                            logger.write("IndexError2 : %f, %f, %f, (%d, %d)" % (tau_pt, tau_eta, corrected_tau.phi(), ev.indexevents, iev))
                            #continue

                        # dR matched jet
                        tau_jet_index   = ev.tau_dR_matched_jet[tau_index]
                        if tau_jet_index > -1:
                            tau_jet_bdiscr = ev.jet_b_discr[tau_jet_index]
                            out_hs[(chan, record_proc, sys_name)]['tau_sign_bdiscr'].Fill(tau_SV_sign, tau_jet_bdiscr, record_weight)
                            #out_hs[(chan, record_proc, sys_name)]['tau_leng_bdiscr'].Fill(tau_SV_leng, tau_jet_bdiscr, record_weight)
                            out_hs[(chan, record_proc, sys_name)]['tau_pat_sign_bdiscr'].Fill(tau_pat_sign, tau_jet_bdiscr, record_weight)

                    #    # also save PAT and refit values
                    #    # calculate from tau_SV_fit_x.., tau_SV_cov
                    #    pv = ROOT.TVector3(ev.PV_fit_x, ev.PV_fit_y, ev.PV_fit_z)
                    #    sv = ROOT.TVector3(ev.tau_SV_fit_x[0], ev.tau_SV_fit_y[0], ev.tau_SV_fit_z[0])
                    #    # SVPV.Mag(), sigmaabs, sign
                    #    tau_ref_leng, tau_ref_sigma, tau_ref_sign = PFTau_FlightLength_significance(pv, ev.PV_cov, sv, ev.tau_SV_cov[0])

                    #    out_hs[(chan, record_proc, sys_name)]['tau_ref_Sign'] .Fill(tau_ref_sign, record_weight)
                    #    out_hs[(chan, record_proc, sys_name)]['tau_ref_Leng'] .Fill(tau_ref_leng, record_weight)
                    #    out_hs[(chan, record_proc, sys_name)]['tau_jet_bdiscr'] .Fill(tau_jet_bdiscr, record_weight)
                    #if refitted and tau_jet_index > -1:
                    #    # for PAT and refit only sign-b and len-energy
                    #    out_hs[(chan, record_proc, sys_name)]['tau_ref_sign_bdiscr'].Fill(tau_ref_sign, tau_jet_bdiscr, record_weight)
                    #    out_hs[(chan, record_proc, sys_name)]['tau_ref_leng_energy'].Fill(tau_ref_leng, tau_energy, record_weight)

                #'njets':       TH1D('%s_%s_%s_njets'     % (chan, record_proc, sys), '', 5, 0, 5),
                #'nMbjets':     TH1D('%s_%s_%s_nMbjets'   % (chan, record_proc, sys), '', 5, 0, 5),
                #'nLbjets':     TH1D('%s_%s_%s_nLbjets'   % (chan, record_proc, sys), '', 5, 0, 5),
                #'ntaus':       TH1D('%s_%s_%s_ntaus'     % (chan, record_proc, sys), '', 5, 0, 5),

                out_hs[(chan, record_proc, sys_name)]['njets_event'].Fill(ev.jet_p4.size(),   record_weight)
                out_hs[(chan, record_proc, sys_name)]['njets']      .Fill(len(all_sel_jets),  record_weight)
                out_hs[(chan, record_proc, sys_name)]['njets_all']  .Fill(len(all_sel_jets_taumatched), record_weight)
                out_hs[(chan, record_proc, sys_name)]['nRjets'] .Fill(n_rest_jets   , record_weight)
                out_hs[(chan, record_proc, sys_name)]['nMbjets'].Fill(n_medium_jets , record_weight)
                out_hs[(chan, record_proc, sys_name)]['nLbjets'].Fill(n_loose_jets  , record_weight)

                out_hs[(chan, record_proc, sys_name)]['nTBjets'].Fill(len(sel_jets.taumatched[0]), record_weight)
                out_hs[(chan, record_proc, sys_name)]['nTRjets'].Fill(len(sel_jets.taumatched[1]), record_weight)

                out_hs[(chan, record_proc, sys_name)]['met_nRjets'] .Fill(met_pt, n_rest_jets   , record_weight)

                # OPTIMIZATION don't make these
                ##out_hs[(chan, record_proc, sys_name)]['Mt_lep_met_d'].Fill(Mt_lep_met_d, record_weight)
                if requires_lj:
                    out_hs[(chan, record_proc, sys_name)]['dijet_mass']       .Fill(w_mass, record_weight)
                    out_hs[(chan, record_proc, sys_name)]['trijet_mass']      .Fill(t_mass, record_weight)
                    out_hs[(chan, record_proc, sys_name)]['2D_dijet_trijet']  .Fill(w_mass, t_mass, record_weight)
                    out_hs[(chan, record_proc, sys_name)]['dijet_trijet_mass'].Fill(lj_var, record_weight)

                    (lj_w1_gen, lj_w2_gen), lj_b_gen = lj_gens
                    out_hs[(chan, record_proc, sys_name)]['lj_gens_b_gen']  .Fill(lj_b_gen, record_weight)
                    out_hs[(chan, record_proc, sys_name)]['lj_gens_w1_gen'] .Fill(lj_w1_gen, record_weight)
                    out_hs[(chan, record_proc, sys_name)]['lj_gens_w2_gen'] .Fill(lj_w2_gen, record_weight)

                    if abs(lj_b_gen) == 6:
                        lj_gen_var = 6
                    else:
                        lj_gen_var = 0
                        lj_b_gen = 0

                    # ID the W pair
                    # cases of only 1 W match
                    if abs(lj_w1_gen) == 5 and abs(lj_w2_gen) != 5:
                        # check if W corresponds to the b, if W has the same sign as b
                        lj_gen_var += 2 if lj_b_gen*lj_w1_gen < 0 else 1
                    elif abs(lj_w1_gen) != 5 and abs(lj_w2_gen) == 5:
                        lj_gen_var += 2 if lj_b_gen*lj_w2_gen < 0 else 1
                    # cases of 2 W
                    # the Ws correspond to each other
                    elif lj_w1_gen*lj_w2_gen == 25:
                        # check if they correspond to b
                        lj_gen_var += 4 if lj_b_gen*lj_w2_gen < 0 else 3
                    # the opposite Ws
                    elif lj_w1_gen*lj_w2_gen == -25:
                        lj_gen_var += 5

                    out_hs[(chan, record_proc, sys_name)]['lj_gens'].Fill(lj_gen_var, record_weight)

                    # and new simple categorization, to not mix it with above:
                    # has the combination propper b and propper Ws
                    if propper_b:
                        combination_has = 3*(lj_b_gen == propper_b) + (lj_w1_gen == propper_w) + (lj_w2_gen == propper_w)
                        out_hs[(chan, record_proc, sys_name)]['combination_has']       .Fill(combination_has, record_weight)
                        out_hs[(chan, record_proc, sys_name)]['input_has']             .Fill(jets_input_has, record_weight)
                        out_hs[(chan, record_proc, sys_name)]['combination_input_have'].Fill(combination_has, jets_input_has, record_weight)

                    # the following two make up probability to pass VS permutations
                    out_hs[(chan, record_proc, sys_name)]['dijet_trijet_mass_N_permutations']  .Fill(len(all_masses), record_weight)
                    if not large_lj:
                        out_hs[(chan, record_proc, sys_name)]['dijet_trijet_mass_N_permutations_passed']  .Fill(len(all_masses), record_weight)
                        if n_bjets_used_in_lj == 1:
                            out_hs[(chan, record_proc, sys_name)]['dijet_trijet_mass_N_permutations_passed_b1']  .Fill(len(all_masses), record_weight)
                        else:
                            out_hs[(chan, record_proc, sys_name)]['dijet_trijet_mass_N_permutations_passed_bM']  .Fill(len(all_masses), record_weight)

                    out_hs[(chan, record_proc, sys_name)]['dijet_trijet_mass_vs_permutations'] .Fill(lj_var, len(all_masses), record_weight)
                    for mass_W, mass_t in all_masses:
                        out_hs[(chan, record_proc, sys_name)]['2D_dijet_trijet_all']  .Fill(mass_W, mass_t, record_weight)

                jets_category = 0
                jets_category += n_rest_jets if n_rest_jets < 5 else 4
                jets_category += 5 *   (n_medium_jets if n_medium_jets < 3 else 2)
                jets_category += 3*5 * (n_loose_jets  if n_loose_jets  < 3 else 2)
                out_hs[(chan, record_proc, sys_name)]['njets_cats'].Fill(jets_category,  record_weight)

                out_hs[(chan, record_proc, sys_name)]['ntaus']  .Fill(len(sel_taus),  record_weight)

                out_hs[(chan, record_proc, sys_name)]['nvtx_raw'] .Fill(ev.nvtx, nom_sys_weight_without_PU * weight_bSF_to_apply)
                out_hs[(chan, record_proc, sys_name)]['nvtx']     .Fill(ev.nvtx, record_weight)

                if isMC:
                    #out_hs[(chan, record_proc, sys_name)]['genproc_id']   .Fill(tt_ids[0], tt_ids[1])
                    out_hs[(chan, record_proc, sys_name)]['nvtx_gen'].Fill(ev.nvtx_gen, record_weight)
                    for jet in all_sel_jets + sel_jets.taumatched[0] + sel_jets.taumatched[1]:
                        jet_genmatch = 0.
                        jet_index = jet[6]
                        if ev.jet_matching_gen_dR[jet_index] < 0.3:
                            jet_genmatch = ev.jet_matching_gen[jet_index]
                        out_hs[(chan, record_proc, sys_name)]['jet_bID_lev']        .Fill(jet[3], record_weight)
                        out_hs[(chan, record_proc, sys_name)]['jet_flavours_hadron'].Fill(abs(jet[4]), record_weight)
                        out_hs[(chan, record_proc, sys_name)]['jet_flavours_parton'].Fill(abs(jet[5]), record_weight)
                        out_hs[(chan, record_proc, sys_name)]['jet_genmatch'].Fill(jet_genmatch,  record_weight)

                    # gen matching  separate jets
                    for jet in sel_jets.medium:
                        jet_genmatch = 0.
                        jet_index = jet[6]
                        if ev.jet_matching_gen_dR[jet_index] < 0.3:
                            jet_genmatch = ev.jet_matching_gen[jet_index]
                        out_hs[(chan, record_proc, sys_name)]['jet_genmatch_Mb'].Fill(jet_genmatch,  record_weight)
                    for jet in sel_jets.loose:
                        jet_genmatch = 0.
                        jet_index = jet[6]
                        if ev.jet_matching_gen_dR[jet_index] < 0.3:
                            jet_genmatch = ev.jet_matching_gen[jet_index]
                        out_hs[(chan, record_proc, sys_name)]['jet_genmatch_Lb'].Fill(jet_genmatch,  record_weight)
                    for jet in sel_jets.rest:
                        jet_genmatch = 0.
                        jet_index = jet[6]
                        if ev.jet_matching_gen_dR[jet_index] < 0.3:
                            jet_genmatch = ev.jet_matching_gen[jet_index]
                        out_hs[(chan, record_proc, sys_name)]['jet_genmatch_R'].Fill(jet_genmatch,  record_weight)

                    lep_genmatch = 0.
                    if lep_matching_gen_dR[0] < 0.3:
                        lep_genmatch = lep_matching_gen[0]
                    out_hs[(chan, record_proc, sys_name)]['lep_genmatch'].Fill(lep_genmatch,  record_weight)

                    if sel_taus:
                        tau_genmatch = 0.
                        tau_index = sel_taus[0][3]
                        if ev.tau_matching_gen_dR[tau_index] < 0.3:
                            tau_genmatch = ev.tau_matching_gen[tau_index]
                        if lep_id[0] > 0:
                            out_hs[(chan, record_proc, sys_name)]['tau_genmatch_p'].Fill(tau_genmatch,  record_weight)
                        else:
                            out_hs[(chan, record_proc, sys_name)]['tau_genmatch_n'].Fill(tau_genmatch,  record_weight)

                out_hs[(chan, record_proc, sys_name)]['control_init_weight'].Fill(weight_init)
                out_hs[(chan, record_proc, sys_name)]['control_bSF_weight'].Fill(weight_bSF)
                out_hs[(chan, record_proc, sys_name)]['control_bSF_weight_applied'].Fill(weight_bSF_to_apply)
                out_hs[(chan, record_proc, sys_name)]['control_PU_weight'] .Fill(weight_PU)
                out_hs[(chan, record_proc, sys_name)]['control_th_weight'] .Fill(weight_th)
                out_hs[(chan, record_proc, sys_name)]['control_top_weight'] .Fill(weight_top_pt)
                out_hs[(chan, record_proc, sys_name)]['control_rec_weight'].Fill(record_weight)

        if save_weights:
          #weight_bSF = 1.
          #weight_bSF_up, weight_bSF_down = 1., 1.
          #weight_bSF_jer_up, weight_bSF_jer_down = 1., 1.
          #weight_bSF_jes_up, weight_bSF_jes_down = 1., 1.
          control_hs['weight_z_mass_pt'] .Fill(weight_z_mass_pt)
          control_hs['weight_bSF']    .Fill(weight_bSF)
          #control_hs['weight_top_pt'] .Fill(weight_top_pt) # done above

          if pass_mu or pass_elmu or pass_mumu:
            # bcdef_weight_trk, bcdef_weight_id, bcdef_weight_iso, gh_weight_trk, gh_weight_id, gh_weight_iso
            #mu_sfs = lepton_muon_SF(abs(ev.lep_p4[0].eta()), ev.lep_p4[0].pt())
            #mu_trg_sf = lepton_muon_trigger_SF(abs(ev.lep_p4[0].eta()), ev.lep_p4[0].pt())

            control_hs['weight_mu_trk_bcdef']        .Fill(mu_sfs_b[0])
            control_hs['weight_mu_trk_bcdef_vtx_gen'].Fill(mu_sfs_b[1])
            control_hs['weight_mu_trk_bcdef_vtx']    .Fill(mu_sfs_b[2])
            control_hs['weight_mu_id_bcdef']         .Fill(mu_sfs_b[3][0])
            control_hs['weight_mu_iso_bcdef']        .Fill(mu_sfs_b[4][0])
            control_hs['weight_mu_trg_bcdef'].Fill(mu_trg_sf_b)
            control_hs['weight_mu_all_bcdef'].Fill(mu_trg_sf_b * mu_sfs_b[0] * mu_sfs_b[1] * mu_sfs_b[3][0] * mu_sfs_b[4][0])

            control_hs['weight_mu_trk_gh']        .Fill(mu_sfs_h[0])
            control_hs['weight_mu_trk_gh_vtx_gen'].Fill(mu_sfs_h[1])
            control_hs['weight_mu_trk_gh_vtx']    .Fill(mu_sfs_h[2])
            control_hs['weight_mu_id_gh']         .Fill(mu_sfs_h[3][0])
            control_hs['weight_mu_iso_gh']        .Fill(mu_sfs_h[4][0])
            control_hs['weight_mu_trg_gh'] .Fill(mu_trg_sf_h)
            control_hs['weight_mu_all_gh'] .Fill(mu_trg_sf_h * mu_sfs_h[0] * mu_sfs_h[1] * mu_sfs_h[3][0] * mu_sfs_h[4][0])

            control_hs['weight_mu_bSF']     .Fill(weight_bSF)
            #control_hs['weight_mu_bSF_up']  .Fill(weight_bSF_up)
            #control_hs['weight_mu_bSF_down'].Fill(weight_bSF_down)

          elif pass_el or pass_elel or pass_elmu_el:
            #el_sfs = lepton_electron_SF(abs(ev.lep_p4[0].eta()), ev.lep_p4[0].pt())
            #el_trg_sf = lepton_electron_trigger_SF(abs(ev.lep_p4[0].eta()), ev.lep_p4[0].pt())

            control_hs['weight_el_trk'].Fill(el_sfs_reco[0])
            control_hs['weight_el_idd'].Fill(el_sfs_id[0])
            control_hs['weight_el_trg'].Fill(el_trg_sf[0])
            control_hs['weight_el_all'].Fill(el_trg_sf[0] * el_sfs_reco[0] * el_sfs_id[0])

            control_hs['weight_el_bSF']     .Fill(weight_bSF)
            #control_hs['weight_el_bSF_up']  .Fill(weight_bSF_up)
            #control_hs['weight_el_bSF_down'].Fill(weight_bSF_down)

    profile.disable()
    #profile.print_stats()
    # there is no returning string
    #profile.dump_stats()

    return out_hs, control_hs, control_counters, profile





#def main(input_dir, dtag, outdir, range_min, range_max):
def main(input_filename, fout_name, outdir, channels_to_select, lumi_bcdef=19252.03, lumi_gh=16290.02):
    '''main(input_filename, outdir, range_min, range_max, lumi_bcdef=19252.03, lumi_gh=16290.02)

    lumi defaults are from _full_ golden json for muon
    -- the bad lumis don't reduce it that much, should not affect the ratio too much
    '''

    print " OLD_MINIAOD_JETS DO_W_STITCHING ALL_JETS with_bSF"
    print OLD_MINIAOD_JETS, DO_W_STITCHING, ALL_JETS, with_bSF

    input_tfile = TFile(input_filename)
    tree = input_tfile.Get('ntupler/reduced_ttree')

    """
    if not range_max: range_max = tree.GetEntries()

    fout_name = input_filename.split('/')[-1].split('.root')[0] + "_%d-%d.root" % (range_min, range_max)

    if isfile(outdir + '/' + fout_name):
        print "output file exists: %s" % (outdir + '/' + fout_name)
        return None
    """

    logger_file = outdir + '/logs/' + fout_name.split('.root')[0] + '.log'

    # this dir should be made at spawning the threads
    if not os.path.exists(outdir + '/logs/'):
        os.makedirs(outdir + '/logs/')

    ## it doesn't deal with threads
    ##logger = logging.getLogger('job_processing_%d' % hash(logger_file))
    #logger = logging.getLogger()
    #hdlr = logging.FileHandler(logger_file)
    #formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    #hdlr.setFormatter(formatter)
    #logger.addHandler(hdlr) 
    ##logger.setLevel(logging.WARNING)
    #logger.setLevel(logging.INFO)
    logger = file(logger_file, 'w')

    #if '-w' in argv:
    #    input_filename, nick = '/eos/user/o/otoldaie/ttbar-leptons-80X_data/v12.7/MC2016_Summer16_WJets_amcatnlo.root', 'wjets'
    #    dtag = "MC2016_Summer16_WJets_madgraph"
    #    #init_bSF_call = 'set_bSF_effs_for_dtag("' + dtag + '");'
    #    #logger.write("init b SFs with: " + init_bSF_call)
    #    #gROOT.ProcessLine(init_bSF_call)
    #else:
    #    input_filename, nick = '/eos/user/o/otoldaie/ttbar-leptons-80X_data/v12.7/MC2016_Summer16_TTJets_powheg_1.root', 'tt'
    #    dtag = "MC2016_Summer16_TTJets_powheg"
    #    #init_bSF_call = 'set_bSF_effs_for_dtag("' + dtag + '");'
    #    #logger.write("init b SFs with: " + init_bSF_call)
    #    #gROOT.ProcessLine(init_bSF_call)

    #input_filename = input_dir + '/' + dtag + '.root'

    #dtag = input_filename.split('/')[-1].split('.')[0]
    #logger.write("dtag = " + dtag)
    logger.write("input file = %s\n" % input_filename)
    logger.write("output dir = %s\n" % outdir)
    #f = TFile('outdir/v12.3/merged-sets/MC2016_Summer16_TTJets_powheg.root')

    logger.write("N entries = %s\n" % tree.GetEntries())

    #logger.write("range = %d, %d\n" % (range_min, range_max))

    logger.write("lumi BCDEF GH = %f %f\n" % (lumi_bcdef, lumi_gh))
    out_hs, c_hs, control_counters, perf_profile = full_loop(tree, input_filename, lumi_bcdef, lumi_gh, logger, channels_to_select=channels_to_select)

    perf_profile.dump_stats(logger_file.split('.log')[0] + '.cprof')

    events_counter = input_tfile.Get('ntupler/events_counter')
    weight_counter = input_tfile.Get('ntupler/weight_counter')
    systematic_weights = input_tfile.Get('ntupler/systematic_weights')
    events_counter.SetDirectory(0)
    weight_counter.SetDirectory(0)
    systematic_weights.SetDirectory(0)

    input_tfile.Close()

    for name, h in c_hs.items():
        try:
            logger.write("%20s %9.5f\n" % (name, h.GetMean()))
        except Exception as e:
            #logger.error("%s\n%s\n%s" % (e.__class__, e.__doc__, e.message))
            logger.write("%s\n%s\n%s\n" % (e.__class__, e.__doc__, e.message))
            continue

    if with_bSF:
        logger.write("eff_b             %f\n" % h_control_btag_eff_b             .GetMean())
        logger.write("eff_c             %f\n" % h_control_btag_eff_c             .GetMean())
        logger.write("eff_udsg          %f\n" % h_control_btag_eff_udsg          .GetMean())
        logger.write("weight_b          %f\n" % h_control_btag_weight_b          .GetMean())
        logger.write("weight_c          %f\n" % h_control_btag_weight_c          .GetMean())
        logger.write("weight_udsg       %f\n" % h_control_btag_weight_udsg       .GetMean())
        logger.write("weight_notag_b    %f\n" % h_control_btag_weight_notag_b    .GetMean())
        logger.write("weight_notag_c    %f\n" % h_control_btag_weight_notag_c    .GetMean())
        logger.write("weight_notag_udsg %f\n" % h_control_btag_weight_notag_udsg .GetMean())

    '''
    for d, histos in out_hs.items():
        for name, histo in histos.items():
            print(d, name)
            histo.Print()
    '''

    # 
    #out_hs = OrderedDict([((chan, proc, sys), {'met': TH1D('met'+chan+proc+sys, '', 40, 0, 400),
    #                                           'Mt_lep_met': TH1D('Mt_lep_met'+chan+proc+sys, '', 20, 0, 200),
    #                                           #'Mt_lep_met_d': TH1D('Mt_lep_met_d'+chan+proc+sys, '', 20, 0, 200), # calculate with method of objects
    #                                           'Mt_tau_met': TH1D('Mt_tau_met'+chan+proc+sys, '', 20, 0, 200),
    #                                           'njets':  TH1D('njets'+chan+proc+sys,  '', 10, 0, 10),
    #                                           'nbjets': TH1D('nbjets'+chan+proc+sys, '', 5, 0, 5),
    #                                           'dijet_trijet_mass': TH1D('dijet_trijet_mass'+chan+proc+sys, '', 20, 0, 400) })
    #            for chan, (procs, _) in channels.items() for proc in procs for sys in systematic_names])

    #fout = TFile("lets_test.root", "RECREATE")
    #fout = TFile(outdir + '/' + dtag + "_%d-%d.root" % (range_min, range_max), "RECREATE")
    #fout_name = outdir + '/' + 
    fout = TFile(outdir + '/' + fout_name, "RECREATE")
    fout.Write()

    for (chan, proc, sys), histos in out_hs.items():
        fout.cd()
        out_dir_name = '%s/%s/%s/' % (chan, proc, sys)
        if fout.Get(out_dir_name):
            #logger.debug('found ' + out_dir_name)
            out_dir = fout.Get(out_dir_name)
        else:
            #logger.debug('made  ' + out_dir_name)
            out_dir_c = fout.Get(chan) if fout.Get(chan) else fout.mkdir(chan)
            out_dir_c.cd()
            out_dir_p = out_dir_c.Get(proc) if out_dir_c.Get(proc) else out_dir_c.mkdir(proc)
            out_dir_p.cd()
            out_dir   = out_dir_p.mkdir(sys)
        out_dir.cd()

        #out_dir.Print()
        for histo in histos.values():
            #histo.Print()
            histo.SetDirectory(out_dir)
            histo.Write()
        #out_dir.Print()

    #events_counter.SetDirectory()
    #weight_counter.SetDirectory()
    fout.cd()
    events_counter.Write() # hopefully these go to the root of the tfile
    weight_counter.Write()
    systematic_weights.Write()
    control_counters.Write()

    fout.Write()

    ##
    #print "trying to exit without segfaults"
    ##ROOT.gSystem.Unload("libUserCodettbar-leptons-80X.so")
    ##ROOT.gSystem.Unload("RoccoR_cc")
    #ROOT.gROOT.Reset()
    #print "all commands done"

