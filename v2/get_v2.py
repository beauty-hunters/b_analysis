"""Main script to extract v2 from data using sWeights."""
import uproot
import ROOT
import pandas as pd
import numpy as np
import argparse
import yaml

def get_data(cfg, cut_set):
    """
    Load data, sweights, and resolution, and compute v2
    
    Parameters
    ----------
    cfg : dict
        Configuration dictionary loaded from YAML file.
    cut_set : dict
        Cut set dictionary loaded from YAML file.
    """
    pt_mins = cut_set["pt"]["mins"]
    pt_maxs = cut_set["pt"]["maxs"]
    pt_lims = pt_mins.copy()
    pt_lims.append(pt_maxs[-1])
    selection_string = ""
    for ipt, (pt_min, pt_max) in enumerate(zip(pt_mins, pt_maxs)):
        cuts =  [k for k in cut_set.keys() if k != "pt"]
        if ipt == 0:
            selection_string += f"({pt_min} < fPt < {pt_max}) "
        else:
            selection_string += f" or ({pt_min} < fPt < {pt_max}) "
        for cut in cuts:
            selection_string += f" and {cut_set[cut]['mins'][ipt]} < {cut} < {cut_set[cut]['maxs'][ipt]}"

    # load data
    df = pd.DataFrame()
    for file in cfg["inputs"]["data"]:
        # same continuous index as in fit/extract_rawyield.py, to match the sweights
        df = pd.concat([df, pd.read_parquet(file)], ignore_index=True)
    df.query(selection_string, inplace=True)

    # load sweights
    sweights = pd.read_parquet(cfg["inputs"]["sweights"])

    # load resolution
    with uproot.open(cfg["inputs"]["resolution"]["file_name"]) as f:
        h_res = f[cfg["inputs"]["resolution"]["hist_name"]]
        res_vals = h_res.values()
        res_edges = h_res.axes[0].edges()

    ibin = np.searchsorted(res_edges, df["fCentrality"].to_numpy(), side="right") - 1
    ibin = np.clip(ibin, 0, len(res_vals) - 1)
    df["resolution"] = res_vals[ibin]
    df["v2"] = df["fScalarProd"] / df["resolution"]

    return df, sweights

def get_v2_distribution(df, sweights):
    """
    Get v2 distribution and fit it with a Gaussian.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the data with v2 values.
    sweights : pandas.DataFrame
        DataFrame containing the sWeights for the data.
    """
    df_with_sweights = df.join(sweights, how="inner")
    assert len(df_with_sweights) == len(sweights)
    h_v2 = ROOT.TH1F("h_v2", ";v2;Counts", 100, -5., 5)
    h_v2.Sumw2()
    x = df_with_sweights["v2"].to_numpy(dtype=np.float64)
    w = df_with_sweights["signal0"].to_numpy(dtype=np.float64)
    h_v2.FillN(len(x), x, w)
    h_v2.Fit("gaus", "")
    return h_v2

def get_v2_mean(df, sweights):
    """
    Get sWeighted mean of v2 and its uncertainty.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the data with v2 values.
    sweights : pandas.DataFrame
        DataFrame containing the sWeights for the data.
    """
    df_with_sweights = df.join(sweights, how="inner")
    x = df_with_sweights["v2"].to_numpy(dtype=np.float64)
    w = df_with_sweights["signal0"].to_numpy(dtype=np.float64)
    mean = np.sum(w * x) / np.sum(w)
    error = np.sqrt(np.sum(w**2 * (x - mean)**2)) / np.sum(w)
    return mean, error

def get_v2_vs_pt(means, errors, pt_lims):
    h_v2 = ROOT.TH1F("h_v2", ";#it{p}_{T} (GeV/#it{c});v_{2}", len(pt_lims) - 1, np.array(pt_lims, dtype=np.float64))
    for ipt, (pt_min, pt_max) in enumerate(zip(pt_lims[:-1], pt_lims[1:])):
        pt_label = f"pt{pt_min*10:.0f}_{pt_max*10:.0f}"
        h_v2.SetBinContent(ipt + 1, means[pt_label])
        h_v2.SetBinError(ipt + 1, errors[pt_label])
    h_v2_ptint = ROOT.TH1F("h_v2_ptint", ";#it{p}_{T} (GeV/#it{c});v_{2}", 1, pt_lims[0], pt_lims[-1])
    h_v2_ptint.SetBinContent(1, means["pt_int"])
    h_v2_ptint.SetBinError(1, errors["pt_int"])
    return h_v2, h_v2_ptint

def main(config_path):
    with open(config_path, "r") as yml_cfg:  # pylint: disable=unspecified-encoding
        cfg = yaml.load(yml_cfg, yaml.FullLoader)

    with open(cfg["cutset_file_name"], "r") as yml_cfg:  # pylint: disable=unspecified-encoding
        cut_set = yaml.load(yml_cfg, yaml.FullLoader)

    pt_mins = cut_set["pt"]["mins"]
    pt_maxs = cut_set["pt"]["maxs"]
    pt_lims = pt_mins.copy()
    pt_lims.append(pt_maxs[-1])

    df, sweights = get_data(cfg, cut_set)

    hists_v2 = {}
    means, means_fit = {}, {}
    errors, errors_fit = {}, {}

    # pt integrated
    hists_v2["pt_int"] = get_v2_distribution(df, sweights.query("pt_bin == 'pt_int'"))
    hists_v2["pt_int"].SetName("h_v2_ptint")
    means["pt_int"], errors["pt_int"] = get_v2_mean(df, sweights.query("pt_bin == 'pt_int'"))
    means_fit["pt_int"] = hists_v2["pt_int"].GetFunction("gaus").GetParameter(1)
    errors_fit["pt_int"] = hists_v2["pt_int"].GetFunction("gaus").GetParError(1)

    for ipt, (pt_min, pt_max) in enumerate(zip(pt_mins, pt_maxs)):
        pt_label = f"pt{pt_min*10:.0f}_{pt_max*10:.0f}"

        df_pt = df.query(f"({pt_min} < fPt < {pt_max})")
        sweights_pt = sweights.query(f"pt_bin == '{pt_label}'")
        hists_v2[pt_label] = get_v2_distribution(df_pt, sweights_pt)
        hists_v2[pt_label].SetName(f"h_v2_ptbin_{ipt}")
        means[pt_label], errors[pt_label] = get_v2_mean(df_pt, sweights_pt)
        means_fit[pt_label] = hists_v2[pt_label].GetFunction("gaus").GetParameter(1)
        errors_fit[pt_label] = hists_v2[pt_label].GetFunction("gaus").GetParError(1)


    h_v2, h_v2_ptint = get_v2_vs_pt(means, errors, pt_lims)
    h_v2_fit, h_v2_fit_ptint = get_v2_vs_pt(means_fit, errors_fit, pt_lims)
    h_v2_fit.SetName("h_v2_fit")
    h_v2_fit_ptint.SetName("h_v2_fit_ptint")

    with ROOT.TFile(cfg["output_file_name"], "RECREATE") as f:
        for hist_name, hist in hists_v2.items():
            hist.Write(f"v2_hist_{hist_name}")
        h_v2.Write("v2")
        h_v2_ptint.Write("v2_ptint")
        h_v2_fit.Write("v2_fit")
        h_v2_fit_ptint.Write("v2_fit_ptint")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract v2")
    parser.add_argument("config", type=str, help="Path to the configuration YAML file")
    args = parser.parse_args()

    main(args.config)