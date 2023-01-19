import React from "react";
import Users from "./Users";

export default function Stat(props) {
  let trans = {
    mean: "Average",
    median: "Median",
    mode: "Mode",
    range: "Range",
    stdev: "Standard Deviation",
    min: "Minimum Value",
    q1: "1st Quartile",
    q3: "3rd Quartile",
    max: "Maximum Value",
  };
  // console.log(props.val);
  let val = Object.keys(trans)[props.val];
  return (
    <div className="min-w-[178px] max-w-[178px] min-h-[178px] flex items-center justify-center mx-2 mb-4 max-w-sm bg-cultured-50 rounded-xl shadow-lg">
      <div className="space-y-2">
        <p className="text-xl text-raisin-600 font-semibold text-center">
          {trans[val]}
        </p>
        <p className="text-3xl text-rhythm-500 font-medium text-center">
          {Users(props.id).measures[val]}
        </p>
      </div>
    </div>
  );
}
