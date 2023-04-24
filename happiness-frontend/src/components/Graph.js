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
  // loops through complete data and adds all unique dates and unique users
  for (let k = 0; k < datas.length; k++) {
    if (!uniq.includes(datas[k].timestamp)) {
      uniq.push(datas[k].timestamp);
    }
  }
  let k = 0; // index of happiness item for user
  let q = 0; // index of item in whole datas length
  let u = 0; // index of user in users array

  while (u < props.users.length) {
    while (k < uniq.length) {
      if (formatted.length === u) {
        formatted.push([]);
      }
      // accounts for missing values
      if (datas[q] && datas[q].timestamp !== uniq[k]) {
        console.log("ok");
        formatted[u].push({
          comment: null,
          id: 0,
          timestamp: uniq[k],
          user_id: datas[q].user_id,
          value: Number.NaN,
        });
        k++;
      } else if (q === datas.length || datas[q].user_id !== props.users[u].id) {
        // if next user's value is shown, fills in the blanks
        formatted[u].push({
          comment: null,
          id: 0,
          timestamp: uniq[k],
          user_id: datas[q - 1].user_id,
          value: Number.NaN,
        });
        k++;
      } else {
        // if there is existing value
        formatted[u].push(datas[q]);
        k++;
        q++;
      }
    }
    u++;
    k = 0;
  }
  console.log(formatted);
  const [pointData, setPointData] = useState([[], 0]);
  // constructs chart data (passed in to LineChart.js)
  const chartData = {
    name: names,
    time: props.time,
    ids: formatted.map((e) => e[0].user_id),
    labels: uniq.map((e) => e.slice(5).split("-").join("/")),
    datasets: IndexData(formatted, names),
  };
  console.log(chartData);
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
