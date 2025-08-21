import pandas as pd 
import ROOT

df = pd.read_csv('fonll.txt', sep='\s+', comment='#')

h_fonll = ROOT.TH1F('h_fonll', 'h_fonll', 100, 0, 100)
for i, row in df.iterrows():
    h_fonll.SetBinContent(h_fonll.FindBin(row['pt']), row['central'])

outfile = ROOT.TFile('fonll.root', 'RECREATE')
h_fonll.Write()
outfile.Close()