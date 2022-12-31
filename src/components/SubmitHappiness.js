import { useState } from "react";

export default function SubmitHappiness(props) {
  console.log(props.happiness);
  return (
    <div className={`h-screen bg-gradient-to-r from-green-400 to-blue-500`}>
      <h1>Hello!</h1>
      <input
        id="default-range"
        type="range"
        onChange={(e) => {
          props.setHappiness(e.target.value * 5);
        }}
        className="w-1/4 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
      />
    </div>
  );
}
