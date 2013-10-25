
from landez import GoogleProjection
from collections import defaultdict
import json
import urllib2, urllib

def fetch(url, data=None, headers={}):
    request = urllib2.Request(url, data, headers=headers)
    return urllib2.urlopen(request).read()

class CartoDBTiles(GoogleProjection):

    def __init__(self, *args, **kwargs):
        self.sql_api_url = 'http://dev.localhost.lan:8080/api/v1/sql'
        super(CartoDBTiles, self).__init__(*args, **kwargs)

    def tileslist(self, bbox):
        return self.tiles(bbox, self.levels[0], self.levels[-1])

    def containsGeometry(self, tile):
        #sql = "select 1 from ne_10m_populated_places_simple_9 where st_contains(CDB_XYZ_Extent(%d,%d,%d), the_geom_webmercator) limit 1" % tile
        sql = "SELECT EXISTS ( SELECT 1 FROM ne_10m_populated_places_simple_9 WHERE ST_Contains(CDB_XYZ_Extent(%d,%d,%d),the_geom_webmercator) limit 1)" % (tile[1], tile[2], tile[0])
        return json.loads(fetch(self.sql_api_url + "?q=" + urllib.quote_plus(sql), headers={'Host': 'dev.localhost.lan'}))['rows'][0]['?column?']

    def tilesForBBox(self, bbox, z):
        xmin, ymin, xmax, ymax = bbox
        l = []

        ll0 = (xmin, ymax)  # left top
        ll1 = (xmax, ymin)  # right bottom

        px0 = self.project_pixels(ll0,z)
        px1 = self.project_pixels(ll1,z)

        for x in range(int(px0[0]/self.tilesize),
                       int(px1[0]/self.tilesize)+1):
            if (x < 0) or (x >= 2**z):
                continue
            for y in range(int(px0[1]/self.tilesize),
                           int(px1[1]/self.tilesize)+1):
                if (y < 0) or (y >= 2**z):
                    continue
                if self.tms_scheme:
                    y = ((2**z-1) - y)
                l.append((z, x, y))
        return l

    def tiles(self, bbox, zoom, maxZoom):
        tiles = []
        boxtiles = self.tilesForBBox(bbox, zoom)
        tiles += boxtiles
        #print zoom, maxZoom
        if zoom < maxZoom:
            for t in boxtiles:
                if self.containsGeometry(t):
                    tiles += [x for x in self.tiles(self.tile_bbox(t), zoom + 1, maxZoom) if x not in tiles]
        return tiles

if __name__ == '__main__':
    p = CartoDBTiles(levels=[0, 7])
    bbox = (-180.0, -90.0, 180.0, 90.0)
    tiles = p.tileslist(bbox)
    zoom = defaultdict(int)
    for x in tiles:
        zoom[x[0]] += 1

    for z in sorted(zoom.items()):
        print "%02d - %d" % z

