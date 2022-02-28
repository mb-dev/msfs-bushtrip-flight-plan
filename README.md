# Flight Simulator 2020 Bush Trip Exporter

![](./example.png)

![](./example2.png)

I love bush trips but I don't like flying them within the bush trip setting. I want to have ATC, GPS and be able to choose my plane without editing pln files. But I still want to get descriptions of waypoints and be able to follow the plan from the world map.

This convert.py script generates for all msfs default bush trips:
1) html file with leg descriptions and images
2) pdf file with links to google maps and sky vector
3) pln file for each leg of the trip

Steps:
1) download https://github.com/leppie/spb2xml and update the path at the top of the file:
2) Update the rest of the paths in convert.py script and execute

Next step: support custom bush trips