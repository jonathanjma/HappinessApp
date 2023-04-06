import Users from "./Users";
import { useState } from "react";
import DayPreview from "./DayPreview";

export default function HistoryCard({ data, name = "", useDate = true }) {
  const parts = data.timestamp.split("-");
  const dayString = new Date(parts[0], parts[1] - 1, parts[2]);
  const [dShow, setDShow] = useState(false);
  return (
    <>
      <div
        className="w-full justify-center min-h-[100px] max-w-[146px] md:max-w-[230px] mx-2.5 mt-4 bg-cultured-50 rounded-xl shadow-lg space-y-2"
        onClick={() => setDShow(true)}
      >
        <div className="flex w-full flex-wrap justify-center items-center bg-buff-300 px-2 py-3 rounded-t-xl h-2/5">
          <p className="text-center text-sm md:text-2xl font-medium text-raisin-600">
            {useDate ? (
              <>
                {dayString.toDateString().slice(0, 3) +
                  ", " +
                  data.timestamp.slice(5).split("-").join("/")}
              </>
            ) : (
              <>{name}</>
            )}
          </p>
        </div>
        <div className="flex w-full flex-wrap justify-center items-center rounded-xl pt-2.5">
          <div className="flex items-center justify-center">
            <p className="text-center text-4xl font-medium text-raisin-600">
              {data.value}
            </p>
            <DayPreview
              open={dShow}
              setOpen={setDShow}
              data={[data]}
              name={name}
            />
          </div>
        </div>
      </div>
    </>
  );
}
