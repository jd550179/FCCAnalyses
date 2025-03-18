import sys
import ROOT

from argparse import ArgumentParser




class Analysis():

    #__________________________________________________________
    def __init__(self, cmdline_args):

        parser = ArgumentParser(
            description='Additional analysis arguments',
            usage='Provide additional arguments after analysis script path')
        parser.add_argument('--muon-pt', default='10.', type=float,
                            help='Minimal pT of the mouns.')
        # Parse additional arguments not known to the FCCAnalyses parsers
        # All command line arguments know to fccanalysis are provided in the
        # `cmdline_arg` dictionary.
        self.ana_args, _ = parser.parse_known_args(cmdline_args['unknown'])

        # self.prod_tag = "FCChh/fcc_v07/II/"
        # self.input_dir = "/bundle/data/ATLAS/jdegens/FCC//DelphesEvents/fcc_v07/II/"
        self.input_dir = "/eos/experiment/fcc/hh/generation/DelphesEvents/fcc_v07/II/"
        
        # Run over the full statistics and save it to one output file named
        # <outputDir>/<process_name>.root
        # 100TeV samples
        # self.process_list = {
            # 'mgp8_pp_tt012j_5f_blvblv': {'fraction': 1, 'chunks': 4},
            # "pwp8_pp_hh_lambda100_5f_hhbbtata":{"fraction": 1},
            # "pwp8_pp_hh_lambda240_5f_hhbbtata":{"fraction": 1},
            # "pwp8_pp_hh_lambda300_5f_hhbbtata":{"fraction": 1},
            # "pwp8_pp_hh_lambda000_5f_hhbbtata":{"fraction": 1}
        # }

        # Run over the full statistics and save it to one output file named
        # <outputDir>/<process_name>.root
        self.process_list = {
            # 'mgp8_pp_tt012j_5f_84TeV_blvblv': {'fraction': 1, 'chunks': 4},
            # 'pwp8_pp_hh_lambda100_5f_80TeV_SA_hhbbtata':{'fraction': 1}
            "pwp8_pp_hh_lambda240_5f_80TeV_SA_hhbbtata": {'fraction':1},
            "pwp8_pp_hh_lambda300_5f_80TeV_SA_hhbbtata": {'fraction':1}
        }
        

        self.analysis_name = 'FCC-hh bbtautau analysis'


        self.output_dir = "/bundle/data/ATLAS/jdegens/FCC/output_2025_03_15/run_analysis/"
    #__________________________________________________________
    def analyzers(self, df):

        df2 = (df
                #.Alias("Jet3", "Jet#3.index")
                #.Define("jet_pt",        "getRP_pt(Jet)")
                #.Define("jet_eta",        "getRP_eta(Jet)")
                #.Define("jet_phi",        "getRP_phi(Jet)")
                #.Define("selected_jets", "selRP_pT(50.)(Jet)")
                #.Define("seljet_pT",     "getRP_pt(selected_jets)"

                # b-tagged jets at medium working point
                .Define("b_tagged_jets_loose", "AnalysisFCChh::get_tagged_jets(Jet, Jet_HF_tags, _Jet_HF_tags_particle, _Jet_HF_tags_parameters, 1)") #bit 1 = medium WP, see: https://github.com/delphes/delphes/blob/master/cards/FCC/scenarios/FCChh_I.tcl
                # select medium b-jets with pT > 30 GeV, |eta| < 4
                .Define("selpt_bjets", "FCCAnalyses::ReconstructedParticle::sel_pt(30.)(b_tagged_jets_loose)")
                .Define("sel_bjets_unsort", "FCCAnalyses::ReconstructedParticle::sel_eta(4)(selpt_bjets)")
                .Define("sel_bjets", "AnalysisFCChh::SortParticleCollection(sel_bjets_unsort)") #sort by pT
                .Define("n_bjets", "FCCAnalyses::ReconstructedParticle::get_n(sel_bjets)")
                .Define("bjet_e",  "FCCAnalyses::ReconstructedParticle::get_e(sel_bjets)")
                .Define("bjet_pt",  "FCCAnalyses::ReconstructedParticle::get_pt(sel_bjets)")
                .Define("bjet_eta",  "FCCAnalyses::ReconstructedParticle::get_eta(sel_bjets)")
                .Define("bjet_phi",  "FCCAnalyses::ReconstructedParticle::get_phi(sel_bjets)")
                .Define("bjet_mass",  "FCCAnalyses::ReconstructedParticle::get_mass(sel_bjets)")

                .Define("bb_pairs_unmerged", "AnalysisFCChh::getPairs(sel_bjets)") # retrieves the leading pT pair of all possible 
                .Define("bb_pairs", "AnalysisFCChh::merge_pairs(bb_pairs_unmerged)") # merge pair into one object to access inv masses etc
                .Define("mbb", "FCCAnalyses::ReconstructedParticle::get_mass(bb_pairs)")
                .Define("dRbb", "ROOT::VecOps::DeltaR(bjet_eta[0], bjet_eta[1], bjet_phi[0], bjet_phi[1])")



                # Get tau jets
                .Define("taus_tagged_loose", "AnalysisFCChh::get_tagged_jets(Jet, Jet_tau_tags, _Jet_tau_tags_particle, _Jet_tau_tags_parameters, 1)") # medium (1) ID to reduce jet->tauh fakes
                .Define("selpt_taus", "FCCAnalyses::ReconstructedParticle::sel_pt(30.)(taus_tagged_loose)")
                .Define("sel_taus_unsort", "FCCAnalyses::ReconstructedParticle::sel_eta(4)(selpt_taus)")
                .Define("sel_taus", "AnalysisFCChh::SortParticleCollection(sel_taus_unsort)") #sort by pT
                .Define("n_taus", "FCCAnalyses::ReconstructedParticle::get_n(sel_taus)")
                .Define("tau_e",  "FCCAnalyses::ReconstructedParticle::get_e(sel_taus)")
                .Define("tau_pt",  "FCCAnalyses::ReconstructedParticle::get_pt(sel_taus)")
                .Define("tau_eta",  "FCCAnalyses::ReconstructedParticle::get_eta(sel_taus)")
                .Define("tau_phi",  "FCCAnalyses::ReconstructedParticle::get_phi(sel_taus)")
                .Define("tau_mass",  "FCCAnalyses::ReconstructedParticle::get_mass(sel_taus)")
                .Define("tau_charge",  "FCCAnalyses::ReconstructedParticle::get_charge(sel_taus)")
                

                # get light (untagged) jets
                #.Define("nontags", 'AnalysisFCChh::get_untagged_jets(Jet, Jet_HF_tags, _Jet_HF_tags_particle, _Jet_tau_tags_particle, 0)')
                .Define("jets_bfiltered", 'AnalysisFCChh::remove_from_collection(Jet, b_tagged_jets_loose)')
                .Define("jets_untagged", 'AnalysisFCChh::remove_from_collection(jets_bfiltered, taus_tagged_loose)')
                .Define("selpt_jets_untagged", "FCCAnalyses::ReconstructedParticle::sel_pt(30.)(jets_untagged)")
                .Define("sel_jets_untagged_unsort", "FCCAnalyses::ReconstructedParticle::sel_eta(4)(selpt_jets_untagged)")
                .Define("sel_jets_untagged", "AnalysisFCChh::SortParticleCollection(sel_jets_untagged_unsort)") #sort by pT
                .Define("n_jets", "FCCAnalyses::ReconstructedParticle::get_n(sel_jets_untagged)")


                .Define("jet_e",   "FCCAnalyses::ReconstructedParticle::get_e(sel_jets_untagged)")
                .Define("jet_pt",  "FCCAnalyses::ReconstructedParticle::get_pt(sel_jets_untagged)")
                .Define("jet_eta", "FCCAnalyses::ReconstructedParticle::get_eta(sel_jets_untagged)")
                .Define("jet_phi", "FCCAnalyses::ReconstructedParticle::get_phi(sel_jets_untagged)")
                .Define("jet_mass", "FCCAnalyses::ReconstructedParticle::get_mass(sel_jets_untagged)")

                # MET        
                .Define("met", "FCCAnalyses::ReconstructedParticle::get_pt(MissingET)[0]")
                .Define("met_eta", "FCCAnalyses::ReconstructedParticle::get_eta(MissingET)[0]")
                .Define("met_phi", "FCCAnalyses::ReconstructedParticle::get_phi(MissingET)[0]")
                .Define("met_mass", "FCCAnalyses::ReconstructedParticle::get_mass(MissingET)[0]")
                .Define("met_px", "FCCAnalyses::ReconstructedParticle::get_px(MissingET)[0]")
                .Define("met_py", "FCCAnalyses::ReconstructedParticle::get_py(MissingET)[0]")
                .Define("met_pz", "FCCAnalyses::ReconstructedParticle::get_pz(MissingET)[0]")
                .Define("met_e", "FCCAnalyses::ReconstructedParticle::get_e(MissingET)[0]")
                
                
                # Leptons
                .Alias('Muon0', 'Muon_objIdx.index')
                # define the muon collection
                .Define(
                    'muons',
                    'ReconstructedParticle::get(Muon0, ReconstructedParticles)')
                # select muons on pT
                .Define('selected_muons',
                        f'ReconstructedParticle::sel_pt(10.)(muons)')
                # create column with muon transverse momentum
                .Define('selected_muons_pt',
                        'ReconstructedParticle::get_pt(selected_muons)')
                # create column with muon rapidity
                .Define('selected_muons_y',
                        'ReconstructedParticle::get_y(selected_muons)')
                # create column with muon total momentum
                .Define('selected_muons_p',
                        'ReconstructedParticle::get_p(selected_muons)')
                # create column with muon energy
                .Define('selected_muons_e',
                        'ReconstructedParticle::get_e(selected_muons)')
                .Alias("Electron0", "Electron_objIdx.index")
                # define the electron collection
                .Define("electrons",  "ReconstructedParticle::get(Electron0, ReconstructedParticles)")
                #select electrons on pT
                .Define("selected_electrons", "ReconstructedParticle::sel_pt(10.)(electrons)")
                # create branch with electron transverse momentum
                .Define("selected_electrons_pt", "ReconstructedParticle::get_pt(selected_electrons)")
                # create branch with electron rapidity
                .Define("selected_electrons_y",  "ReconstructedParticle::get_y(selected_electrons)")
                # create branch with electron total momentum
                .Define("selected_electrons_p",     "ReconstructedParticle::get_p(selected_electrons)")
                # create branch with electron energy
                .Define("selected_electrons_e",     "ReconstructedParticle::get_e(selected_electrons)")


                .Define("leptons", "FCCAnalyses::ReconstructedParticle::merge(selected_electrons, selected_muons)")
                .Define("n_leptons", "FCCAnalyses::ReconstructedParticle::get_n(leptons)")
                .Define("n_electrons", "FCCAnalyses::ReconstructedParticle::get_n(selected_electrons)")
                .Define("n_muons", "FCCAnalyses::ReconstructedParticle::get_n(selected_muons)")
                .Define("sel_leptons", "AnalysisFCChh::SortParticleCollection(leptons)") #sort by pT

                .Define("lepton_e",   "FCCAnalyses::ReconstructedParticle::get_e(sel_leptons)")
                .Define("lepton_pt",  "FCCAnalyses::ReconstructedParticle::get_pt(sel_leptons)")
                .Define("lepton_eta", "FCCAnalyses::ReconstructedParticle::get_eta(sel_leptons)")
                .Define("lepton_phi", "FCCAnalyses::ReconstructedParticle::get_phi(sel_leptons)")
                .Define("lepton_mass", "FCCAnalyses::ReconstructedParticle::get_mass(sel_leptons)")
                .Define("lepton_charge", "FCCAnalyses::ReconstructedParticle::get_charge(sel_leptons)")


                .Filter("n_taus >= 1")
                #.Filter("Min(lepton_eta) > - 6 && Max(lepton_eta) < 6")
                .Filter("n_bjets >= 2")





                

                
                
                #OLD STUFF

                # .Define("c_tagged_jets_loose", 'getJet_btag(Jet3, ParticleIDs, ParticleIDs_0, "c")')
                # .Define("tautags", 'getJet_btag(Jet3, ParticleIDs, ParticleIDs_0, "tau")')
                # .Define("n_bjets", "get_n(btags)")
                # # .Define("n_cjets", "get_n(ctags)")
                # .Define("n_taus", "get_n(tautags)")
                # .Define("n_jets", "get_n(Jet) - n_bjets - ntaus")
                # .Filter("n_jets >= 1")
                # #.Filter("Min(lepton_eta) > - 6 && Max(lepton_eta) < 6")
                # .Filter("n_bjets >= 2")
                
                # # Apply non-tagging mask to jets collection
                # .Define("masked_jet_e", "getRP_e(Jet)*nontags")
                # .Define("masked_jet_px", "getRP_px(Jet)*nontags")
                # .Define("masked_jet_py", "getRP_py(Jet)*nontags")
                # .Define("masked_jet_pz", "getRP_pz(Jet)*nontags")
                # .Define("masked_jet_pt", "getRP_pt(Jet)*nontags")
                # .Define("masked_jet_eta", "getRP_eta(Jet)*nontags")
                # .Define("masked_jet_phi", "getRP_phi(Jet)*nontags")
                # .Define("masked_jet_mass", "getRP_mass(Jet)*nontags")

                # # Apply btagging mask to jets collection
                # .Define("masked_bjet_e", "getRP_e(Jet)*btags")
                # .Define("masked_bjet_px", "getRP_px(Jet)*btags")
                # .Define("masked_bjet_py", "getRP_py(Jet)*btags")
                # .Define("masked_bjet_pz", "getRP_pz(Jet)*btags")
                # .Define("masked_bjet_pt", "getRP_pt(Jet)*btags")
                # .Define("masked_bjet_eta", "getRP_eta(Jet)*btags")
                # .Define("masked_bjet_phi", "getRP_phi(Jet)*btags")
                # .Define("masked_bjet_mass", "getRP_mass(Jet)*btags")

                # # Apply ctagging mask to jets collection
                # .Define("masked_cjet_e", "getRP_e(Jet)*ctags")
                # .Define("masked_cjet_px", "getRP_px(Jet)*ctags")
                # .Define("masked_cjet_py", "getRP_py(Jet)*ctags")
                # .Define("masked_cjet_pz", "getRP_pz(Jet)*ctags")
                # .Define("masked_cjet_pt", "getRP_pt(Jet)*ctags")
                # .Define("masked_cjet_eta", "getRP_eta(Jet)*ctags")
                # .Define("masked_cjet_phi", "getRP_phi(Jet)*ctags")
                # .Define("masked_cjet_mass", "getRP_mass(Jet)*ctags")

                # # Apply tau tagging mask to jets collection
                # .Define("masked_tau_e", "getRP_e(Jet)*tautags")
                # .Define("masked_tau_px", "getRP_px(Jet)*tautags")
                # .Define("masked_tau_py", "getRP_py(Jet)*tautags")
                # .Define("masked_tau_pz", "getRP_pz(Jet)*tautags")
                # .Define("masked_tau_pt", "getRP_pt(Jet)*tautags")
                # .Define("masked_tau_eta", "getRP_eta(Jet)*tautags")
                # .Define("masked_tau_phi", "getRP_phi(Jet)*tautags")
                # .Define("masked_tau_mass", "getRP_mass(Jet)*tautags")
                # .Define("masked_tau_charge", "getRP_charge(Jet)*tautags")

                # # Get MC info
                # .Alias("Particle0","Particle#0.index")
                # .Alias("MCRecoAssociations0","MCRecoAssociations#0.index")
                # .Alias("MCRecoAssociations1","MCRecoAssociations#1.index")
                # .Define("MC_pdg", "getMC_pdg(Particle)")
                # .Define("RP_MC_index", "getRP2MC_index(MCRecoAssociations0, MCRecoAssociations1,ReconstructedParticles)")
                # .Define("RP_MC_parentindex", "getMC_parentid(RP_MC_index,Particle,Particle0)")
                # .Define("RP_MC_grandparentindex", "getMC_parentid(RP_MC_parentindex,Particle,Particle0)")
                # .Define("RP_MC_parentpdg", "getMC_parentpdg(RP_MC_parentindex, MC_pdg)")
                # .Define("RP_MC_grandparentpdg", "getMC_parentpdg(RP_MC_grandparentindex, MC_pdg)")
                
                # #.Define("RP_MC_test", "getRP2MC_index(MCRecoAssociations0, MCRecoAssociations1,Jet)")
                # #.Define("RP_MC_testindex", "getMC_parentid(RP_MC_test,Particle,Particle0)")
                # #.Define("RP_MC_testpdg", "getMC_parentpdg(RP_MC_testindex, MC_pdg)")
                # # Fill branches

                # .Define("jet_e", "masked_jet_e[masked_jet_e!=0]")
                # .Define("jet_px", "masked_jet_px[masked_jet_px!=0]")
                # .Define("jet_py", "masked_jet_py[masked_jet_py!=0]")
                # .Define("jet_pz", "masked_jet_pz[masked_jet_pz!=0]")
                # .Define("jet_pt", "masked_jet_pt[masked_jet_pt!=0]")
                # .Define("jet_eta", "masked_jet_eta[masked_jet_eta!=0]")
                # .Define("jet_phi", "masked_jet_phi[masked_jet_phi!=0]")
                # .Define("jet_mass", "masked_jet_mass[masked_jet_mass!=0]")

                # .Define("bjet_e", "masked_bjet_e[masked_bjet_e!=0]")
                # .Define("bjet_px", "masked_bjet_px[masked_bjet_px!=0]")
                # .Define("bjet_py", "masked_bjet_py[masked_bjet_py!=0]")
                # .Define("bjet_pz", "masked_bjet_pz[masked_bjet_pz!=0]")
                # .Define("bjet_pt", "masked_bjet_pt[masked_bjet_pt!=0]")
                # .Define("bjet_eta", "masked_bjet_eta[masked_bjet_eta!=0]")
                # .Define("bjet_phi", "masked_bjet_phi[masked_bjet_phi!=0]")
                # .Define("bjet_mass", "masked_bjet_mass[masked_bjet_mass!=0]")

                # .Define("cjet_e", "masked_cjet_e[masked_cjet_e!=0]")
                # .Define("cjet_px", "masked_cjet_px[masked_cjet_px!=0]")
                # .Define("cjet_py", "masked_cjet_py[masked_cjet_py!=0]")
                # .Define("cjet_pz", "masked_cjet_pz[masked_cjet_pz!=0]")
                # .Define("cjet_pt", "masked_cjet_pt[masked_cjet_pt!=0]")
                # .Define("cjet_eta", "masked_cjet_eta[masked_cjet_eta!=0]")
                # .Define("cjet_phi", "masked_cjet_phi[masked_cjet_phi!=0]")
                # .Define("cjet_mass", "masked_cjet_mass[masked_cjet_mass!=0]")

                # .Define("tau_e", "masked_tau_e[masked_tau_e!=0]")
                # .Define("tau_px", "masked_tau_px[masked_tau_px!=0]")
                # .Define("tau_py", "masked_tau_py[masked_tau_py!=0]")
                # .Define("tau_pz", "masked_tau_pz[masked_tau_pz!=0]")
                # .Define("tau_pt", "masked_tau_pt[masked_tau_pt!=0]")
                # .Define("tau_eta", "masked_tau_eta[masked_tau_eta!=0]")
                # .Define("tau_phi", "masked_tau_phi[masked_tau_phi!=0]")
                # .Define("tau_mass", "masked_tau_mass[masked_tau_mass!=0]")              
                # .Define("tau_charge", "masked_tau_charge[masked_tau_charge!=0]")

                # .Alias("Electron0", "Electron#0.index")
                # .Alias("Muon0", "Muon#0.index")
                # .Alias("Photon0", "Photon#0.index")
                # .Define("electrons", "getRP(Electron0, ReconstructedParticles)")
                # .Define("muons", "getRP(Muon0, ReconstructedParticles)")
                # .Define("photons", "getRP(Photon0, ReconstructedParticles)")

                # .Define("n_electrons", "getRP_n(electrons)")
                # .Define("n_muons", "getRP_n(muons)")
                # .Define("n_photons", "getRP_n(photons)")

                # .Define("leptons", "mergeParticles(electrons, muons)")
                # .Define("n_leptons", "getRP_n(leptons)")
                # .Define("lepton_e", "getRP_e(leptons)")
                # .Define("lepton_px", "getRP_px(leptons)")
                # .Define("lepton_py", "getRP_py(leptons)")
                # .Define("lepton_pz", "getRP_pz(leptons)")
                # .Define("lepton_pt", "getRP_pt(leptons)")
                # .Define("lepton_eta", "getRP_eta(leptons)")
                # .Define("lepton_phi", "getRP_phi(leptons)")
                # .Define("lepton_mass", "getRP_mass(leptons)")
                # .Define("lepton_charge", "getRP_charge(leptons)")

                # .Define("photon_e", "getRP_e(photons)")
                # .Define("photon_px", "getRP_px(photons)")
                # .Define("photon_py", "getRP_py(photons)")
                # .Define("photon_pz", "getRP_pz(photons)")
                # .Define("photon_pt", "getRP_pt(photons)")
                # .Define("photon_eta", "getRP_eta(photons)")
                # .Define("photon_phi", "getRP_phi(photons)")
                # .Define("photon_mass", "getRP_mass(photons)")

                # .Define("met", "getRP_pt(MissingET)")
                # .Define("met_phi", "getRP_phi(MissingET)")
                # .Define("met_eta", "getRP_eta(MissingET)")
                # .Define("met_mass", "getRP_mass(MissingET)")
                # .Define("met_px", "getRP_px(MissingET)")
                # .Define("met_py", "getRP_py(MissingET)")
                # .Define("met_pz", "getRP_pz(MissingET)")
                # .Define("met_e", "getRP_e(MissingET)")

                # #.Define("dphi_lep1_met", "abs(lepton_phi[0] - met_phi)")
                # #.Define("dphi_tau1_met", "abs(tau_phi[0] - met_phi)")
                # #.Define("mtW_lep1", "sqrt(2*lepton_pt[0]*met*(1-cos(dphi_lep1_met)))")
                # #.Define("mtW_tau1", "sqrt(2*tau_pt[0]*met*(1-cos(dphi_tau1_met)))")
                # .Define("mbb", "ROOT::VecOps::InvariantMass(bjet_pt, bjet_eta, bjet_phi, bjet_mass)")
                # .Define("mgamgam", "ROOT::VecOps::InvariantMass(photon_pt, photon_eta, photon_phi, photon_mass)")

                # #.Define("dRtautau", "ROOT::VecOps::DeltaR(lepton_eta[0], tau_eta[0], lepton_phi[0], tau_phi[0])")
                # #.Define("mtautau", "ROOT::VecOps::InvariantMass(tau_pt + lepton_pt + met, tau_eta + lepton_eta + met_eta, tau_phi + lepton_phi + met_phi, tau_mass + lepton_mass + met_mass)")

                # #.Filter("n_leptons >= 1")
                # #.Filter("n_taus >= 1")
                
                )
        return df2

        # select branches for output file
        #branchList = ROOT.vector('string')()
    def output(self):
        branch_list = [
            #"nontags",
            "n_jets",
            "jet_pt",
            "jet_eta",
            "jet_phi",
            "jet_mass",
            #"btags",
            "n_bjets",
            "bjet_pt",
            "bjet_eta",
            "bjet_phi",
            "bjet_mass",
            # "ctags",
            # "n_cjets",
            # "cjet_pt",
            # "cjet_eta",
            # "cjet_phi",
            # "cjet_mass",
            # "tautags",
            "n_taus",
            "tau_pt",
            "tau_eta",
            "tau_phi",
            "tau_mass",
            "tau_charge",
            "met",
            "met_phi",
            "met_px",
            "met_py",
            "met_pz",
            "met_e",
            #"particle_id",
            #"RP_MC_index",
            "n_leptons",
            "n_muons",
            "n_electrons",
            "lepton_pt",
            "lepton_eta",
            "lepton_phi",
            "lepton_charge",
                
            # "dphi_lep1_met",
            # "dphi_tau1_met",
            # "mtW_lep1",
            # "mtW_tau1",
            # "mbb",
            # "dRbb",
            #"dRtautau",

            # "MC_pdg",
            # "RP_MC_index",
            # "RP_MC_parentindex",
            # "RP_MC_grandparentindex",
            # "RP_MC_parentpdg",
            # "RP_MC_grandparentpdg",
            # #"RP_MC_test"

            #"mtautau"
            #"muon_pT"
            #"n_electron",
            #"n_muon"
        ]
        return branch_list

# example call for standalone file
# python FCChhAnalyses/FCChh/ttHH/dataframe/analysis.py /eos/experiment/fcc/hh/generation/DelphesEvents/fcc_v04/mgp8_pp_tthh_lambda100_5f/events_152512217.root
