import { useState } from "react";
import Graph from "../components/Graph";

function Statistics() {
  const index = 0;
  return (
    <>
      {/* <div> */}
      <div className="flex flex-wrap justify-center items-center">
        <Graph index={[0, 1, 2]} time="Weekly" />
        <Graph index={[0, 1, 2, 3, 4, 5]} time="Monthly" />
      </div>
    </>
  );
}
export default Statistics;
