import { Avatar, Box, Card, Typography } from "@mui/material";
import React from "react";

export default function CommentCard({
  commenter,
  commenterAvatar,
  groupName,
  commentDate,
  comment,
}) {
  return (
    <Card
      className="rounded-none py-4 px-6 shadow-none"
      style={{ borderRadius: "12px" }}
    >
      <Box className="flex flex-row">
        <Avatar src={commenterAvatar} />
        <Box className="w-4" />
        <Box className="flex flex-col">
          <Typography className="comment-header">
            {commenter + " • " + groupName}
          </Typography>
          <Typography className="comment-body"> {comment} </Typography>
          <Typography className="body2-grey">{commentDate} </Typography>
        </Box>
      </Box>
    </Card>
  );
}
