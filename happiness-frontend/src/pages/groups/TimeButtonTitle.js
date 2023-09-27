// Title for tab with buttons to change the currently viewed time range
// size is the text size of the main tab
export function TimeButtonTitle({
                                    text,
                                    radioValue,
                                    setStart,
                                    setEnd,
                                    size = "sm:text-3xl text-2xl",
                                }) {
    return (
        <div className="flex items-center justify-center">
            {/* View earlier time period button */}
            <button
                type="button"
                className="px-3 me-3 w-[50px] h-[40px] rounded-lg text-cultured-50 bg-raisin-600 text-xl"
                onClick={() => {
                    setStart((start) => {
                        if (radioValue === 1) {
                            start.setDate(start.getDate() - 7);
                        } else {
                            start.setMonth(start.getMonth() - 1);
                        }
                        return new Date(start);
                    });
                    setEnd((end) => {
                        if (radioValue === 1) {
                            end.setDate(end.getDate() - 7);
                        } else {
                            end.setMonth(end.getMonth() - 1);
                        }
                        return new Date(end);
                    });
                }}
            >
                &lt;
            </button>
            {/* Title text */}
            <p className={"font-medium m-3 text-raisin-600 " + size}>{text}</p>
            {/* View later time period button */}
            <button
                type="button"
                className="px-3 ms-3 w-[50px] h-[40px] rounded-lg text-cultured-50 bg-raisin-600 text-xl"
                onClick={() => {
                    setStart((start) => {
                        if (radioValue === 1) {
                            start.setDate(start.getDate() + 7);
                        } else {
                            start.setMonth(start.getMonth() + 1);
                        }
                        return new Date(start);
                    });
                    setEnd((end) => {
                        if (radioValue === 1) {
                            end.setDate(end.getDate() + 7);
                        } else {
                            end.setMonth(end.getMonth() + 1);
                        }
                        return new Date(end);
                    });
                }}
            >
                &gt;
            </button>
        </div>
    );
}