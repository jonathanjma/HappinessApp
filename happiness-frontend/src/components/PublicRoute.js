import { Navigate } from "react-router-dom";
import { useUser } from "../contexts/UserProvider";
import { Keys } from "../keys";
import {useEffect} from "react";

export default function PublicRoute({ children }) {
  const { user: userState, GetUserFromToken} = useUser();
  useEffect( () => {
    GetUserFromToken()
  }, [])
  if (userState.type === Keys.LOADING) {
    return null;
  } else if (userState.type === Keys.SUCCESS) {
    return <Navigate to="/home" />;
  } else {
    return children;
  }

}
