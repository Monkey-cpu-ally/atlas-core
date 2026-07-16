import "@/App.css";
import "@/hud-clean-mode.css";
import HUDInterface from "./components/HUDInterface";
import CoreChatBridge from "./components/HUD/CoreChatBridge";

function App() {
  return (
    <div className="App">
      <HUDInterface />
      <CoreChatBridge />
    </div>
  );
}

export default App;
