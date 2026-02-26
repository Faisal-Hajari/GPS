import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const TILE_URL = "/stac/tiles/{z}/{x}/{y}";
const SAUDI_ARABIA_BOUNDS: [number, number, number, number] = [32.5, 14.3, 57.7, 34.2];
const RIYADH_CENTER: [number, number] = [46.6753, 24.7136];
const MIN_ZOOM: number = 5; 
const TILE_SIZE: number = 256;
const STARTING_ZOOM: number = 10;
const STARTING_CENTER: [number, number] = RIYADH_CENTER;

export default function Map() {
    const containerRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        const map = new maplibregl.Map({
            container: containerRef.current!,
            style: {
                version: 8,
                sources: {
                    osm: {
                        type: "raster",
                        tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                        tileSize: TILE_SIZE,
                        attribution: "© OpenStreetMap contributors",
                        minzoom: MIN_ZOOM, 
                        bounds: SAUDI_ARABIA_BOUNDS,
                    },
                    sentinel: {
                        type: "raster",
                        tiles: [TILE_URL],
                        tileSize: TILE_SIZE,
                        minzoom: MIN_ZOOM, 
                        bounds: SAUDI_ARABIA_BOUNDS,
                    },
                },
                layers: [
                    {
                        id: "osm-layer",
                        type: "raster",
                        source: "osm"
                    },
                    {
                        id: "sentinel-layer",
                        type: "raster",
                        source: "sentinel",
                        paint: {
                            "raster-opacity": 1.0
                        },
                    },
                ],
            },
            center: STARTING_CENTER,
            zoom: STARTING_ZOOM,
            minZoom: MIN_ZOOM,
            maxBounds: SAUDI_ARABIA_BOUNDS,
        });
        return () => map.remove();
    }, []);
    return (
        <div ref={containerRef} style={{ width: "100vw", height: "100vh" }} />
    );
}