import ROOT 
import numpy as np
import sys
sys.path.append('utils')
from analysis_utils import get_n_events_from_zorro
from style_formatter import root_colors_from_matplotlib_colormap

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadLeftMargin(0.12)
ROOT.gStyle.SetPadBottomMargin(0.1)
ROOT.gStyle.SetPadTopMargin(0.05)
ROOT.gStyle.SetPadRightMargin(0.05)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)

if __name__ == '__main__':

    # Get cross section
    data_file = ROOT.TFile.Open('systematics/cross_section_default_DK_MC_enlarged_templates_fix_evsel_pt_cuts_w_syst_fabio_fix_TT_vs_phi.root')
    h_stat = data_file.Get('h_stat')
    h_stat.SetDirectory(0)
    h_syst = data_file.Get('h_syst_no_br_no_lumi')
    h_syst.SetDirectory(0)
    g_syst = ROOT.TGraphErrors(h_syst)
    data_file.Close()

    h_stat.Scale(1.e-6)
    h_syst.Scale(1.e-6)
    g_syst.Scale(1.e-6)

    # Get predictions
    fonll_file = ROOT.TFile.Open('fonll/fonll_bhadron_nnpdfs_13dot6tev.root')
    g_pred_fonll = fonll_file.Get('gBhadrNNPDF30')
    fonll_file.Close()
    g_pred_fonll.Scale(1.e-6)

    nnlo_nnll_file = ROOT.TFile.Open('nnlo_nnll/nnlo_nnll.root')
    g_pred_nnlo_nnll = nnlo_nnll_file.Get('g_cross_sec')
    g_pred_nnlo_nnll.Scale(1.e-6)
    nnlo_nnll_file.Close()
   
    pt_bins = np.append(np.asarray(g_pred_fonll.GetX(), 'd') - np.asarray(g_pred_fonll.GetEXlow(), 'd'), g_pred_fonll.GetX()[g_pred_fonll.GetN()-1] + g_pred_fonll.GetEXhigh()[g_pred_fonll.GetN()-1])

    h_pred_fonll = ROOT.TH1F('h_pred_fonll', 'h_pred_fonll', g_pred_fonll.GetN(), pt_bins)
    for i in range(1, g_pred_fonll.GetN()+1):
        h_pred_fonll.SetBinContent(i, g_pred_fonll.GetY()[i-1])
        h_pred_fonll.SetBinError(i, 1.e-10)
    
    h_pred_nnlo_nnll = ROOT.TH1F('h_pred_nnlo_nnll', 'h_pred_nnlo_nnll', g_pred_nnlo_nnll.GetN(), pt_bins)
    for i in range(1, g_pred_nnlo_nnll.GetN()+1):
        h_pred_nnlo_nnll.SetBinContent(i, g_pred_nnlo_nnll.GetY()[i-1])
        h_pred_nnlo_nnll.SetBinError(i, 1.e-10)

    # Set the style
    colors, _ = root_colors_from_matplotlib_colormap('tab10')
    h_stat.SetMarkerStyle(ROOT.kFullCircle)
    h_stat.SetMarkerSize(1.5)
    h_stat.SetMarkerColor(ROOT.kBlack)
    h_stat.SetLineColor(ROOT.kBlack)
    h_stat.SetLineWidth(2)

    g_syst.SetMarkerStyle(ROOT.kFullCircle)
    g_syst.SetMarkerSize(1.5)
    g_syst.SetMarkerColor(ROOT.kBlack)
    g_syst.SetLineColor(ROOT.kBlack)
    g_syst.SetLineWidth(2)
    g_syst.SetFillStyle(0)
    for i in range(0, g_syst.GetN()):
        g_syst.SetPointError(i, g_syst.GetErrorX(i)/2, g_syst.GetErrorY(i))

    g_pred_fonll.SetLineColorAlpha(colors[0], 1)
    g_pred_fonll.SetLineWidth(2)
    g_pred_fonll.SetMarkerColorAlpha(ROOT.kBlack, 0.)
    g_pred_fonll.SetFillStyle(1001)
    g_pred_fonll.SetFillColorAlpha(colors[0], 0.35)

    h_pred_fonll.SetLineColorAlpha(colors[0], 1)
    h_pred_fonll.SetLineWidth(2)
    h_pred_fonll.SetMarkerColorAlpha(ROOT.kBlack, 0.)
    h_pred_fonll.SetFillColorAlpha(colors[0], 0.35)

    g_pred_nnlo_nnll.SetLineColorAlpha(ROOT.kRed+2, 1)
    g_pred_nnlo_nnll.SetLineWidth(2)
    g_pred_nnlo_nnll.SetMarkerColorAlpha(ROOT.kBlack, 0.)
    g_pred_nnlo_nnll.SetFillStyle(1001)
    g_pred_nnlo_nnll.SetFillColorAlpha(ROOT.kRed+2, 0.3)

    h_pred_nnlo_nnll.SetLineColorAlpha(ROOT.kRed+2, 1)
    h_pred_nnlo_nnll.SetLineWidth(2)
    h_pred_nnlo_nnll.SetMarkerColorAlpha(ROOT.kBlack, 0.)
    h_pred_nnlo_nnll.SetFillColorAlpha(ROOT.kRed+2, 0.3)

    # Draw
    c = ROOT.TCanvas('c', 'c', 900, 600)
    pad_cross_sec = ROOT.TPad('pad_cross_sec', 'pad_cross_sec', 0, 0, 0.5, 1)
    pad_cross_sec.Draw()
    pad_cross_sec.cd()
    pad_cross_sec.SetLogy()
    h_frame = pad_cross_sec.DrawFrame(0, 2.e-2, 23.5, 3.e2, ';#it{p}_{T} (GeV/#it{c});d^{2}#it{#sigma}/d#it{p}_{T}d#it{y} (#mub GeV^{#minus1}#kern[0.25]{#it{c}})')
    h_frame.GetXaxis().SetTitleOffset(1.)
    h_frame.GetYaxis().SetTitleOffset(1.1)
    h_frame.GetXaxis().SetTitleSize(0.045)
    h_frame.GetYaxis().SetTitleSize(0.045)
    h_frame.GetXaxis().SetLabelSize(0.04)
    h_frame.GetYaxis().SetLabelSize(0.04)
    g_pred_fonll.Draw('same E2')
    g_pred_nnlo_nnll.Draw('same E2')
    h_pred_fonll.Draw('same e')
    h_pred_nnlo_nnll.Draw('same e')
    h_stat.Draw('same p')
    g_syst.Draw('same 5')

    # Legend
    leg = ROOT.TLegend(0.4, 0.605, 0.55, 0.755)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.04)
    leg.SetMargin(0.7)
    leg.AddEntry(h_stat, 'Data', 'lp')
    leg.AddEntry(g_pred_fonll, 'FONLL', 'fl')
    leg.AddEntry(g_pred_nnlo_nnll, 'NNLO+NNLL', 'fl')
    leg.Draw()

    # Add the text
    text_decay = ROOT.TLatex(0.41, 0.765, 'B^{0} mesons')
    text_decay.SetNDC()
    text_decay.SetTextSize(0.04)
    text_decay.SetTextFont(42)
    text_decay.Draw()

    text_ALICE = ROOT.TLatex(0.15, 0.885, 'ALICE')
    text_ALICE.SetNDC()
    text_ALICE.SetTextSize(0.06)
    text_ALICE.SetTextFont(42)
    text_ALICE.Draw()

    text_pp = ROOT.TLatex(0.15, 0.855, 'pp collisions,#kern[0.05]{#sqrt{#it{s}} = 13.6 TeV}')
    text_pp.SetNDC()
    text_pp.SetTextSize(0.04)
    text_pp.SetTextFont(42)
    text_pp.Draw()

    text_rapidity = ROOT.TLatex(0.15, 0.82, '|#it{y}| < 0.5')
    text_rapidity.SetNDC()
    text_rapidity.SetTextSize(0.04)
    text_rapidity.SetTextFont(42)
    text_rapidity.Draw()

    text_lumi = ROOT.TLatex(0.15, 0.785, '#font[132]{#it{L}}_{int} = 43 pb^{#minus1}')
    text_lumi.SetNDC()
    text_lumi.SetTextSize(0.04) 
    text_lumi.SetTextFont(42)
    text_lumi.Draw()

    text_unc_lumi = ROOT.TLatex(0.15, 0.2, '#pm 10% #kern[-0.2]{#font[132]{#it{L}}_{int}} uncertainty')
    text_unc_lumi.SetNDC()
    text_unc_lumi.SetTextSize(0.035) 
    text_unc_lumi.SetTextFont(42)
    text_unc_lumi.Draw()

    text_unc_br = ROOT.TLatex(0.15, 0.17, '#pm 3.6% BR uncertainty')
    text_unc_br.SetNDC()
    text_unc_br.SetTextSize(0.035) 
    text_unc_br.SetTextFont(42)
    text_unc_br.Draw()

    ROOT.gPad.RedrawAxis()


    c.cd()
    pad_ratios_axis_label = ROOT.TPad('pad_ratios_axis_label', 'pad_ratios_axis_label', 0.5, 0, 1, 1)
    pad_ratios_axis_label.SetLeftMargin(0.15)
    pad_ratios_axis_label.Draw()
    pad_ratios_axis_label.cd()
    h_frame_axis_label = pad_ratios_axis_label.DrawFrame(0, 0.123, 23.5, 0.9876, ';#it{p}_{T} (GeV/#it{c});')
    h_frame_axis_label.GetXaxis().SetTitleOffset(1.)
    h_frame_axis_label.GetYaxis().SetTitleOffset(1.1)
    h_frame_axis_label.GetXaxis().SetTitleSize(0.045)
    h_frame_axis_label.GetYaxis().SetTitleSize(0.045)
    h_frame_axis_label.GetXaxis().SetLabelSize(0.04)
    h_frame_axis_label.GetYaxis().SetLabelSize(0.04)

    c.cd()

    pad_ratios = ROOT.TPad('pad_ratios', 'pad_ratios', 0.5, 0.1, 1, 0.95)
    pad_ratios.Draw()
    pad_ratios.cd()

    pad_ratio_fonll = ROOT.TPad('pad_ratio_fonll', 'pad_ratio_fonll', 0, 0.5, 1, 1)
    pad_ratio_fonll.Draw()
    pad_ratio_fonll.cd()
    pad_ratio_fonll.SetBottomMargin(0)
    pad_ratio_fonll.SetLeftMargin(0.15)
    pad_ratio_fonll.SetTopMargin(0)
    h_frame_ratio_fonll = pad_ratio_fonll.DrawFrame(0, 0.2, 23.5,2.995, ';#it{p}_{T} (GeV/#it{c});#frac{Data}{FONLL}')
    h_frame_ratio_fonll.GetXaxis().SetTitleOffset(1.1)
    h_frame_ratio_fonll.GetYaxis().SetTitleOffset(0.9)
    h_frame_ratio_fonll.GetYaxis().SetDecimals(True)
    h_frame_ratio_fonll.GetYaxis().CenterTitle(True)
    h_frame_ratio_fonll.GetXaxis().SetTitleSize(0.12)
    h_frame_ratio_fonll.GetYaxis().SetTitleSize(0.08)
    h_frame_ratio_fonll.GetXaxis().SetLabelSize(0.12)
    h_frame_ratio_fonll.GetYaxis().SetLabelSize(0.07)
    h_frame_ratio_fonll.GetYaxis().SetNdivisions(606)

    g_fonll_unc = g_pred_fonll.Clone('g_fonll_unc')
    for i in range(0, g_fonll_unc.GetN()):
        g_fonll_unc.SetPoint(i, g_pred_fonll.GetX()[i], 1)
        g_fonll_unc.SetPointError(i, g_pred_fonll.GetErrorXlow(i), g_pred_fonll.GetErrorXhigh(i), g_pred_fonll.GetErrorYlow(i)/g_pred_fonll.GetY()[i], g_pred_fonll.GetErrorYhigh(i)/g_pred_fonll.GetY()[i])

    g_fonll_unc.Draw("same 2")

    line_one_fonll = ROOT.TLine(1, 1, 23.5, 1)
    line_one_fonll.SetLineStyle(2)
    line_one_fonll.SetLineColor(ROOT.kBlack)
    line_one_fonll.Draw("same")

    h_ratio_data_fonll_stat = h_stat.Clone('h_ratio_data_fonll_stat')
    h_ratio_data_fonll_stat.Divide(h_pred_fonll)
    h_ratio_data_fonll_stat.Draw('same p')

    g_ratio_data_fonll_syst = g_syst.Clone('g_ratio_data_fonll_syst')
    for i in range(0, g_ratio_data_fonll_syst.GetN()):
        g_ratio_data_fonll_syst.SetPoint(i, g_syst.GetX()[i], g_syst.GetY()[i]/g_pred_fonll.GetY()[i])
        g_ratio_data_fonll_syst.SetPointError(i, g_syst.GetErrorX(i), g_syst.GetErrorY(i)/g_pred_fonll.GetY()[i])

    g_ratio_data_fonll_syst.Draw('same 5') 

    pad_ratio_fonll.RedrawAxis()

    pad_ratios.cd()

    pad_ratio_nnlo_nnll = ROOT.TPad('pad_ratio_nnlo_nnll', 'pad_ratio_nnlo_nnll', 0, 0, 1, 0.5)
    pad_ratio_nnlo_nnll.Draw()
    pad_ratio_nnlo_nnll.cd()
    pad_ratio_nnlo_nnll.SetBottomMargin(0)
    pad_ratio_nnlo_nnll.SetLeftMargin(0.15)
    pad_ratio_nnlo_nnll.SetTopMargin(0)
    h_frame_ratio_nnlo_nnll = pad_ratio_nnlo_nnll.DrawFrame(0, 0.2, 23.5,2.995, ';#it{p}_{T} (GeV/#it{c});#lower[0.1]{#frac{Data}{NNLO+NNLL}}')
    h_frame_ratio_nnlo_nnll.GetXaxis().SetTitleOffset(1.1)
    h_frame_ratio_nnlo_nnll.GetYaxis().SetTitleOffset(0.9)
    h_frame_ratio_nnlo_nnll.GetYaxis().SetDecimals(True)
    h_frame_ratio_nnlo_nnll.GetYaxis().CenterTitle(True)
    h_frame_ratio_nnlo_nnll.GetXaxis().SetTitleSize(0.12)
    h_frame_ratio_nnlo_nnll.GetYaxis().SetTitleSize(0.08)
    h_frame_ratio_nnlo_nnll.GetXaxis().SetLabelSize(0.12)
    h_frame_ratio_nnlo_nnll.GetYaxis().SetLabelSize(0.07)
    h_frame_ratio_nnlo_nnll.GetYaxis().SetNdivisions(606)

    g_nnlo_nnll_unc = g_pred_nnlo_nnll.Clone('g_nnlo_nnll_unc')
    for i in range(0, g_nnlo_nnll_unc.GetN()):
        g_nnlo_nnll_unc.SetPoint(i, g_pred_nnlo_nnll.GetX()[i], 1)
        g_nnlo_nnll_unc.SetPointError(i, g_pred_nnlo_nnll.GetErrorXlow(i), g_pred_nnlo_nnll.GetErrorXhigh(i), g_pred_nnlo_nnll.GetErrorYlow(i)/g_pred_nnlo_nnll.GetY()[i], g_pred_nnlo_nnll.GetErrorYhigh(i)/g_pred_nnlo_nnll.GetY()[i])

    g_nnlo_nnll_unc.Draw("same 2")

    line_one_nnlo_nnll = ROOT.TLine(1, 1, 23.5, 1)
    line_one_nnlo_nnll.SetLineStyle(2)
    line_one_nnlo_nnll.SetLineColor(ROOT.kBlack)
    line_one_nnlo_nnll.Draw("same")

    h_ratio_data_nnlo_nnll_stat = h_stat.Clone('h_ratio_data_nnlo_nnll_stat')
    h_ratio_data_nnlo_nnll_stat.Divide(h_pred_nnlo_nnll)
    h_ratio_data_nnlo_nnll_stat.Draw('same p')

    g_ratio_data_nnlo_nnll_syst = g_syst.Clone('g_ratio_data_nnlo_nnll_syst')
    for i in range(0, g_ratio_data_nnlo_nnll_syst.GetN()):
        g_ratio_data_nnlo_nnll_syst.SetPoint(i, g_syst.GetX()[i], g_syst.GetY()[i]/g_pred_nnlo_nnll.GetY()[i])
        g_ratio_data_nnlo_nnll_syst.SetPointError(i, g_syst.GetErrorX(i), g_syst.GetErrorY(i)/g_pred_nnlo_nnll.GetY()[i])

    g_ratio_data_nnlo_nnll_syst.Draw('same 5') 

    c.SaveAs('figures/cross_section/cross_section_vs_NNLO_NNLL_TT_dk_mc_fix_evsel.pdf')
