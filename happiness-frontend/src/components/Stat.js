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

  function getSortedVals(data) {
    const vals = [];
    data.map((e) => {
      if (e !== undefined) {
        vals.push(e);
      }
    });
    vals.sort();
    return vals;
  }
  const vals = getSortedVals(props.data);

  function mean(vals) {
    let a = 0;
    vals.map((d) => (a = d + a));
    return Math.round((a / vals.length) * 100) / 100;
  }

  function median(vals) {
    if (vals.length % 2 === 0) {
      return (
        (vals[Math.round(vals.length / 2) - 1] +
          vals[Math.round(vals.length / 2)]) /
        2
      );
    }
    return vals[Math.round(vals.length / 2) - 1];
  }
  function mode(vals) {
    let max = 0,
      count = 0,
      val = -1,
      maxNum = 0;
    for (let m = 0; m < vals.length; m++) {
      if (vals[m] !== val) {
        count = 1;
        val = vals[m];
      } else count++;
      if (count > max) {
        max = count;
        maxNum = val;
      }
    }
    return maxNum;
  }
  function range(vals) {
    return vals[vals.length - 1] - vals[0];
  }
  function stdev(vals) {
    const n = vals.length;
    const mean = vals.reduce((a, b) => a + b) / n;
    const a = Math.sqrt(
      vals.map((x) => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / n
    );
    return Math.round(a * 100) / 100;
  }
  function min(vals) {
    return vals[0];
  }
  function q1(vals) {
    let med = vals.length / 2;
    return median(vals.slice(0, med));
  }
  function q3(vals) {
    let med = Math.floor(vals.length / 2);
    if (med % 2 === 0) {
      return median(vals.slice(med));
    }
    return median(vals.slice(med + 1));
  }
  function max(vals) {
    return vals[vals.length - 1];
  }

  let calcs = {
    mean: mean(vals),
    median: median(vals),
    mode: mode(vals),
    range: range(vals),
    stdev: stdev(vals),
    min: min(vals),
    q1: q1(vals),
    q3: q3(vals),
    max: max(vals),
  };

  let val = Object.keys(trans)[props.val];
  return (
    <div className="max-w-[150px] max-h-[150px] min-w-[150px] min-h-[150px] md:min-w-[178px] md:max-w-[178px] md:min-h-[178px] flex items-center justify-center mx-2 mb-4 lg:my-4 bg-cultured-50 rounded-xl shadow-lg">
      <div className="space-y-2">
        <p className="text-lg md:text-xl text-raisin-600 font-semibold text-center">
          {trans[val]}
        </p>
        <p className="text-2xl md:text-3xl text-rhythm-500 font-medium text-center">
          {calcs[val]}
        </p>
      </div>
    </div>
  );
}
