The purpose of this repository is to provide code to determine the Hermitian-adjacency matrix spectra of directed graphs, whose underlying graph is $K_5$. 
A hermitian matrix $H = [h={ij}]$ of a digraph $D = (V,A)$, with $|V(D) = n|$ is an $n \times n$ matrix such that
- $h_{ij} = 1$ if $ij, ji \in A(D)$
- $h_{ij} = i$ if $ij \in A(D)$
- $h_{ij} = -i$ if $ji \in A(D)$
- $h_{ij} = 0$ otherwise.

The data (dig5.d6) is taken from Brendan McKay (https://users.cecs.anu.edu.au/~bdm/data/digraphs.html) and includes all digraphs on 5 vertices.

### How to use:
If you simply want to look at the spectra of digraphs on $5$ vertices with underlying graph $K_5$ and at least one digon, open spectra_UD_K5_dig. 
If you want to check spectra of digraphs on $5$ vertices with underlying graph $K_5$ without the restriction on digon count, run python3 filter_UD_K5.py H_spectra_n=5.json --csv spectra_UD_K5_dig.csv.
