import { useState } from "react";
import ChartPreview from "./ChartPreview";
import LineChart from "./LineChart";
import DayPreview from "./DayPreview";

function IndexData(data, names) {
  // constructs array of data values based on given indices for the LineChart
  let colors = [
    "blue",
    "red",
    "green",
    "purple",
    "orange",
    "salmon",
    "brown",
    "pink",
    "turquoise",
    "black",
    "magenta",
    "yellow",
    "gray",
    "violet",
    "indigo",
  ];
  var selectedData = [];
  data.map((i, t) => {
    selectedData.push({
      label: names[t],
      data: i.map((e) => e.value),
      tension: 0.4,
      borderColor: colors[t % 15],
    });
    return selectedData;
  });
  return selectedData;
}

// props.data: List of objects of all data objects (can be in any time order or user_id order)
// Requires: props.users must be a list of user objects in ascending order

// exports graph element with embedded chart and title
export default function Graph(props) {
  let names = props.users.map((e) => e.username);
  let datas = props.data;
  // console.log("checking sort");
  // console.log(datas);
  datas.sort((a, b) => a.timestamp - b.timestamp);
  // console.log(datas);
  datas.sort((a, b) => a.user_id - b.user_id);
  // console.log(datas);
  const formatted = Array();
  let seen = [];
  let uniq = [];
  let ctr = -1;
  // loops through complete data and adds all unique dates
  for (let k = 0; k < datas.length; k++) {
    if (!uniq.includes(datas[k].timestamp)) {
      uniq.push(datas[k].timestamp);
    }
  }
  let k = 0;
  let q = 0;
  while (q < datas.length) {
    // new user that not accessed previously
    if (!seen.includes(datas[q].user_id)) {
      ctr++;
      formatted.push([datas[q]]);
      seen.push(datas[q].user_id);
      k = 1;
      q++;
    } else {
      // accounts for missing values
      if (datas[q].timestamp !== uniq[k]) {
        formatted[ctr].push({
          comment: null,
          id: 0,
          timestamp: uniq[q],
          user_id: datas[q].user_id,
          value: Number.NaN,
        });
        k++;
        // if there is existing value
      } else {
        formatted[ctr].push(datas[q]);
        k++;
        q++;
      }
    }
  }
  // console.log(formatted);
  const [pointData, setPointData] = useState([[], 0]);
  // constructs chart data (passed in to LineChart.js)
  const chartData = {
    name: names,
    time: props.time,
    ids: formatted.map((e) => e[0].user_id),
    labels: uniq.map((e) => e.slice(5).split("-").join("/")),
    datasets: IndexData(formatted, names),
  };
  const [cShow, setCShow] = useState(false);
  const [dShow, setDShow] = useState(false);

  const chartPreview = (
    <ChartPreview
      chartData={chartData}
      open={cShow}
      setOpen={setCShow}
      users={props.users}
      formatted={formatted}
    />
  );
  // console.log(formatted);
  const dayPreview = (
    <DayPreview
      open={dShow}
      setOpen={setDShow}
      data={pointData[0].map((e) => formatted[e][pointData[1]])}
      users={pointData[0].map((e) => props.users[e])}
    />
  );
  return (
    <>
      <div className="flex w-full justify-center">
        <div className="flex flex-wrap justify-center w-full max-w-[1000px] @lg:min-h-[500px] min-h-[380px] max-h-[380px] mb-4 py-8 bg-cultured-50 rounded-xl shadow-lg space-y-2">
          <p className="flex w-full justify-center font-medium text-xl text-raisin-600">
            {chartData.time} Happiness
          </p>
          <div className="flex w-full justify-center mx-2 @lg:min-h-[400px] min-h-[285px] max-h-[285px]">
            <LineChart
              chartData={chartData}
              chartShow={setCShow}
              dayShow={setDShow}
              setPointData={setPointData}
            />
            {chartPreview}
            {dayPreview}
          </div>
        </div>
      </div>
    </>
  );
}
