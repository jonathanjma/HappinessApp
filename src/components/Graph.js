import { useState } from "react";
import Users from "../components/Users";
import LineChart from "../components/LineChart";

function Graph(props) {
  const [chartData, setChartData] = useState({
    name: props.name,
    time: props.time,
    labels: Users()[0].data.map((e) => e.date),
    datasets: [
      {
        label: "Happiness",
        data: Users()[0].data.map((e) => e.level),
        tension: 0.3,
        borderColor: "red",
      },
    ],
  });

  return (
    <>
      <div className=" min-w-[500px] max-w-[500px] m-2 py-8 px-8 max-w-sm bg-white rounded-xl shadow-lg space-y-2 sm:py-4 sm:flex sm:items-center sm:space-y-0 sm:space-x-6">
        <LineChart chartData={chartData} />
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
