// TODO: Rewrite with date code once backend integrated
import { useState } from "react";
import Users from "./Users";

import OldHistoryCard from "./OldHistoryCard";

function ReturnColor(level) {
  let happiness = level * 10;
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
}

function MonthItem(props) {
  const [dShow, setDShow] = useState(false);
  return (
    <>
      <div className="w-full flex flex-wrap justify-center h-[60px] md:h-[100px] bg-cultured-50 rounded-sm">
        <div className="hidden md:block w-full md:h-1/4 justify-center">
          <p className="text-center text-sm sm:text-md md:text-lg font-medium lg:text-raisin-600">
            {props.day}
          </p>
        </div>
        {/* The color for the box below can change depending on happiness value */}
        <div
          className={
            ReturnColor(props.value) +
            " flex w-full justify-center items-center h-full md:h-3/4"
          }
        >
          <p className="md:hidden text-center text-lg sm:text-xl md:text-2xl font-medium text-raisin-600">
            {props.day}
          </p>
          <p className="hidden md:block text-center text-lg sm:text-xl md:text-2xl font-medium text-raisin-600">
            {props.value}
          </p>
        </div>
      </div>
    </>
  );
}

function WeekItem(props) {
  const tiles = [];
  let i = props.start;
  let limit = Math.min(i + 7, 31);
  for (let b = 0; b < props.day; b++) {
    tiles.push(<th></th>);
  }
  for (i; i + props.day < limit; i++) {
    tiles.push(
      <>
        <th className="border border-raisin-600 border-collapse">
          <MonthItem day={i} value={Math.floor(Math.random() * 20) / 2} />
        </th>
      </>
    );
  }
  return <>{tiles}</>;
}

export default function MonthView(props) {
  let tiles = [];
  tiles.push(
    <>
      <tr>
        <WeekItem start={1} day={props.startday} />
      </tr>
    </>
  );
  for (let d = 8 - props.startday; d < 32; d += 7) {
    tiles.push(
      <>
        <tr>
          <WeekItem start={d} day={0} />
        </tr>
      </>
    );
  }
  return (
    <>
      <div className="flex flex-wrap w-full justify-center items-center mt-3">
        <div className="flex flex-wrap justify-center border-solid w-full max-w-[550px]">
          <div className="font-medium relative w-full text-center text-2xl py-2 my-0 bg-buff-200 h-[60px]">
            <button className="absolute top-3 left-4 w-[40px] md:w-[60px] h-[40px] rounded-lg text-cultured-50 bg-raisin-600 text-xl">
              &lt;
            </button>
            <p className="py-2">
              {props.month} {props.year}
            </p>
            <button className="absolute top-3 right-4 w-[40px] md:w-[60px] h-[40px] rounded-lg text-cultured-50 bg-raisin-600 text-xl">
              &gt;
            </button>
          </div>

          <table className="table-fixed w-full rounded-sm border-collapse border border-raisin-600">
            <tbody>{tiles}</tbody>
          </table>
        </div>
        <div className="w-full flex justify-center">
            <OldHistoryCard id={1} data={Users(1).data[3]} shown={true} useDate={true} />
        </div>
      </div>
    </>
  );
}
