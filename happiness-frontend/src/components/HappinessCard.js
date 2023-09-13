import * as React from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import { CardActionArea } from "@mui/material";

export default function HappinessCard({ data, click }) {
  const date = new Date(data.timestamp + "T00:00:00");

  return (
    <Card className="my-2 border shadow-none">
      <CardActionArea onClick={click}>
        <CardContent className="p-2">
          <Typography className="text-sm mb-3" sx={{ color: "#6B727A" }}>
            {date.toLocaleString("en-us", { weekday: "long" })}
            <br />
            {date.toLocaleString("en-us", { month: "short", day: "numeric" })}
          </Typography>
          <Typography className="text-sm" sx={{ color: "#575F68" }}>
            Score
          </Typography>
          <Typography className="text-3xl font-medium">
            {data.value !== undefined ? data.value.toFixed(1) : "-"}
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
