import { useState } from "react";
import Graph from "../components/Graph";

function Statistics() {
  const index = 0;
  return (
    <>
      {/* <div> */}
      <div className="flex flex-wrap justify-center items-center">
        <Graph name="Alex" time="Weekly" />
        <Graph name="Alex" time="Monthly" />
      </div>
    </>
  );
}
export default Statistics;
