import { useState } from "react";
import Users from "../components/Users";
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
//

// Requires: The list props.names is sorted by corresponding id in ascending order.
// exports graph element with embedded chart and title
export default function Graph(props) {
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
  for (let k = 0; k < datas.length; k++) {
    if (!uniq.includes(datas[k].timestamp)) {
      uniq.push(datas[k].timestamp);
    }
    if (!seen.includes(datas[k].user_id)) {
      ctr++;
      formatted.push([datas[k]]);
      seen.push(datas[k].user_id);
    } else {
      formatted[ctr].push(datas[k]);
    }
  }
  const [chartData, setChartData] = useState({
    name: props.names,
    time: props.time,
    ids: formatted.map((e) => e[0].user_id),
    labels: uniq.map((e) => e.slice(5).split("-").join("/")),
    datasets: IndexData(formatted, props.names),
  });
  const [cShow, setCShow] = useState(false);
  const [dShow, setDShow] = useState(false);
  const [day, setDay] = useState(0);
  const [selUser, setSelUser] = useState([0]);

  const chartPreview = (
    <ChartPreview
      chartData={chartData}
      open={cShow}
      setOpen={setCShow}
      name={props.names}
      idsList={seen}
      dayData={formatted}
    />
  );
  const ids = seen.map((e, t) => {
    if (selUser.includes(e)) {
      return t;
    } else {
      return 0;
    }
  });
  console.log(ids);
  console.log(formatted);
  const dayPreview = (
    <DayPreview
      open={dShow}
      setOpen={setDShow}
      data={ids.map((e, t) => formatted[e][day[t]])}
      name={props.names}
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
              daySet={setDay}
              userSet={setSelUser}
            />
            {chartPreview}
            {dayPreview}
          </div>
        </div>
      </div>
    </>
  );
}
