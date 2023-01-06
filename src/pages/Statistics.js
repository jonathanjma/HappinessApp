import { useState } from "react";
import Graph from "../components/Graph";

function Statistics() {
  const index = 0;
  return (
    <>
      <div className="flex flex-wrap justify-center items-center">
        <Graph name="Alex" time="Weekly" />
      </div>
    </>
  );
}
export default Statistics;
