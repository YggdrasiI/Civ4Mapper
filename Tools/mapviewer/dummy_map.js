var round = getUrlParameter("r", "dummy_map/").replace("/","") + "/";


// Overwrite default map values
// Defaults defined at head of CivMap.js
L.extend(metadata, {
  //  map_offset: L.point(32 + 7*map_plot_dim[0], 281 - 2*map_plot_dim[1]),
  folder: round
});

var x = getIntUrlParameter("x", metadata.plot_num.x/2),
    y = getIntUrlParameter("y", metadata.plot_num.y/2),
    z = getIntUrlParameter("z", -4);

metadata.start.zoom = z;
metadata.start.plot = L.point(x, y);

