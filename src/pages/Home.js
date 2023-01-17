import Welcome from "./Welcome";
import SubmitHappiness from "./SubmitHappiness";

export default function Home({ logged_in }) {
  if (logged_in) return <SubmitHappiness />;
  return <Welcome />;
}
