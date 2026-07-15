The purpose of this repository is to provide code to determine the Hermitian-adjacency matrix spectra of directed graphs, whose underlying graph is $K_5$. 
A hermitian matrix $H = [h={ij}]$ of a digraph $D = (V,A)$, with $|V(D) = n|$ is an $n \times n$ matrix such that
- $h_{ij} = 1$ if $ij, ji \in A(D)$
- $h_{ij} = i$ if $ij \in A(D)$
- $h_{ij} = -i$ if $ji \in A(D)$
- $h_{ij} = 0$ otherwise.

### How to use:
If you simply want to look at the spectra of digraphs on $5$ vertices with underlying graph $K_5$ and at least one digon, open spectra_UD_K5_dig.csv 

If you want to check spectra of digraphs on $5$ vertices with underlying graph $K_5$ without the restriction on digon count, run python3 filter_UD_K5.py H_spectra_n=5.json --csv spectra_UD_K5_dig.csv.

- **dig5.d6**: Contains all digraphs on 5 vertices in d6 format. The data source is Brendan McKay (https://users.cecs.anu.edu.au/~bdm/data/digraphs.html).
- **compute_H_spectra.py**: Takes in d6 or upper-triangle-matrix tournament files and returns a json file storing the graph's d6 code, number of vertices, number of edges, adjacency matrix and hermitian eigenvalues.
- **H_spectra_n=5.json**: Output of compute_H_spectra.py.
- **filter_UD_Kn.py**: Takes a Json file as defined above as the input and returns a Json or csv file containing all H-spectra of the digraphs of the input file whose underlying graph is $K_n$. Optional, it returns only the spectra of digraphs whose underlying graph is $K_n$ and which contain at least $1$ digon.
- **spectra_UD_K5_dig.csv**: Output of filter_UD_Kn.py on n = 5 and digraphs containing at least $1$ digon.

If you are interested in exploring more digraphs, feel free to check out https://katiekuehr.github.io/digraph/.
