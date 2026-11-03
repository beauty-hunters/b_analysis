"""Script to preprocess data for analysis."""
import argparse
import numpy as np
import pandas as pd
import uproot
import yaml


def preprocess(config_path):
    """
    Preprocess the data for analysis.
    
    Parameters
    ----------
    config_path : str
        Path to the configuration YAML file.
    """
    with open(config_path, "r") as yml_cfg:  # pylint: disable=unspecified-encoding
        cfg = yaml.load(yml_cfg, yaml.FullLoader)

    for ifile, (infile, resfile) in enumerate(zip(
            cfg["inputs"]["data"]["files"],
            cfg["inputs"]["resolution"]["files"],
            strict=True
    )):

        # load data
        with uproot.open(infile) as file:
            df = []
            for k in file.keys(cycle=False):
                if k.endswith(cfg["inputs"]["data"]["treename"]):
                    df.append(file[k].arrays(library="pd"))
            df = pd.concat(df, ignore_index=True)

        # load resolution
        with uproot.open(resfile) as f:
            h_res = f[cfg["inputs"]["resolution"]["histname"]]
            res_vals = h_res.values()
            res_edges = h_res.axes[0].edges()

        ibin = np.searchsorted(res_edges, df["fCentrality"].to_numpy(), side="right") - 1
        ibin = np.clip(ibin, 0, len(res_vals) - 1)
        df["resolution"] = res_vals[ibin]
        df["v2"] = df["fScalarProd"] / df["resolution"]

        if cfg["shifts"][ifile]:
            df["fM"] = df["fM"] + cfg["shifts"][ifile] * 0.001 # convert MeV to GeV

        if "ML_output" not in df.columns:
            df["ML_output"] = df["fMlScoreSig"]

        for icent, (cent_min, cent_max) in enumerate(zip(cfg["centralities"][:-1], cfg["centralities"][1:])):
            df_c = df[(df["fCentrality"] >= cent_min) & (df["fCentrality"] < cent_max)]
            output_file = cfg["outputs"][ifile][icent]
            df_c.to_parquet(output_file)
            print(f"Saved {len(df_c)} events to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess data for analysis.")
    parser.add_argument("--config", "-c", type=str, required=True, help="Path to the configuration YAML file.")
    args = parser.parse_args()

    preprocess(args.config)
