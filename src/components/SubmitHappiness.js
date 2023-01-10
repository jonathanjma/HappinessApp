import { Link } from "react-router-dom";
import LSUModel from "./LSUModal";
export default function SubmitHappiness(props) {
  console.log(props.happiness);
  let happinessColor = (happiness) => {
    if (happiness < 10) {
      return "bg-red-700";
    } else if (happiness < 20) {
      return "bg-red-600";
    } else if (happiness < 30) {
      return "bg-yellow-500";
    } else if (happiness < 40) {
      return "bg-yellow-400";
    } else if (happiness < 60) {
      return "bg-yellow-300";
    } else if (happiness < 70) {
      return "bg-yellow-300";
    } else if (happiness < 80) {
      return "bg-green-400";
    } else if (happiness < 100) {
      return "bg-green-500";
    } else {
      return "bg-green-600";
    }
  };
  let happinessNumberEdges = (happiness) => {
    //Saddest point: 200
    //Happiest point: 160
    return 190 - (happiness / 10) * 4;
  };
  let happinessNumberMiddle = (happiness) => {
    //Saddest point: 160
    //Happiest point: 200
    return 150 + (happiness / 10) * 4;
  };

  return (
    <div
      className={`min-h-screen duration-500 bg-size-200 ${happinessColor(
        props.happiness
      )}`}
    >
      <div className="flex flex-col justify-center items-center ">
        {/* Prompt */}
        <p className="text-7xl text-white text-stroke-3 text-center mt-5 font-roboto">
          <b>How are you feeling today?</b>
        </p>
        {/* Happiness slider */}
        <input
          id="default-range"
          type="range"
          onChange={(e) => {
            props.setHappiness(e.target.value);
          }}
          className="w-1/2 h-2 rounded-lg appearance-none cursor-pointer dark:bg-white-300 scale-150 flex-col justify-center mt-20"
        />
        {/* Happiness number */}
        <p className="flex-1 text-8xl text-white text-stroke-4 mt-5">
          <b>{Math.floor(props.happiness / 10)}</b>
        </p>
        {/* Smiley Face */}
        <svg
          width="256"
          height="256"
          viewBox="0 0 256 256"
          className="mt-10 flex-1"
        >
          <circle cx="128" cy="128" r="120" className="smile-head" />
          <circle cx="98" cy="94" r="12" />
          <circle cx="158" cy="94" r="12" />
          <path
            className="smile-mouth"
            d={`M80,${happinessNumberEdges(
              props.happiness
            )}, Q128,${happinessNumberMiddle(
              props.happiness
            )} 176,${happinessNumberEdges(props.happiness)}`}
          />
        </svg>

        {/* Submit button: */}
        <LSUModel />
      </div>
    </div>
  );
}
