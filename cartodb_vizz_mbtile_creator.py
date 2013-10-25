import logging
from landez import MBTilesBuilder
import sys
import urllib2
import urllib
import json


CDN_URL = 'api.cartocdn.com'

def fetch(url, data=None, headers={}):
    if data:
        pass
        #data = urllib.quote_plus(data)
    request = urllib2.Request(url, data, headers=headers)
    return urllib2.urlopen(request).read()

def get_layergroup_url(vizjson_url):
    vizjson = vizjson_url
    username = vizjson.split('.')[0].replace('http://', '')

    vizjson = json.loads(fetch(sys.argv[1]))
    layerdef = vizjson['layers'][1]['options']['layer_definition']
    layers = [ { "type": 'cartodb', 'ttl': 3600*24*265, "options": x['options'] } for x in layerdef['layers'] ]
    layerdef = json.dumps({ "version": "1.0.1", "layers": layers })
    layerid = json.loads(fetch('http://' + username + '.cartodb.com/tiles/layergroup', layerdef,  headers={ 'Content-Type': 'application/json' }))
    return 'http://' + username + ".cartodb.com/tiles/layergroup/" + layerid['layergroupid'] + "/{z}/{x}/{y}.png"

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "vizsjon_url max_zoom mbtiles [nthreads]"
        sys.exit()
    nthreads = 20
    if len(sys.argv) > 4:
        nthreads = int(sys.argv[4])

    logging.basicConfig(level=logging.DEBUG)
    template_url = get_layergroup_url(sys.argv[1])
    logging.info("%d threads" % nthreads)
    mb = MBTilesBuilder(tiles_url=template_url, filepath=sys.argv[3], thread_number=nthreads, errors_as_warnings=True)
    mb.add_coverage(
        bbox=(-180.0, -90.0, 180.0, 90.0),
        zoomlevels=[0, int(sys.argv[2])]
    )
    mb.run()
