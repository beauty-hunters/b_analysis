import argparse
from pathlib import Path
import uproot
import pandas as pd
import ROOT
import yaml
import numpy as np

def get_cross_section(cfg_path):
    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)

    input_path = Path(f"{cfg['inputs']['folder']}/{cfg['inputs']['mode']}")
    pt_edges = cfg["pt"]["mins"] + [cfg["pt"]["maxs"][-1]]
    h_cross_section = ROOT.TH1F("hCrossSection", ";#it{p}_{T} (GeV/#it{c}); d^{2}#sigma/ d#it{p}_{T} d#it{y} #mub (GeV/#it{c})^{-1}", len(pt_edges)-1, np.asarray(pt_edges, 'd'))

    df = []
    sigma_gen = []
    n_accepted = 0

    for file in input_path.glob(f"b0_pythia8_{cfg['inputs']['mode']}_seed*.root"):
        with uproot.open(file) as f:
            try:
                df.append(f["treeB"].arrays(library="pd"))
                h_sigma_gen = f["hSigmaGen"]
                h_accepted_ev = f["hAcceptedEvents"]

                sigma_gen.append(h_sigma_gen.values()[0])
                n_accepted += h_accepted_ev.values()[0]
            except KeyError:
                continue

    df = pd.concat(df, ignore_index=True)
    sigma_gen = np.mean(sigma_gen)

    for pt_min, pt_max in zip(cfg["pt"]["mins"], cfg["pt"]["maxs"]):
        df_pt = df.query(f"abs(pdgB) == 511 and {pt_min} <= ptB < {pt_max} and abs(yB) < 0.5")

        cross_section = sigma_gen * len(df_pt) / n_accepted  # in mb
        uncertainty = sigma_gen * np.sqrt(len(df_pt)) / n_accepted
        cross_section *= 1e3  # convert to μb
        uncertainty *= 1e3
        cross_section /= 2 # particle + antiparticle
        uncertainty /= 2
        bin_width = pt_max - pt_min
        cross_section /= bin_width
        uncertainty /= bin_width

        h_cross_section.SetBinContent(h_cross_section.FindBin((pt_min + pt_max) / 2), cross_section)
        h_cross_section.SetBinError(h_cross_section.FindBin((pt_min + pt_max) / 2), uncertainty)

    with ROOT.TFile(cfg["output"], "RECREATE") as f_out:
        h_cross_section.Write()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get Pythia cross section for B0 production")
    parser.add_argument("config", type=str, help="Path to config file")
    args = parser.parse_args()

    get_cross_section(args.config)