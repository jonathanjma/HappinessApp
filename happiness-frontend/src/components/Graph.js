import { useState } from "react";
import Users from "../components/Users";
import ChartPreview from "./ChartPreview";
import LineChart from "./LineChart";
import DayPreview from "./DayPreview";

function IndexData(ids) {
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
  ids.map((i, t) => {
    selectedData.push({
      label: Users(i).name,
      data: Users(i).data.map((e) => e.level),
      tension: 0.4,
      borderColor: colors[t % 15],
    });
    return selectedData;
  });
  return selectedData;
}

// exports graph element with embedded chart and title
export default function Graph(props) {
  const [chartData, setChartData] = useState({
    name: props.name,
    time: props.time,
    ids: props.index,
    labels: Users(props.id).data.map((e) => e.date),
    datasets: IndexData(props.index),
  });
  const [cShow, setCShow] = useState(false);
  const [dShow, setDShow] = useState(false);
  const [day, setDay] = useState(0);
  const [selUser, setSelUser] = useState([props.id]);

  const chartPreview = (
    <ChartPreview chartData={chartData} open={cShow} setOpen={setCShow} />
  );
  const ids = props.index.map((e) => {
    if (selUser.includes(e)) {
      return e;
    } else {
      return 0;
    }
  });
  const dayPreview = (
    <DayPreview open={dShow} setOpen={setDShow} ids_list={ids} day={day} />
  );
  return (
    <>
      <div className="flex w-full justify-center">
        <div className="flex flex-wrap justify-center w-full @lg:min-h-[580px] min-h-[380px] max-h-[380px] mb-4 py-8 bg-cultured-50 rounded-xl shadow-lg space-y-2">
          <p className="flex w-full justify-center font-medium text-xl text-raisin-600">
            {chartData.time} Happiness
          </p>
          <div className="flex w-full justify-center mx-2 @lg:min-h-[480px] min-h-[285px] max-h-[285px]">
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
