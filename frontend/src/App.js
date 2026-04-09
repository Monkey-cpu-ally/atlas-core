import { useState, useRef, useCallback, useEffect } from "react";
import "@/App.css";
import HUDInterface from "./components/HUDInterface";

function App() {
  return (
    <div className="App">
      <HUDInterface />
    </div>
  );
}

export default App;
