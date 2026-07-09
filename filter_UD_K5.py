"""
Find digraphs whose underlying graph U(D) is the complete graph K_n.
An underlying graph is "complete" (K_n) if every pair of vertices i != j has
an edge in U(D), i.e. H[i][j] and H[j][i] is nonzero for ALL i != j.

Two ways to use this:

1. Scan a whole file and report every digraph whose underlying graph is
    complete (for whatever n it happens to have):

        python3 filter_UD_K5.py H_spectra_n=5.json --csv spectra_UD_K5_dig.csv

2. To additionally require at least one digon (an edge present in BOTH
directions, i.e. H[i][j] == H[j][i] == 1 for some pair), use:

        python3 filter_UD_K5.py H_spectra_n=5.json --min-digons 1 --csv spectra_UD_K5_dig.csv
"""

import json
import csv
import argparse


# ----------------------------------------------------------------------
# Tolerant loader: recovers complete top-level JSON objects even if the
# file got truncated at the very end.
# ----------------------------------------------------------------------
def load_records(path):
    with open(path) as f:
        text = f.read()
    text = text.strip()
    if not text.startswith('['):
        raise ValueError("Expected a top-level JSON list")

    decoder = json.JSONDecoder()
    pos = 1
    n = len(text)
    records = []
    truncated = False
    while True:
        while pos < n and text[pos] in ' \t\n\r,':
            pos += 1
        if pos >= n or text[pos] == ']':
            break
        try:
            obj, end = decoder.raw_decode(text, pos)
        except json.JSONDecodeError:
            truncated = True
            break
        records.append(obj)
        pos = end
    return records, truncated

def is_complete_underlying(adj):
    """True iff every pair i != j has adj[i][j] or adj[j][i] nonzero."""
    n = len(adj)
    for i in range(n):
        for j in range(i + 1, n):
            if not (adj[i][j] or adj[j][i]):
                return False
    return True

def count_digons(adj):
    """Number of pairs i < j with a digon (both adj[i][j] and adj[j][i] set)."""
    n = len(adj)
    c = 0
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] and adj[j][i]:
                c += 1
    return c

def parse_eigs(h_eigs_str):
    return [float(p.strip()) for p in h_eigs_str.split(',')]

def main():
    parser = argparse.ArgumentParser(description="Find digraphs whose underlying graph is complete (K_n).")
    parser.add_argument("infile", help="input JSON file (list of {d6, n, e, adj, h_eigs} records)")
    parser.add_argument("--n", type=int, default=None, nargs='+',
                        help="restrict to these specific n value(s) (i.e. underlying graph "
                            "K_n). Accepts one or more, e.g. --n 5 6. "
                            "If omitted, all n are included.")
    parser.add_argument("--out", default="complete_underlying_out.json",
                        help="output JSON file (default: complete_underlying_out.json)")
    parser.add_argument("--csv", default=None,
                        help="also write a CSV file (e.g. --csv results.csv). Columns: "
                            "n, e, d6, num_distinct_eigenvalues, spectrum (semicolon-separated), "
                            "max_eig, min_eig")
    parser.add_argument("--min-digons", type=int, default=0,
                        help="require at least this many digons (edges present in BOTH "
                            "directions) in the digraph. Default 0 (no digon requirement). "
                            "Use --min-digons 1 to require at least one digon.")
    args = parser.parse_args()

    records, truncated = load_records(args.infile)
    if truncated:
        print(f"NOTE: input file appears truncated; recovered {len(records)} "
                f"complete records (trailing incomplete record discarded).\n")

    matches = []
    for rec in records:
        adj = rec.get('adj')
        h_eigs_str = rec.get('h_eigs')
        if adj is None or h_eigs_str is None:
            continue

        n = rec.get('n', len(adj))
        if args.n is not None and n not in args.n:
            continue

        if not is_complete_underlying(adj):
            continue

        n_digons = count_digons(adj)
        if n_digons < args.min_digons:
            continue

        eigs = parse_eigs(h_eigs_str)
        matches.append({
            'n': n,
            'e': rec.get('e'),
            'd6': rec.get('d6'),
            'adj': adj,
            'num_digons': n_digons,
            'spectrum': sorted(eigs, reverse=True),
        })

    matches.sort(key=lambda r: (r['n'], -max(r['spectrum'])))

    with open(args.out, 'w') as f:
        json.dump(matches, f, indent=2)

    if args.csv:
        with open(args.csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['n', 'e', 'd6', 'num_digons', 'num_distinct_eigenvalues',
                                'spectrum', 'max_eig', 'min_eig'])
            for m in matches:
                spec = m['spectrum']
                writer.writerow([
                    m['n'],
                    m['e'],
                    m['d6'],
                    m['num_digons'],
                    len(set(round(v, 6) for v in spec)),
                    ';'.join(f"{v:.6f}" for v in spec),
                    f"{max(spec):.6f}",
                    f"{min(spec):.6f}",
                ])

    if args.n is None:
        label = "K_n (any n)"
    elif len(args.n) == 1:
        label = f"K_{args.n[0]}"
    else:
        label = "K_n for n in {" + ", ".join(str(x) for x in sorted(args.n)) + "}"
    if args.min_digons > 0:
        label += f", with >= {args.min_digons} digon(s)"
    print(f"Scanned {len(records)} records.")
    print(f"Found {len(matches)} digraphs with underlying graph {label}.")
    print(f"Results written to: {args.out}")
    if args.csv:
        print(f"CSV also written to: {args.csv}")
    print()

    for m in matches:
        eig_str = ', '.join(f"{v:g}" for v in m['spectrum'])
        print(f"  n={m['n']} e={m['e']} digons={m['num_digons']} d6={m['d6']}: spectrum = [ {eig_str} ]")

if __name__ == "__main__":
    main() 