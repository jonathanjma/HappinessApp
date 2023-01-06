import React from "react";
import { Chart } from "chart.js/auto";
import { Line } from "react-chartjs-2";

function LineChart({ chartData }) {
  return (
    <div className="chart-container">
      <h2 style={{ textAlign: "center" }}>Weekly happiness for Alex</h2>
      <Line
        data={chartData}
        options={{
          scales: {
            y: {
              max: 10,
              min: 0,
            },
          },
          plugins: {
            title: {
              display: true,
              text: "Week of 1/5/23",
            },
            legend: {
              display: false,
            },
          },
        }}
      />
    </div>
  );
}
export default LineChart;
