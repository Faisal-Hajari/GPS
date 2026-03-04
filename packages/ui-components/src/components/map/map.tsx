import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";


interface MapProps {
    tileUrl: string;
    coverage: [number, number, number, number];
    minZoom?: number;
    tileSize?: number;
    startingZoom?: number;
    startingCenter?: [number, number];
    maxParallelImageRequests?: number;
}


export default function Map({ tileUrl, coverage, minZoom = 5, tileSize = 256, startingZoom = 10, startingCenter = [46.6753, 24.7136], maxParallelImageRequests = 32 }: MapProps) {
    maplibregl.setMaxParallelImageRequests(maxParallelImageRequests);
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
                        tileSize: tileSize,
                        attribution: "© OpenStreetMap contributors",
                        minzoom: minZoom,
                        bounds: coverage,
                    },
                    sentinel: {
                        type: "raster",
                        tiles: [tileUrl],
                        tileSize: tileSize,
                        minzoom: minZoom,
                        bounds: coverage,
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
            center: startingCenter,
            zoom: startingZoom,
            minZoom: minZoom,
            maxBounds: coverage,
        });
        return () => map.remove();
    }, []);
    return (
        <div ref={containerRef} style={{ width: "100vw", height: "100vh" }} />
    );
}