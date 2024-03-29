import { useState } from "react";
import React from "react";

export default function DateDropdown(props) {
  const dateList = props.dateList;
  const [dropDownShowing, setDropDownShowing] = useState(false);

  return (
    <>
      {/* Header div */}
      <div className="flex flex-col ml-3 mt-3 drop-shadow-md ">
        <div className="h-1/2 w-full bg-red-500 p-2 rounded-t-2xl ">
          <p className="md:text-2xl text-xl text-white text-center font-medium -mb-1">
            {getWeekDay(dateList[props.selectedIndex])}
          </p>
        </div>
        <div
          className="h-1/2 w-full bg-white p-2 rounded-b-2xl flex flex-row"
          onClick={() => {
            setDropDownShowing(!dropDownShowing);
          }}
        >
          <p className="md:text-4xl text-xl text-red text-center font-medium -mb-1 -mt-1">
            {dateList[props.selectedIndex].getDate()}
          </p>
          <ArrowIcon className="ml-1 md:h-7 md:w-7" />
        </div>
        {/* Dropdown selection */}
        <div
          className={
            dropDownShowing
              ? "absolute bg-white md:mt-24 mt-20 rounded-xl w-16 "
              : "collapse"
          }
        >
          {dateList.map((val, i, arr) => {
            if (i === props.selectedIndex) return;
            return (
              <p
                key={i}
                className=" rounded-xl p-2 text-lg md:text-2xl"
                onClick={() => {
                  props.setSelectedIndex(i);
                  setDropDownShowing(false);
                }}
              >
                {val.getDate()}
              </p>
            );
          })}
        </div>
      </div>
    </>
  );
}
const ArrowIcon = (props) => {
  return (
    <svg height="20" width="20" viewBox="0 0 20 20" className={props.className}>
      <path d="M4.516 7.548c0.436-0.446 1.043-0.481 1.576 0l3.908 3.747 3.908-3.747c0.533-0.481 1.141-0.446 1.574 0 0.436 0.445 0.408 1.197 0 1.615-0.406 0.418-4.695 4.502-4.695 4.502-0.217 0.223-0.502 0.335-0.787 0.335s-0.57-0.112-0.789-0.335c0 0-4.287-4.084-4.695-4.502s-0.436-1.17 0-1.615z"></path>
    </svg>
  );
};

const getWeekDay = (date) => {
  const daysOfWeek = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
  return daysOfWeek[date.getDay()];
};
