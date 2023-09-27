import {Spinner} from "react-bootstrap";
import {Box} from "@mui/material";
import CommentCard from "../../components/CommentCard";

export default function Comments({commentsResult}) {
    if (
        commentsResult.isLoading ||
        commentsResult.isError ||
        commentsResult.data == null
    ) {
        return (
            <>
                <Spinner/>
            </>
        );
    }

    return (
        <Box className="overflow-auto h-full">
            {commentsResult.data.map((item) => (
                <CommentCard
                    comment={item.text}
                    commenter={item.author.username}
                    commenterAvatar={item.author.profile_picture}
                    groupName={"Cornell"} // TODO get the actual group
                    commentDate={item.timestamp}
                    key={item.id}
                />
            ))}
        </Box>
    );
};