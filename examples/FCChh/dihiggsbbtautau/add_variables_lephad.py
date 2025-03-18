import os
import sys
import ROOT
from ROOT import gInterpreter

class add_variables():
 
    def __init__(self, inputlist, outname, ncpu):
 
        # Enable multithreading
        ROOT.ROOT.EnableImplicitMT(ncpu)
 
        self.outname = outname
        self.df = ROOT.RDataFrame("events", inputlist)
 
    def run(self):
 
        # Define the custom function to find the first non-matching jet and return pT, eta, and phi
        gInterpreter.Declare("""
        #include <ROOT/RVec.hxx>
        #include <tuple>
        
        std::tuple<float, float, float> getFirstNonMatchingJet(const ROOT::VecOps::RVec<float>& jet_pt, 
                                                               const ROOT::VecOps::RVec<float>& jet_eta, 
                                                               const ROOT::VecOps::RVec<float>& jet_phi,
                                                               const ROOT::VecOps::RVec<float>& tau_pt) {
            for (size_t i = 0; i < jet_pt.size(); ++i) {
                bool is_tau = false;
                for (size_t j = 0; j < tau_pt.size(); ++j) {
                    if (jet_pt[i] == tau_pt[j]) {
                        is_tau = true;
                        break;
                    }
                }
                if (!is_tau) {
                    return std::make_tuple(jet_pt[i], jet_eta[i], jet_phi[i]);
                }
            }
            // Return (-999, -999, -999) if no non-matching jet is found
            return std::make_tuple(-999, -999, -999);
        }

        // Define a function to filter out tau that are also bjets
        std::tuple<ROOT::VecOps::RVec<float>, ROOT::VecOps::RVec<float>, ROOT::VecOps::RVec<float>, ROOT::VecOps::RVec<int>> 
        filterTau(const ROOT::VecOps::RVec<float>& tau_pt, 
                  const ROOT::VecOps::RVec<float>& tau_eta, 
                  const ROOT::VecOps::RVec<float>& tau_phi,
                  const ROOT::VecOps::RVec<int>& tau_charge,
                  const ROOT::VecOps::RVec<float>& bjet_pt) {
            ROOT::VecOps::RVec<float> filtered_tau_pt;
            ROOT::VecOps::RVec<float> filtered_tau_eta;
            ROOT::VecOps::RVec<float> filtered_tau_phi;
            ROOT::VecOps::RVec<int> filtered_tau_charge;
            for (size_t i = 0; i < tau_pt.size(); ++i) {
                bool is_bjet = false;
                for (size_t j = 0; j < bjet_pt.size(); ++j) {
                    if (tau_pt[i] == bjet_pt[j]) {
                        is_bjet = true;
                        break;
                    }
                }
                if (!is_bjet) {
                    filtered_tau_pt.push_back(tau_pt[i]);
                    filtered_tau_eta.push_back(tau_eta[i]);
                    filtered_tau_phi.push_back(tau_phi[i]);
                    filtered_tau_charge.push_back(tau_charge[i]);
                }
            }
            return std::make_tuple(filtered_tau_pt, filtered_tau_eta, filtered_tau_phi, filtered_tau_charge);
        }
        """)

        # Create new dataframe with new variables
        df2 = (self.df
               .Define("filtered_tau", "filterTau(tau_pt, tau_eta, tau_phi, tau_charge, bjet_pt)")  # Filter tau objects
               .Define("filtered_tau_pt", "std::get<0>(filtered_tau)")  # Extract pT from the filtered tau
               .Define("filtered_tau_eta", "std::get<1>(filtered_tau)")  # Extract eta from the filtered tau
               .Define("filtered_tau_phi", "std::get<2>(filtered_tau)")  # Extract phi from the filtered tau
               .Define("filtered_tau_charge", "std::get<3>(filtered_tau)")  # Extract charge from the filtered tau
               .Define("tau0_pT", "filtered_tau_pt.size() > 0 ? filtered_tau_pt[0] : -999")  # Define tau0_pT for use in subsequent filters
               .Define("tau0_eta", "filtered_tau_eta.size() > 0 ? filtered_tau_eta[0] : -999")  # Define tau0_eta
               .Define("tau0_phi", "filtered_tau_phi.size() > 0 ? filtered_tau_phi[0] : -999")  # Define tau0_phi
               .Define("tau0_charge", "filtered_tau_charge.size() > 0 ? filtered_tau_charge[0] : -999")  # Define tau0_charge
 
               .Define("jetInfo", "getFirstNonMatchingJet(jet_pt, jet_eta, jet_phi, filtered_tau_pt)")
               .Define("pTj1", "std::get<0>(jetInfo)")  # Extract pT from the tuple
               .Define("etaj1", "std::get<1>(jetInfo)")  # Extract eta from the tuple
               .Define("phij1", "std::get<2>(jetInfo)")  # Extract phi from the tuple
 
               .Define("pTb1", "bjet_pt[0]")
               .Define("etab1", "bjet_eta[0]")
               .Define("phib1", "bjet_phi[0]")
 
               .Define("pTb2", "bjet_pt[1]")
               .Define("etab2", "bjet_eta[1]")
               .Define("phib2", "bjet_phi[1]")
 
               .Define("pTl1", "lepton_pt[0]")
               .Define("etal1", "lepton_eta[0]")
               .Define("phil1", "lepton_phi[0]")
 
               .Define("pTt1", "filtered_tau_pt.size() > 0 ? filtered_tau_pt[0] : -999")
               .Define("etat1", "filtered_tau_eta.size() > 0 ? filtered_tau_eta[0] : -999")
               .Define("phit1", "filtered_tau_phi.size() > 0 ? filtered_tau_phi[0] : -999")
 
               .Define("ETMiss", "met")
               .Define("ETMissPhi", "met_phi")
               # Selections on number of b-jets, leptons and MET
               .Filter("n_bjets == 2")
               .Filter("n_leptons == 1")
               .Filter("filtered_tau_pt.size() == 1")  # Update filter to use filtered_tau_pt
               .Filter("abs(lepton_eta[0]) < 6")
               .Filter("bjet_pt[0] > 30 && bjet_pt[1] > 30")
               .Filter("filtered_tau_charge[0] != lepton_charge[0]")  # Update filter to use filtered_tau_charge
               .Filter("filtered_tau_pt[0] > 20")
               .Filter("lepton_pt[0] > 20")
               )
 
        # Select branches for output file
        branchList = ROOT.vector('string')()
        # Choose whether to keep or throw away all branches from the input
        keep_all_branches = True
        if keep_all_branches:
            for branchName in self.df.GetColumnNames():
                branchList.push_back(branchName)
        # Add new branches
        for branchName in [
                "pTj1",
                "etaj1",
                "phij1",
                "pTb1",
                "etab1",
                "phib1",
                "pTb2",
                "etab2",
                "phib2",
                "pTl1",
                "etal1",
                "phil1",
                "pTt1",
                "etat1",
                "phit1",
                "ETMiss",
                "ETMissPhi"
                ]:
            branchList.push_back(branchName)
        # Save new dataframe to file
        df2.Snapshot("events", self.outname, branchList)
 
if __name__ == "__main__":
 
    # Define input and output files
    import argparse
    parser = argparse.ArgumentParser(description="Run RDF ntuple analysis") 
    parser.add_argument("--cpus", "-c", default = 0, type = int, help = "Number of CPUs to use")
    parser.add_argument("--output", "-o",  default = "outputfile.root", help = "name of output rootfile")
    parser.add_argument("--input", "-i", nargs='+', help = "input rootfile")
    args = parser.parse_args()
    # Set number of CPUs for running
    ncpus = 0
    # Run the script
    print(len(args.input))
    add_variables = add_variables(args.input, args.output, args.cpus)
    add_variables.run()

