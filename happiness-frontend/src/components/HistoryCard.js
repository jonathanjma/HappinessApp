import Users from "./Users";
import { useState } from "react";
import DayPreview from "./DayPreview";

export default function HistoryCard({ id, data, useDate = true }) {
  const [dShow, setDShow] = useState(false);
  const dayPreview = (
    <DayPreview open={dShow} setOpen={setDShow} ids_list={[id]} data={data} />
  );
  return (
    <>
      <div
        className="w-full justify-center min-h-[100px] max-w-[146px] md:max-w-[230px] mx-2.5 mt-4 bg-cultured-50 rounded-xl shadow-lg space-y-2"
        onClick={() => setDShow(true)}
      >
        <div className="flex w-full flex-wrap justify-center items-center bg-buff-300 px-2 py-3 rounded-t-xl h-2/5">
          <p className="text-center text-sm md:text-2xl font-medium text-raisin-600">
            {useDate ? <>Wednesday, {data.date}</> : <>{Users(id).name}</>}
          </p>
        </div>
        <div className="flex w-full flex-wrap justify-center items-center rounded-xl pt-2.5">
          <div className="flex items-center justify-center">
            <p className="text-center text-4xl font-medium text-raisin-600">
              {data.level}
            </p>
            {dayPreview}
          </div>
        </div>
      </div>
    </>
  );
}
