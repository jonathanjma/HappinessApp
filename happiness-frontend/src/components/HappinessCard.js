import * as React from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import { CardActionArea } from "@mui/material";

export default function HappinessCard({ data, click, selected }) {
  const date = new Date(data.timestamp + "T00:00:00");

  return (
    <Card className={"my-2 transition-transform duration-1000 border-solid border-[#ECECEC] border-[1px] shadow-none"}>
      <CardActionArea onClick={click}> 
        <CardContent className="p-2">
          <Typography sx={{ fontSize: 14, mb: 3, color: "#6B727A" }}>
            {date.toLocaleString("en-us", { weekday: "long" })} 
            <br />
            {date.toLocaleString("en-us", { month: "short", day: "numeric" })}
          </Typography>
          <Typography sx={{ fontSize: 14, color: "#575F68" }}>Score</Typography>
          <Typography sx={{ fontSize: 32, fontWeight: 500, lineHeight: 1 }}>
            {data.value !== undefined ? data.value.toFixed(1) : "-"}
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
