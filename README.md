# Cycleway Coverage

Calculate the cycleway coverage (cycleway route-km / total route-km) over a collection of spanning polygons. 

## Usage
### Data
Please see `./data/README.md` for data requirements and potential sources. File names and paths are specified in the beginning lines of the script, alter as appropriate.

### Dependancies
 - `geopandas`
 - `matplotlib` (optionally required for producing output maps only)


For initial run usage: 
```{bash}
conda env create -f conda-env.yml
conda activate cycleway-coverage-env
python cycleway_coverage.py
```

