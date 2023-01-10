import "./App.css";
import { useState } from "react";
import SubmitHappiness from "./components/SubmitHappiness";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function App() {
  const [happiness, setHappiness] = useState(50);

  return (
    <>
      <SubmitHappiness happiness={happiness} setHappiness={setHappiness} />
    </>
  );
}

export default App;
