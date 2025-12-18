import ROOT 
import numpy as np
import seaborn as sns
import sys
sys.path.append('utils')
from analysis_utils import get_n_events_from_zorro, rebin_tgraph_asymm_errors
from style_formatter import root_colors_from_matplotlib_colormap

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadLeftMargin(0.11)
ROOT.gStyle.SetPadBottomMargin(0.1)
ROOT.gStyle.SetPadTopMargin(0.05)
ROOT.gStyle.SetPadRightMargin(0.05)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.TH1.AddDirectory(0)

if __name__ == '__main__':

    pt_bins = [2., 4., 6., 8., 16]
    min_pt_canvas = 0.3 # for logx scale

    # Get cross section
    data_file = ROOT.TFile.Open('/home/fchinu/Run3/B0_pp/systematics/cross_section_default_DK_MC_enlarged_templates_fix_evsel_pt_cuts_w_syst_fabio_fix_TT_vs_phi.root')
    h_stat = data_file.Get('h_stat')
    h_syst = data_file.Get('h_syst')
    g_syst = ROOT.TGraphErrors(h_syst)
    data_file.Close()

    h_stat.Scale(1.e-6) # convert to µb
    g_syst.Scale(1.e-6) # convert to µb

    # Get CMS results
    cms_file = ROOT.TFile.Open('cms/cms_bplus_13_tev_table_2.root')
    g_stat_cms_1p45 = ROOT.TGraphAsymmErrors()
    g_stat_cms_2p1 = ROOT.TGraphAsymmErrors()
    g_syst_cms_1p45 = ROOT.TGraphAsymmErrors()
    g_syst_cms_2p1 = ROOT.TGraphAsymmErrors()

    g_stat_cms = cms_file.Get('g_stat')
    g_syst_cms = cms_file.Get('g_syst')
    for i in range(g_stat_cms.GetN()):
        if g_stat_cms.GetPointX(i) < 17:
            g_stat_cms_1p45.SetPoint(i, g_stat_cms.GetPointX(i), g_stat_cms.GetPointY(i))
            g_stat_cms_1p45.SetPointError(i, g_stat_cms.GetErrorXlow(i), g_stat_cms.GetErrorXhigh(i), g_stat_cms.GetErrorYlow(i), g_stat_cms.GetErrorYhigh(i))
            g_syst_cms_1p45.SetPoint(i, g_syst_cms.GetPointX(i), g_syst_cms.GetPointY(i))
            g_syst_cms_1p45.SetPointError(i, g_syst_cms.GetErrorXlow(i)/2, g_syst_cms.GetErrorXhigh(i)/2, g_syst_cms.GetErrorYlow(i), g_syst_cms.GetErrorYhigh(i))
        else:
            g_stat_cms_2p1.SetPoint(i-2, g_stat_cms.GetPointX(i), g_stat_cms.GetPointY(i))
            g_stat_cms_2p1.SetPointError(i-2, g_stat_cms.GetErrorXlow(i), g_stat_cms.GetErrorXhigh(i), g_stat_cms.GetErrorYlow(i), g_stat_cms.GetErrorYhigh(i))
            g_syst_cms_2p1.SetPoint(i-2, g_syst_cms.GetPointX(i), g_syst_cms.GetPointY(i))
            g_syst_cms_2p1.SetPointError(i-2, g_syst_cms.GetErrorXlow(i)/2, g_syst_cms.GetErrorXhigh(i)/2, g_syst_cms.GetErrorYlow(i), g_syst_cms.GetErrorYhigh(i))
    cms_file.Close()

    g_stat_cms_1p45.Scale(1./2.9) # divide by rapidity range
    g_stat_cms_2p1.Scale(1./4.2) # divide by rapidity range

    g_syst_cms_1p45.Scale(1./2.9) # divide by rapidity range
    g_syst_cms_2p1.Scale(1./4.2) # divide by rapidity range

    g_stat_cms_1p45.Print()

    # Get LHCb results
    lhcb_file = ROOT.TFile.Open('lhcb/HEPData-ins1630633-v1-root.root')
    h_central_lhcb, h_stat_err_lhcb, h_syst_err_lhcb, h_stat_lhcb, h_syst_lhcb = [], [], [], [], []
    for iy in range(5):
        h_central_lhcb.append(lhcb_file.Get(f'Table 2/Hist1D_y{iy+1}'))
        h_stat_err_lhcb.append(lhcb_file.Get(f'Table 2/Hist1D_y{iy+1}_e1'))
        h_syst_err_lhcb.append(lhcb_file.Get(f'Table 2/Hist1D_y{iy+1}_e2'))
        pt_bins = np.asarray(h_central_lhcb[-1].GetXaxis().GetXbins(), 'd')
        pt_bins[0] = min_pt_canvas
        h_stat_lhcb.append(ROOT.TH1D(f'h_stat_lhcb_y{2 + iy * 0.5:.2f}', f'h_stat_lhcb_y{2 + iy * 0.5:.2f}', len(pt_bins)-1, pt_bins))
        h_syst_lhcb.append(ROOT.TH1D(f'h_syst_lhcb_y{2 + iy * 0.5:.2f}', f'h_syst_lhcb_y{2 + iy * 0.5:.2f}', len(pt_bins)-1, pt_bins))
        for i in range(1, h_central_lhcb[-1].GetNbinsX()+1):
            h_stat_lhcb[-1].SetBinContent(i, h_central_lhcb[-1].GetBinContent(i))
            h_stat_lhcb[-1].SetBinError(i, h_stat_err_lhcb[-1].GetBinContent(i))
            h_syst_lhcb[-1].SetBinContent(i, h_central_lhcb[-1].GetBinContent(i))
            h_syst_lhcb[-1].SetBinError(i, h_syst_err_lhcb[-1].GetBinContent(i))
        h_stat_lhcb[-1].Scale(0.5) # particle/antiparticle
        h_stat_lhcb[-1].Scale(1.e-3) # convert to µb
        h_stat_lhcb[-1].Scale(2**(-2*iy-2)) # drawing
        h_syst_lhcb[-1].Scale(0.5) # particle/antiparticle
        h_syst_lhcb[-1].Scale(1.e-3) # convert to µb
        h_syst_lhcb[-1].Scale(2**(-2*iy-2)) # drawing
    lhcb_file.Close()

    # Get predictions
    fonll_file = ROOT.TFile.Open('fonll/fonll_bhadron_nnpdfs_13dot6tev.root')
    g_pred_fonll_alice = fonll_file.Get('gBhadrNNPDF30')
    fonll_file.Close()

    g_pred_fonll_alice.Scale(1.e-6) # convert to µb

    pt_bins_fonll = np.append(np.asarray(g_pred_fonll_alice.GetX(), 'd') - np.asarray(g_pred_fonll_alice.GetEXlow(), 'd'), g_pred_fonll_alice.GetX()[g_pred_fonll_alice.GetN()-1] + g_pred_fonll_alice.GetEXhigh()[g_pred_fonll_alice.GetN()-1])

    h_pred_fonll_alice = ROOT.TH1F('h_pred_fonll', 'h_pred_fonll', g_pred_fonll_alice.GetN(), pt_bins_fonll)
    for i in range(1, g_pred_fonll_alice.GetN()+1):
        h_pred_fonll_alice.SetBinContent(i, g_pred_fonll_alice.GetY()[i-1])
        h_pred_fonll_alice.SetBinError(i, 1.e-12)

    # Get predictions
    fonll_file = ROOT.TFile.Open('fonll/fonll_bhadron_nnpdfs_13tev_y1p45.root')
    g_pred_fonll_cms_1p45 = fonll_file.Get('gBhadrNNPDF30')
    fonll_file.Close()

    g_pred_fonll_cms_1p45.Scale(1.e-6) # convert to µb
    g_pred_fonll_cms_1p45.Scale(1./2.9) # divide by rapidity range

    pt_bins_fonll = np.append(np.asarray(g_pred_fonll_cms_1p45.GetX(), 'd') - np.asarray(g_pred_fonll_cms_1p45.GetEXlow(), 'd'), g_pred_fonll_cms_1p45.GetX()[g_pred_fonll_cms_1p45.GetN()-1] + g_pred_fonll_cms_1p45.GetEXhigh()[g_pred_fonll_cms_1p45.GetN()-1])

    h_pred_fonll_cms_1p45 = ROOT.TH1F('h_pred_fonll', 'h_pred_fonll', g_pred_fonll_cms_1p45.GetN(), pt_bins_fonll)
    for i in range(1, g_pred_fonll_cms_1p45.GetN()+1):
        h_pred_fonll_cms_1p45.SetBinContent(i, g_pred_fonll_cms_1p45.GetY()[i-1])
        h_pred_fonll_cms_1p45.SetBinError(i, 1.e-12)

    # Get predictions
    fonll_file = ROOT.TFile.Open('fonll/fonll_bhadron_nnpdfs_13tev_y2p1.root')
    g_pred_fonll_cms_2p1 = fonll_file.Get('gBhadrNNPDF30')
    fonll_file.Close()

    g_pred_fonll_cms_2p1.Scale(1.e-6) # convert to µb
    g_pred_fonll_cms_2p1.Scale(1./4.2) # divide by rapidity range

    pt_bins_fonll = np.append(np.asarray(g_pred_fonll_cms_2p1.GetX(), 'd') - np.asarray(g_pred_fonll_cms_2p1.GetEXlow(), 'd'), g_pred_fonll_cms_2p1.GetX()[g_pred_fonll_cms_2p1.GetN()-1] + g_pred_fonll_cms_2p1.GetEXhigh()[g_pred_fonll_cms_2p1.GetN()-1])

    h_pred_fonll_cms_2p1 = ROOT.TH1F('h_pred_fonll', 'h_pred_fonll', g_pred_fonll_cms_2p1.GetN(), pt_bins_fonll)
    for i in range(1, g_pred_fonll_cms_2p1.GetN()+1):
        h_pred_fonll_cms_2p1.SetBinContent(i, g_pred_fonll_cms_2p1.GetY()[i-1])
        h_pred_fonll_cms_2p1.SetBinError(i, 1.e-12)

    # Get predictions
    rap_lhcb = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
    h_pred_fonll_lhcb = []
    g_pred_fonll_lhcb = []
    for iy in range(5):
        fonll_file = ROOT.TFile.Open(f'fonll/fonll_bhadron_finebins_nnpdfs_y{rap_lhcb[iy]*10:.0f}_{rap_lhcb[iy+1]*10:.0f}_13tev.root')
        g_pred_fonll_lhcb.append(fonll_file.Get(f'gfonll_bhadron_finebins_nnpdfs_y{rap_lhcb[iy]*10:.0f}_{rap_lhcb[iy+1]*10:.0f}_13tev'))
        fonll_file.Close()

        pt_bins_fonll = np.append(np.asarray(g_pred_fonll_lhcb[-1].GetX(), 'd') - np.asarray(g_pred_fonll_lhcb[-1].GetEXlow(), 'd'), g_pred_fonll_lhcb[-1].GetX()[g_pred_fonll_lhcb[-1].GetN()-1] + g_pred_fonll_lhcb[-1].GetEXhigh()[g_pred_fonll_lhcb[-1].GetN()-1])
        pt_bins_fonll[0] = min_pt_canvas
        g_pred_fonll_lhcb[-1].SetPoint(0, (pt_bins_fonll[1] - min_pt_canvas)/2 + min_pt_canvas, g_pred_fonll_lhcb[-1].GetY()[0]) # set first point to min pt of canvas
        g_pred_fonll_lhcb[-1].SetPointError(0, (pt_bins_fonll[1] - min_pt_canvas)/2, (pt_bins_fonll[1] - min_pt_canvas)/2, g_pred_fonll_lhcb[-1].GetEYlow()[0], g_pred_fonll_lhcb[-1].GetEYhigh()[0])
        g_pred_fonll_lhcb[-1].Scale(1.e-6)
        g_pred_fonll_lhcb[-1].Scale(2) # divide by rapidity range
        h_pred_fonll_lhcb.append(ROOT.TH1F(f'h_pred_fonll_y{rap_lhcb[iy]*10:.0f}_{rap_lhcb[iy+1]*10:.0f}', f'h_pred_fonll_y{rap_lhcb[iy]*10:.0f}_{rap_lhcb[iy+1]*10:.0f}', g_pred_fonll_lhcb[-1].GetN(), pt_bins_fonll))
        for i in range(1, g_pred_fonll_lhcb[-1].GetN()+1):
            h_pred_fonll_lhcb[-1].SetBinContent(i, g_pred_fonll_lhcb[-1].GetY()[i-1])
            h_pred_fonll_lhcb[-1].SetBinError(i, 1.e-12)
        h_pred_fonll_lhcb[-1].Scale(2**(-2*iy-2)) # drawing
        g_pred_fonll_lhcb[-1].Scale(2**(-2*iy-2)) # drawing

    # Set the style
    colors, _ = root_colors_from_matplotlib_colormap('tab10')
    h_stat.SetMarkerStyle(ROOT.kFullCircle)
    h_stat.SetMarkerSize(1.2)
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

    cmap = sns.color_palette("crest", as_cmap=True)
    # Sample n_colors evenly spaced values between 0 and 1
    colors_lhcb = [cmap(i) for i in np.linspace(0, 1, 10)]

    root_color_indices = []
    root_colors = []
    for color in colors_lhcb:
        idx = ROOT.TColor.GetFreeColorIndex()
        # color is RGBA, take only RGB
        root_colors.append(ROOT.TColor(idx, color[0], color[1], color[2], f"color{idx}"))
        root_color_indices.append(idx)

    g_stat_cms_1p45.SetMarkerStyle(ROOT.kOpenDiamond)
    g_stat_cms_1p45.SetMarkerSize(1.5)
    g_stat_cms_1p45.SetMarkerColor(root_color_indices[1])
    g_stat_cms_1p45.SetLineColor(root_color_indices[1])
    g_stat_cms_1p45.SetLineWidth(2)

    g_syst_cms_1p45.SetMarkerStyle(ROOT.kOpenDiamond)
    g_syst_cms_1p45.SetMarkerSize(1.5)
    g_syst_cms_1p45.SetMarkerColor(root_color_indices[1])
    g_syst_cms_1p45.SetLineColor(root_color_indices[1])
    g_syst_cms_1p45.SetLineWidth(2)
    g_syst_cms_1p45.SetFillStyle(0)

    g_stat_cms_2p1.SetMarkerStyle(ROOT.kFullDiamond)
    g_stat_cms_2p1.SetMarkerSize(1.5)
    g_stat_cms_2p1.SetMarkerColor(root_color_indices[1])
    g_stat_cms_2p1.SetLineColor(root_color_indices[1])
    g_stat_cms_2p1.SetLineWidth(2)

    g_syst_cms_2p1.SetMarkerStyle(ROOT.kFullDiamond)
    g_syst_cms_2p1.SetMarkerSize(1.5)
    g_syst_cms_2p1.SetMarkerColor(root_color_indices[1])
    g_syst_cms_2p1.SetLineColor(root_color_indices[1])
    g_syst_cms_2p1.SetLineWidth(2)
    g_syst_cms_2p1.SetFillStyle(0)

    color_fonll_alice = cmap(0.5)
    idx = ROOT.TColor.GetFreeColorIndex()
    root_color_fonll_alice = ROOT.TColor(idx, 39/255, 150/255, 179/255, "color_fonll_alice")
    g_pred_fonll_alice.SetLineColorAlpha(idx, 0.5)
    g_pred_fonll_alice.SetLineWidth(2)
    g_pred_fonll_alice.SetFillStyle(1001)
    g_pred_fonll_alice.SetFillColorAlpha(idx, 0.5)

    h_pred_fonll_alice.SetLineColorAlpha(idx, 0.5)
    h_pred_fonll_alice.SetLineWidth(2)
    h_pred_fonll_alice.SetMarkerColorAlpha(idx, 0.5)

    g_pred_fonll_cms_1p45.SetLineColorAlpha(root_color_indices[2], 0.5)
    g_pred_fonll_cms_1p45.SetLineWidth(2)
    g_pred_fonll_cms_1p45.SetFillStyle(1001)
    g_pred_fonll_cms_1p45.SetFillColorAlpha(root_color_indices[2], 0.5)

    h_pred_fonll_cms_1p45.SetLineColorAlpha(root_color_indices[2], 0.5)
    h_pred_fonll_cms_1p45.SetLineWidth(2)
    h_pred_fonll_cms_1p45.SetMarkerColorAlpha(root_color_indices[2], 0.5)

    g_pred_fonll_cms_2p1.SetLineColorAlpha(root_color_indices[2], 0.5)
    g_pred_fonll_cms_2p1.SetLineWidth(2)
    g_pred_fonll_cms_2p1.SetFillStyle(1001)
    g_pred_fonll_cms_2p1.SetFillColorAlpha(root_color_indices[2], 0.5)

    h_pred_fonll_cms_2p1.SetLineColorAlpha(root_color_indices[2], 0.5)
    h_pred_fonll_cms_2p1.SetLineWidth(2)
    h_pred_fonll_cms_2p1.SetMarkerColorAlpha(root_color_indices[2], 0.5)

    markers_lhcb = [ROOT.kFullDoubleDiamond, ROOT.kOpenCircle, ROOT.kFullCross, ROOT.kFullSquare, ROOT.kFullCrossX]

    for i, (histo_stat, histo_syst) in enumerate(zip(h_stat_lhcb, h_syst_lhcb)):
        histo_stat.SetMarkerStyle(markers_lhcb[i])
        histo_stat.SetMarkerSize(1.2)
        histo_stat.SetMarkerColor(root_color_indices[i+5])
        histo_stat.SetLineColor(root_color_indices[i+5])
        histo_stat.SetLineWidth(2)

        histo_syst.SetMarkerStyle(markers_lhcb[i])
        histo_syst.SetMarkerSize(1.2)
        if i == 0 or i == 4:
            histo_syst.SetMarkerSize(1.5)
        elif i == 3:
            histo_syst.SetMarkerSize(1.)
        histo_syst.SetMarkerColor(root_color_indices[i+5])
        histo_syst.SetLineColor(root_color_indices[i+5])
        histo_syst.SetLineWidth(2)
        histo_syst.SetFillStyle(0)
    
    for histo in h_pred_fonll_lhcb:
        histo.SetLineColorAlpha(root_color_indices[h_pred_fonll_lhcb.index(histo)+2], 0.5)
        histo.SetLineWidth(2)
        histo.SetMarkerColorAlpha(root_color_indices[h_pred_fonll_lhcb.index(histo)+2], 0.5)

    for graph in g_pred_fonll_lhcb:
        graph.SetLineColorAlpha(root_color_indices[g_pred_fonll_lhcb.index(graph)+2], 0.5)
        graph.SetLineWidth(2)
        graph.SetFillStyle(1001)
        graph.SetFillColorAlpha(root_color_indices[g_pred_fonll_lhcb.index(graph)+2], 0.5)

    # Draw
    c = ROOT.TCanvas('c', 'c', 600, 600)
    c.SetLogy()
    c.SetLogx()
    h_frame = c.DrawFrame(3.e-1, 5e-9, 100, 1.e2, ';#it{p}_{T} (GeV/#it{c});d^{2}#it{#sigma}/d#it{p}_{T}d#it{y} (#mub GeV^{#minus1}#kern[0.25]{#it{c}}) ')
    h_frame.GetXaxis().SetLabelOffset(0.)
    h_frame.GetXaxis().SetTitleOffset(1.1)
    h_frame.GetYaxis().SetTitleOffset(1.3)
    h_frame.GetXaxis().SetTitleSize(0.04)
    h_frame.GetYaxis().SetTitleSize(0.04)
    h_frame.GetXaxis().SetLabelSize(0.03)
    h_frame.GetYaxis().SetLabelSize(0.03)

    g_pred_fonll_cms_2p1.Draw('same 2')
    h_pred_fonll_cms_2p1.Draw('same e')
    g_pred_fonll_alice.Draw('same 2')
    h_pred_fonll_alice.Draw('same e')
    g_pred_fonll_cms_1p45.Draw('same 2')
    h_pred_fonll_cms_1p45.Draw('same e')
    g_stat_cms_1p45.Draw('same pZ')
    g_stat_cms_2p1.Draw('same pZ')
    g_syst_cms_1p45.Draw('same 5')
    g_syst_cms_2p1.Draw('same 5')
    for graph, histo in zip(g_pred_fonll_lhcb, h_pred_fonll_lhcb):
        graph.Draw('same 2')
        histo.Draw('same e')
    for histo_stat, histo_syst in zip(h_stat_lhcb, h_syst_lhcb):
        histo_stat.Draw('same')
        histo_syst.Draw('same E2')
    g_stat_cms_1p45.Draw('same pZ')
    g_stat_cms_2p1.Draw('same pZ')
    h_stat.Draw('same p')
    g_syst.Draw('same 5')

    # Legend
    leg_alice = ROOT.TLegend(0.78, 0.83, 0.9, 0.93)
    leg_alice.SetBorderSize(0)
    leg_alice.SetFillStyle(0)
    leg_alice.SetTextSize(0.035)
    leg_alice.SetTextAlign(32)
    leg_alice.SetMargin(-0.65)
    leg_alice.SetHeader('ALICE, B^{0},#kern[0.1]{#sqrt{#it{s}} = 13.6 TeV}')
    leg_alice.AddEntry(h_stat, '  |#it{y}| < 0.5', 'lp')
    leg_alice.Draw()

    leg_cms = ROOT.TLegend(0.55, 0.13, 0.65, 0.255)
    leg_cms.SetBorderSize(0)
    leg_cms.SetFillStyle(0)
    leg_cms.SetTextSize(0.035)
    leg_cms.SetMargin(0.7)
    leg_cms.SetHeader('CMS, B^{+},#kern[0.1]{#sqrt{#it{s}} = 13 TeV}')
    leg_cms.AddEntry(g_stat_cms_1p45, '|#it{y}| < 1.45', 'lp')
    leg_cms.AddEntry(g_stat_cms_2p1, '|#it{y}| < 2.1', 'lp')
    leg_cms.Draw()

    leg_lhcb = ROOT.TLegend(0.13, 0.13, 0.23, 0.38)
    leg_lhcb.SetBorderSize(0)
    leg_lhcb.SetFillStyle(0)
    leg_lhcb.SetTextSize(0.035)
    leg_lhcb.SetMargin(0.7)
    leg_lhcb.SetHeader('LHCb, B^{+},#kern[0.1]{#sqrt{#it{s}} = 13 TeV}')
    for iy in range(5):
        leg_lhcb.AddEntry(h_stat_lhcb[iy], f"{rap_lhcb[iy]:.1f} <#kern[1.]{{#it{{y}}}} < {rap_lhcb[iy+1]:.1f} (#times 2^{{#minus{2+2*iy}}})", 'lp')
    leg_lhcb.Draw()


    hist_leg_fonll = ROOT.TH1F('hist_leg_fonll', 'hist_leg_fonll', 1, 0, 1)
    hist_leg_fonll.SetLineColor(ROOT.kGray+2)
    hist_leg_fonll.SetFillColor(ROOT.kGray)

    leg_fonll = ROOT.TLegend(0.78, 0.78, 0.9, 0.83)
    leg_fonll.SetBorderSize(0)
    leg_fonll.SetFillStyle(0)
    leg_fonll.SetTextSize(0.035)
    leg_fonll.SetTextAlign(32)
    leg_fonll.SetMargin(-0.65)
    leg_fonll.AddEntry(hist_leg_fonll, 'FONLL', 'lf')
    leg_fonll.Draw()

    # Add the text

    text_ALICE = ROOT.TLatex(0.15, 0.89, 'ALICE')
    text_ALICE.SetNDC()
    text_ALICE.SetTextSize(0.05)
    text_ALICE.SetTextFont(42)
    text_ALICE.Draw()

    text_pp = ROOT.TLatex(0.15, 0.85, 'pp collisions')
    text_pp.SetNDC()
    text_pp.SetTextSize(0.04)
    text_pp.SetTextFont(42)
    text_pp.Draw()


    ROOT.gPad.RedrawAxis()


    c.SaveAs('figures/cross_section/cross_section_vs_CMS_LHCb_DK_MC_fix_evsel.pdf')
