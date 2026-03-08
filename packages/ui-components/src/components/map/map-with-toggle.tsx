import { useState } from "react";
import { Map, LayerToggleButton } from "@gps/ui-components";
import type { MapLayer, MapProps } from "@gps/ui-components";

interface MapWithToggleProps extends Omit<MapProps, "activeLayer"> {
    layers: [MapLayer, MapLayer];
    initialActiveLayer?: string;
}

export default function MapWithToggle({ layers, initialActiveLayer, ...mapProps }: MapWithToggleProps) {
    const [activeLayer, setActiveLayer] = useState(initialActiveLayer ?? layers[0].id);

    const toggleOptions = [
        { value: layers[0].id, label: layers[0].label },
        { value: layers[1].id, label: layers[1].label },
    ] as [{ value: string; label: string }, { value: string; label: string }];

    return (
        <div style={{ position: "relative", width: "100vw", height: "100vh" }}>
            <Map {...mapProps} layers={layers} activeLayer={activeLayer} />
            <div style={{ position: "absolute", top: 12, left: "50%", transform: "translateX(-50%)", zIndex: 1 }}>
                <LayerToggleButton
                    options={toggleOptions}
                    active={activeLayer}
                    onChange={setActiveLayer}
                />
            </div>
        </div>
    );
}