import { createContext, useContext, useState } from "react";
import { useApi } from "./ApiProvider";
import { Keys } from "../keys";
import { useQuery } from "react-query";
import { UserState } from "../models/UserState";

const UserContext = createContext();

/**
 * The UserProvider context provides functionality for getting the user
 * for all child components. The main point of the context is to allow child
 * components to access the state of the current user object, but this also
 * has functionality for the core user methods, such as logging in,
 * deleting the user, logging out, and registering a user.
 */

export default function UserProvider({ children }) {
  const [user, setUser] = useState(UserState.loading());
  const api = useApi();

  const loginHeader = (username, password) => {
    return {
      headers: {
        Authorization: "Basic " + btoa(`${username}:${password}`),
      },
    };
  };

  const authHeader = {
    headers: {
      Authorization: "Bearer " + localStorage.getItem(Keys.TOKEN)
    }
  }

  /**
   * Attempts to get the current user and update the user object.
   */

  /**
   * Precondition: the user is logged in.
   */
  function Logout() {
    console.log("Logout has begun.")
    api
        .delete("/token/", authHeader).then((res) => {
      localStorage.setItem(Keys.TOKEN, null);
      setUser(UserState.error());
    })
  }

  function Login(username, password) {
    // TODO reroute user
    console.log("Login: trying login");
    setUser(UserState.loading());

    api
        .post("/token/", {}, loginHeader(username, password))
        .then((res) => {
          console.log("Login: success")
          localStorage.setItem(Keys.TOKEN, res.data["session_token"]);
          GetUserFromToken();
        })
        .catch((err) => {console.log(`Login: error ${err}`); setUser(UserState.error())});
  }

  /**
   * Precondition: the lcoal storage must have a valid token.
   * Postcondition: the user object is either null, or has data.
   */
  function GetUserFromToken() {
    setUser(UserState.loading());

    if (localStorage.getItem(Keys.TOKEN) !== null) {
      api
          .get("/user/self/", {}, authHeader)
          .then((res) => {
            setUser(UserState.success(res.data));
            console.log("GetUserFromToken: User found")
          })
          .catch((err) => {
            console.log(`GetUserFromToken: error ${err}`);
            console.log(`GetUserFromToken: current token ${localStorage.getItem(Keys.TOKEN)}`)
            setUser(UserState.error());
          });
    } else {
      setUser(UserState.error())
    }
  }

  // TODO implement and test
  function CreateUser(email, username, password) {
    api
        .post("/user/", {
          email: email,
          username: username,
          password: password,
        })
        .then((res) => {
          const data = res.data
          localStorage.setItem(Keys.TOKEN, data);
          GetUserFromToken()
        }).catch((err) => {
          setUser(UserState.error());
          console.log(`CreateUser: user error: ${err}`)
    })
  }

  function DeleteUser() {
    // TODO: broken
    const { isLoading, error, data } = useQuery(
      `${localStorage.getItem(Keys.TOKEN)} DELETE`,
      api.delete("/user/").then((res) => res.data)
    );

    if (error) {
      return;
    }

    if (isLoading) {
      setUser(UserState.loading());
    }

    // This if statement should ensure that the user was properly deleted
    // But this comparison is very precarious.
    // TODO test this!
    if (data === user) {
      setUser(UserState.error());
    }
  }

  return (
    <UserContext.Provider value={{ user, setUser, Login, Logout, GetUserFromToken}}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
