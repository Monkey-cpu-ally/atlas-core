import "@/App.css";
import "@/hud-clean-mode.css";
import HUDInterface from "./components/HUDInterface";
import CoreChatBridge from "./components/HUD/CoreChatBridge";
import WorkspaceController from "./components/workspaces/WorkspaceController";
import HermesPresenceBridge from "./components/workspaces/HermesPresenceBridge";

function App() {
  return (
    <div className="App">
      <HUDInterface />
      <CoreChatBridge />
      <HermesPresenceBridge />
      <WorkspaceController />
    </div>
  );
}

export default App;
