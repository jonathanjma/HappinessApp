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

  function getSortedVals(data) {
    const vals = [];
    data.map((e) => e.map((f) => vals.push(f)));
    vals.sort();
    return vals;
  }

  function mean(data) {
    let vals = getSortedVals(data);
    let a = 0;
    vals.map((d) => (a = d + a));
    return Math.round((a / vals.length) * 10) / 10;
  }

  function median(data) {
    let vals = getSortedVals(data);
    if (vals.length % 2 === 0) {
      return vals[vals.length / 2 - 1] + vals[vals.length / 2] / 2;
    }
    return vals[vals.length / 2];
  }
  function mode(data) {
    let vals = getSortedVals(data);

    let max = 0,
      count = 0,
      val = -1;
    for (let m = 0; m < vals.length; m++) {
      if (vals[m] !== val) {
        count = 1;
      } else count++;
      if (count > max) {
        max = count;
      }
    }
    return max;
  }
  function range(data) {
    let vals = getSortedVals(data);
    return vals[vals.length - 1] - vals[0];
  }
  function stdev(data) {
    let vals = getSortedVals(data);
    const n = vals.length;
    const mean = vals.reduce((a, b) => a + b) / n;
    return Math.sqrt(
      vals.map((x) => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / n
    );
  }
  function min(data) {
    let vals = getSortedVals(data);
    return vals[0];
  }
  function q1(data) {
    let vals = getSortedVals(data);
    let med = vals.length / 2;
    return median(data.slice(0, med));
  }
  function q3(data) {
    let vals = getSortedVals(data);
    let med = vals.length / 2;
    if (vals.length / 2 === 0) {
      return median(data.slice(med));
    }
    return median(data.slice(med) + 1);
  }
  function max(data) {
    let vals = getSortedVals(data);
    return vals[vals.length - 1];
  }

  let calcs = [mean, median, mode, range, stdev, min, q1, q3, max];

  let val = Object.keys(trans)[props.val];
  return (
    <div className="min-w-[150px] min-h-[150px] md:min-w-[178px] md:max-w-[178px] md:min-h-[178px] flex items-center justify-center mx-2 mb-4 lg:my-4 max-w-sm bg-cultured-50 rounded-xl shadow-lg">
      <div className="space-y-2">
        <p className="text-lg md:text-xl text-raisin-600 font-semibold text-center">
          {trans[val]}
        </p>
        <p className="text-2xl md:text-3xl text-rhythm-500 font-medium text-center">
          {calcs[val](props.data)}
        </p>
      </div>
    </div>
  );
}
