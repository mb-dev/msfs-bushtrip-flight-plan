# Flight Simulator 2020 Bush Trip Exporter

![](./example.png)

![](./example2.png)

I love bush trips but I don't like flying them within the bush trip setting. I want to have ATC, GPS and be able to choose my plane without editing pln files. But I still want to get descriptions of waypoints and be able to follow the plan from the world map.

This convert.py script converts bush trip xml file + flight plan to:
1) html file with leg descriptions and images (which can be converted to pdf)
2) append comments / poi names to existing little nav map flight plan

Steps:
1) choose a bush trip
2) decode the bsp using https://github.com/leppie/spb2xml. Example:

```bash
spb2xml-msfs.exe -s "C:\Program Files (x86)\Steam\steamapps\common\MicrosoftFlightSimulator\Packages\fs-base-propdefs\Propdefs\1.0\Common" "C:\Users\mb-dev\AppData\Roaming\Microsoft Flight Simulator\Packages\Official\Steam\asobo-bushtrip-nevada\Missions\Asobo\BushTrips\nevada\Nevada.spb"
```

3) Open the flt in Little Nav Map and save it as a lnmpln file in the "original" path
4) Update paths in convert.py script and execute
5) open html in Internet Explorer, save as Complete HTML file
6) use powertools to mass resize the images in the complete html file to Small preset
7) open the saved complete html - print as PDF.