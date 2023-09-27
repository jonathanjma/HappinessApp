export default function CommentHeader({commentsResult}) {
    if (
        commentsResult.isLoading ||
        commentsResult.isError ||
        commentsResult.data == null
    ) {
        return (
            <>
                <h5 className="h5 border-solid border-[#E4E0E0] border-b-2 border-x-0 border-t-0 py-0.5">
                    Comments
                </h5>
            </>
        );
    }
    return (
        <h5 className="h5 border-solid border-[#E4E0E0] border-b-2 border-x-0 border-t-0 py-0.5">
            {`Comments (${commentsResult.data.length})`}
        </h5>
    );
};