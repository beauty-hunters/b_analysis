
#!/usr/bin/env python3

import sys
import ROOT
from array import array


def txt_to_graph(input_file, output_file, pt_bins,
                 graph_name="gFONLL"):

    # Read original data
    x = []
    ex = []
    central = []
    minimum = []
    maximum = []

    with open(input_file, "r") as infile:
        for line in infile:

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            values = line.split()

            if len(values) < 5:
                continue

            x.append(float(values[0]))
            ex.append(float(values[1]))
            central.append(float(values[2]))
            minimum.append(float(values[3]))
            maximum.append(float(values[4]))

    # Check bin edges
    if len(pt_bins) < 2:
        raise ValueError("At least two bin edges are required")

    if any(b <= a for a, b in zip(pt_bins[:-1], pt_bins[1:])):
        raise ValueError("Bin edges must be strictly increasing")

    # Output graph arrays
    gx, gy = [], []
    gexl, gexh = [], []
    geyl, geyh = [], []

    # Rebin
    for bin_low, bin_high in zip(pt_bins[:-1], pt_bins[1:]):

        bin_width = bin_high - bin_low

        # Integrate original bins over the new bin boundaries
        sum_central = 0.
        sum_minimum = 0.
        sum_maximum = 0.
        covered_width = 0.

        for i in range(len(x)):

            # Original bin boundaries
            old_low = x[i] - ex[i]
            old_high = x[i] + ex[i]

            # Overlap with new bin
            overlap = max(
                0.,
                min(old_high, bin_high) - max(old_low, bin_low)
            )

            if overlap <= 0:
                continue

            sum_central += central[i] * overlap
            sum_minimum += minimum[i] * overlap
            sum_maximum += maximum[i] * overlap

            covered_width += overlap

        # Check that the new bin is fully covered
        if abs(covered_width - bin_width) > 1.e-6 * bin_width:
            raise ValueError(
                f"Bin [{bin_low}, {bin_high}] is not fully covered "
                f"by the original data (covered {covered_width}, "
                f"expected {bin_width})"
            )

        # Calculate rebinned differential cross section
        y = sum_central / bin_width
        y_min = sum_minimum / bin_width
        y_max = sum_maximum / bin_width

        # New bin center and horizontal uncertainties
        gx.append(0.5 * (bin_low + bin_high))
        gexl.append(0.5 * bin_width)
        gexh.append(0.5 * bin_width)

        gy.append(y)
        geyl.append(y - y_min)
        geyh.append(y_max - y)

    # Convert to C-compatible arrays
    gx = array('d', gx)
    gy = array('d', gy)
    gexl = array('d', gexl)
    gexh = array('d', gexh)
    geyl = array('d', geyl)
    geyh = array('d', geyh)

    # Create TGraphAsymmErrors
    graph = ROOT.TGraphAsymmErrors(
        len(gx),
        gx, gy,
        gexl, gexh,
        geyl, geyh
    )

    graph.SetName(graph_name)
    graph.SetTitle(
        ";#it{p}_{T} (GeV/#it{c});"
        "d#sigma/d#it{p}_{T} (pb/GeV)"
    )

    # Save ROOT file
    outfile = ROOT.TFile.Open(output_file, "RECREATE")

    if not outfile or outfile.IsZombie():
        raise OSError(f"Could not create ROOT file: {output_file}")

    outfile.cd()
    graph.Write()
    outfile.Close()

    print(f"Saved {len(gx)} rebinned points to {output_file}")


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            f"Usage: {sys.argv[0]} input.txt output.root "
            "[pt_bin_edges]"
        )
        print("Example: 0.25,1,2,4,6,10,15,23.75")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Custom bin edges (or use defaults)
    if len(sys.argv) >= 4:
        pt_bins = [float(v) for v in sys.argv[3].split(",")]
    else:
        pt_bins = [
            0.25, 1., 2., 4., 6., 10., 15., 23.75
        ]

    txt_to_graph(input_file, output_file, pt_bins)
