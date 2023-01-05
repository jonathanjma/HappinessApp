import { useState } from "react";
import Users from "../components/Users";
import LineChart from "../components/LineChart";

function Statistics() {
  const cur = {
    id: 1,
    name: "Alex",
    time: "Weekly",
  };
  const [chartData, setChartData] = useState({
    name: cur.name,
    labels: Users()[0].data.map((e) => e.date),
    datasets: [
      {
        label: cur.time + " happiness for " + cur.name,
        data: Users()[0].data.map((e) => e.level),
        tension: 0.3,
      },
    ],
  });
  return (
    <>
      <div>
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
export default Statistics;
