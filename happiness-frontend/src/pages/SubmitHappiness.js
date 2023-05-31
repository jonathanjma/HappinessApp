import React, { useEffect, useReducer, useState } from "react";

import "../App.css";
import SubmittedHappinessIcon from "../media/submitted-happiness-icon.svg";
import EditIcon from "../media/pencil-square-outline-icon.png";
import TrashIcon from "../media/recycle-bin-line-icon.svg"
import DynamicSmile from "../components/submitHappiness/DynamicSmile";
import DateDropdown from "../components/submitHappiness/DateDropdown";
import { useApi } from "../contexts/ApiProvider";
import { useQuery, useMutation } from "react-query";
import { useUser } from "../contexts/UserProvider";
import { Spinner } from "react-bootstrap";
import { PageState } from "../keys";
import HappinessEditor from "../components/submitHappiness/HappinessEditor";
import ConfirmModal from "../components/ConfirmModal";


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
  const [happinessId, setHappinessId] = useState(-1);
  const [confirmDeleteShowing, setConfirmDeleteShowing] = useState(false);
  const [confirmSubmitShowing, setConfirmSubmitShowing] = useState(false);
  // When the user submits a day, we will store locally the submitted days so the UI can update accordingly.
  // This only stores submitted days in current session, when user refreshes the query will run again anyway.
  // const [submittedDays, setSubmittedDays] = useState([]);
  const { user } = useUser();
  const api = useApi();
  useEffect(() => {
    refetch();
    setComment("");
  }, [selectedIndex]);
  const { isLoading, data, isError, refetch } = useQuery(
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

  const deleteHappinessMutation = useMutation({
    mutationFn: () => {
      return api.delete(`/happiness/${happinessId}`);
    },
  });

  const editHappinessMutation = useMutation({
    mutationFn: (newHappiness) => {
      return api.put(`/happiness/${happinessId}`, newHappiness);
    },
  });

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
      setPageState(PageState.ERROR);
    }
    if (isLoading) {
      setPageState(PageState.LOADING);
    }
    checkSubmitted();
  }, [isLoading, isError]);

  // When they change date we need to check again if happiness is submitted.
  useEffect(() => {
    console.log("Checking data")
    checkSubmitted();
  }, [selectedIndex, data]);


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
        console.log("set happiness id")
        setHappinessId(happinessEntry.id);
        wasFound = true;
        setPageState(PageState.SUBMITTED);
      }
    });
    if (!wasFound) {
      setPageState(PageState.UNSUBMITTED);
      setHappiness(5);
    }
  };

  useEffect(() => {
    async function updateScreen() {
      if (postHappinessMutation.isSuccess || editHappinessMutation.isSuccess
        || deleteHappinessMutation.isSuccess) {
        setPageState(PageState.LOADING);
        await refetch();
        checkSubmitted();
        setPageState(PageState.SUBMITTED);
      }
    }
    updateScreen();
  }, [postHappinessMutation.isSuccess, editHappinessMutation.isSuccess, deleteHappinessMutation.isSuccess])
  // TODO happiness id's are not being updated properly, causing delete
  // request to try to delete the wrong id
  const submitNewHappiness = async () => {
    // Weird math but avoids floating point rounding errors (hopefully)
    if (happiness % 0.5 !== 0) {
      setHappiness(formatHappinessNum(happiness));
    }
    postHappinessMutation.mutate({
      value: formatHappinessNum(happiness),
      comment: comment,
      timestamp: formatDate(dateList[selectedIndex]),
    });
  };

  const editHappiness = async () => {
    if (happiness % .5 !== 0) {
      setHappiness(formatHappinessNum(happiness))
    }
    editHappinessMutation.mutate({
      value: formatHappinessNum(happiness),
      comment: comment,
    });
  };

  const EditButton = () => {
    return (
      <img
        src={EditIcon}
        width={50}
        height={50}
        className={
          "ml-8 hover:scale-110 hover:shadow-xl duration-100 hover:cursor-pointer"
        }
        onClick={() => {
          if (pageState === PageState.EDITING) {
            setPageState(PageState.SUBMITTED);
            // console.log("Pre edit happiness: " + preEditHappiness);
            setHappiness(preEditHappiness);
          } else {
            setPageState(PageState.EDITING);
            // console.log("Pre edit happinesss: " + preEditHappiness);
            setPreEditHappiness(happiness);
          }
        }}
      />
    );
  };

  const DeleteButton = () => {

    return (
      <>
        <img src={TrashIcon} className="bg-white p-2 ml-3 rounded-md hover:scale-110 hover:shadow-xl duration-100 hover:cursor-pointer border-2 border-solid" width={50} height={50} onClick={() => {
          setConfirmDeleteShowing(true)
        }} />
        <ConfirmModal
          heading={<div className="font-semibold font-sans text-2xl">Are you sure you want to continue?</div>}
          body={<>
            <p>
              You are deleting happiness for {" "}
              <b>{`${formatFullDate(dateList[selectedIndex])}`}</b>

            </p>
          </>}
          show={confirmDeleteShowing}
          setShow={setConfirmDeleteShowing}
          onConfirm={async () => {
            console.log("Deleting happiness")
            deleteHappinessMutation.mutate();
            setPageState(PageState.LOADING)
            await refetch();
            setPageState(PageState.UNSUBMITTED);
          }}
        />
      </>

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
  // console.log(`Page state = ${pageState}`);

  switch (pageState) {
    case PageState.SUBMITTED:
      return (
        <div
          className={`fullbg duration-500 bg-size-200 ${happinessColor(
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
            <DeleteButton />
          </div>
          {/* Items */}
          <div className="flex flex-col justify-center items-center">
            <h1 className="md:text-7xl text-5xl text-white md:text-stroke-4 text-stroke-2 text-center mt-3 font-roboto md:px-10 px-2 w-9/12">
              <b>Happiness submitted for this day.</b>
            </h1>
            <img
              src={SubmittedHappinessIcon}
              className={"md:w-1/5 md:h-1/5 h-3/5 w-3/5 mt-10"}
            />
          </div>
        </div>
      );
    case PageState.UNSUBMITTED:
      return (
        <div
          className={`fullbg duration-500 bg-size-200 ${happinessColor(
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
            onSubmitClick={() => {
              const hours = (new Date()).getHours();
              if (hours < 11 && selectedIndex === 0) {
                setConfirmSubmitShowing(true);
              } else {
                submitNewHappiness();
              }
            }}
          />
          <ConfirmModal
            heading={<div className="font-semibold font-sans text-2xl">Are you sure you want to continue?</div>}
            body={<>
              <p>
                You are already submitting happiness at
                {`${(new Date()).getHours() === 0 ? ` 12:${(new Date().getMinutes())} AM ` : ` ${(new Date()).getHours()}:${new Date().getMinutes()} AM `}`}
                for <br /> <b>{`${formatFullDate(dateList[selectedIndex])}`}</b> . Are you sure?
              </p>
            </>}
            show={confirmSubmitShowing}
            setShow={setConfirmSubmitShowing}
            onConfirm={async () => {
              submitNewHappiness();
            }}
          />
        </div>
      );

    case PageState.EDITING:
      return (
        <div
          className={`fullbg duration-500 bg-size-200 ${happinessColor(
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
            <DeleteButton />
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
      );
    default: <>Error: you weren't supposed to see this. Screenshot this and send to the devs :/</>
  }
}

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
const formatFullDate = (date) => {
  const options = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' };
  return date.toLocaleDateString('en-US', options);
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
  let colors = [
    "bg-[#ff0000]",
    "bg-[#ff4628]",
    "bg-[#ff8423]",
    "bg-[#ff9d23]",
    "bg-[#ffbf2a]",
    "bg-[#ffdd0b]",
    "bg-[#94e000]",
    "bg-[#68c600]",
    "bg-[#12b500]",
    "bg-[#009f05]",
    "bg-[#007e17]",
  ];
  return colors[Math.floor(happiness)];
  // return colors[Math.floor(happiness / 0.5)];
}
export function formatHappinessNum(happiness) {
  return (Math.round(happiness * 2) / 2).toFixed(1);
}
