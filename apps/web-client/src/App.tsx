import { Map } from "@gps/ui-components";

export default function App() {
  return (
    <Map
      tileUrl={import.meta.env.VITE_TILE_URL}
      coverage={JSON.parse(import.meta.env.VITE_KSA_COVERAGE)}
      startingCenter={JSON.parse(import.meta.env.VITE_RIYADH_CENTER)}
    />
  );
}