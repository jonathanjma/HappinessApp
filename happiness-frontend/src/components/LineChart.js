import React from "react";
import { Chart as ChartJS } from "chart.js/auto";
import { Line } from "react-chartjs-2";

export default function LineChart({
  chartData,
  chartShow,
  dayShow,
  daySet,
  userSet,
}) {
  const leg = chartData.datasets.length > 1 ? true : false;
  return (
    <div className="container flex w-full">
      <Line
        data={chartData}
        options={{
          onClick: (evt, element) => {
            if (dayShow) {
              if (element.length > 0) {
                console.log(element);
                dayShow(true);
                daySet(element[0].index);
                console.log(chartData.ids);
                userSet(chartData.ids[element[0].datasetIndex]);
              } else {
                chartShow(true);
              }
            }
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
