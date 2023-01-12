import WelcomeCarousel from "../components/WelcomeCarousel";
import {useNavigate} from "react-router-dom";

export default function Welcome() {
  const navigate = useNavigate();

  const onSubmit = (ev) => {
    ev.preventDefault();
    navigate("/happiness");
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
      <button
        onClick={onSubmit}
        className=" bg-gradient-to-br from-tangerine-50 to-raisin-50 hover:scale-110 hover:drop-shadow-xl hover:bg-raisin-400 drop-shadow-md duration-200 rounded-md mb-15"
      >
        <div className="m-2 text-3xl hover:anime-gradient hover:font-bold font-semibold">
          Show Me More
        </div>
      </button>
    </div>
  );
}
