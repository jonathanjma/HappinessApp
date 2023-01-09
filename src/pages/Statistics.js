import { useState } from "react";
import Graph from "../components/Graph";
import Stat from "../components/Stat";

function Statistics() {
  /*
  0 = mean
  1 = median
  2 = mode
  3 = range
  4 = standard deviation
  5 = minimum
  6 = q1
  7 = q3
  8 = maximum 
  */
  // future conversion to boolean array
  const datavals = [
    { value: true, key: 0 },
    { value: true, key: 1 },
    { value: true, key: 2 },
    { value: false, key: 3 },
    { value: true, key: 4 },
    { value: true, key: 5 },
    { value: true, key: 6 },
    { value: true, key: 7 },
    { value: true, key: 8 },
  ];
  return (
    <>
      <p className="text-center text-4xl font-medium m-4">Statistics</p>
      <div className="flex flex-wrap justify-center items-center">
        <Graph index={[0, 1, 2]} time="Weekly" />
        <Graph index={[0, 1, 2, 3, 4, 5]} time="Monthly" />
      </div>
      <div className="flex flex-wrap justify-center items-center">
        {datavals.map((e) => {
          if (e.value) {
            return <Stat key={e.key} val={e.key} />;
          }
          return null;
        })}
      </div>
    </>
  );
}
export default Statistics;
