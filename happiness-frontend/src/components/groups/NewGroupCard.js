import { useNavigate } from "react-router-dom";
import Card from "@mui/material/Card";
import { Button } from "@mui/material";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";

export default function NewGroupCard({ data }) {
  const navigate = useNavigate();

  return (
    <Card className="border rounded-lg shadow-none">
      <CardContent className="p-4">
        <Typography className="text-sm">{data.users.length} members</Typography>
        <Typography className="text-3xl font-semibold mb-4">
          {data.name}
        </Typography>
        <div className="flex gap-2">
          <Button
            variant="outlined"
            className="flex-grow border-slate-400 text-black normal-case"
            onClick={() => navigate("/groups/" + data.id)}
          >
            Open Group
          </Button>
          <Button variant="outlined" className="p-2 border-slate-400">
            <MoreHorizIcon sx={{ color: "black" }} />
          </Button>
        </div>
        {/*<div className="grid">*/}
        {/*  <div className="grid-cols-3">*/}
        {/*    {data.users.slice(0, 3).map((user) => (*/}
        {/*      <img*/}
        {/*        key={user.id}*/}
        {/*        src={user.profile_picture}*/}
        {/*        title={user.username}*/}
        {/*        className="m-1 max-w-[40px] rounded-full"*/}
        {/*      />*/}
        {/*    ))}*/}
        {/*  </div>*/}
        {/*</div>*/}
      </CardContent>
    </Card>
  );
}
