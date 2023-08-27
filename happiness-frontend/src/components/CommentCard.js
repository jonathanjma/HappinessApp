import { Avatar, Card, CardContent, CardHeader, Typography, Box } from '@mui/material'
import React from 'react'

export default function CommentCard({
  commenter,
  commenterAvatar,
  groupName,
  commentDate,
  comment
}) {
  return (
    <Card className='min-w-[300px] mr-3 rounded-xl' style={{ borderRadius: "12px" }}>
      {/* TODO ensure CardHeader supports long usernames / group naems */}
      <CardHeader
        title={commenter}
        subheader={groupName}
        avatar={<Avatar alt={commenter} src={commenterAvatar} />}
        action={<Box className=" flex-1 flex pr-3 mt-0 h-[36px] items-center">
          <Typography variant='body2'>{commentDate}</Typography>
        </Box>}
      />
      <CardContent>
        <Typography variant='h7' className='body1'>{comment}</Typography>
      </CardContent>
    </Card>
  )
}
