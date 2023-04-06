import LSUModal from "../components/LSUModal";
import React, { useEffect, useState } from "react";
import "../App.css";
import Journal from "../media/journal-icon.svg";
import HappinessCommentModal from "../components/HappinessCommentModal";
import DynamicSmile from "../components/DynamicSmile";
import DateDropdown from "../components/DateDropdown";

export default function SubmitHappiness() {
  // happiness represents how happy the user is on a scale of 0 to 10.
  // this value appears as a scale from one to ten for the user.
  // Variable invariant: This variable must be between 0 and 10, and can only be 0.5 between whole numbers.


  // Create an empty array to store the Date objects
  const dateList = [];
  initializeDateList(dateList);



  const [happiness, setHappiness] = useState(5.0);
  const [comment, setComment] = useState("");
  const [date, setDate] = useState(new Date());
  const [selectedIndex, setSelectedIndex] = useState(0);


  const formatHappinessNum = (happiness) => {
    if (happiness * 10 % 10 >= 5) {
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



  const submitHappiness = () => {
    // const {
    //   isLoading: isLoadingH,
    //   data: dataH,
    //   error: errorH,
    // } = useQuery("stats happiness data", () =>
    //   api
    //     .post("/happiness/", {
    //       "value": happiness,
    //       "comment": comment,
    //       "timestamp": dateList[selectedIndex]
    //     })
    //     .then((res) => res.data)
    // );
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
        <DateDropdown selectedIndex={selectedIndex} setSelectedIndex={setSelectedIndex} dateList={dateList} />

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
function initializeDateList(dateList) {
  const today = new Date();

  // Loop through the past 7 days (including today)
  for (let i = 0; i < 7; i++) {
    // Create a new Date object representing the current day in the loop
    const date = new Date(today.getFullYear(), today.getMonth(), today.getDate() - i);

    // Check if the current date is the first day of the month
    if (date.getDate() === 1 && i !== 0) {
      // If it is, adjust the month of the previous date in the array
      let previousDate = dateList[i - 1];
      while (previousDate.getMonth() !== date.getMonth()) {
        previousDate.setMonth(previousDate.getMonth() - 1);
      }
    }

    // Add the new Date object to the array
    dateList.push(date);
  }
}

function happinessColor(happiness) {
  switch (true) {
    case (happiness < 1.0):
      return "bg-red-700";
    case (happiness < 2.0):
      return "bg-red-600";
    case (happiness < 3.0):
      return "bg-yellow-500";
    case (happiness < 4.0):
      return "bg-yellow-400";
    case (happiness < 6.0):
      return "bg-yellow-300";
    case (happiness < 8.0):
      return "bg-green-400";
    case (happiness < 10.0):
      return "bg-green-500";
    default:
      return "bg-green-600";
  }
}
