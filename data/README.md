# Data Requirements 

| File | Purpose | Notes |
|------|---------|-------|
| Network | A network dataset containing links and node information | Designed to work with networks built [using this repo](https://github.com/matsim-melbourne/network) |
| Region | (Multi)polygons defining the extent of area to be studied | |
| Sub-regions | Polygon collection, coverage is calculated for the section of the network that intersect each polygon | Built to use ABS [Statistical Area 2s](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/main-structure-and-greater-capital-city-statistical-areas/statistical-area-level-2) from 2021, using other polygons may require altering index names in some places | 