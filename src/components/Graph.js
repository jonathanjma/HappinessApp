import { useState } from "react";
import Users from "../components/Users";
import Preview from "./Preview";
import LineChart from "./LineChart";

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

export default function Graph(props) {
  const [chartData, setChartData] = useState({
    name: props.name,
    time: props.time,
    labels: Users(props.id).data.map((e) => e.date),
    datasets: IndexData(props.index),
  });

  return (
    <>
      <div className="w-full justify-center min-w-[330px] max-w-[560px] min-h-[325px] mx-4 mb-4 py-8 px-8 bg-cultured-50 rounded-xl shadow-lg space-y-2">
        <p className="flex w-full justify-center font-medium text-xl text-raisin-600">
          {chartData.time} Happiness
        </p>
        <div className="flex w-full justify-center min-h-[280px] max-h-[280px]">
          <Preview chartData={chartData} />
        </div>
      </div>
    </>
  );
}
