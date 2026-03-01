from rio_tiler.io import COGReader
import morecantile

def read_tile(url: str, x: int, y: int, z: int, **kw):
    with COGReader(url) as cog:
        return cog.tile(x, y, z, **kw)
    
def tile_intersects_coverage(x: int, y: int, z: int, coverage:list[float]) -> bool:
    tms = morecantile.tms.get("WebMercatorQuad")
    t = tms.bounds(x, y, z)
    west, south, east, north = coverage
    return not (t.right < west or t.left > east or t.top < south or t.bottom > north)
