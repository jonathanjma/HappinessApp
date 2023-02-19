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
    "brown",
    "pink",
    "black",
    "yellow",
    "gray",
  ];
  var selectedData = [];
  ids.map((i) => {
    selectedData.push({
      label: Users(i).name,
      data: Users(i).data.map((e) => e.level),
      tension: 0.4,
      borderColor: colors[0],
    });
    // removes first element of color array
    colors.splice(0, 1);
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
  const [day, setDay] = useState();
  const [selUser, setSelUser] = useState(props.id);

  const chartPreview = (
    <ChartPreview chartData={chartData} open={cShow} setOpen={setCShow} />
  );
  const dayPreview = (
    <DayPreview open={dShow} setOpen={setDShow} id={selUser} data={Users(selUser).data[day]} />
  );
  return (
    <>
      <div className="w-full justify-center min-w-[330px] max-w-[560px] min-h-[325px] mx-4 mb-4 py-8 px-8 bg-cultured-50 rounded-xl shadow-lg space-y-2">
        <p className="flex w-full justify-center font-medium text-xl text-raisin-600">
          {chartData.time} Happiness
        </p>
        <div className="flex w-full justify-center min-h-[280px] max-h-[280px]">
          <div className="flex w-full justify-center">
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
