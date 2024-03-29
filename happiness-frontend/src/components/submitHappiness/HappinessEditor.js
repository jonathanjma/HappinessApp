import DateDropdown from "./DateDropdown";
import EditIcon from "../../media/pencil-square-outline-icon.png";
import { PageState } from "../../keys";
import DynamicSmile from "./DynamicSmile";
import React, { useRef } from "react";
import {
  formatHappinessNum,
  happinessColor,
} from "../../pages/SubmitHappiness";

export default function HappinessEditor(props) {
  // Props for this page:
  const happiness = props.happiness;
  const setHappiness = props.setHappiness;
  const pageState = props.pageState;
  const setPageState = props.setPageState;
  const comment = props.comment;
  const setComment = props.setComment;
  const pageMessage = props.pageMessage;
  const onSubmitClick = props.onSubmitClick;
  const commentBox = useRef();
  console.log(`Comment box = ${commentBox.current}`);

  return (
    <div
      className={`duration-500 bg-size-200 ${happinessColor(
        happiness
      )}`}
    >
      {/* Items */}
      <div className="flex flex-col justify-center items-center">
        {/* Prompt */}
        <>
          <h1 className="md:text-7xl text-5xl text-white md:text-stroke-3 text-stroke-2 text-center mt-3 font-roboto">
            <b>{pageMessage}</b>
          </h1>
        </>

        {/* Happy Face, Slider, and Happiness Number (Desktop only) */}
        <div className="flex flex-row items-center justify-center mobile-hidden">
          {/* Happy Face Decorator */}
          <span className="mr-28 mt-10">
            <DynamicSmile happiness={happiness} />
          </span>
          {/* Happiness Slider */}
          <input
            id="default-range"
            type="range"
            onChange={(e) => {
              setHappiness(e.target.value / 10);
            }}
            onMouseUp={(e) => {
              setHappiness(prevHappiness => formatHappinessNum(prevHappiness));
            }}
            value={happiness * 10}
            className="w-40 md:w-72 h-2 rounded-lg appearance-none cursor-pointer dark:bg-white-300 scale-150 mt-20"
          />

          {/* Happiness Number */}
          <p className="text-8xl text-white text-stroke-4 mt-10 ml-28 font-roboto flex-none flex-row w-40">
            <b>{formatHappinessNum(happiness)}</b>
          </p>
        </div>

        {/* Happiness Number Input Field (Mobile Only) */}
        <input
          className="mt-10 w-24 h-20 text-4xl text-center rounded-2xl bg-gray-100 focus:border-raisin-600 border-raisin-100 border-2 focus:border-4 md:hidden"
          type="number"
          inputMode="decimal"
          value={happiness}
          placeholder=""
          onChange={(e) => {
            setHappiness(e.target.value)
            if (e.target.value < 0) {
              setHappiness(0);
            }
            if (e.target.value.length > 3) {
              setHappiness(e.target.value.toString().substring(0, 3))
            }
          }}
          onBlur={() => {
            if (happiness != 10) {
              setHappiness(prevHappiness => formatHappinessNum(prevHappiness))
            }
          }}
        />

        {/* Happiness Comment Box */}
        <textarea
          ref={commentBox}
          id="large-input"
          value={comment}
          className={`md:w-5/12 w-3/4 px-4 py-2 bg-gray-200 rounded mt-10 border-raisin-100 outline-none focus:border-raisin-200 border-2 focus:border-4 text-left`}
          style={{ height: `${commentBox.current == undefined ? 100 : Math.max(commentBox.current.scrollHeight, `100`)}px`, scrollbarColor: "#9191b6" }}
          placeholder="Add a comment about the day, briefly summarizing the main events"
          onChange={(e) => {
            setComment(e.target.value);
          }}
        />

        {/* Submit button: */}
        <>
          <button
            onClick={onSubmitClick}
            className="flex-1 scale-150 text-white bg-gradient-to-r from-raisin-500 via-raisin-600 to-raisin-700 shadow-lg font-roboto font-semibold rounded-lg text-sm px-5 outline-none py-2.5 text-center mr-2 mb-5 mt-9"
          >
            Submit
          </button>
        </>
      </div>
    </div>
  );
}
