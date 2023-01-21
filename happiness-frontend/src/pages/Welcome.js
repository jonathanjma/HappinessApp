import WelcomeCarousel from "../components/WelcomeCarousel";
import { Link } from "react-router-dom";
import LSUModal from "../components/LSUModal";

export default function Welcome(props) {
  let logIn = () => {
    props.setIsLoggedIn(true);
  };

  return (
    // Root div
    <div className="bg-raisin-700 min-h-screen grid place-items-center bg-cover bg-center">
      {/* Main animated text */}
      <h1 className="font-Rubik text-tangerine-50 text-6xl text-center">
        <b>
          <span className="anime-gradient">Happiness</span> App
        </b>
      </h1>
      {/* Carousel containing information about the site */}
      <WelcomeCarousel />
      {/* Button to continue */}
      <LSUModal />
    </div>
  );
}
