import argparse

import pandas as pd 
import numpy as np
import ROOT 

def convert_to_root(output_file):
    pt_mins = [1, 2, 4, 6, 8, 10, 14]
    pt_maxs = [2, 4, 6, 8, 10, 14, 23.5]
    pt_bins = list(pt_mins) + [pt_maxs[-1]]

    # pT differential cross section
    input_file = "ALICE_histogram.dat"
    df = pd.read_csv(input_file, delimiter=r"\s+", comment='#', names=['central', 'err_low', 'err_high'])
    df['ptmin'] = pt_mins
    df['ptmax'] = pt_maxs

    h_cross_sec = ROOT.TH1F('h_cross_sec', 'h_cross_sec', len(pt_bins)-1, np.asarray(pt_bins, "d"))
    for i in range(1, len(pt_bins)):
        h_cross_sec.SetBinContent(i, df['central'].values[i-1])
        h_cross_sec.SetBinError(i, 0)
    
    g_cross_sec = ROOT.TGraphAsymmErrors(h_cross_sec)
    for i in range(1, len(pt_bins)):
        g_cross_sec.SetPointEYlow(i-1, -df['err_low'].values[i-1]) # they gave us low
        g_cross_sec.SetPointEYhigh(i-1, df['err_high'].values[i-1]) 

    # mid/fwd ratio
    rap_mins = [2, 3, 4]
    rap_maxs = [2.5, 3.5, 4.5]
    h_rap_ratios = []
    g_rap_ratios = []
    for rap_min, rap_max in zip(rap_mins, rap_maxs):
        input_file = f"ALICE_LHCb_ratio_{rap_min}-{rap_max:.1f}.dat"
        df = pd.read_csv(input_file, delimiter=r"\s+", comment='#', names=['central', 'err_low', 'err_high'])
        df['ptmin'] = pt_mins
        df['ptmax'] = pt_maxs

        h_rap_ratios.append(ROOT.TH1F(f'h_rap_ratio_{rap_min}_{rap_max:.1f}', f'h_rap_ratio_{rap_min}_{rap_max:.1f}', len(pt_bins)-1, np.asarray(pt_bins, "d")))
        for i in range(1, len(pt_bins)):
            h_rap_ratios[-1].SetBinContent(i, df['central'].values[i-1])
            h_rap_ratios[-1].SetBinError(i, 0)

        g_rap_ratios.append(ROOT.TGraphAsymmErrors(h_rap_ratios[-1]))
        for i in range(1, len(pt_bins)):
            g_rap_ratios[-1].SetPointEYlow(i-1, -df['err_low'].values[i-1]) # they gave us low
            g_rap_ratios[-1].SetPointEYhigh(i-1, df['err_high'].values[i-1]) 

    # extrapolation
    input_file = "ALICE_extrapolation.dat"
    df = pd.read_csv(input_file, delimiter=r"\s+", comment='#', names=['central', 'err_low', 'err_high'])

    h_extrap = ROOT.TH1F('h_extrap', 'h_extrap', 1, 0, 1)

    h_extrap.SetBinContent(1, df['central'].values[0])
    h_extrap.SetBinError(1, 0)

    g_extrap = ROOT.TGraphAsymmErrors(h_extrap)
    g_extrap.SetPointEYlow(0, -df['err_low'].values[0]) # they gave us low
    g_extrap.SetPointEYhigh(0, df['err_high'].values[0]) 


    output_file = ROOT.TFile(output_file, 'RECREATE')
    h_cross_sec.Write("h_cross_sec")
    g_cross_sec.Write("g_cross_sec")
    for i, (rap_min, rap_max) in enumerate(zip(rap_mins, rap_maxs)):
        h_rap_ratios[i].Write(f"h_rap_ratio_{rap_min}_{rap_max:.1f}")
        g_rap_ratios[i].Write(f"g_rap_ratio_{rap_min}_{rap_max:.1f}")
    h_extrap.Write("h_extrap")
    g_extrap.Write("g_extrap")
    output_file.Close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert NNLO+NNLL cross section to ROOT file')
    parser.add_argument('output_file', type=str, help='Output file')
    args = parser.parse_args()

    convert_to_root(args.output_file)