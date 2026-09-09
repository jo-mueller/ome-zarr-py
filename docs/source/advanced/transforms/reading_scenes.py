# %% [markdown]
# # Reading scenes

# %%
import networkx as nx

from ome_zarr import OMEZarrScene

# %%
scene = OMEZarrScene.from_ome_zarr("https://radosgw.public.os.wwu.de/s2v/P2A_B6_M2.ome.zarr")

# %% [markdown]
# This step requires matplotlib

# %%
nx.draw(scene._graph.graph, with_labels=True)

# %%



