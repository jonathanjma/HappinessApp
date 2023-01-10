import { useState } from "react";
import Users from "../components/Users";
import LineChart from "../components/LineChart";

function IndexData(indices) {
  // constructs array of data values based on given indices for the LineChart
  let colors = [
    "red",
    "blue",
    "green",
    "purple",
    "orange",
    "brown",
    "pink",
    "black",
  ];
  var selectedData = [];
  indices.map((i) => {
    console.log(Users()[i].data);
    selectedData.push({
      label: Users()[i].name,
      data: Users()[i].data.map((e) => e.level),
      tension: 0.4,
      borderColor: colors[0],
    });
    // removes first element of color array
    colors.splice(0, 1);
    return selectedData;
  });
  return selectedData;
}

function Graph(props) {
  const [chartData, setChartData] = useState({
    name: props.name,
    time: props.time,
    labels: Users()[0].data.map((e) => e.date),
    datasets: IndexData(props.index),
  });

  return (
    <>
      <div className="w-full justify-center min-w-[350px] max-w-[560px] min-h-[325px] m-4 py-8 px-8 max-w-sm bg-white rounded-xl shadow-lg space-y-2">
        <p className="flex w-full justify-center font-medium text-xl text-raisin-600">
          {chartData.time} Happiness
        </p>
        <div className="flex w-full justify-center min-h-[280px] max-h-[280px]">
          <LineChart chartData={chartData} />
        </div>
      </div>
    </>
  );
}
export default Graph;
