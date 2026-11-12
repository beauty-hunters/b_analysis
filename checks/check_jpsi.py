"""
Script for checking the JPsi->MuMu/EE in the B decays
"""

import argparse
import numpy as np
import pandas as pd
import yaml

import ROOT

def set_style(histo, color=ROOT.kBlack, alpha=1.1, fillstyle=0):
    """
    """
    histo.SetDirectory(0)
    histo.SetMarkerStyle(ROOT.kFullCircle)
    histo.SetLineWidth(2)
    if alpha >= 1.:
        histo.SetMarkerColor(color)
        histo.SetLineColor(color)
        histo.SetFillColor(color)
    else:
        histo.SetMarkerColorAlpha(color, alpha)
        histo.SetLineColorAlpha(color, alpha)
        histo.SetFillColorAlpha(color, alpha)
    histo.SetFillStyle(fillstyle)

def project_distributions(config_file):
    """
    Method for the QA of B->JPsiX channels
    """

    ROOT.gStyle.SetPadRightMargin(0.035)
    ROOT.gStyle.SetPadTopMargin(0.065)
    ROOT.gStyle.SetPadLeftMargin(0.15)
    ROOT.gStyle.SetPadBottomMargin(0.12)
    ROOT.gStyle.SetTitleSize(0.045, "xy")
    ROOT.gStyle.SetLabelSize(0.045, "xy")
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetPalette(ROOT.kRainBow)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.TGaxis.SetMaxDigits(3)
    ROOT.gROOT.SetBatch(True)

    with open(config_file, "r") as yml_cfg:  # pylint: disable=unspecified-encoding
        cfg = yaml.load(yml_cfg, yaml.FullLoader)

    with open(cfg["cutset_file_name"], "r") as yml_cfg:  # pylint: disable=unspecified-encoding
        cut_set = yaml.load(yml_cfg, yaml.FullLoader)

    pt_mins = cut_set["pt"]["mins"]
    pt_maxs = cut_set["pt"]["maxs"]
    selection_string = ""
    for ipt, (pt_min, pt_max) in enumerate(zip(pt_mins, pt_maxs)):
        cuts =  [k for k in cut_set.keys() if k != "pt"]
        if ipt == 0:
            selection_string += f"({pt_min} < fPt < {pt_max}) "
        else:
            selection_string += f" or ({pt_min} < fPt < {pt_max}) "
        for cut in cuts:
            if "NSig" not in cut:
                selection_string += f" and {cut_set[cut]['mins'][ipt]} < {cut} < {cut_set[cut]['maxs'][ipt]}"

    df = pd.DataFrame()
    for ifile, file in enumerate(cfg["data"]):
        df_file = pd.read_parquet(file)
        if "data_mass_shifts" in cfg and cfg["data_mass_shifts"] is not None:
            df_file["fM"] = df_file["fM"] + cfg["data_mass_shifts"][ifile]
        # continuous index over all input files, used to match the sweights to the candidates
        df = pd.concat([df, df_file], ignore_index=True)
    df.query(selection_string, inplace=True)


    particle = cfg["particle"]
    if particle == "Bplus":
        decay_channel = r"J/\psi K^{\plus}"
        mass_lims = [5.2, 5.4]
    elif particle == "B0":
        decay_channel = r"J/\psi K*^{0}"
        mass_lims = [5.2, 5.4]
    elif particle == "Bs":
        decay_channel = r"J/\psi \phi"
        mass_lims = [5.2, 5.4]

    hist_mass = ROOT.TH1D(f"hist_mass_{particle}", f";#it{{M}}({decay_channel});counts", 100, 5., 5.8)
    hist_mass_veto = ROOT.TH1D(f"hist_mass_veto_{particle}", f";#it{{M}}({decay_channel});counts", 100, 5., 5.8)
    hist_massJpsi = ROOT.TH1D("hist_massJpsi", ";#it{M}(#mu#mu);counts", 100, 2.8, 3.4)
    hist_massJpsi_veto = ROOT.TH1D("hist_massJpsi_veto", ";#it{M}(#mu#mu);counts", 100, 2.8, 3.4)
    hist_massJpsi_vs_mass = ROOT.TH2D(f"hist_massJpsi_vs_mass{particle}",
                                      f";#it{{M}}({decay_channel});#it{{M}}(#mu#mu);counts", 100, 5., 5.8, 100, 2.8, 3.4)
    set_style(hist_mass)
    set_style(hist_massJpsi)
    set_style(hist_mass_veto, ROOT.kRed)
    set_style(hist_massJpsi_veto, ROOT.kRed)
    hist_mass.Sumw2()
    hist_massJpsi.Sumw2()
    hist_mass_veto.Sumw2()
    hist_massJpsi_veto.Sumw2()
    hist_nsigma_el = ROOT.TH2D("hist_nsigma_el", ";#it{N}_{#sigma}^{TPC}(e) pos track;#it{N}_{#sigma}^{TPC}(e) neg track",
                               100, -10., 10., 100, -10., 10.)
    hist_nsigma_mu = ROOT.TH2D("hist_nsigma_mu", ";#it{N}_{#sigma}^{TPC}(#mu) pos track;#it{N}_{#sigma}^{TPC}(#mu) neg track",
                               100, -10., 10., 100, -10., 10.)
    for mass, mass_jpsi, ns_mu_n, ns_mu_p, ns_el_n, ns_el_p in zip(df["fM"].to_numpy(),
                                                                   df["fMJpsi"].to_numpy(),
                                                                   df["fNSigTpcMuJpsiDauNeg"].to_numpy(),
                                                                   df["fNSigTpcMuJpsiDauPos"].to_numpy(),
                                                                   df["fNSigTpcElJpsiDauNeg"].to_numpy(),
                                                                   df["fNSigTpcElJpsiDauPos"].to_numpy()):
        hist_massJpsi_vs_mass.Fill(mass, mass_jpsi)
        hist_mass.Fill(mass)
        if np.sqrt(ns_el_n**2 + ns_el_p**2) < cfg["veto_radius"]:
            hist_mass_veto.Fill(mass)
            hist_massJpsi_veto.Fill(mass_jpsi)
        if mass_lims[0] < mass < mass_lims[1]:
            hist_massJpsi.Fill(mass_jpsi)
            hist_nsigma_el.Fill(ns_el_p, ns_el_n)
            hist_nsigma_mu.Fill(ns_mu_p, ns_mu_n)

    veto = ROOT.TEllipse(0., 0., cfg["veto_radius"], cfg["veto_radius"], 0., 360.)
    veto.SetLineColor(ROOT.kRed)
    veto.SetLineWidth(2)
    veto.SetFillStyle(0)

    lat = ROOT.TLatex()
    lat.SetNDC()
    lat.SetTextSize(0.045)
    lat.SetTextColor(ROOT.kRed)

    canv = ROOT.TCanvas("canv", "", 1500, 1000)
    leg = ROOT.TLegend(0.2, 0.6, 0.8, 0.8)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.045)
    leg.AddEntry(hist_mass, "BDT selected candidates", "lp")
    leg.AddEntry(hist_mass_veto, "PID veto rejected candidates", "lp")
    canv.Divide(3, 2)
    canv.cd(1)
    hist_massJpsi_vs_mass.Draw("colz")
    canv.cd(2)
    hist_mass.Draw("e")
    hist_mass_veto.Draw("esame")
    canv.cd(3)
    hist_massJpsi.Draw("e")
    hist_massJpsi_veto.Draw("esame")
    canv.cd(4)
    hist_nsigma_mu.Draw("colz")
    canv.cd(5)
    hist_nsigma_el.Draw("colz")
    veto.Draw()
    lat.DrawLatex(0.6, 0.65, "veto on e PID")
    canv.cd(6)
    leg.Draw()
    canv.SaveAs(f"check_{particle}_JPsi.pdf")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("--config", "-c", metavar="text", default="config_fit.yml",
                        help="yaml config file for fit", required=True)
    args = parser.parse_args()

    project_distributions(args.config)
