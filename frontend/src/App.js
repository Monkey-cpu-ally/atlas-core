import "@/App.css";
import HUDInterface from "./components/HUDInterface";
import GenesisHub from "./genesis/GenesisHub";
import useAtlasVisualBridge from "./hooks/useAtlasVisualBridge";

function App() {
  const visualBridge = useAtlasVisualBridge();
  const genesisEnabled = process.env.REACT_APP_ATLAS_GENESIS_HUB === "true";

  return (
    <div
      className="App"
      data-atlas-visual-status={visualBridge.status}
      data-atlas-last-event={visualBridge.lastEvent?.event || "none"}
    >
      {genesisEnabled ? (
        <GenesisHub visualBridge={visualBridge} />
      ) : (
        <HUDInterface visualBridge={visualBridge} />
      )}
    </div>
  );
}

export default App;
