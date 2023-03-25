import { Navigate } from "react-router-dom";
import { useUser } from "../contexts/UserProvider";
import { Keys } from "../keys";

export default function PublicRoute({ children }) {
  const { user: userState } = useUser();

  console.log(userState);

  if (userState.type === Keys.LOADING) {
    return null;
  } else if (userState.type === Keys.SUCCESS) {
    return <Navigate to="/home" />;
  } else {
    return children;
  }
}
