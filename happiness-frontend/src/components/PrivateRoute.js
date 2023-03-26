import { Navigate, useLocation } from "react-router-dom";
import { useUser } from "../contexts/UserProvider";
import { Keys } from "../keys";
import {useEffect} from "react";

export default function PrivateRoute({ children }) {
  const { user: userState, GetUserFromToken } = useUser();
  useEffect( () => {
    GetUserFromToken()
  }, [])
  const location = useLocation();

  console.log(userState);

  if (userState.type === Keys.LOADING) {
    return null;
  } else if (userState.type === Keys.SUCCESS) {
    return children;
  } else {
    const url = location.pathname + location.search + location.hash;
    return <Navigate to="/" state={{ next: url }} />;
  }
}
