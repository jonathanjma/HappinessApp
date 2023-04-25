import DateDropdown from "./DateDropdown";
import EditIcon from "../../media/pencil-square-outline-icon.png";
import {PageState} from "../../keys";
import DynamicSmile from "./DynamicSmile";
import React from "react";
import {formatHappinessNum, happinessColor} from "../../pages/SubmitHappiness";

export default function HappinessEditor (props) {
    // Props for this page:
    const happiness = props.happiness;
    const setHappiness = props.setHappiness;
    const pageState = props.pageState;
    const setPageState = props.setPageState;
    const comment = props.comment;
    const setComment = props.setComment;
    const pageMessage = props.pageMessage;
    const onSubmitClick = props.onSubmitClick;


    return (
        <div
            className={`min-h-screen duration-500 bg-size-200 ${happinessColor(
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
                            setHappiness(formatHappinessNum(happiness));
                        }}
                        value={happiness*10}
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
                    value={happiness}
                    placeholder=""
                    onChange={(e) => {
                        setHappiness(parseFloat(e.target.value))
                        if (e.target.value < 0) {
                            setHappiness(0)}
                    }}
                    onBlur={() => {
                        if ((happiness * 10) % 10 >= 5) {
                            setHappiness(Math.floor(happiness) + 0.5)
                        } else if (isNaN(happiness)) {
                            setHappiness(5)
                        } else {
                            setHappiness(Math.floor(happiness))
                        }
                    }
                    }
                />

                {/* Happiness Comment Box */}
            <textarea
                id="large-input"
                value={comment}
                className="md:w-5/12 w-3/4 p-4 bg-gray-200 rounded mt-10 border-raisin-100 outline-none focus:border-raisin-200 border-2 focus:border-4"
                placeholder="Add a comment about the day"
                onChange={(e) => {
                    setComment(e.target.value);
                }}
            />

                {/* Submit button: */}
                <>
                    <button
                        onClick={onSubmitClick}
                        className="flex-1 scale-150 text-white bg-gradient-to-r from-raisin-500 via-raisin-600 to-raisin-700 shadow-lg font-roboto font-semibold rounded-lg text-sm px-5 outline-none py-2.5 text-center mr-2 mb-2 mt-9"
                    >
                        Submit
                    </button>
                </>
            </div>
        </div>
    );
}