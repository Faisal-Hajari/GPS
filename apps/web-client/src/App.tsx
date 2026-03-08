import { MapWithToggle } from "@gps/ui-components";
import type { MapLayer } from "@gps/ui-components";

const layers: [MapLayer, MapLayer] = [
  {
    id: "Map",
    label: "Map",
    source: { type: "raster", tiles: [import.meta.env.VITE_TILE_URL_1], tileSize: 256 },
  },
  {
    id: "Satellite",
    label: "Satellite",
    source: { type: "raster", tiles: [import.meta.env.VITE_TILE_URL_2], tileSize: 256 },
  },
];

export default function App() {
  return (
    <MapWithToggle
      layers={layers}
      startingCenter={JSON.parse(import.meta.env.VITE_RIYADH_CENTER)}
      maxBounds={JSON.parse(import.meta.env.VITE_KSA_COVERAGE)}
    />
  );
}