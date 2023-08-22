import * as React from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import { CardActionArea } from "@mui/material";

export default function HappinessCard({ data, click }) {
  const date = new Date(data.timestamp);

  return (
    <Card className={"m-2"}>
      <CardActionArea onClick={() => click()}>
        <CardContent>
          <Typography sx={{ fontSize: 14 }} color="text.secondary">
            {date.toLocaleString("en-us", { weekday: "long" })}
            <br />
            {date.toLocaleString("en-us", { month: "short", day: "numeric" })}
          </Typography>
          <p></p>
          <div>
            <Typography sx={{ fontSize: 14 }} color="text.secondary">
              Score
            </Typography>
            <Typography variant="h4">{data.value.toFixed(1)}</Typography>
          </div>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
