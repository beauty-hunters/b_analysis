import argparse
import sys
sys.path.append('utils') # pylint: disable=wrong-import-position
import ROOT
from style_formatter import root_colors_from_matplotlib_colormap # pylint: disable=import-error

def draw_efficiency_figure(input_file, output_file, particle="B0"):
    """
    Draw the efficiency and acceptance histograms.

    Args:
        input_file (str): Path to the input ROOT file containing efficiency histograms.
        output_file (str): Path to the output PDF file for the efficiency figure.

    Returns:
        None
    """

    # Set style
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPadLeftMargin(0.14)
    ROOT.gStyle.SetPadBottomMargin(0.12)
    ROOT.gStyle.SetPadTopMargin(0.05)
    ROOT.gStyle.SetPadRightMargin(0.05)
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)

    colors, _ = root_colors_from_matplotlib_colormap("tab10")

    with ROOT.TFile.Open(input_file) as f:
        h_eff = f.Get('h_eff')
        h_eff.SetDirectory(0)
        h_acc = f.Get('h_acc')
        h_acc.SetDirectory(0)

    h_eff.SetMarkerStyle(ROOT.kFullCircle)
    h_eff.SetMarkerColor(colors[0])
    h_eff.SetMarkerSize(2)
    h_eff.SetLineColor(colors[0])
    h_eff.SetLineWidth(2)

    h_acc.SetMarkerStyle(ROOT.kFullDiamond)
    h_acc.SetMarkerColor(colors[2])
    h_acc.SetMarkerSize(2.5)
    h_acc.SetLineColor(colors[2])
    h_acc.SetLineWidth(2)
    h_acc.SetLineStyle(7)

    leg = ROOT.TLegend(0.35, 0.2, 0.65, 0.3)
    leg.SetTextSize(0.045)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.AddEntry(h_acc, "Acceptance", "pl")
    leg.AddEntry(h_eff, "Acceptance#timesEfficiency", "pl")

    c_eff = ROOT.TCanvas('c_eff', '', 800, 800)
    c_eff.SetLogy()
    h_frame = c_eff.DrawFrame(h_eff.GetBinLowEdge(1), 1.e-4, h_eff.GetBinLowEdge(h_eff.GetNbinsX()+1), 10.,
                ';#it{p}_{T} (GeV/#it{c});#it{c}_{#Delta#it{y}}#kern[0.01]{#times Correction factor};')
    h_frame.GetXaxis().SetTitleOffset(1.2)
    h_frame.GetYaxis().SetTitleOffset(1.5)
    h_frame.GetYaxis().SetTitleSize(0.04)
    h_frame.GetYaxis().SetLabelSize(0.04)
    h_frame.GetXaxis().SetTitleSize(0.04)
    h_frame.GetXaxis().SetLabelSize(0.04)
    h_eff.Draw('][ hist same')
    h_eff.DrawClone('pe X0 same')
    h_acc.Draw('][ hist same')
    h_acc.DrawClone('pe X0 same')
    leg.Draw()

    # Add the text
    decay_channel = ''
    if particle == "Bplus":
        decay_channel = 'B^{+}#rightarrow#bar{D}^{#font[122]{0}}#pi^{+}\
            #rightarrow #pi^{#font[122]{-}}K^{+}#pi^{+}'
    if particle == "B0":
        decay_channel = 'B^{0}#rightarrow D^{#font[122]{-}}#pi^{+}#rightarrow#pi^{#font[122]{-}}K^{+}#pi^{#font[122]{-}}#pi^{+}'

    text_decay = ROOT.TLatex(0.36, 0.365, decay_channel)
    text_decay.SetNDC()
    text_decay.SetTextSize(0.04)
    text_decay.SetTextFont(42)
    text_decay.Draw()

    text_conj = ROOT.TLatex(0.36, 0.32, 'and charge conjugate')
    text_conj.SetNDC()
    text_conj.SetTextSize(0.04)
    text_conj.SetTextFont(42)
    text_conj.Draw()

    text_alice = ROOT.TLatex(0.18, 0.88, 'ALICE')
    text_alice.SetNDC()
    text_alice.SetTextSize(0.06)
    text_alice.SetTextFont(42)
    text_alice.Draw()

    text_pp = ROOT.TLatex(0.18, 0.83, 'pp collisions,#kern[0.05]{#sqrt{#it{s}} = 13.6 TeV}')
    text_pp.SetNDC()
    text_pp.SetTextSize(0.04)
    text_pp.SetTextFont(42)
    text_pp.Draw()

    text_rapidity = ROOT.TLatex(0.18, 0.78, '|y| < 0.5')
    text_rapidity.SetNDC()
    text_rapidity.SetTextSize(0.04)
    text_rapidity.SetTextFont(42)
    text_rapidity.Draw()

    c_eff.SaveAs(output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw efficiency figure")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input ROOT file containing efficiency histograms")  # /home/fchinu/Run3/B0_pp/efficiency/reco_rap_0p5/efficiency_i3_i4_from_bdt_test.root
    parser.add_argument("--output", "-o", type=str, required=True, help="Output PDF file for the efficiency figure")
    parser.add_argument("--particle", "-p", type=str, default="B0", choices=["B0", "Bplus", "Bs"], help="Particle type (default: B0)")
    args = parser.parse_args()

    draw_efficiency_figure(input_file=args.input, output_file=args.output, particle=args.particle)