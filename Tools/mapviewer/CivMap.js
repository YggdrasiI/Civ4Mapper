// Values matching for 'dummy_map'
var metadata = {
  tile_dim: L.point(256, 256),
  tile_sum: L.point(5046, 3436),
  num_level: 5, // 0, …, num_level-1
  plot_dim: L.point(116, 116),
  plot_num: L.point(40, 24),
  map_offset: L.point(30, 279),
  start: { zoom: -2, plot: L.point(0, 0) },
  url_root: "./",
  folder: "dummy_map/"
}

// Centralise
metadata.start.plot.x = metadata.plot_num.x / 2;
metadata.start.plot.y = metadata.plot_num.y / 2;

//=================================================================
// Helper functions
var getUrlParameter = function getUrlParameter(sParam, default_val) {
  var sPageURL = decodeURIComponent(window.location.search.substring(1)),
      sURLVariables = sPageURL.split('&'),
      sParameterName,
      i;

  for (i = 0; i < sURLVariables.length; i++) {
    sParameterName = sURLVariables[i].split('=');

    if (sParameterName[0] === sParam) {
      return sParameterName[1] === undefined ? true : sParameterName[1];
    }
  }

  return default_val;
};

var getIntUrlParameter = function getIntUrlParameter(sParam, default_val) {
  var iVal = parseInt(getUrlParameter(sParam, default_val))
   return isFinite(iVal) ? iVal : default_val;
};

// Stub
function isAlive(playerId){
  return true;
}

function loadRound(folder){
  if( civMap ){
    metadata.folder = folder.replace("/","") + "/";
    url = metadata.url_root + metadata.folder + "{z}/{index}";
    civMap.tiles.setUrl(url);
    civMap.tiles.redraw();
  }
}

// Abort click if double clicked.
function singleclick(map, ftarget){
  ftarget.foo = 0;
  function start(e){
    if( ftarget. foo == 0 ){
      setTimeout(function() {
        if (ftarget.foo < 2 ) {
          ftarget(e);
        }
        ftarget.foo = 0;
      },250);
    }
    ftarget.foo = 1; //one timeout set for target
  }
  function abort(e){
    ftarget.foo = 2;
  }

  map.on('click', start);
  map.on('dblclick', abort);
}

// Gen Feature Map Skeletton by map size
function genFeatureMap(civmap_dim, data){

}

//=================================================================

/* If transformation scale on complete image (sum of all tiles) */
/*
function latlngToCoords(latlng, modulo_on_map){
  //vertial flipped coordinates
  var origin = [metadata.map_offset.x, metadata.tile_sum.y-metadata.map_offset.y],
      pos_transposed = [latlng.lng-origin[0], origin[1]-latlng.lat];

  var coords = [Math.floor(pos_transposed[0]/metadata.plot_dim.x),
      Math.floor(pos_transposed[1]/metadata.plot_dim.y) ];

  // Torus restriction
  if( modulo_on_map ){
    coords[0] = (coords[0] + metadata.plot_num.x) % metadata.plot_num.x; // Stupid js-%
    coords[1] = (coords[1] + metadata.plot_num.y) % metadata.plot_num.y;
  }

  return coords;
}

function plotVerticeToCoords(plot){
  var outX = plot.x * metadata.plot_dim.x + metadata.map_offset.x,
      outY = metadata.tile_sum.y - plot.y * metadata.plot_dim.y + metadata.map_offset.y;
  // Torus restriction
  outX = (outX + metadata.tile_sum.x) % metadata.tile_sum.x;
  outY = (outY + metadata.tile_sum.y) % metadata.tile_sum.y;

  return [outX, outY];
}
*/

/* For ideal transformation where latlng represents the plot inidices.*/
function latlngToCoords(latlng, modulo_on_map){
  var coords = [Math.floor(latlng.lng), Math.floor(latlng.lat)];

  if( modulo_on_map ){
    // Torus restriction
    coords[0] = (coords[0] + metadata.plot_num.x) % metadata.plot_num.x; // Stupid js-%
    coords[1] = (coords[1] + metadata.plot_num.y) % metadata.plot_num.y;
  }

  return coords;
}
function plotVerticeToCoords(plot){
  return [plot.x, plot.y];
}

// Derivative helper functions
function latlngToPlot(latlng, modulo_on_map){
  var coords = latlngToCoords(latlng, modulo_on_map);
  return L.point(coords[0], coords[1]);
}

function plotCenterToLatlng(plot){
  return plotVerticeToLatlng(plot.add(L.point(0.5, 0.5)));
}

function plotVerticeToLatlng(plot){
  var coords = plotVerticeToCoords(plot)
  return new L.LatLng(coords[1], coords[0]);
}
function plotVerticeToPoint(plot){
  var coords = plotVerticeToCoords(plot)
  return L.point(coords[0], coords[1]);
}


//=================================================================

function linkPopup(map){
  var popup = L.popup();

  function onMapClick(e) {
    if( map.getZoom() < -2) return;

    plot = latlngToPlot(e.latlng, true);
    plot2 = latlngToPlot(e.latlng, false);

    popup
      //.setLatLng(e.latlng)
      .setLatLng(plotCenterToLatlng(plot2))
      .setContent("Direct link to this plot:<br><a href='?r=" +
     metadata.folder.replace("/","") + "&x=" + plot.x + "&y=" + plot.y +
     "&z=" + map.getZoom() + "'>" + plot.toString() + 
          "</a><br>")
      .openOn(map);
  }

  //map.on('click', onMapClick);
  singleclick(map, onMapClick);
}

function initMap(id) {
  /* Hier muss so skaliert werden, dass bei Map-Größe 64x40 das ungefähr den 
   * Endkoordinaten entspricht. Dazu kommt oben noch ein großer Rand und links ein kleiner
   * was vom Startpunkt bei der Kartenerstellung abhängt. In Civ beginnen wir allerdings unten,
   * d.h. die Nordgrenze variiert....*/
  //var f = Math.pow(2, - (metadata.num_level - 1)),
  var f = Math.pow(2, 0),
      fx =  f * metadata.plot_dim.x,
      fy =  f * metadata.plot_dim.y;
  L.CRS.Test = L.extend({}, L.CRS.Simple, {
    /* Entspricht 1:1-pixel-Verhältnis auf Stufe 0. 
    */
    //transformation: new L.Transformation(1.0, 0, 1.0, 0)
    /* An Kartendimensionen angepasst, so das 1:1-Verhältnis
     * auf höchster Stufe erreicht wird.
     */
    /*
    transformation: new L.Transformation(
                      Math.pow(2, - (metadata.num_level - 1)), 0,
                      Math.pow(2, - (metadata.num_level - 1)), 0)
    */
    /* Feldgröße auf eine Längeneinheit normiert und Ursprung korrigiert.
     */
    transformation: new L.Transformation( fx,
                        f * metadata.map_offset.x,
                        -fy,
                        f * (metadata.tile_sum.y - metadata.map_offset.y) )
  })

  var map = L.map(id,
      {crs: L.CRS.Test,
        minZoom: -metadata.num_level+1,
        maxZoom: 0}
      ).setView(plotCenterToLatlng(metadata.start.plot), metadata.start.zoom);
      
  return map;
}

function initTileLayer(map){
  //var tile_layer = L.tileLayer(metadata.url_root + metadata.folder + '{z}/{index}',
  var tile_layer = new CivTileLayer(metadata.url_root + metadata.folder + '{z}/{index}',
      {
        attribution: 'Content &copy; ?, Imagery &copy; <a href="http://www.civforum.de/member.php?18777-Ramkhamhaeng">Ramkhamhaeng</a>',
      tileSize: metadata.tile_dim,
      continuousWorld: true, // coordinates of flat map
      noWrap: true,
      minZoom: -metadata.num_level + 1,
      maxZoom: 0,
      maxNativeZoom: 0,
      // my stuff
      mapWidth: metadata.tile_sum.x,
      mapHeight: metadata.tile_sum.y,
      index: '{index}'
      })

  // Overload url parsing
  function getIndex(coords, options){
    //layer and source dimension indicate images per row.
    var tW = (1 << ( options.maxNativeZoom-coords.z)) * metadata.tile_dim.x,
    tH = (1 << ( options.maxNativeZoom-coords.z)) * metadata.tile_dim.y, 
    nW = Math.ceil(options.mapWidth/tW),
    nH = Math.ceil(options.mapHeight/tH),
    index = (coords.y) * nW + (coords.x);
    index = (coords.y % nH) * nW + (coords.x % nW); // modular for torus.

    if( coords.y < 0 || coords.x < 0 || coords.y >= nH || coords.x >= nW ) return "../transparent.png";
    return "tile_"+index.toString()+".jpg";
  }
  tile_layer._getTileUrl = tile_layer.getTileUrl;
  tile_layer.getTileUrl = function(coords){
    stage1 = this._getTileUrl(coords);
    return L.Util.template(stage1, {index: getIndex(coords, this.options)})
  };

  // Overwrite _forceSize
  tile_layer._forceSize = function (tile, coords) {
    var tileSize = this.getTileSize();
    var tW = (1 << ( this.options.maxNativeZoom-coords.z)) * tileSize.x,
        tH = (1 << ( this.options.maxNativeZoom-coords.z)) * tileSize.y,
        nW = Math.ceil(this.options.mapWidth/tW),
        nH = Math.ceil(this.options.mapHeight/tH);
    return (coords[0] == nW-1 || coords[1] == nH-1 );
  }
      

  map.addLayer(tile_layer);

  return tile_layer;
}

//=================================================================


function CivMap(){
  this.metadata = metadata;
}

CivMap.prototype.plotTiledJsonPluginA = function(map) {
  var style = {};
  //var geojsonURL = 'http://tile.example.com/{z}/{x}/{y}.json';
  var geojsonURL = 'culture2.json';
  var geojsonTileLayer = new L.TileLayer.GeoJSON(geojsonURL, {
    maxZoom: 0,
    minZoom: -6,
//      tileSize: [metadata.plot_dim.x*10, metadata.plot_dim.y*10],
    clipTiles: true,
      unique: function (feature) {
        return feature.id; 
      }
  }, {
    style: style,
      onEachFeature: function (feature, layer) {
        if (feature.properties) {
          var popupString = '<div class="popup">';
          for (var k in feature.properties) {
            var v = feature.properties[k];
            popupString += k + ': ' + v + '<br />';
          }
          popupString += '</div>';
          layer.bindPopup(popupString);
        }
        if (!(layer instanceof L.Point)) {
          layer.on('mouseover', function () {
            layer.setStyle(hoverStyle);
          });
          layer.on('mouseout', function () {
            layer.setStyle(style);
          });
        }
      }
  }
  );
  map.addLayer(geojsonTileLayer);

  return geojsonTileLayer;
}


function getCivPlot(point){
  var x = (metadata.plot_num.x + Math.round(point.x)) % metadata.plot_num.x,
      y = Math.round(point.y);

  /* //Not included
     if( 0 <= x && x < civ_plots.length && 0 <= y && y <= civ_plots[x].length ){
     var ret = civ_plots[x][y];
  // Set plot info for debugging.
  if( !ret.x ) ret.x = x;
  if( !ret.y ) ret.y = y;
  return ret;
  }
  */
  // Define dummy for debugging
  plot_dummy = {"x": x, "y": y, "owner": -1, "culture":[],
  "plottype": 1, "terrain": 0, "feature": 0,
  "improvement": 0, "bonus": 0, "route": 0
  }
  return plot_dummy;
}

function plot_info_terrain(plot){
  //not included
}
function plot_info_culture(plot){
  //not included
}

CivMap.prototype.initPlotInfo = function() {

  // Info overlay
  var plot_info = L.control({position: "bottomleft"});

  plot_info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'plot_info'); // create a div with a class "plot_info"
    this.update();
    return this._div;
  };

  // method that we will use to update the control based on feature properties passed
  plot_info.update = function (plot) {
    var list = '';
    if( plot ){
      list += "<h4>Plot ("+plot.x+","+plot.y+")</h4>";
      //list += plot_info_terrain(plot);
      //list += plot_info_culture(plot);
    }
    this._div.innerHTML = list  +  (plot ?  '' : 'Hover over a plot.');
  };
  function onMapMove(e){
    var civ_plot = getCivPlot(latlngToPlot(e.latlng, true)); /* Note: It's a L.Point, not L.LatLng */
    plot_info.update(civ_plot);
  }

  this.plot_info = plot_info;
  this.plot_info.addTo(this.map);

  this.map.on('mousemove', onMapMove);
}

CivMap.prototype.init = function(id) {
  this.map = initMap(id);
  this.tiles = initTileLayer(this.map);
  this.grid = initGridLayerB(this.map);
  this.initPlotInfo();
  
  var baseLayers = {
    "3D Map" : this.map
  };
  var overlays = {
//    "Culture": this.culture,
    "Grid": this.grid
  };
  L.control.layers(baseLayers, overlays).addTo(this.map);

  linkPopup(this.map);
}
