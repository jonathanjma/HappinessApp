import React from "react";
import { Chart } from "chart.js/auto";
import { Line } from "react-chartjs-2";

function LineChart({ chartData }) {
  return (
    <div className="container">
      <Line
        data={chartData}
        options={{
          plugins: {
            title: {
              display: false,
              text: "",
            },
            legend: {
              display: true,
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
export default LineChart;
