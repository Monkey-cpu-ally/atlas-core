import GenesisHub from "./genesis/GenesisHub";
import useAtlasVisualBridge from "./hooks/useAtlasVisualBridge";

function App() {
  const visualBridge = useAtlasVisualBridge();

  return (
    <div
      className="App"
      data-atlas-visual-status={visualBridge.status}
      data-atlas-last-event={visualBridge.lastEvent?.event || "none"}
    >
      <GenesisHub visualBridge={visualBridge} />
    </div>
  );
}

export default App;
