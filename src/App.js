import "./App.css";
import { useState } from "react";
import SubmitHappiness from "./components/SubmitHappiness";

function App() {
  const [happiness, setHappiness] = useState(100);

  return (
    <>
      <SubmitHappiness setHappiness={setHappiness} happiness={happiness} />
    </>
  );
}

export default App;
