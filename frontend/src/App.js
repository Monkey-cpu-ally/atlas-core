import "@/App.css";
import "@/hud-clean-mode.css";
import HUDInterface from "./components/HUDInterface";
import CoreChatBridge from "./components/HUD/CoreChatBridge";
import HUDErrorBoundary from "./components/HUD/HUDErrorBoundary";
import WorkspaceController from "./components/workspaces/WorkspaceController";
import HermesPresenceBridge from "./components/workspaces/HermesPresenceBridge";

function App() {
  return (
    <div className="App">
      <HUDErrorBoundary>
        <HUDInterface />
        <CoreChatBridge />
        <HermesPresenceBridge />
        <WorkspaceController />
      </HUDErrorBoundary>
    </div>
  );
}

export default App;
