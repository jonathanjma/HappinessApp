import { useState } from "react";
import ChartPreview from "./ChartPreview";
import LineChart from "./LineChart";
import DayPreview from "./DayPreview";

function IndexData(data, users, colors) {
  // constructs array of data values based on given indices for the LineChart
  var selectedData = [];
  data.map((i, t) => {
    selectedData.push({
      label: users[t].username,
      data: i.map((e) => e.value),
      tension: 0.4,
      borderColor: colors[t],
    });
    return selectedData;
  });
  return selectedData;
}

// props.data: List of objects of all data objects (can be in any time order or user_id order)
// Requires: props.users must be a list of user objects in ascending order

// exports graph element with embedded chart and title
export default function Graph(props) {
  let colors = [
    "royalblue",
    "crimson",
    "seagreen",
    "slateblue",
    "darkorchid",
    "deeppink",
    "olive",
    "orange",
    "salmon",
    "saddlebrown",
    "navy",
    "pink",
    "turquoise",
    "black",
    "limegreen",
    "mediumvioletred",
    "darkkhaki",
    "darkgray",
    "violet",
    "aquamarine",
    "indigo",
  ];
  let names = props.users.map((e) => e.username);
  let ids_list = props.users.map((e) => e.id);
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
    if (!seen.includes(datas[k].user_id)) {
      seen.push(datas[k].user_id);
    }
  }
  let k = 0; // index of happiness item for user
  let q = 0; // index of item in whole datas length
  let u = 0; // index of user in users array

  while (u < seen.length) {
    while (k < uniq.length) {
      if (formatted.length === u) {
        formatted.push([]);
      }
      // accounts for missing values
      if (datas[q] && datas[q].timestamp !== uniq[k]) {
        formatted[u].push({
          comment: null,
          id: 0,
          timestamp: uniq[k],
          user_id: datas[q].user_id,
          value: Number.NaN,
        });
        k++;
      } else if (q === datas.length || datas[q].user_id !== seen[u]) {
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
  const shownUsers = seen.map((e) => props.users[ids_list.indexOf(e)]);

  const [pointData, setPointData] = useState([[], 0]);
  // constructs chart data (passed in to LineChart.js)
  const chartData = {
    name: seen.map((e) => names[ids_list.indexOf(e)]),
    time: props.time,
    ids: formatted.map((e) => e[0].user_id),
    labels: uniq.map((e) => e.slice(5).split("-").join("/")),
    datasets: IndexData(
      formatted,
      shownUsers,
      seen.map((e) => colors[ids_list.indexOf(e)])
    ),
  };
  // console.log(chartData);
  const [cShow, setCShow] = useState(false);
  const [dShow, setDShow] = useState(false);

  const chartPreview = (
    <ChartPreview
      chartData={chartData}
      open={cShow}
      setOpen={setCShow}
      users={shownUsers}
      formatted={formatted}
    />
  );
  // console.log(formatted);
  const dayPreview = (
    <DayPreview
      open={dShow}
      setOpen={setDShow}
      data={pointData[0].map((e) => formatted[e][pointData[1]])}
      users={pointData[0].map((e) => shownUsers[e])}
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
