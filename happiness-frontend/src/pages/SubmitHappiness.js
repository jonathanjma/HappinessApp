import React, { useEffect, useState } from "react";

import "../App.css";
import SubmittedHappinessIcon from "../media/submitted-happiness-icon.svg";
import DynamicSmile from "../components/DynamicSmile";
import DateDropdown from "../components/DateDropdown";
import { useApi } from "../contexts/ApiProvider";
import { useQuery, useMutation } from "react-query";
import { useUser } from "../contexts/UserProvider";
import { Spinner } from "react-bootstrap";

export default function SubmitHappiness() {
  // happiness represents how happy the user is on a scale of 0 to 10.
  // this value appears as a scale from one to ten for the user.
  // Variable invariant: This variable must be between 0 and 10, and can only be 0.5 between whole numbers.

  // Create an empty array to store the Date objects
  const dateList = [];
  initializeDateList(dateList);

  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [happiness, setHappiness] = useState(5.0);
  const [comment, setComment] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  // When the user submits a day, we will store locally the submitted days so the UI can update accordingly.
  // This only stores submitted days in current session, when user refreshes the query will run again anyway.
  const [submittedDays, setSubmittedDays] = useState([]);
  const { user } = useUser();
  const api = useApi();
  const { isLoading, data, isError } = useQuery(
    `happiness for ${user.id}`,
    () => {
      return api
        .get("/happiness/", {
          start: formatDate(dateList[6]),
          end: formatDate(dateList[0]),
        })
        .then((res) => res.data);
    }
  );
  const happinessMutation = useMutation({
    mutationFn: (newHappiness) => {
      return api.post("/happiness/", newHappiness);
    },
  });

  useEffect(() => {
    if (happiness > 10 && happiness - 10 < 1) {
      setHappiness(10);
    } else if (happiness > 10) {
      setHappiness(happiness / 10);
    }
  }, [happiness]);

  useEffect(() => {
    if (isError) {
      return;
    }
    if (isLoading) {
      return;
    }
    checkSubmitted();
  }, [isLoading]);

  useEffect(() => {
    checkSubmitted();
  }, [selectedIndex]);

  const checkSubmitted = () => {
    if (isLoading) {
      return;
    }
    let wasFound = false;
    // First check the local session storage:
    if (submittedDays.includes(formatDate(dateList[selectedIndex]))) {
      setHasSubmitted(true);
      return;
    }
    data.forEach((happinessEntry) => {
      if (happinessEntry.timestamp === formatDate(dateList[selectedIndex])) {
        setHappiness(happinessEntry.value);
        wasFound = true;
        setHasSubmitted(true);
      }
    });
    if (!wasFound) {
      setHasSubmitted(false);
      setHappiness(5)
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-row items-center justify-center ">
        <Spinner />
      </div>
    );
  }

  if (isError) {
    return (
      <span>
        Error loading data (try to logout and log back in, or alert the devs{" "}
        <a href={"https://forms.gle/n3aFRA9fmpM22UdEA"}>here</a>)
      </span>
    );
  }

  return (
    // Submitted happiness view:
    hasSubmitted ? (
      <div
        className={`min-h-screen duration-500 bg-size-200 ${happinessColor(
          happiness
        )}`}
      >
        {/* Items */}
        <div className="flex flex-col justify-center items-center">
          <DateDropdown
            selectedIndex={selectedIndex}
            setSelectedIndex={setSelectedIndex}
            dateList={dateList}
          />

          <h1 className="md:text-7xl text-5xl text-white md:text-stroke-4 text-stroke-2 text-center mt-3 font-roboto md:px-10 px-2 w-5/8">
            <b>Happiness already submitted for this day.</b>
          </h1>
          <img src={SubmittedHappinessIcon} className={"md:w-1/5 md:h-1/5 h-2/5 w-2/5 mt-10"} />
        </div>
      </div>
    ) : (
      //       Default submit happiness view:
      <div
        className={`min-h-screen duration-500 bg-size-200 ${happinessColor(
          happiness
        )}`}
      >
        {/* Items */}
        <div className="flex flex-col justify-center items-center">
          {/* Today's Date */}
          <DateDropdown
            selectedIndex={selectedIndex}
            setSelectedIndex={setSelectedIndex}
            dateList={dateList}
          />

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
                  onMouseUp={(e) => {
                    setHappiness(formatHappinessNum(e.target.value / 10));
                  }}
                  className="w-40 md:w-72 h-2 rounded-lg appearance-none cursor-pointer dark:bg-white-300 scale-150 mt-20"
              />

              {/* Happiness Number */}
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
                  if (e.target.value < 0) {
                    setHappiness(0)}
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
              onClick={() => {
                happinessMutation.mutate({
                  value: happiness,
                  comment: comment,
                  timestamp: formatDate(dateList[selectedIndex]),
                });
                setHasSubmitted(true);
                submittedDays.push(formatDate(dateList[selectedIndex]));
              }}
              className="flex-1 scale-150 text-white bg-gradient-to-r from-raisin-500 via-raisin-600 to-raisin-700 shadow-lg font-roboto font-semibold rounded-lg text-sm px-5 outline-none py-2.5 text-center mr-2 mb-2 mt-9"
            >
              Submit
            </button>
          </>
        </div>
      </div>
    )
  );
}

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function initializeDateList(dateList) {
  const today = new Date();

  // Loop through the past 7 days (including today)
  for (let i = 0; i < 7; i++) {
    // Create a new Date object representing the current day in the loop
    const date = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate() - i
    );

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
    case happiness < 1.0:
      return "bg-red-700";
    case happiness < 2.0:
      return "bg-red-600";
    case happiness < 3.0:
      return "bg-yellow-500";
    case happiness < 4.0:
      return "bg-yellow-400";
    case happiness < 6.0:
      return "bg-yellow-300";
    case happiness < 8.0:
      return "bg-green-400";
    case happiness < 10.0:
      return "bg-green-500";
    default:
      return "bg-green-600";
  }
}
function formatHappinessNum(happiness) {
  if ((happiness * 10) % 10 >= 5) {
    return (Math.floor(happiness) + 0.5).toFixed(1);
  } else {
    return Math.floor(happiness).toFixed(1);
  }
}
