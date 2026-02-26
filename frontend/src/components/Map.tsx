import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const TILE_URL = "/stac/tiles/{z}/{x}/{y}";
const COVERAGE: [number, number, number, number] = JSON.parse(import.meta.env.VITE_COVERAGE);
const RIYADH_CENTER: [number, number] = [46.6753, 24.7136];
const MIN_ZOOM: number = 5; 
const TILE_SIZE: number = 256;
const STARTING_ZOOM: number = 10;
const STARTING_CENTER: [number, number] = RIYADH_CENTER;
const MAX_PARALLEL_IMAGE_REQUESTS: number = 32;
maplibregl.setMaxParallelImageRequests(MAX_PARALLEL_IMAGE_REQUESTS);

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
                        bounds: COVERAGE,
                    },
                    sentinel: {
                        type: "raster",
                        tiles: [TILE_URL],
                        tileSize: TILE_SIZE,
                        minzoom: MIN_ZOOM, 
                        bounds: COVERAGE,
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
            maxBounds: COVERAGE,
        });
        return () => map.remove();
    }, []);
    return (
        <div ref={containerRef} style={{ width: "100vw", height: "100vh" }} />
    );
}