import React from "react";
// don't delete below import!
import { Chart as ChartJS } from "chart.js/auto";
import { Line } from "react-chartjs-2";

export default function LineChart({
  chartData,
  chartShow,
  dayShow,
  setPointData,
}) {
  const leg = chartData.datasets.length > 1 ? true : false;

  function change_data(element) {
    if (dayShow) {
      if (element.length > 0) {
        let index = element[0].index;
        let dataindices = element.map((e) => e.datasetIndex);
        setPointData([dataindices, index]);
        dayShow(true);
      } else {
        if (chartShow) chartShow(true);
      }
    }
  }

  return (
    <div className="container flex w-full">
      <Line
        data={chartData}
        options={{
          onClick: (evt, element) => {
            change_data(element);
          },
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: leg,
              labels: {
                boxWidth: 15,
              },
            },
          },
          scales: {
            y: {
              max: 10,
              min: 0,
            },
          },
          layout: {
            padding: {},
          },
        }}
      />
    </div>
  );
}
