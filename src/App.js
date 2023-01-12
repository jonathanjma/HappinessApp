import "./App.css";
import { useState } from "react";
import SubmitHappiness from "./pages/SubmitHappiness";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Welcome from "./pages/Welcome";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  const [happiness, setHappiness] = useState(50);

  return (
    <>
      <Welcome />
      {/* <SubmitHappiness setHappiness={setHappiness} happiness={happiness} /> */}
    </>
  );
}

export default App;
