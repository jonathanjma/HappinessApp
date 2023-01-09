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
      tension: 0.3,
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
      <div className="min-w-[350px] max-w-[350px] m-4 py-8 px-8 max-w-sm bg-white rounded-xl shadow-lg space-y-2">
        <div>
          <p className="text-center font-medium">{chartData.time} Happiness</p>
          <LineChart chartData={chartData} />
        </div>
      </div>
    </>

    // <div>
    //   <img className="h-[400px] w-[800px]" src={props.img} />
    //   <div className="space-y-0.5">
    //     <p className="text-lg text-black text-center font semi-bold">
    //       {props.name} Graph for "name"
    //     </p>
    //   </div>
    // </div>
  );
}
export default Graph;
