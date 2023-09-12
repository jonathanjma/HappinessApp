import { Spinner } from "react-bootstrap"
import { Box } from "@mui/material"
import CommentCard from "./CommentCard"

export default function SideScrollingComments ({commentsResult, className=""})  {

  const formatCommentDate = (commentDate) => {
    const date = new Date(commentDate)
    return `${(date.getMonth()+1).toString().padStart(2, '0')}/${(date.getDate()).toString().padStart(2, '0')}
    `  
}
  if (commentsResult.isLoading || commentsResult.isError || commentsResult.data == null) {
      return <Box className={className}><Spinner /></Box>  
  }
  else {
      return <Box className={"flex flex-row pb-1 overflow-x-auto " + className}>
      {commentsResult.data.map((item) =>
       <CommentCard
          comment={item.text}
          commenter={item.author.username}
          commenterAvatar={item.author.profile_picture}
          groupName={"Cornell"}  // TODO get the actual group
          commentDate={formatCommentDate(item.timestamp)}
          key={item.id}
       />)}
      </Box>
  }
}