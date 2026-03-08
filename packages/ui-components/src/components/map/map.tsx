import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import type { RasterSourceSpecification } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

export interface MapLayer {
    id: string;
    label: string;
    source: RasterSourceSpecification;
}

export interface MapProps {
    layers: MapLayer[];
    activeLayer: string;
    minZoom?: number;
    startingZoom?: number;
    startingCenter?: [number, number];
    maxBounds?: [number, number, number, number];
    maxParallelImageRequests?: number;
}

export default function Map({
    layers,
    activeLayer,
    minZoom = 5,
    startingZoom = 10,
    startingCenter = [46.6753, 24.7136],
    maxBounds,
    maxParallelImageRequests = 32,
}: MapProps) {
    maplibregl.setMaxParallelImageRequests(maxParallelImageRequests);
    const containerRef = useRef<HTMLDivElement>(null);
    const mapRef = useRef<maplibregl.Map | null>(null);

    useEffect(() => {
        const map = new maplibregl.Map({
            container: containerRef.current!,
            style: {
                version: 8,
                sources: Object.fromEntries(layers.map(l => [l.id, l.source])),
                layers: layers.map(l => ({
                    id: l.id,
                    type: "raster" as const,
                    source: l.id,
                })),
            },
            center: startingCenter,
            zoom: startingZoom,
            minZoom,
            ...(maxBounds !== undefined && { maxBounds }),
        });
        mapRef.current = map;
        return () => map.remove();
    }, []);

    useEffect(() => {
        const map = mapRef.current;
        if (!map) return;
        const applyVisibility = () => {
            layers.forEach(l => {
                map.setLayoutProperty(l.id, "visibility", l.id === activeLayer ? "visible" : "none");
            });
        };
        if (map.isStyleLoaded()) {
            applyVisibility();
        } else {
            map.once("load", applyVisibility);
        }
    }, [activeLayer]);

    return <div ref={containerRef} style={{ width: "100%", height: "100%" }} />;
}