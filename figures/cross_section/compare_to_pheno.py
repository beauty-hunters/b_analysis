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
    h_syst = data_file.Get('h_syst')
    h_syst.SetDirectory(0)
    g_syst = ROOT.TGraphErrors(h_syst)
    data_file.Close()

    h_stat.Scale(1.e-6)
    h_syst.Scale(1.e-6)
    g_syst.Scale(1.e-6)

    # Get predictions
    tamu_file = ROOT.TFile.Open('tamu/tamu_bhadr_13dot6.root')
    g_pred_tamu = tamu_file.Get('gBhadr')
    g_pred_tamu.Scale(1.e6)
    g_pred_tamu.Scale(1.e-6)
    tamu_file.Close()

    catania_file = ROOT.TFile.Open('catania/B0_meson_13_6TeV_band.root')
    g_pred_catania = catania_file.Get('gBhadr')
    catania_file.Close()

    epos_file = ROOT.TFile.Open('epos4hq/EPOS4HQ_B0pred_pp13dot6TeV_pp_coal_frag.root')
    g_pred_epos = epos_file.Get('graph_bzero_y05')
    epos_file.Close()

    pt_bins = np.append(np.asarray(g_pred_epos.GetX(), 'd') - np.asarray(g_pred_epos.GetEXlow(), 'd'), g_pred_epos.GetX()[g_pred_epos.GetN()-1] + g_pred_epos.GetEXhigh()[g_pred_epos.GetN()-1])
    h_pred_epos = ROOT.TH1F('h_pred_epos', 'h_pred_epos', g_pred_epos.GetN(), pt_bins)
    for i in range(1, g_pred_epos.GetN()+1):
        h_pred_epos.SetBinContent(i, g_pred_epos.GetY()[i-1])
        h_pred_epos.SetBinError(i, 1.e-10)

    ampt_48_file = ROOT.TFile.Open('ampt/AMPT_13TeV_mb4.8_rebinned.root')
    h_pred_ampt_48 = ampt_48_file.Get('B0_mid_rebin')
    h_pred_ampt_48.SetDirectory(0)
    ampt_48_file.Close()
    g_pred_ampt_48 = ROOT.TGraphAsymmErrors(h_pred_ampt_48)
    h_pred_ampt_line_48 = h_pred_ampt_48.Clone('h_pred_ampt_line_48')
    for i in range(1, h_pred_ampt_line_48.GetNbinsX()+1):
        h_pred_ampt_line_48.SetBinError(i, 1.e-10)

    ampt_66_file = ROOT.TFile.Open('ampt/AMPT_13TeV_mb6.6_rebinned.root')
    h_pred_ampt_66 = ampt_66_file.Get('B0_mid_rebin')
    h_pred_ampt_66.SetDirectory(0)
    ampt_66_file.Close()
    g_pred_ampt_66 = ROOT.TGraphAsymmErrors(h_pred_ampt_66)
    h_pred_ampt_line_66 = h_pred_ampt_66.Clone('h_pred_ampt_line_66')
    for i in range(1, h_pred_ampt_line_66.GetNbinsX()+1):
        h_pred_ampt_line_66.SetBinError(i, 1.e-10)

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

    g_pred_tamu.SetLineColorAlpha(colors[3], 1)
    g_pred_tamu.SetLineWidth(3)
    g_pred_tamu.SetFillStyle(1001)
    g_pred_tamu.SetLineStyle(9)
    g_pred_tamu.SetFillColorAlpha(colors[3], 0.5)

    g_pred_catania.SetLineColorAlpha(colors[5], 0.5)
    g_pred_catania.SetLineWidth(0)
    g_pred_catania.SetMarkerColorAlpha(ROOT.kBlack, 0.)
    g_pred_catania.SetFillStyle(1001)
    g_pred_catania.SetFillColorAlpha(colors[5], 0.7)

    g_pred_epos.SetLineColorAlpha(ROOT.kGreen+2, 1)
    g_pred_epos.SetLineWidth(2)
    g_pred_epos.SetFillStyle(1001)
    g_pred_epos.SetFillColorAlpha(ROOT.kGreen+2, 0.2)

    h_pred_epos.SetLineColorAlpha(ROOT.kGreen+2, 0.5)
    h_pred_epos.SetLineWidth(2)
    h_pred_epos.SetMarkerColorAlpha(ROOT.kBlack, 0.)
    h_pred_epos.SetFillColorAlpha(ROOT.kGreen+2, 1)

    g_pred_ampt_48.SetLineColorAlpha(ROOT.kMagenta+2, 0.5)
    g_pred_ampt_48.SetLineWidth(2)
    g_pred_ampt_48.SetLineStyle(2)
    g_pred_ampt_48.SetFillStyle(1001)
    g_pred_ampt_48.SetFillColorAlpha(ROOT.kMagenta+2, 0.2)
    g_pred_ampt_48.SetMarkerColorAlpha(ROOT.kMagenta+2, 0.)

    h_pred_ampt_48.SetLineColorAlpha(ROOT.kMagenta+2, 1)
    h_pred_ampt_48.SetLineWidth(2)
    h_pred_ampt_48.SetLineStyle(2)
    h_pred_ampt_48.SetFillStyle(0)
    h_pred_ampt_48.SetMarkerSize(0)
    h_pred_ampt_48.SetMarkerColorAlpha(ROOT.kMagenta+2, 0.)

    h_pred_ampt_line_48.SetLineColorAlpha(ROOT.kMagenta+2, 0.5)
    h_pred_ampt_line_48.SetLineWidth(2)
    h_pred_ampt_line_48.SetFillStyle(0)
    h_pred_ampt_line_48.SetMarkerSize(0)
    h_pred_ampt_line_48.SetMarkerColorAlpha(ROOT.kMagenta+2, 0.)

    g_pred_ampt_66.SetLineColorAlpha(ROOT.kBlue+3, 0.7)
    g_pred_ampt_66.SetLineWidth(2)
    g_pred_ampt_66.SetLineStyle(1)
    g_pred_ampt_66.SetFillStyle(1001)
    g_pred_ampt_66.SetFillColorAlpha(ROOT.kBlue+3, 0.2)
    g_pred_ampt_66.SetMarkerSize(0)
    g_pred_ampt_66.SetMarkerColorAlpha(ROOT.kBlue+3, 0.)

    h_pred_ampt_66.SetLineColorAlpha(ROOT.kBlue+3, 1)
    h_pred_ampt_66.SetLineWidth(2)
    h_pred_ampt_66.SetLineStyle(1)
    h_pred_ampt_66.SetFillStyle(0)
    h_pred_ampt_66.SetMarkerSize(0)
    h_pred_ampt_66.SetMarkerColorAlpha(ROOT.kBlue+3, 0.)

    h_pred_ampt_line_66.SetLineColorAlpha(ROOT.kBlue+3, 0.4)
    h_pred_ampt_line_66.SetLineWidth(2)
    h_pred_ampt_line_66.SetFillStyle(0)
    h_pred_ampt_line_66.SetMarkerSize(0)
    h_pred_ampt_line_66.SetMarkerColorAlpha(ROOT.kBlue+3, 0.)

    # Draw
    c = ROOT.TCanvas('c', 'c', 900, 600)
    pad_cross_sec = ROOT.TPad('pad_cross_sec', 'pad_cross_sec', 0, 0, 0.5, 1)
    pad_cross_sec.Draw()
    pad_cross_sec.cd()
    pad_cross_sec.SetLogy()
    h_frame = pad_cross_sec.DrawFrame(0, 2.e-2, 23.5, 3.e2, ';#it{p}_{T} (GeV/#it{c});d^{2}#it{#sigma}/d#it{p}_{T}d#it{y} (#mub GeV^{#minus1}#kern[0.25]{#it{c}})')
    h_frame.GetXaxis().SetTitleOffset(1.1)
    h_frame.GetYaxis().SetTitleOffset(1.3)
    h_frame.GetXaxis().SetTitleSize(0.04)
    h_frame.GetYaxis().SetTitleSize(0.04)
    h_frame.GetXaxis().SetLabelSize(0.04)
    h_frame.GetYaxis().SetLabelSize(0.04)
    g_pred_catania.Draw('same E3')
    g_pred_tamu.Draw('same L')
    g_pred_epos.Draw('same E3L')
    # h_pred_epos.Draw('same e')
    g_pred_ampt_48.DrawClone('same E3L')
    # h_pred_ampt_line_48.Draw('same e')
    g_pred_ampt_66.DrawClone('same E3L')
    # h_pred_ampt_line_66.Draw('same e')
    h_stat.Draw('same p')
    g_syst.Draw('same 5')


    ROOT.gStyle.SetLineStyleString(11,"40 20")
    g_pred_tamu_leg = g_pred_tamu.Clone('g_pred_tamu_leg')
    g_pred_tamu_leg.SetLineStyle(11)

    # Legend
    leg = ROOT.TLegend(0.4, 0.55, 0.55, 0.755)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.04)
    leg.SetMargin(0.7)
    leg.AddEntry(h_stat, 'Data', 'lp')
    leg.AddEntry(g_pred_catania, 'Catania', 'f')
    leg.AddEntry(g_pred_tamu_leg, 'TAMU', 'l')
    leg.AddEntry(g_pred_epos, 'EPOS4HQ', 'fl')
    leg.AddEntry(g_pred_ampt_48, 'AMPT, #kern[-0.07]{#it{m}_{b} = 4.8 GeV/#it{c}^{2}}', 'fl')
    leg.AddEntry(g_pred_ampt_66, 'AMPT, #kern[-0.07]{#it{m}_{b} = 6.6 GeV/#it{c}^{2}}', 'fl')
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

    text_pp = ROOT.TLatex(0.15, 0.855, 'pp collisions, #sqrt{#it{s}} = 13.6 TeV')
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

    ROOT.gPad.RedrawAxis()


    c.cd()
    pad_ratios_axis_label = ROOT.TPad('pad_ratios_axis_label', 'pad_ratios_axis_label', 0.5, 0, 1, 1)
    pad_ratios_axis_label.SetLeftMargin(0.15)
    pad_ratios_axis_label.Draw()
    pad_ratios_axis_label.cd()
    h_frame_axis_label = pad_ratios_axis_label.DrawFrame(0, 0.123, 23.5, 0.9876, ';#it{p}_{T} (GeV/#it{c});')
    h_frame_axis_label.GetXaxis().SetTitleOffset(1.1)
    h_frame_axis_label.GetYaxis().SetTitleOffset(1.3)
    h_frame_axis_label.GetXaxis().SetTitleSize(0.04)
    h_frame_axis_label.GetYaxis().SetTitleSize(0.04)
    h_frame_axis_label.GetXaxis().SetLabelSize(0.04)
    h_frame_axis_label.GetYaxis().SetLabelSize(0.04)

    c.cd()

    pad_ratios = ROOT.TPad('pad_ratios', 'pad_ratios', 0.5, 0.1, 1, 0.95)
    pad_ratios.Draw()
    pad_ratios.cd()

    pad_ratio_catania = ROOT.TPad('pad_ratio_catania', 'pad_ratio_catania', 0, 0.8, 1, 1)
    pad_ratio_catania.Draw()
    pad_ratio_catania.cd()
    pad_ratio_catania.SetBottomMargin(0)
    pad_ratio_catania.SetLeftMargin(0.15)
    pad_ratio_catania.SetTopMargin(0)
    h_frame_ratio_catania = pad_ratio_catania.DrawFrame(0, 0.2, 23.5,2.995, ';#it{p}_{T} (GeV/#it{c});#frac{Data}{Catania}')
    h_frame_ratio_catania.GetXaxis().SetTitleOffset(1.1)
    h_frame_ratio_catania.GetYaxis().SetTitleOffset(0.45)
    h_frame_ratio_catania.GetYaxis().SetDecimals(True)
    h_frame_ratio_catania.GetYaxis().CenterTitle(True)
    h_frame_ratio_catania.GetXaxis().SetTitleSize(0.12)
    h_frame_ratio_catania.GetYaxis().SetTitleSize(0.16)
    h_frame_ratio_catania.GetXaxis().SetLabelSize(0.12)
    h_frame_ratio_catania.GetYaxis().SetLabelSize(0.14)
    h_frame_ratio_catania.GetYaxis().SetNdivisions(505)

    h_catania_int = h_stat.Clone()
    h_catania_int.Reset()
    catania_step = 0.2
    for i in range(0, g_pred_catania.GetN()):
        h_catania_int.Fill(g_pred_catania.GetX()[i], g_pred_catania.GetY()[i] * catania_step / h_catania_int.GetBinWidth(h_catania_int.FindBin(g_pred_catania.GetX()[i])))
    h_catania_int.SetBinContent(h_catania_int.GetNbinsX()-1, 1.e-12)

    for i in range(1, h_catania_int.GetNbinsX()+1):
        err = 0
        for j in range(0, g_pred_catania.GetN()):
            if g_pred_catania.GetX()[j] >= h_catania_int.GetXaxis().GetBinLowEdge(i) and g_pred_catania.GetX()[j] < h_catania_int.GetXaxis().GetBinUpEdge(i):
                err += g_pred_catania.GetErrorYhigh(j)

        h_catania_int.SetBinError(i, catania_step * err / h_catania_int.GetBinWidth(i))
    h_catania_int.SetBinError(h_catania_int.GetNbinsX()-1, 0)

    # pad_cross_sec.cd()
    # h_catania_int.Draw('same e2')
    # pad_ratio_catania.cd()

    pt_bins = h_catania_int.GetXaxis().GetXbins()

    g_catania_unc = ROOT.TGraphAsymmErrors(h_catania_int.Clone('g_catania_unc'))
    for i in range(0, g_catania_unc.GetN()-1):
        g_catania_unc.SetPoint(i, g_catania_unc.GetX()[i], 1)
        g_catania_unc.SetPointError(i, g_catania_unc.GetErrorXlow(i), g_catania_unc.GetErrorXhigh(i), g_catania_unc.GetErrorYlow(i)/h_catania_int.GetBinContent(i+1), g_catania_unc.GetErrorYhigh(i)/h_catania_int.GetBinContent(i+1))

    g_catania_unc.SetMarkerSize(0)
    g_catania_unc.SetLineColorAlpha(colors[5], 1)
    g_catania_unc.SetLineWidth(0)
    g_catania_unc.SetFillStyle(1001)
    # g_catania_unc.SetLineStyle(9)
    g_catania_unc.SetFillColorAlpha(colors[5], 0.5)

    g_catania_unc.Draw("same 5")

    line_one_catania = ROOT.TLine(1, 1, 23.5, 1)
    line_one_catania.SetLineStyle(2)
    line_one_catania.SetLineColor(ROOT.kBlack)
    line_one_catania.Draw("same")

    h_ratio_data_catania_stat = h_stat.Clone('h_ratio_data_catania_stat')
    for i in range(1, h_ratio_data_catania_stat.GetNbinsX()):
        h_ratio_data_catania_stat.SetBinContent(i, h_stat.GetBinContent(i)/h_catania_int.GetBinContent(i))
        h_ratio_data_catania_stat.SetBinError(i, h_stat.GetBinError(i)/h_catania_int.GetBinContent(i))
        h_ratio_data_catania_stat.Draw('same p')

    g_ratio_data_catania_syst = g_syst.Clone('g_ratio_data_catania_syst')
    for i in range(0, g_ratio_data_catania_syst.GetN()-1):
        g_ratio_data_catania_syst.SetPoint(i, g_syst.GetX()[i], g_syst.GetY()[i]/h_catania_int.GetBinContent(i+1))
        g_ratio_data_catania_syst.SetPointError(i, g_syst.GetErrorX(i), g_syst.GetErrorY(i)/h_catania_int.GetBinContent(i+1))

    g_ratio_data_catania_syst.Draw('same 5') 

    pad_ratio_catania.RedrawAxis()

    pad_ratios.cd()

    pad_ratio_tamu = ROOT.TPad('pad_ratio_tamu', 'pad_ratio_tamu', 0, 0.6, 1, 0.8)
    pad_ratio_tamu.Draw()
    pad_ratio_tamu.cd()
    pad_ratio_tamu.SetBottomMargin(0)
    pad_ratio_tamu.SetLeftMargin(0.15)
    pad_ratio_tamu.SetTopMargin(0)
    h_frame_ratio_tamu = pad_ratio_tamu.DrawFrame(0, 0.2, 23.5,2.995, ';#it{p}_{T} (GeV/#it{c});#frac{Data}{TAMU}')
    h_frame_ratio_tamu.GetXaxis().SetTitleOffset(1.1)
    h_frame_ratio_tamu.GetYaxis().SetTitleOffset(0.45)
    h_frame_ratio_tamu.GetYaxis().SetDecimals(True)
    h_frame_ratio_tamu.GetYaxis().CenterTitle(True)
    h_frame_ratio_tamu.GetXaxis().SetTitleSize(0.12)
    h_frame_ratio_tamu.GetYaxis().SetTitleSize(0.16)
    h_frame_ratio_tamu.GetXaxis().SetLabelSize(0.12)
    h_frame_ratio_tamu.GetYaxis().SetLabelSize(0.14)
    h_frame_ratio_tamu.GetYaxis().SetNdivisions(505)

    h_tamu_int = h_stat.Clone()
    h_tamu_int.Reset()
    tamu_step = 0.2
    for i in range(0, g_pred_tamu.GetN()):
        h_tamu_int.Fill(g_pred_tamu.GetX()[i], g_pred_tamu.GetY()[i] * tamu_step / h_tamu_int.GetBinWidth(h_tamu_int.FindBin(g_pred_tamu.GetX()[i])))
    h_tamu_int.SetBinContent(h_tamu_int.GetNbinsX(), 1.e-12)

    for i in range(1, h_tamu_int.GetNbinsX()+1):
        h_tamu_int.SetBinError(i, 0)

    pt_bins = h_tamu_int.GetXaxis().GetXbins()
    h_tamu_unc = ROOT.TH1D('h_tamu_unc', 'h_tamu_unc', g_pred_tamu.GetN(), 0, 20.)
    for i in range(1, h_tamu_unc.GetNbinsX()+1):
        h_tamu_unc.SetBinContent(i, 1)
        h_tamu_unc.SetBinError(i, 0.)

    h_tamu_unc.SetMarkerSize(0)
    h_tamu_unc.SetLineColorAlpha(colors[3], 1)
    h_tamu_unc.SetLineWidth(3)
    h_tamu_unc.SetFillStyle(0)
    h_tamu_unc.SetLineStyle(9)
    h_tamu_unc.SetFillColorAlpha(colors[3], 0.5)

    line_one_tamu = ROOT.TLine(1, 1, 23.5, 1)
    line_one_tamu.SetLineStyle(2)
    line_one_tamu.SetLineColor(ROOT.kBlack)
    line_one_tamu.Draw("same")

    h_tamu_unc.Draw("same l")

    h_ratio_data_tamu_stat = h_stat.Clone('h_ratio_data_tamu_stat')
    h_ratio_data_tamu_stat.Divide(h_tamu_int)
    h_ratio_data_tamu_stat.Draw('same p')

    g_ratio_data_tamu_syst = g_syst.Clone('g_ratio_data_tamu_syst')
    for i in range(0, g_ratio_data_tamu_syst.GetN()):
        g_ratio_data_tamu_syst.SetPoint(i, g_syst.GetX()[i], g_syst.GetY()[i]/h_tamu_int.GetBinContent(i+1))
        g_ratio_data_tamu_syst.SetPointError(i, g_syst.GetErrorX(i), g_syst.GetErrorY(i)/h_tamu_int.GetBinContent(i+1))

    g_ratio_data_tamu_syst.Draw('same 5') 

    pad_ratio_tamu.RedrawAxis()

    pad_ratios.cd()

    pad_ratio_eposhq = ROOT.TPad('pad_ratio_eposhq', 'pad_ratio_eposhq', 0, 0.4, 1, 0.6)
    pad_ratio_eposhq.Draw()
    pad_ratio_eposhq.cd()
    pad_ratio_eposhq.SetBottomMargin(0)
    pad_ratio_eposhq.SetLeftMargin(0.15)
    pad_ratio_eposhq.SetTopMargin(0)
    h_frame_ratio_eposhq = pad_ratio_eposhq.DrawFrame(0, 0.2, 23.5,2.495, ';#it{p}_{T} (GeV/#it{c});#lower[0.09]{#frac{Data}{EPOS4HQ}}')
    h_frame_ratio_eposhq.GetXaxis().SetTitleOffset(1.1)
    h_frame_ratio_eposhq.GetYaxis().SetTitleOffset(0.45)
    h_frame_ratio_eposhq.GetYaxis().SetDecimals(True)
    h_frame_ratio_eposhq.GetYaxis().CenterTitle(True)
    h_frame_ratio_eposhq.GetXaxis().SetTitleSize(0.12)
    h_frame_ratio_eposhq.GetYaxis().SetTitleSize(0.16)
    h_frame_ratio_eposhq.GetXaxis().SetLabelSize(0.12)
    h_frame_ratio_eposhq.GetYaxis().SetLabelSize(0.14)
    h_frame_ratio_eposhq.GetYaxis().SetNdivisions(505)

    g_eposhq_unc = g_pred_epos.Clone('g_eposhq_unc')
    for i in range(0, g_eposhq_unc.GetN()):
        g_eposhq_unc.SetPoint(i, g_pred_epos.GetX()[i], 1)
        g_eposhq_unc.SetPointError(i, g_pred_epos.GetErrorXlow(i), g_pred_epos.GetErrorXhigh(i), g_pred_epos.GetErrorYlow(i)/g_pred_epos.GetY()[i], g_pred_epos.GetErrorYhigh(i)/g_pred_epos.GetY()[i])

    g_eposhq_unc.SetFillColorAlpha(ROOT.kGreen+2, 0.4)
    g_eposhq_unc.Draw("same 2")

    line_one_eposhq = ROOT.TLine(1, 1, 23.5, 1)
    line_one_eposhq.SetLineStyle(2)
    line_one_eposhq.SetLineColor(ROOT.kBlack)
    line_one_eposhq.Draw("same")

    # h_pred_epos = ROOT.TH1F('h_pred_epos', 'h_pred_epos', g_pred_epos.GetN(), np.asarray(g_pred_epos.GetX(), 'd'))
    # for i in range(1, g_pred_epos.GetN()+1):
    #     h_pred_epos.SetBinContent(i, g_pred_epos.GetY()[i-1])
    #     h_pred_epos.SetBinError(i, 1.e-10)

    h_ratio_data_eposhq_stat = h_stat.Clone('h_ratio_data_eposhq_stat')
    h_ratio_data_eposhq_stat.Divide(h_pred_epos)
    h_ratio_data_eposhq_stat.Draw('same p')

    g_ratio_data_eposhq_syst = g_syst.Clone('g_ratio_data_eposhq_syst')
    for i in range(0, g_ratio_data_eposhq_syst.GetN()):
        g_ratio_data_eposhq_syst.SetPoint(i, g_syst.GetX()[i], g_syst.GetY()[i]/g_pred_epos.GetY()[i])
        g_ratio_data_eposhq_syst.SetPointError(i, g_syst.GetErrorX(i), g_syst.GetErrorY(i)/g_pred_epos.GetY()[i])

    g_ratio_data_eposhq_syst.Draw('same 5') 

    pad_ratio_eposhq.RedrawAxis()

    pad_ratios.cd()

    pad_ratio_ampt_48 = ROOT.TPad('pad_ratio_ampt_48', 'pad_ratio_ampt_48', 0, 0.2, 1, 0.4)
    pad_ratio_ampt_48.Draw()
    pad_ratio_ampt_48.cd()
    pad_ratio_ampt_48.SetBottomMargin(0)
    pad_ratio_ampt_48.SetLeftMargin(0.15)
    pad_ratio_ampt_48.SetTopMargin(0)
    h_frame_ratio_ampt_48 = pad_ratio_ampt_48.DrawFrame(0, 0.2, 23.5,2.495, ';#it{p}_{T} (GeV/#it{c});#lower[0.09]{#frac{Data}{AMPT_{4.8}}}')
    h_frame_ratio_ampt_48.GetXaxis().SetTitleOffset(1.1)
    h_frame_ratio_ampt_48.GetYaxis().SetTitleOffset(0.45)
    h_frame_ratio_ampt_48.GetYaxis().SetDecimals(True)
    h_frame_ratio_ampt_48.GetYaxis().CenterTitle(True)
    h_frame_ratio_ampt_48.GetXaxis().SetTitleSize(0.12)
    h_frame_ratio_ampt_48.GetYaxis().SetTitleSize(0.16)
    h_frame_ratio_ampt_48.GetXaxis().SetLabelSize(0.12)
    h_frame_ratio_ampt_48.GetYaxis().SetLabelSize(0.14)
    h_frame_ratio_ampt_48.GetYaxis().SetNdivisions(505)

    h_pred_ampt_48_from_one = ROOT.TH1F('h_pred_ampt_48_from_one', 'h_pred_ampt_48_from_one', h_pred_ampt_48.GetNbinsX()-1, np.asarray(h_pred_ampt_48.GetXaxis().GetXbins(), 'd')[1:])
    for i in range(1, h_pred_ampt_48_from_one.GetNbinsX()+1):
        h_pred_ampt_48_from_one.SetBinContent(i, h_pred_ampt_48.GetBinContent(i+1))
        h_pred_ampt_48_from_one.SetBinError(i, h_pred_ampt_48.GetBinError(i+1))

    h_pred_ampt_48_from_one.SetLineColorAlpha(ROOT.kMagenta+2, 1)
    h_pred_ampt_48_from_one.SetLineWidth(3)
    h_pred_ampt_48_from_one.SetFillStyle(1001)
    h_pred_ampt_48_from_one.SetLineStyle(2)
    h_pred_ampt_48_from_one.SetFillColorAlpha(ROOT.kMagenta+2, 0.6)
    h_pred_ampt_48_from_one.SetMarkerSize(0)
    h_pred_ampt_48_from_one.SetMarkerColorAlpha(ROOT.kMagenta+2, 0.)
    g_pred_ampt_48_for_ratio = ROOT.TGraphAsymmErrors(h_pred_ampt_48_from_one)

    # pad_cross_sec.cd()
    # h_pred_ampt_48_from_one.SetFillStyle(1001)
    # h_pred_ampt_48_from_one.SetFillColor(ROOT.kBlack)
    # h_pred_ampt_48_from_one.Draw('same e2')
    # pad_ratio_ampt_48.cd()

    g_ampt_48_unc = g_pred_ampt_48_for_ratio.Clone('g_ampt_48_unc')
    for i in range(0, g_ampt_48_unc.GetN()):
        g_ampt_48_unc.SetPoint(i, g_pred_ampt_48_for_ratio.GetX()[i], 1)
        g_ampt_48_unc.SetPointError(i, g_pred_ampt_48_for_ratio.GetErrorXlow(i), g_pred_ampt_48_for_ratio.GetErrorXhigh(i), g_pred_ampt_48_for_ratio.GetErrorYlow(i)/g_pred_ampt_48_for_ratio.GetY()[i], g_pred_ampt_48_for_ratio.GetErrorYhigh(i)/g_pred_ampt_48_for_ratio.GetY()[i])

    g_ampt_48_unc.Draw("same 2")

    line_one_ampt_48 = ROOT.TLine(1, 1, 23.5, 1)
    line_one_ampt_48.SetLineStyle(2)
    line_one_ampt_48.SetLineColor(ROOT.kBlack)
    line_one_ampt_48.Draw("same")

    h_ratio_data_ampt_48_stat = ROOT.TH1F('h_stat_no_last', 'h_stat_no_last', h_stat.GetNbinsX()-1, np.asarray(h_stat.GetXaxis().GetXbins(), 'd')[:-1])
    for i in range(1, h_ratio_data_ampt_48_stat.GetNbinsX()+1):
        h_ratio_data_ampt_48_stat.SetBinContent(i, h_stat.GetBinContent(i))
        h_ratio_data_ampt_48_stat.SetBinError(i, h_stat.GetBinError(i))
    h_ratio_data_ampt_48_stat.Divide(h_pred_ampt_48_from_one)
    h_ratio_data_ampt_48_stat.Draw('same p')

    h_ratio_data_ampt_48_stat.SetMarkerStyle(ROOT.kFullCircle)
    h_ratio_data_ampt_48_stat.SetMarkerSize(1.5)
    h_ratio_data_ampt_48_stat.SetMarkerColor(ROOT.kBlack)
    h_ratio_data_ampt_48_stat.SetLineColor(ROOT.kBlack)
    h_ratio_data_ampt_48_stat.SetLineWidth(2)

    g_ratio_data_ampt_48_syst = g_syst.Clone('g_ratio_data_ampt_48_syst')
    for i in range(0, g_ratio_data_ampt_48_syst.GetN()-1):
        g_ratio_data_ampt_48_syst.SetPoint(i, g_syst.GetX()[i], g_syst.GetY()[i]/g_pred_ampt_48_for_ratio.GetY()[i])
        g_ratio_data_ampt_48_syst.SetPointError(i, g_syst.GetErrorX(i), g_syst.GetErrorY(i)/g_pred_ampt_48_for_ratio.GetY()[i])

    g_ratio_data_ampt_48_syst.Draw('same 5') 

    pad_ratio_ampt_48.RedrawAxis()
    pad_ratios.cd()

    pad_ratio_ampt_66 = ROOT.TPad('pad_ratio_ampt_66', 'pad_ratio_ampt_66', 0, 0., 1, 0.2)
    pad_ratio_ampt_66.Draw()
    pad_ratio_ampt_66.cd()
    pad_ratio_ampt_66.SetBottomMargin(0)
    pad_ratio_ampt_66.SetLeftMargin(0.15)
    pad_ratio_ampt_66.SetTopMargin(0)
    h_frame_ratio_ampt_66 = pad_ratio_ampt_66.DrawFrame(0, 0.2, 23.5,2.495, ';#it{p}_{T} (GeV/#it{c});#lower[0.09]{#frac{Data}{AMPT_{6.6}}}')
    h_frame_ratio_ampt_66.GetXaxis().SetTitleOffset(1.1)
    h_frame_ratio_ampt_66.GetYaxis().SetTitleOffset(0.45)
    h_frame_ratio_ampt_66.GetYaxis().SetDecimals(True)
    h_frame_ratio_ampt_66.GetYaxis().CenterTitle(True)
    h_frame_ratio_ampt_66.GetXaxis().SetTitleSize(0.12)
    h_frame_ratio_ampt_66.GetYaxis().SetTitleSize(0.16)
    h_frame_ratio_ampt_66.GetXaxis().SetLabelSize(0.12)
    h_frame_ratio_ampt_66.GetYaxis().SetLabelSize(0.14)
    h_frame_ratio_ampt_66.GetYaxis().SetNdivisions(505)

    h_pred_ampt_66_from_one = ROOT.TH1F('h_pred_ampt_66_from_one', 'h_pred_ampt_66_from_one', h_pred_ampt_66.GetNbinsX()-1, np.asarray(h_pred_ampt_66.GetXaxis().GetXbins(), 'd')[1:])
    for i in range(1, h_pred_ampt_66_from_one.GetNbinsX()+1):
        h_pred_ampt_66_from_one.SetBinContent(i, h_pred_ampt_66.GetBinContent(i+1))
        h_pred_ampt_66_from_one.SetBinError(i, h_pred_ampt_66.GetBinError(i+1))

    h_pred_ampt_66_from_one.SetLineColorAlpha(ROOT.kBlue+3, 1)
    h_pred_ampt_66_from_one.SetLineWidth(3)
    h_pred_ampt_66_from_one.SetFillStyle(1001)
    h_pred_ampt_66_from_one.SetLineStyle(3)
    h_pred_ampt_66_from_one.SetFillColorAlpha(ROOT.kBlue+3, 0.6)
    h_pred_ampt_66_from_one.SetMarkerSize(0)
    h_pred_ampt_66_from_one.SetMarkerColorAlpha(ROOT.kBlue+3, 0.)
    g_pred_ampt_66_for_ratio = ROOT.TGraphAsymmErrors(h_pred_ampt_66_from_one)

    # pad_cross_sec.cd()
    # h_pred_ampt_66_from_one.SetFillStyle(1001)
    # h_pred_ampt_66_from_one.SetFillColor(ROOT.kBlack)
    # h_pred_ampt_66_from_one.Draw('same e2')
    # pad_ratio_ampt_66.cd()

    g_ampt_66_unc = g_pred_ampt_66_for_ratio.Clone('g_ampt_66_unc')
    for i in range(0, g_ampt_66_unc.GetN()):
        g_ampt_66_unc.SetPoint(i, g_pred_ampt_66_for_ratio.GetX()[i], 1)
        g_ampt_66_unc.SetPointError(i, g_pred_ampt_66_for_ratio.GetErrorXlow(i), g_pred_ampt_66_for_ratio.GetErrorXhigh(i), g_pred_ampt_66_for_ratio.GetErrorYlow(i)/g_pred_ampt_66_for_ratio.GetY()[i], g_pred_ampt_66_for_ratio.GetErrorYhigh(i)/g_pred_ampt_66_for_ratio.GetY()[i])

    g_ampt_66_unc.Draw("same 2")

    line_one_ampt_66 = ROOT.TLine(1, 1, 23.5, 1)
    line_one_ampt_66.SetLineStyle(2)
    line_one_ampt_66.SetLineColor(ROOT.kBlack)
    line_one_ampt_66.Draw("same")

    h_ratio_data_ampt_66_stat = ROOT.TH1F('h_stat_no_last', 'h_stat_no_last', h_stat.GetNbinsX()-1, np.asarray(h_stat.GetXaxis().GetXbins(), 'd')[:-1])
    for i in range(1, h_ratio_data_ampt_66_stat.GetNbinsX()+1):
        h_ratio_data_ampt_66_stat.SetBinContent(i, h_stat.GetBinContent(i))
        h_ratio_data_ampt_66_stat.SetBinError(i, h_stat.GetBinError(i))
    h_ratio_data_ampt_66_stat.Divide(h_pred_ampt_66_from_one)
    h_ratio_data_ampt_66_stat.Draw('same p')

    h_ratio_data_ampt_66_stat.SetMarkerStyle(ROOT.kFullCircle)
    h_ratio_data_ampt_66_stat.SetMarkerSize(1.5)
    h_ratio_data_ampt_66_stat.SetMarkerColor(ROOT.kBlack)
    h_ratio_data_ampt_66_stat.SetLineColor(ROOT.kBlack)
    h_ratio_data_ampt_66_stat.SetLineWidth(2)

    g_ratio_data_ampt_66_syst = g_syst.Clone('g_ratio_data_ampt_66_syst')
    for i in range(0, g_ratio_data_ampt_66_syst.GetN()-1):
        g_ratio_data_ampt_66_syst.SetPoint(i, g_syst.GetX()[i], g_syst.GetY()[i]/g_pred_ampt_66_for_ratio.GetY()[i])
        g_ratio_data_ampt_66_syst.SetPointError(i, g_syst.GetErrorX(i), g_syst.GetErrorY(i)/g_pred_ampt_66_for_ratio.GetY()[i])

    g_ratio_data_ampt_66_syst.Draw('same 5') 

    pad_ratio_ampt_66.RedrawAxis()

    c.SaveAs('figures/cross_section/cross_section_vs_pheno_TT_dk_mc_fix_evsel.pdf')
