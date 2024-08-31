"""
Script for the raw-yield extraction of B0 mesons
"""

import os
import argparse
import yaml
import pandas as pd
import numpy as np
import uproot
from hist import Hist
from flarefly.data_handler import DataHandler
from flarefly.fitter import F2MassFitter

def create_hist(pt_lims, contents, errors, label_pt=r"$p_\mathrm{T}~(\mathrm{GeV}/c)$"):
    """
    Helper method to create histogram

    Parameters
    ----------

    - pt_lims (list): list of pt limits
    - contents (list): histogram contents
    - errors (list): histogram errors
    - label_pt (str): label for x axis

    Returns
    ----------
    - histogram (hist.Hist)

    """

    pt_cent = [(pt_min+pt_max)/2 for pt_min, pt_max in zip(pt_lims[:-1], pt_lims[1:])]
    histo = Hist.new.Var(pt_lims, name="x", label=label_pt).Weight()
    histo.fill(pt_cent, weight=contents)
    histo.view(flow=False).variance = np.array(errors)**2

    return histo


def fit(config_file): # pylint: disable=too-many-locals,too-many-statements
    """
    Main function for fitting

    Parameters
    ----------

    - config_file (string): config file name
    """

    with open(config_file, "r") as yml_cfg:  # pylint: disable=unspecified-encoding
        cfg = yaml.load(yml_cfg, yaml.FullLoader)

    pt_mins = cfg["selections"]["pt_mins"]
    pt_maxs = cfg["selections"]["pt_maxs"]
    pt_lims = pt_mins.copy()
    pt_lims.append(pt_maxs[-1])
    bdt_cuts = cfg["selections"]["bdt_sel"]
    selection_string = ""
    for ipt, (pt_min, pt_max, bdt_cut) in enumerate(zip(pt_mins, pt_maxs, bdt_cuts)):
        if ipt == 0:
            selection_string += f"({pt_min} < fPt < {pt_max} and ML_output > {bdt_cut})"
        else:
            selection_string += f" or ({pt_min} < fPt < {pt_max} and ML_output > {bdt_cut})"

    # load data
    df = pd.DataFrame()
    for file in cfg["inputs"]["data"]:
        df = pd.concat([df, pd.read_parquet(file)])
    df.query(selection_string, inplace=True)

    # load mc
    df_mc = pd.DataFrame()
    for file in cfg["inputs"]["mc"]:
        df_mc = pd.concat([df_mc, pd.read_parquet(file)])
    df_mc.query(selection_string, inplace=True)

    df_mc_bkg = df_mc.query("fFlagMcMatchRec == 4")
    df_mc_sig = df_mc.query("fFlagMcMatchRec == 1")

    # define output file
    outdir = cfg["outputs"]["directory"]
    outfile_name = os.path.join(outdir,
                                f"B0_mass{cfg['outputs']['suffix']}.root")
    file_root = uproot.recreate(outfile_name)
    file_root.close()

    # we first perform a pT-integrated fit
    if cfg["fit_configs"]["pt_int"]["activate"]:
        # we first fit MC only
        data_hdl_mc = DataHandler(df_mc_sig, var_name="fM",
                                  limits=cfg["fit_configs"]["pt_int"]["mass_limits"],
                                  nbins=56)
        fitter_mc_ptint = F2MassFitter(data_hdl_mc,
                                       ["doublegaus"],
                                       ["nobkg"],
                                       name="b0_mc_ptint")
        fitter_mc_ptint.set_signal_initpar(0, "sigma1", 0.03, limits=[0.01, 0.08])
        fitter_mc_ptint.set_signal_initpar(0, "sigma2", 0.08, limits=[0.01, 0.25])
        fitter_mc_ptint.set_particle_mass(0, pdg_id=511)
        result = fitter_mc_ptint.mass_zfit()
        if result.converged:
            fig = fitter_mc_ptint.plot_mass_fit(style="ATLAS",
                                                figsize=(8, 8),
                                                axis_title=r"$M(\mathrm{D^-\pi^+})$ (GeV/$c^2$)")
            fig_res = fitter_mc_ptint.plot_raw_residuals(style="ATLAS",
                                                        figsize=(8, 8),
                                                        axis_title=r"$M(\mathrm{D^-\pi^+})$ (GeV/$c^2$)")

            fig.savefig(os.path.join(outdir, "B0_mass_ptint_MC.pdf"))
            fig_res.savefig(os.path.join(outdir, "B0_massres_ptint_MC.pdf"))

        # then we fit data
        data_hdl = DataHandler(df, var_name="fM",
                               limits=cfg["fit_configs"]["pt_int"]["mass_limits"],
                               nbins=56)
        bkg_funcs = cfg["fit_configs"]["pt_int"]["bkg_funcs"]
        if cfg["fit_configs"]["pt_int"]["use_bkg_templ"]:
            data_hdl_bkg = DataHandler(df_mc_bkg, var_name="fM",
                                       limits=cfg["fit_configs"]["pt_int"]["mass_limits"],
                                       nbins=56)
            bkg_funcs.append("kde_grid")

        fitter_ptint = F2MassFitter(data_hdl,
                                    cfg["fit_configs"]["pt_int"]["signal_funcs"],
                                    bkg_funcs,
                                    name="b0_ptint")

        if cfg["fit_configs"]["pt_int"]["use_bkg_templ"]:
            fitter_ptint.set_background_kde(1, data_hdl_bkg)

        fitter_ptint.set_signal_initpar(0, "sigma", 0.03, limits=[0.01, 0.08])
        fitter_ptint.set_particle_mass(0, pdg_id=511)
        fitter_ptint.set_signal_initpar(0, "frac", 0.05, limits=[0., 1.])
        result = fitter_ptint.mass_zfit()
        if result.converged:
            fig = fitter_ptint.plot_mass_fit(style="ATLAS",
                                             figsize=(8, 8),
                                             axis_title=r"$M(\mathrm{D^-\pi^+})$ (GeV/$c^2$)",
                                             show_extra_info=True)
            fig_res = fitter_ptint.plot_raw_residuals(style="ATLAS",
                                                    figsize=(8, 8),
                                                    axis_title=r"$M(\mathrm{D^-\pi^+})$ (GeV/$c^2$)")

            fig.savefig(os.path.join(outdir, "B0_mass_ptint.pdf"))
            fig_res.savefig(os.path.join(outdir, "B0_massres_ptint.pdf"))


    raw_yields, raw_yields_unc = [], []
    signif, signif_unc, s_over_b, s_over_b_unc = [], [], [], []
    means, means_unc, sigmas, sigmas_unc = [], [], [], []
    means_mc, means_mc_unc, sigmas_mc, sigmas_mc_unc = [], [], [], []

    for ipt, (pt_min, pt_max) in enumerate(zip(pt_mins, pt_maxs)):

        # we first fit MC only
        df_mc_sig_pt = df_mc_sig.query(f"{pt_min} < fPt < {pt_max}")
        data_hdl_mc = DataHandler(df_mc_sig_pt, var_name="fM",
                                  limits=cfg["fit_configs"]["mass_limits"][ipt],
                                  nbins=56)
        fitter_mc_pt = F2MassFitter(data_hdl_mc,
                                    ["doublegaus"],
                                    ["nobkg"],
                                    name=f"b0_mc_pt{pt_min:.0f}_{pt_max:.0f}")
        fitter_mc_pt.set_signal_initpar(0, "sigma1", 0.03, limits=[0.01, 0.08])
        fitter_mc_pt.set_signal_initpar(0, "sigma2", 0.08, limits=[0.01, 0.25])
        fitter_mc_pt.set_particle_mass(0, pdg_id=511)
        result = fitter_mc_pt.mass_zfit()
        if result.converged:
            fig = fitter_mc_pt.plot_mass_fit(style="ATLAS",
                                            figsize=(8, 8),
                                            axis_title=r"$M(\mathrm{D^-\pi^+})$ (GeV/$c^2$)")
            fig_res = fitter_mc_pt.plot_raw_residuals(style="ATLAS",
                                                    figsize=(8, 8),
                                                    axis_title=r"$M(\mathrm{D^-\pi^+})$ (GeV/$c^2$)")

            fig.savefig(os.path.join(outdir, f"B0_mass_pt{pt_min:.0f}_{pt_max:.0f}_MC.pdf"))
            fig_res.savefig(os.path.join(outdir, f"B0_massres_pt{pt_min:.0f}_{pt_max:.0f}_MC.pdf"))

            mean, mean_unc = fitter_mc_pt.get_signal_parameter(0, "mu")
            sigma, sigma_unc = fitter_mc_pt.get_signal_parameter(0, "sigma1")

            means_mc.append(mean)
            means_mc_unc.append(mean_unc)
            sigmas_mc.append(sigma)
            sigmas_mc_unc.append(sigma_unc)

        # then we fit data
        df_pt = df.query(f"{pt_min} < fPt < {pt_max}")
        df_mc_bkg_pt = df_mc_bkg.query(f"{pt_min} < fPt < {pt_max}")
        data_hdl = DataHandler(df_pt, var_name="fM",
                               limits=cfg["fit_configs"]["mass_limits"][ipt],
                               nbins=56)

        bkg_funcs = cfg["fit_configs"]["bkg_funcs"][ipt]
        if cfg["fit_configs"]["use_bkg_templ"][ipt]:
            data_hdl_bkg = DataHandler(df_mc_bkg_pt, var_name="fM",
                                       limits=cfg["fit_configs"]["mass_limits"][ipt],
                                       nbins=56)
            bkg_funcs.append("kde_grid")

        fitter_pt = F2MassFitter(data_hdl,
                                 cfg["fit_configs"]["signal_funcs"][ipt],
                                 bkg_funcs,
                                 name=f"b0_pt{pt_min:.0f}_{pt_max:.0f}")
        if cfg["fit_configs"]["use_bkg_templ"][ipt]:
            fitter_pt.set_background_kde(1, data_hdl_bkg)

        fitter_pt.set_signal_initpar(0, "sigma", 0.03, limits=[0.01, 0.8])
        fitter_pt.set_particle_mass(0, pdg_id=511)
        fitter_pt.set_signal_initpar(0, "frac", 0.05, limits=[0., 1.])
        fitter_pt.set_background_initpar(0, "frac", 0.8, limits=[0., 1.])
        result = fitter_pt.mass_zfit()
        if result.converged:
            fig = fitter_pt.plot_mass_fit(style="ATLAS",
                                          figsize=(8, 8),
                                          axis_title=r"$M(\mathrm{D^-\pi^+})$ (GeV/$c^2$)",
                                          show_extra_info=True)
            fig_res = fitter_pt.plot_raw_residuals(style="ATLAS",
                                                   figsize=(8, 8),
                                                   axis_title=r"$M(\mathrm{D^-\pi^+})$ (GeV/$c^2$)")

            fig.savefig(os.path.join(outdir, f"B0_mass_pt{pt_min:.0f}_{pt_max:.0f}.pdf"))
            fig_res.savefig(os.path.join(outdir, f"B0_massres_pt{pt_min:.0f}_{pt_max:.0f}.pdf"))

            rawy, rawy_unc = fitter_pt.get_raw_yield(0)
            sign, sign_unc = fitter_pt.get_significance(0)
            soverb, soverb_unc = fitter_pt.get_signal_over_background(0)
            mean, mean_unc = fitter_pt.get_signal_parameter(0, "mu")
            sigma, sigma_unc = fitter_pt.get_signal_parameter(0, "sigma")

            raw_yields.append(rawy)
            raw_yields_unc.append(rawy_unc)
            signif.append(sign)
            signif_unc.append(sign_unc)
            s_over_b.append(soverb)
            s_over_b_unc.append(soverb_unc)
            means.append(mean)
            means_unc.append(mean_unc)
            sigmas.append(sigma)
            sigmas_unc.append(sigma_unc)

            fitter_pt.dump_to_root(outfile_name, option="update")

    file_root = uproot.update(outfile_name)
    file_root["h_rawyields"] = create_hist(pt_lims, raw_yields, raw_yields_unc)
    file_root["h_significance"] = create_hist(pt_lims, signif, signif_unc)
    file_root["h_soverb"] = create_hist(pt_lims, s_over_b, s_over_b_unc)
    file_root["h_means"] = create_hist(pt_lims, means, means_unc)
    file_root["h_sigmas"] = create_hist(pt_lims, sigmas, sigmas_unc)
    file_root["h_means_mc"] = create_hist(pt_lims, means_mc, means_mc_unc)
    file_root["h_sigmas_mc"] = create_hist(pt_lims, sigmas_mc, sigmas_mc_unc)
    file_root.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("--config", "-c", metavar="text", default="config_fit.yml",
                        help="yaml config file for fit", required=True)
    args = parser.parse_args()
    fit(args.config)