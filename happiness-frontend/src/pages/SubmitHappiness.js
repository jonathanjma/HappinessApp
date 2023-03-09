import LSUModal from "../components/LSUModal";
import React, {useEffect, useState} from "react";
import "../App.css";
import Journal from "../media/journal-icon.svg";
import HappinessCommentModal from "../components/HappinessCommentModal";
import DynamicSmile from "../components/DynamicSmile";

export default function SubmitHappiness() {
  // happiness represents how happy the user is on a scale of 0 to 10.
  // this value appears as a scale from one to ten for the user.
  // Variable invariant: This variable must be between 0 and 10, and can only be 0.5 between whole numbers.

  const [happiness, setHappiness] = useState(5.0);
  const [comment, setComment] = useState("");
  let happinessColor = (happiness) => {
    if (happiness < 1.0) {
      return "bg-red-700";
    } else if (happiness < 2.0) {
      return "bg-red-600";
    } else if (happiness < 3.0) {
      return "bg-yellow-500";
    } else if (happiness < 4.0) {
      return "bg-yellow-400";
    } else if (happiness < 6.0) {
      return "bg-yellow-300";
    } else if (happiness < 7.0) {
      return "bg-yellow-300";
    } else if (happiness < 8.0) {
      return "bg-green-400";
    } else if (happiness < 10.0) {
      return "bg-green-500";
    } else {
      return "bg-green-600";
    }
  };

  let formatHappinessNum = (happiness) => {
    if (happiness*10 % 10 >= 5) {
      return (Math.floor(happiness) + 0.5).toFixed(1);
    } else {
      return Math.floor(happiness).toFixed(1);
    }
  };

  useEffect(() => {
    if (happiness > 10 && happiness - 10 < 1) {
      setHappiness(10)
    }
    else if (happiness > 10) {
      setHappiness(happiness / 10)
    }
  }, [happiness])

  let getNumDay = () => {
    const today = new Date();
    return today.getDate();
  };

  let getWeekDay = () => {
    const daysOfWeek = [
      "SUN",
      "MON",
      "TUE",
      "WED",
      "THU",
      "FRI",
      "SAT",
    ];
    const today = new Date();
    return daysOfWeek[today.getDay()];
  }

  const submitHappiness = () => {
    //TODO submit happiness with backend.
  };

  return (
    // Background:
    <div
      className={`min-h-screen duration-500 bg-size-200 ${happinessColor(
        happiness
      )}`}
    >
      {/* Items */}
      <div className="flex flex-col justify-center items-center">
        {/* Today's Date */}
        <div className="mr-auto flex flex-col ml-3 mt-3 drop-shadow-md ">
          <div className="h-1/2 w-full bg-red-500 p-2 rounded-t-2xl ">
            <p className="md:text-2xl text-xl text-white text-center font-medium -mb-1">
              {getWeekDay()}
            </p>
          </div>
          <div className="h-1/2 w-full bg-white p-2 rounded-b-2xl">
            <p className="md:text-4xl text-xl text-red text-center font-medium -mb-1 -mt-1">
              {getNumDay()}
            </p>
          </div>
        </div>

        {/* Prompt */}
        <>
          <h1 className="md:text-7xl text-5xl text-white md:text-stroke-3 text-stroke-2 text-center mt-3 font-roboto">
            <b>How are you feeling today?</b>
          </h1>
        </>






        {/* Happy Face, Slider, and Happiness Number (Desktop only) */}
        <div className="flex flex-row items-center justify-center mobile-hidden">
          {/* Happy Face Decorator */}
          <span className="mr-28 mt-10">
            <DynamicSmile happiness={happiness} />
          </span>
          {/* Happiness Slider */}
          <input
            id="default-range"
            type="range"
            onChange={(e) => {
              setHappiness(e.target.value / 10);
            }}
            className="w-40 md:w-72 h-2 rounded-lg appearance-none cursor-pointer dark:bg-white-300 scale-150 mt-20"
          />

          {/* Happiness Number */}
          {/* TODO the fixed width causes it to be off center,
           but good enough for now I guess */}
          <p className="text-8xl text-white text-stroke-4 mt-10 ml-28 font-roboto flex-none flex-row w-40">
            <b>{formatHappinessNum(happiness)}</b>
          </p>
        </div>

        {/* Happiness Number Input Field (Mobile Only) */}
        <input
          className="mt-10 w-24 h-20 text-4xl text-center rounded-2xl bg-gray-100 focus:border-raisin-600 border-raisin-100 border-2 focus:border-4 md:hidden"
          type="number"
          value={happiness}
          placeholder=""
          onChange={(e) => {
            setHappiness(parseFloat(e.target.value))
          }}
          onBlur={() => {
            if ((happiness * 10) % 10 >= 5) {
              setHappiness(Math.floor(happiness) + 0.5)
            } else if (isNaN(happiness)) {
              setHappiness(5)
            } else {
              setHappiness(Math.floor(happiness))
            }
          }
          }
        />

        {/* Happiness Comment Box */}
        <>
          <textarea
            id="large-input"
            value={comment}
            className="md:w-5/12 w-3/4 p-4 bg-gray-200 rounded mt-10 border-raisin-100 outline-none focus:border-raisin-200 border-2 focus:border-4"
            placeholder="Add a comment about the day"
            onChange={(e) => {
              setComment(e.target.value);
            }}
          />
        </>

        {/* Submit button: */}
        <>
          <button
            onClick={submitHappiness}
            className="flex-1 scale-150 text-white bg-gradient-to-r from-raisin-500 via-raisin-600 to-raisin-700 shadow-lg font-roboto font-semibold rounded-lg text-sm px-5 outline-none py-2.5 text-center mr-2 mb-2 mt-9"
          >
            Submit
          </button>
        </>
      </div>
    </div>
  );
}
