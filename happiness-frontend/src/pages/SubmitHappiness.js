import LSUModal from "../components/LSUModal";
import React, { useState } from "react";
import "../App.css";
import Journal from "../media/journal-icon.svg";
import HappinessCommentModal from "../components/HappinessCommentModal";

export default function SubmitHappiness() {
  const [happiness, setHappiness] = useState(50);
  const [comment, setComment] = useState("");
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

  let formatHappinessNum = (happiness) => {
    if (happiness % 10 >= 5) {
      return (Math.floor(happiness / 10) + 0.5).toFixed(1);
    } else {
      return Math.floor(happiness / 10).toFixed(1);
    }
  };

  let getDate = () => {
    const daysOfWeek = [
      "Sunday",
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
    ];
    const today = new Date();
    const day = daysOfWeek[today.getDay()];
    const numDay = today.getDate();
    const month = today.getMonth() + 1;
    return `${day}, ${month}/${numDay}`;
  };

  const submitHappiness = () => {
    //TODO submit happiness with backend.
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
    // Background:
    <div
      className={`min-h-screen duration-500 bg-size-200 ${happinessColor(
        happiness
      )}`}
    >
      {/* Items */}
      <div className="flex flex-col justify-center items-center">
        {/* Prompt */}
        <>
          <h1 className="md:text-7xl text-5xl text-white md:text-stroke-3 text-stroke-2 text-center mt-5 font-roboto">
            <b>How are you feeling today?</b>
          </h1>
        </>

        {/* Today's Date */}
        <div className="bg-gray-200  rounded-3xl object-contain mt-5   p-3 border-gray-500 border-4">
          <p className="md:text-4xl text-3xl text-black text-center font-light">
            <b>{getDate()}</b>
          </p>
        </div>

        {/* Happy Face, Slider, and Happiness Number (Desktop only) */}
        <div className="flex flex-row items-center justify-center mobile-hidden">
          {/* Happy Face Decorator */}
          <div className="flex-1 flex-row ">
            <svg
              width="90"
              height="90"
              viewBox="0 0 256 256"
              className="mt-10 flex-1 mr-28"
            >
              <circle cx="128" cy="128" r="120" className="smile-head" />
              <circle cx="98" cy="94" r="13" />
              <circle cx="158" cy="94" r="13" />
              <path
                className="smile-mouth"
                d={`M80,${happinessNumberEdges(
                  happiness
                )}, Q128,${happinessNumberMiddle(
                  happiness
                )} 176,${happinessNumberEdges(happiness)}`}
              />
            </svg>
          </div>

          {/* Happiness Slider */}
          <input
            id="default-range"
            type="range"
            onChange={(e) => {
              setHappiness(e.target.value);
            }}
            className="w-40 md:w-72 h-2 rounded-lg appearance-none cursor-pointer dark:bg-white-300 scale-150 justify-center mt-20 flex-2"
          />

          {/* Happiness Number */}
          <p className="text-8xl text-white text-stroke-4 ml-28 mt-10 font-roboto flex-3 flex-row  ">
            <b>{formatHappinessNum(happiness)}</b>
          </p>
        </div>

        {/* Happiness Number Input Field (Mobile Only) */}
        <input
          className="mt-10 w-24 h-20 text-4xl text-center rounded-2xl bg-gray-100 focus:border-raisin-600 border-raisin-100 border-2 focus:border-4 md:hidden"
          type="number"
          placeholder="5.0"
          onChange={(e) => {
            // TODO fix input validation
            e.target.value === ""
              ? setHappiness(5.0)
              : setHappiness(e.target.value * 10);
          }}
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
