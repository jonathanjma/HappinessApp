import React, { useEffect, useState } from "react";

import "../App.css";
import SubmittedHappinessIcon from "../media/submitted-happiness-icon.svg";
import EditIcon from "../media/pencil-square-outline-icon.png"
import DynamicSmile from "../components/DynamicSmile";
import DateDropdown from "../components/DateDropdown";
import { useApi } from "../contexts/ApiProvider";
import { useQuery, useMutation } from "react-query";
import { useUser } from "../contexts/UserProvider";
import { Spinner } from "react-bootstrap";
import {PageState} from "../keys";
import HappinessEditor from "../components/HappinessEditor";

export default function SubmitHappiness() {
  // happiness represents how happy the user is on a scale of 0 to 10.
  // this value appears as a scale from one to ten for the user.
  // Variable invariant: This variable must be between 0 and 10, and can only be 0.5 between whole numbers.

  // Create an empty array to store the Date objects
  const dateList = [];
  initializeDateList(dateList);

  const [pageState, setPageState] = useState(PageState.UNSUBMITTED);
  const [happiness, setHappiness] = useState(5.0);
  const [comment, setComment] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [preEditHappiness, setPreEditHappiness] = useState(0);
  const [happinessId, setHappinessId] = useState(0);
  // When the user submits a day, we will store locally the submitted days so the UI can update accordingly.
  // This only stores submitted days in current session, when user refreshes the query will run again anyway.
  // const [submittedDays, setSubmittedDays] = useState([]);
  const { user } = useUser();
  const api = useApi();
  useEffect(() => {
      refetch();
      setComment("");
  }, [selectedIndex])
  const { isLoading, data, isError, refetch} = useQuery(
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
  const postHappinessMutation = useMutation({
    mutationFn: (newHappiness) => {
      return api.post("/happiness/", newHappiness);
    },
  });

  const editHappinessMutation = useMutation({
      mutationFn: (newHappiness) => {
          return api.put(`/happiness/${happinessId}`, newHappiness);
      },
  })

  // Keeps happiness in valid range
  useEffect(() => {
    if (happiness > 10 && happiness - 10 < 1) {
      setHappiness(10);
    } else if (happiness > 10) {
      setHappiness(happiness / 10);
    }
  }, [happiness]);

  // Checks if happiness is submitted after the query is finished
  useEffect(() => {
    if (isError) {
      return;
    }
    if (isLoading) {
      return;
    }
    checkSubmitted();
  }, [isLoading]);

  // When they change date we need to check again if happiness is submitted.
  useEffect(() => {
    checkSubmitted();
  }, [selectedIndex]);

  // Logic for checking whether happiness was submitted.
  const checkSubmitted = () => {
    if (isLoading) {
      return;
    }
    let wasFound = false;
    // First check the local session storage:
    // if (submittedDays.includes(formatDate(dateList[selectedIndex]))) {
    //   setPageState(PageState.SUBMITTED);
    //   return;
    // }
    data.forEach((happinessEntry) => {
      if (happinessEntry.timestamp === formatDate(dateList[selectedIndex])) {
        setHappiness(happinessEntry.value);
        setComment(happinessEntry.comment);
        setHappinessId(happinessEntry.id);
        wasFound = true;
        setPageState(PageState.SUBMITTED);
      }
    });
    if (!wasFound) {
      setPageState(PageState.UNSUBMITTED);
      setHappiness(5)
    }
  };

  const submitNewHappiness = () => {
      postHappinessMutation.mutate({
          value: happiness,
          comment: comment,
          timestamp: formatDate(dateList[selectedIndex]),
      });
      setPageState(PageState.SUBMITTED);
      // submittedDays.push(formatDate(dateList[selectedIndex]));
  }

  const editHappiness = () => {
      editHappinessMutation.mutate({
          value: happiness,
          comment: comment,
      });
      setPageState(PageState.SUBMITTED);
  }

  const EditButton = () => {
      return (
        <img src={EditIcon} width={50} height={50} className={"ml-8 hover:scale-110 hover:shadow-xl duration-100 hover:cursor-pointer"} onClick={() => {

          if (pageState === PageState.EDITING) {
              setPageState(PageState.SUBMITTED)
              console.log("Pre edit happiness: " + preEditHappiness)
              setHappiness(preEditHappiness)
          } else {
              setPageState(PageState.EDITING)
              console.log("Pre edit happinesss: " + preEditHappiness)
              setPreEditHappiness(happiness)
          }}} />
      )
  }

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
  console.log(`Page state = ${pageState}`)

  switch (pageState) {
    case PageState.SUBMITTED:
      return (
          <div
              className={`min-h-screen duration-500 bg-size-200 ${happinessColor(
                  happiness
              )}`}
          >
            <div className="flex items-center">
            <DateDropdown
                selectedIndex={selectedIndex}
                setSelectedIndex={setSelectedIndex}
                dateList={dateList}
            />
              <EditButton />
          </div>
            {/* Items */}
            <div className="flex flex-col justify-center items-center">



              <h1 className="md:text-7xl text-5xl text-white md:text-stroke-4 text-stroke-2 text-center mt-3 font-roboto md:px-10 px-2 w-9/12">
                <b>Happiness submitted for this day.</b>
              </h1>
              <img src={SubmittedHappinessIcon} className={"md:w-1/5 md:h-1/5 h-3/5 w-3/5 mt-10"} />
            </div>
          </div>
      );
    case PageState.UNSUBMITTED:
        console.log("this case")
      return (
          <div
              className={`min-h-screen duration-500 bg-size-200 ${happinessColor(
                  happiness
              )}`}
          >
              <div className="flex items-center">
                  <DateDropdown
                      selectedIndex={selectedIndex}
                      setSelectedIndex={setSelectedIndex}
                      dateList={dateList}
                  />
              </div>
              <HappinessEditor
                  happiness={happiness}
                  setHappiness={setHappiness}
                  comment={comment}
                  setComment={setComment}
                  pageMessage={"How are you feeling today?"}
                  pageState={pageState}
                  setPageState={setPageState}
                  onSubmitClick={submitNewHappiness}
              />
          </div>
      );

    case PageState.EDITING:
      return (
          <div
              className={`min-h-screen duration-500 bg-size-200 ${happinessColor(
                  happiness
              )}`}
          >
              <div className="flex items-center">
                  <DateDropdown
                      selectedIndex={selectedIndex}
                      setSelectedIndex={setSelectedIndex}
                      dateList={dateList}
                  />
                  <EditButton />

              </div>
              <HappinessEditor
                  happiness={happiness}
                  setHappiness={setHappiness}
                  comment={comment}
                  setComment={setComment}
                  pageMessage={"Edit your happiness"}
                  pageState={pageState}
                  setPageState={setPageState}
                  onSubmitClick={editHappiness}
              />
          </div>
      )
  }
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

export function happinessColor(happiness) {
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
export function formatHappinessNum(happiness) {
  if ((happiness * 10) % 10 >= 5) {
    return (Math.floor(happiness) + 0.5).toFixed(1);
  } else {
    return Math.floor(happiness).toFixed(1);
  }
}
