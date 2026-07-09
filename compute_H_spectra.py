"""
generate_database.py

Run this locally to generate graphs_slim.json, then paste the data
into digraph_database.html to update the website.

Usage:
    python generate_database.py

Requirements: dichromatic.py in the same folder, plus sympy, matplotlib, numpy.
Edit D6_FILES to include whichever .d6 files you have downloaded.
"""


import json
import sympy as sp
from sympy import symbols
import numpy as np

k = symbols('k')

D6_FILES = ["dig5.d6",]

OUTPUT_JSON = "H_spectra_n=5.json"

def _n_from_bytes(data, pos):
    if data[pos] != 126:
        return data[pos] - 63, pos + 1
    pos += 1
    if data[pos] != 126:
        x = 0
        for _ in range(3):
            x = (x << 6) | (data[pos] - 63); pos += 1
        return x, pos
    pos += 1
    x = 0
    for _ in range(6):
        x = (x << 6) | (data[pos] - 63); pos += 1
    return x, pos

def parse_d6(s):
    """digraph6 string → n×n adjacency matrix."""
    s = s.strip()
    if s.startswith(">>digraph6<<"): s = s[len(">>digraph6<<"):]
    if s.startswith("&"): s = s[1:]
    data = s.encode("ascii")
    n, pos = _n_from_bytes(data, 0)
    bits = []
    for byte in data[pos:]:
        v = byte - 63
        for shift in range(5, -1, -1):
            bits.append((v >> shift) & 1)
    adj = [[0]*n for _ in range(n)]
    idx = 0
    for i in range(n):
        for j in range(n):
            if idx < len(bits):
                adj[i][j] = bits[idx]; idx += 1
    return adj

def to_d6(adj):
    """n×n adjacency matrix → digraph6 string."""
    n = len(adj)
    if n <= 62:
        n_bytes = bytes([n + 63])
    elif n <= 258047:
        x = n; b = []
        for _ in range(3): b.append((x & 0x3F) + 63); x >>= 6
        n_bytes = bytes([126]) + bytes(reversed(b))
    else:
        x = n; b = []
        for _ in range(6): b.append((x & 0x3F) + 63); x >>= 6
        n_bytes = bytes([126, 126]) + bytes(reversed(b))
    bits = [adj[i][j] for i in range(n) for j in range(n)]
    while len(bits) % 6: bits.append(0)
    r_bytes = []
    for i in range(0, len(bits), 6):
        v = 0
        for b in bits[i:i+6]: v = (v << 1) | b
        r_bytes.append(v + 63)
    return "&" + (n_bytes + bytes(r_bytes)).decode("ascii")

def _n(adj): return len(adj)

def count_edges(adj):
    n = len(adj)
    return sum(adj[i][j] for i in range(n) for j in range(n))

def hermitian_adj(adj):
    n = len(adj)
    H = np.zeros((n, n), dtype=complex)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if adj[i][j] and adj[j][i]:
                H[i][j] = 1.0
            elif adj[i][j]:
                H[i][j] = 1j
            elif adj[j][i]:
                H[i][j] = -1j
    return H

def hermitian_eigenvalues(adj, tol=1e-8):
    H = hermitian_adj(adj)
    eigs = np.linalg.eigvalsh(H)
    result = []
    for e in sorted(eigs):
        e_real = float(e.real)
        if abs(e_real - round(e_real)) < tol:
            result.append(int(round(e_real)))
        else:
            result.append(round(e_real, 8))
    return result

def format_eigenvalues(eig_list):
    return ", ".join(str(e) for e in eig_list)

def process_graph(args):
    """Process a single graph. args = (adj, upper_tri_string_or_None)"""
    adj = args
    n = _n(adj)
    e = count_edges(adj)
    h_eigs = format_eigenvalues(hermitian_eigenvalues(adj))

    return {
        "d6": str(to_d6(adj)),
        "n": int(n),
        "e": int(e),
        "adj": adj,
        "h_eigs": h_eigs,
    }

def generate():
    graphs = []
    total_files = 0

    # --- d6 files (sequential) ---
    for fname in D6_FILES:
        try:
            with open(fname) as f:
                lines = [l.strip() for l in f if l.strip()]
            print(f"  {fname}: {len(lines)} graphs", flush=True)
            total_files += 1
            for i, line in enumerate(lines):
                if i % 100 == 0:
                    print(f"    {i}/{len(lines)}...", end='\r', flush=True)
                adj = parse_d6(line)
                graphs.append(process_graph((adj)))
            print(f"    done.           ", flush=True)
        except FileNotFoundError:
            print(f"  WARNING: {fname} not found, skipping.")

    print(f"\nTotal: {len(graphs)} graphs from {total_files} files.")

    with open(OUTPUT_JSON, 'w') as f:
        json.dump(graphs, f, separators=(',', ':'))
    print(f"Wrote {OUTPUT_JSON} ({len(json.dumps(graphs))//1024}KB)")


if __name__ == "__main__":
    generate()