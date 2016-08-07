function initGridLayerB(map){
  var zOut=-metadata.num_level+1,
      /*
      bounds = new L.LatLngBounds(
          new L.LatLng(0.0, -0.0),
          new L.LatLng(metadata.plot_num.y, metadata.plot_num.x + 0)),
      */
      dl = Math.ceil(metadata.map_offset.x / metadata.plot_dim.x),
      dr = Math.ceil((metadata.tile_sum.x - metadata.map_offset.x) / metadata.plot_dim.x),
      bounds = new L.LatLngBounds(
          new L.LatLng(0.0, -dl ),
          new L.LatLng(metadata.plot_num.y, dr )),
      options = {interval: 1,
    showOriginLabel: false,
    redraw: 'move', //'move'
    zoomIntervals: [
    {start: zOut, end: -5, interval: 10},
    {start: -4, end: -3, interval: 5},
    {start: -2, end: -2, interval: 2},
    {start: -1, end: 0, interval: 1}],
    bounds: bounds
      };

  return  L.simpleGraticule(options);
}
