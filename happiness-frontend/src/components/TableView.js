import { Table } from "react-bootstrap";
import { useState } from "react";
import OldHistoryCard from "./OldHistoryCard";

// Color table cell based on happiness value
const cellColor = (level) => {
  let happiness = level * 10;
  if (happiness < 10) return "rgb(185 28 28)";
  else if (happiness < 20) return "rgb(220 38 38)";
  else if (happiness < 30) return "rgb(234 179 8)";
  else if (happiness < 40) return "rgb(250 204 21)";
  else if (happiness < 60) return "rgb(253 224 71)";
  else if (happiness < 70) return "rgb(253 224 71)";
  else if (happiness < 80) return "rgb(74 222 128)";
  else if (happiness < 100) return "rgb(34 197 94)";
  else return "rgb(22 163 74)";
};

// Sets border styles if table cell marks beginning of new week
const weekEdge = (isBound) => {
  return {
    borderLeftWidth: isBound ? "2px" : "inherit",
    borderLeftColor: !isBound ? "rgb(107 114 128)" : "inherit",
  };
};

// Fixes bootstrap edge bug when using responsive and bordered table (super wierd)
const border_fix = { borderWidth: ".8px" };

// Represents table cell for a user's happiness
function TableCell({ entry, setCard, boundary }) {
  let value = "-";
  if (entry !== undefined) {
    // make all values 2 digits
    value = entry.value < 10 ? entry.value.toFixed(1) : entry.value;
  }

  return (
    <td
      style={{
        backgroundColor:
          entry !== undefined ? cellColor(entry.value) : "rgb(211,211,211)",
        ...border_fix,
        ...weekEdge(boundary),
      }}
      className="text-center text-md font-medium text-raisin-600"
      onClick={() => setCard(entry)}
    >
      {value}
    </td>
  );
}

// TODO: smaller comment modals, why is week table so large?

export default function TableView({ groupData, happinessData, selected }) {
  const [card, setCard] = useState();

  const groupUsers = groupData.users.sort((u1, u2) => u1.id - u2.id);

  // For any 2 dates, calculates all dates in between, any week boundaries (Mondays),
  // and the amount of days in the data that are in each month (monthSpan)
  const getDatesInBetween = (start, end) => {
    const getMonthName = (month) =>
      month.toLocaleString("en-US", { month: "long" });

    let dates = [];
    let weekBoundaries = [];
    let prevMonth = start.getMonth();
    let monthSpan = { [getMonthName(start)]: 0 };
    while (start <= end) {
      dates.push(start.toISOString().substring(0, 10));
      if (start.toDateString().slice(0, 3) === "Mon") {
        weekBoundaries.push(start.toISOString().substring(0, 10));
      }
      if (start.getMonth() === prevMonth) {
        monthSpan[getMonthName(start)] += 1;
      } else {
        monthSpan[getMonthName(start)] = 1;
      }
      prevMonth = start.getMonth();
      start.setDate(start.getDate() + 1);
    }
    return [dates, weekBoundaries, monthSpan];
  };

  // Sets start date of table depending on if week or month view is selected
  const lastPeriod = new Date();
  if (selected === 1) {
    lastPeriod.setDate(lastPeriod.getDate() - 7);
  } else {
    lastPeriod.setMonth(lastPeriod.getMonth() - 1);
    lastPeriod.setDate(lastPeriod.getDate() + 1);
  }
  const [allDates, weekBounds, monthSpan] = getDatesInBetween(
    lastPeriod,
    new Date()
  );

  // Construct table rows using happiness data
  const rows = [];
  const byDate = Object.fromEntries(allDates.map((k) => [k, []]));
  for (let user of groupUsers) {
    const entries = [];
    entries.push(<td style={border_fix}>{user.username}</td>);
    for (let date of allDates) {
      let entry = happinessData.find(
        (entry) => entry.user_id === user.id && entry.timestamp === date
      );
      entries.push(
        <TableCell
          entry={entry}
          setCard={setCard}
          boundary={weekBounds.includes(date)}
        />
      );
      if (entry !== undefined) {
        byDate[date].push(entry.value);
      }
    }
    rows.push(<tr>{entries}</tr>);
  }

  // Calculate average happiness for every day
  let averages = Object.entries(byDate).map(([date, vList]) => [
    date,
    (vList.reduce((a, b) => a + b, 0.0) / vList.length).toFixed(1),
  ]);

  return (
    <div className="flex flex-col items-center">
      <Table bordered responsive>
        <thead>
          {/* Month */}
          <tr>
            <th style={border_fix}></th>
            {Object.entries(monthSpan).map(([month, span]) => (
              <th
                colSpan={span}
                className="text-center text-md font-bold text-raisin-600"
                style={border_fix}
              >
                {month}
              </th>
            ))}
          </tr>
          {/* Day */}
          <tr>
            <th></th>
            {allDates.map((date) => (
              <th
                style={weekEdge(weekBounds.includes(date))}
                className="text-center text-md font-bold text-raisin-600"
              >
                {date.substring(8)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {/* Happiness data for each user */}
          {rows.map((row) => row)}
          {/* Average happiness for each day */}
          <tr>
            <td style={border_fix}>Average</td>
            {averages.map(([date, avg]) => (
              <td
                style={{
                  backgroundColor: !isNaN(avg)
                    ? cellColor(avg)
                    : "rgb(211,211,211)",
                  ...border_fix,
                  ...weekEdge(weekBounds.includes(date)),
                }}
                className="text-center text-md font-medium text-raisin-600"
              >
                {isNaN(avg) ? "-" : avg}
              </td>
            ))}
          </tr>
        </tbody>
      </Table>
      {/* Show comment for selected happiness entry */}
      {card && <OldHistoryCard data={card} shown={true} />}
    </div>
  );
}
