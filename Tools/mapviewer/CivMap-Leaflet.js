//=================================================================
/* Extensions/Mixins/Modifications of leaflet functions/classes. */
//=================================================================
/* Extend L.Bounds with intersect method. (It modifies this.)
 * Note that L.Bounds.intersects just return a boolean, but not change
 * the object. */
L.Bounds.intersect = function (bounds) {
  bounds = L.Bounds(bounds);

  var sw = this.min,
      ne = this.max,
      sw2 = bounds.getBottomLeft(),
      ne2 = bounds.getTopRight();

  sw.x = Math.max(sw.x, sw2.x);
  sw.y = Math.max(sw.y, sw2.y);
  ne.x = Math.min(ne.x, ne2.x);
  ne.y = Math.min(ne.y, ne2.y);

  return (sw.x < ne.x) && (sw.y < ne.y);
};

/* Extend L.LatLngBounds with intersect method. */
L.LatLngBounds.prototype.intersect = function (bounds) {
      bounds = L.latLngBounds(bounds);

      var sw = this._southWest,
    ne = this._northEast,
    sw2 = bounds.getSouthWest(),
    ne2 = bounds.getNorthEast();

sw.lat = Math.max(sw.lat, sw2.lat);
sw.lng = Math.max(sw.lng, sw2.lng);
ne.lat = Math.min(ne.lat, ne2.lat);
ne.lng = Math.min(ne.lng, ne2.lng);

return (sw.lat < ne.lat) && (sw.lng < ne.lng);
    };

//=================================================================
/* Mixin of to properties into TilesLayer:
 * 1. Allow to disable the foring of tile sizes. This omit stetching
 *    of non-squared tiles nearby the border of a 2D-map.
 *
 * 2. Add offset parameter to shift all tiles.
 *    Note that big offsets disturb estimation of displayed tiles.
 */

var TileLayerMixin = {

  // 2. ========================================================
  // @option forceSize: Boolean = true
  // If `true` the tile size will set on options.tileSize before the image loads. Disable option to allow non-squared images at the border of the tiled grid. Overwrite _forceSize to decide for every tile separatly.
  forceSize: true,
  _forceSize: function (tile, coords) {
    return this.forceSize;
  },
  // 2. ========================================================
  //tileOffset: L.point(0.0, 0.0),
  _tileOffset: function (tile) {
    if( this.options.tileOffset === undefined )
      return;
		var o = this.options.tileOffset.multiplyBy(
        Math.pow(2, this._tileZoom - this.options.maxNativeZoom)).round();
    tile.style.marginLeft = o.x + 'px';
    tile.style.marginTop = o.y + 'px';
  },

  // ===========================================================
  /* Overwritten/Extended Leaflet functions.
   * Added was lines with relation to 'forceSize'.*/
	_addTile: function (coords, container) {
		var tilePos = this._getTilePos(coords),
		    key = this._tileCoordsToKey(coords);

		var tile = this.createTile(this._wrapCoords(coords), L.bind(this._tileReady, this, coords));
    var forceSize = this._forceSize(tile, coords);

		this._initTile(tile, forceSize);

		// if createTile is defined with a second argument ("done" callback),
		// we know that tile is async and will be ready later; otherwise
		if (this.createTile.length < 2) {
			// mark tile as ready, but delay one frame for opacity animation to happen
			L.Util.requestAnimFrame(L.bind(this._tileReady, this, coords, null, tile));
		}

		L.DomUtil.setPosition(tile, tilePos);

		// save tile in cache
		this._tiles[key] = {
			el: tile,
			coords: coords,
			current: true
		};

		container.appendChild(tile);
		// @event tileloadstart: TileEvent
		// Fired when a tile is requested and starts loading.
		this.fire('tileloadstart', {
			tile: tile,
			coords: coords
		});
	},
	_initTile: function (tile, forceSize) {
		L.DomUtil.addClass(tile, 'leaflet-tile');

		var tileSize = this.getTileSize();
    //Bad for the speed, but omit stretching of non-squared images.
    if( forceSize ){
      tile.style.width = tileSize.x + 'px';
      tile.style.height = tileSize.y + 'px';
    }
    this._tileOffset(tile);

		tile.onselectstart = L.Util.falseFn;
		tile.onmousemove = L.Util.falseFn;

		// update opacity on tiles in IE7-8 because of filter inheritance problems
		if (L.Browser.ielt9 && this.options.opacity < 1) {
			L.DomUtil.setOpacity(tile, this.options.opacity);
		}

		// without this hack, tiles disappear after zoom on Chrome for Android
		// https://github.com/Leaflet/Leaflet/issues/2078
		if (L.Browser.android && !L.Browser.android23) {
			tile.style.WebkitBackfaceVisibility = 'hidden';
		}
	}
};

var CivTileLayer= L.TileLayer.extend({
    includes: TileLayerMixin,
    statics: {},
});

