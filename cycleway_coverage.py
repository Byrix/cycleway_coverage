
# === INIT ====================================================================
# --- Modules ---------------
import os
import logging
import geopandas as gpd 

# --- Input Data ------------
data_dir = os.path.join(os.getcwd(), "data")

# Reads from root of data directory, if file is within a subdirectory of the data folder
# given above specify the subdirectory path in the filenames here
network_filename = "network_melbourne.sqlite"
region_filename = "greater_melbourne.sqlite"
sas_filename = "SA2_2021_AUST_SHP_GDA2020.zip"

# Desired layers within the files above
# If no layer, leave as empty string
network_layer = "links" 
region_layer = "" 
sas_layer = "" 

# --- Outputs ---------------
output_dir = os.path.join(os.getcwd(), "outputs")
output_filename = "coverage_melbourne.sqlite"
output_layer = "coverage"

# --- Project vars ----------
PROJ = 7899  # Desired CRS
OVERWRITE = True  # Overwrite output if it exists
CLIP_EXTENT = True  # Clip network to region


# === UTILS ===================================================================
def load(filename: str|os.PathLike, layer: str|int, **kwargs) -> gpd.GeoDataFrame: 
  """
  Load a file from into a geopandas gpd 
  :param filename: the file name of the file to load, can include subdir path if file is not within the root ./data/ dir
  :param layer: the name or index of the desired layer, defaults to the first layer if an empty string is passed
  :param kwargs: additional keyword arguments to pass to geopandas.read_file()
  :raises RuntimeError: if filename does not have geometry
  :returns: the specified file or layer loaded into a GeoDataFrame
  """
  # TODO: Rework to ensure works with fiona too, currently only works for pyogrio

  layer = 0 if layer=="" else layer
  gdf = gpd.read_file(os.path.join(data_dir, filename), layer=layer, **kwargs)

  # Ensure only files with geometries are returned
  if not isinstance(gdf, gpd.GeoDataFrame):
    raise RuntimeError("Error loading {filename}, either no geometry exists, or was not detected.")

  return gdf.to_crs(PROJ)

def get_coverage(
    polys: gpd.GeoDataFrame, 
    links: gpd.GeoDataFrame, 
    name: str,
    group: str = "SA2_CODE21", 
  ) -> gpd.GeoDataFrame: 
  """
  Gets the ratio between the total network length within a polygon and the length of a given subset
    of the network 
  :param polys: a geopandas.GeoDataFrame with the underlying polygons 
  :param links: a geopandas.GeoDataFrame with the network links 
    `links` features must have attributes "split_length" with the length of that feature and a second
    attribute with index of the polygon feature corresponds to 
  :param name: the name to give this coverage
  :param group: the feature to groupby, presumably the name of attribute linking polys and links
    Defaults to "SA2_CODE21"
  :param mask: a mask array where mask_i = True means that links_i will be included in coverage sum
  """
  if "links_length" not in polys.columns:
    link_lengths = links.groupby([group])['split_length'].sum()
    polys = polys.join(link_lengths, validate="1:1")
    polys = polys.rename(columns={"split_length": "links_length"})

  link_condition_length = links[links[name]].groupby([group])['split_length'].sum()
  polys = polys.join(link_condition_length, validate='1:1')
  polys = polys.rename(columns={"split_length": f"{name}_length"})

  polys = polys.fillna(value = {f"{name}_length": 0})
  polys[f"{name}_coverage"] = polys[f"{name}_length"] / polys['links_length']

  return polys

# === RUN =====================================================================
def run():
  # Load data
  links = load(network_filename, network_layer)
  sas = load(sas_filename, sas_layer).set_index('SA2_CODE21', drop=False)

  # Pre-processing 
  agg_dict = {
    "is_cycle": "any",
    "cycleway": "any"
  }
  links = links.dissolve(by='osm_id', aggfunc=agg_dict)

  # Processing
  split_links = links.overlay(sas)
  split_links['split_length'] = split_links.geometry.length
  # NOTE: split_length is NOT equivalent to real-length as geometry has been modified, use for 
  # relative calculations ONLY

  sas = get_coverage(sas, split_links, "cycleway")
  # sas = get_coverage(sas, split_links, "is_cycle")
  # sas['cycleway_to_bikeable'] = sas['cycleway_coverage'] / sas['is_cycle_coverage']

  # Save output 
  output_file = os.path.join(output_dir, output_filename)
  # TODO: Needs to check if overwrite is false and (file exists OR layer exists)
  if not OVERWRITE and os.path.exists(output_file):
    raise FileExistsError("Output {output_file} already exists, ending. To overwrite set OVERWRITE=True")

  if CLIP_EXTENT:
    extent = load(region_filename, region_layer).geometry[0]
    sas = sas.clip(extent)
  sas.to_file(output_file, layer=output_layer, driver='SQLite', index=False)

if __name__ == "__main__":
  run()