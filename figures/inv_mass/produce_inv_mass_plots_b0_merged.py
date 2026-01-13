"""

"""
import argparse
import ROOT
import sys
sys.path.append("../../utils")
from style_formatter import root_colors_from_matplotlib_colormap
ci = ROOT.TColor.GetFreeColorIndex()

def set_data_style(hist, isnorm=False):
    """

    """

    hist.SetDirectory(0)
    hist.Sumw2()
    hist.SetMarkerStyle(ROOT.kFullCircle)
    hist.SetMarkerColor(ROOT.kBlack)
    hist.SetMarkerSize(0.8)
    hist.SetLineWidth(2)
    hist.SetLineColor(ROOT.kBlack)
    if isnorm:
        hist.GetYaxis().SetTitle(
            f"Normalised counts per {hist.GetBinWidth(1)*1000:.0f} MeV/#it{{c}}^{{2}}")
        hist.GetYaxis().SetRangeUser(0., hist.GetMaximum() * 1.2)
        hist.SetMarkerSize(1.6)
    else:
        hist.GetYaxis().SetTitle(f"Counts per {hist.GetBinWidth(1)*1000:.0f} MeV/#it{{c}}^{{2}}")
        hist.GetYaxis().SetRangeUser(0.1, hist.GetMaximum() * 1.2)
    hist.GetXaxis().SetTitle("#it{M}(D^{#mp}#pi^{#pm}) (GeV/#it{c}^{2})")

    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetXaxis().SetNdivisions(505)
    hist.GetYaxis().SetNdivisions(505)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleOffset(1.45)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetDecimals()
    hist.GetYaxis().SetMaxDigits(3)
    hist.GetXaxis().SetRangeUser(4.9, 5.66)


def get_function_fromhist(hist, func_type="totfunc", norm_fact = 1., colors=None):
    """

    """
    hist.Scale(norm_fact)
    hist.SetFillStyle(1001)
    hist.SetLineWidth(0)

    spline = ROOT.TSpline3(hist)
    spline.SetLineWidth(3)
    if func_type == "totfunc":
        spline.SetLineColor(ROOT.kBlue + 2)
        hist.SetFillColorAlpha(ROOT.kBlue + 2, 0.5)
    elif func_type == "bkg":
        spline.SetLineColor(ROOT.kRed + 1)
        hist.SetLineColor(0)
        hist.SetFillColor(10)
        hist.SetLineStyle(9)
        spline.SetLineStyle(9)
    elif "bkg_corr" in func_type:
        colors_map = {
            0: 3,
            1: 6,
            2: 7,
            3: 1,
            4: 4,
            5: 2
        }
        i_bkg = int(func_type.split("_")[-1])
        spline.SetLineColor(colors[colors_map[i_bkg]*2 + 1])
        hist.SetFillColor(colors[colors_map[i_bkg]*2 + 1])
        spline.SetFillColor(colors[colors_map[i_bkg]*2 + 1])
        spline.SetFillStyle(1000)
        spline.SetLineStyle(i_bkg+2)
    elif func_type == "signal":
        spline.SetLineColor(ROOT.kAzure + 4)
        hist.SetFillColorAlpha(ROOT.kAzure + 4, 0.5)

    return spline

def plot(infile_name, colors, version, pt_mins, pt_maxs):
    """

    """
    ROOT.gStyle.SetPadRightMargin(0.035)
    ROOT.gStyle.SetPadTopMargin(0.065)
    ROOT.gStyle.SetPadLeftMargin(0.14)
    ROOT.gStyle.SetPadBottomMargin(0.12)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.TGaxis.SetMaxDigits(2)

    infile = ROOT.TFile.Open(infile_name)
    hist_mass, hist_signal, hist_bkg = [], [], []
    hist_bkg_corr = [[] for _ in range(6)]
    func_bkg, func_signal, func_totfunc = [], [], []
    func_bkg_corr = [[] for _ in range(6)]
    corr_bkg_stack = []


    h_ry_pt_int = infile.Get("h_rawyields_ptint")
    h_ry = infile.Get("h_rawyields")
    ry_pt_int = h_ry_pt_int.GetBinContent(1)
    ry_unc_pt_int = h_ry_pt_int.GetBinError(1)
    ry = []
    ry_unc = []

    lat = ROOT.TLatex()
    lat.SetNDC()
    lat.SetTextFont(42)
    lat.SetTextColor(ROOT.kBlack)
    lat.SetTextSize(0.07)
    lat.SetTextAlign(22)

    lat_small = ROOT.TLatex()
    lat_small.SetNDC()
    lat_small.SetTextFont(42)
    lat_small.SetTextColor(ROOT.kBlack)
    lat_small.SetTextSize(0.05)
    lat_small.SetTextAlign(22)

    lat_right_align = ROOT.TLatex()
    lat_right_align.SetNDC()
    lat_right_align.SetTextFont(42)
    lat_right_align.SetTextColor(ROOT.kBlack)
    lat_right_align.SetTextSize(0.05)
    lat_right_align.SetTextAlign(32)

    for pt_min, pt_max in zip(pt_mins, pt_maxs):
        if pt_min is None and pt_max is None:
            pt_suffix = "ptint"
        else:
            pt_suffix = f"pt{pt_min}_{pt_max}"

        hist_mass.append(infile.Get(f"hdata_{pt_suffix}"))
        set_data_style(hist_mass[-1])
        if pt_min==2 and pt_max==4:
            hist_mass[-1].GetYaxis().SetRangeUser(0.1, 400)
        hist_signal.append(infile.Get(f"signal_0_{pt_suffix}"))
        hist_bkg.append(infile.Get(f"bkg_6_{pt_suffix}"))
        for i in range(6):
            hist_bkg_corr[i].append(infile.Get(f"bkg_{i}_{pt_suffix}"))

        func_bkg.append(get_function_fromhist(hist_bkg[-1], "bkg"))
        for i in range(6):
            func_bkg_corr[i].append(
                get_function_fromhist(
                    hist_bkg_corr[i][-1],
                    f"bkg_corr_{i}",
                    1.,
                    colors
                )
            )

        corr_bkg_stack.append(ROOT.THStack("corr_bkg_stack", ""))
        corr_bkg_stack[-1].Add(hist_bkg[-1])
        for i in range(6):
            corr_bkg_stack[-1].Add(hist_bkg_corr[i][-1])

        func_signal.append(get_function_fromhist(hist_signal[-1], "signal"))
        func_totfunc.append(get_function_fromhist(infile.Get(f"total_func_{pt_suffix}"), "totfunc"))

        if pt_min is not None and pt_max is not None:
            ry.append(h_ry.GetBinContent(h_ry.FindBin((pt_min+pt_max)/2)))
            ry_unc.append(h_ry.GetBinError(h_ry.FindBin((pt_min+pt_max)/2)))

    canv_masses = ROOT.TCanvas("canv_masses", "", 1000, 1000)
    ROOT.gPad.SetRightMargin(0.)
    ROOT.gPad.SetTopMargin(0.)
    ROOT.gPad.SetLeftMargin(0.)
    ROOT.gPad.SetBottomMargin(0.)
    canv_masses.Divide(2, 2)
    for i, (pt_min, pt_max) in enumerate(zip(pt_mins, pt_maxs)):
        if i == 0:
            canv_masses.cd(1)
        else:
            canv_masses.cd(i+2)
        hist_mass[i].DrawCopy()

        corr_bkg_stack[i].Draw("NOCLEAR hist same")
        hist_bkg[i].Draw("histsame")
        func_bkg[i].Draw("lsame")
        hist_mass[i].DrawCopy("same")
        func_totfunc[i].Draw("lsame")
        hist_signal[i].DrawCopy("histsame")
        func_signal[i].Draw("lsame")

        ROOT.gPad.RedrawAxis()
        
        if pt_min is None and pt_max is None:
            lat_right_align.DrawLatex(0.9, 0.85, "1 < #kern[-0.3]{#it{p}_{T}} < 23.5 GeV/#it{c}")
            lat_right_align.DrawLatex(0.9, 0.79, f"#it{{S}} = {ry_pt_int:.0f}#kern[0.1]{{#pm {ry_unc_pt_int:.0f}}}")
        else:
            lat_right_align.DrawLatex(0.9, 0.85, f"{pt_min} < #kern[-0.3]{{#it{{p}}_{{T}}}} < {pt_max} GeV/#it{{c}}")
            lat_right_align.DrawLatex(0.9, 0.79, f"#it{{S}} = {ry[i-1]:.0f}#kern[0.1]{{#pm {ry_unc[i-1]:.0f}}}")

        # lat_right_align.DrawLatex(0.3, 0.3, "S = XX #pm X.X")

    canv_masses.cd(2)
    lat.DrawLatex(0.5, 0.9, "ALICE")
    lat_small.DrawLatex(0.5, 0.84,
                        "pp,#kern[0.04]{#sqrt{#it{s}} = 13.6 TeV},#kern[0.09]{#font[132]{#it{L}}_{int} = 43 pb^{#minus1}}")


    leg_corr = ROOT.TLegend(0.25, 0.1, 0.55, 0.5)
    leg_corr.SetTextSize(0.045)
    leg_corr.SetBorderSize(0)
    leg_corr.SetFillStyle(0)
    leg_corr.AddEntry(hist_bkg_corr[5][-1], "B^{0}#rightarrow D^{#minus}K^{+}", "f")
    leg_corr.AddEntry(hist_bkg_corr[1][-1], "B^{0}#rightarrow D*^{#minus}#pi^{+}#rightarrow D^{0}#pi^{#minus}#pi^{+}", "f")
    leg_corr.AddEntry(hist_bkg_corr[2][-1], "B_{s}^{0}#rightarrow D_{s}^{#minus}#pi^{+}#rightarrow K^{+}K^{#minus}#pi^{+}#pi^{+}", "f")
    leg_corr.AddEntry(hist_bkg_corr[3][-1], "#Lambda_{b}^{0}#rightarrow #kern[-0.5]{#Lambda_{c}^{+}}#pi^{#minus}#rightarrow pK^{#minus}#pi^{+}#pi^{#minus}", "f")
    leg_corr.AddEntry(hist_bkg_corr[0][-1], "B^{0}#rightarrow D*^{#minus}#pi^{+}#rightarrow D^{#minus}#pi^{+}{#pi^{0},#gamma}", "f")
    leg_corr.AddEntry(hist_bkg_corr[4][-1], "B^{0}#rightarrow D^{#minus}#rho^{+}#rightarrow D^{#minus}#pi^{+}{#pi^{0},#gamma}", "f")

    leg_corr.Draw()


    leg = ROOT.TLegend(0.25, 0.5, 0.55, 0.8)
    leg.SetTextSize(0.045)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(hist_mass[-1], "Data", "p")
    leg.AddEntry(hist_signal[-1], "#splitline{#lower[0.05]{B^{0}#rightarrow D^{#minus}#pi^{#plus}}}{#lower[-0.05]{and charge conj.}}", "f")
    leg.AddEntry(func_bkg[-1], "Comb. background", "l")
    leg.AddEntry(func_totfunc[-1], "Total fit function", "l")

    leg2 = ROOT.TLegend(0.25, 0.5, 0.55, 0.8)
    leg2.SetTextSize(0.045)
    leg2.SetBorderSize(0)
    leg2.SetFillStyle(0)
    leg2.AddEntry(hist_mass[-1], "Data", "p")
    leg2.AddEntry(func_signal[-1], "#splitline{#lower[0.05]{B^{0}#rightarrow D^{#minus}#pi^{#plus}#rightarrow#pi^{#minus}K^{#plus}#pi^{#minus}#pi^{#plus}}}{#lower[-0.05]{and charge conj.}}", "f")
    leg2.AddEntry(func_bkg[-1], "Comb. background", "l")
    leg2.AddEntry(func_totfunc[-1], "Total fit function", "l")

    leg.Draw()
    leg2.Draw()

    canv_masses.SaveAs(f"B0_mass_full.pdf")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments")
    parser.add_argument("--input_file", "-i", metavar="text",
                        default="../b0_analysis/fit/B0_mass.root",
                        help="input root file", required=False)
    parser.add_argument("--palette", "-p", metavar="text",
                        default="tab20",
                        help="matplotlib palette name for corr. bkg", required=False)
    args = parser.parse_args()

    pt_mins = [None, 2, 10]
    pt_maxs = [None, 4, 14]

    ROOT.TH1.AddDirectory(False)
    COLORS, _ = root_colors_from_matplotlib_colormap(args.palette)

    plot(args.input_file, COLORS, 3, pt_mins, pt_maxs)
