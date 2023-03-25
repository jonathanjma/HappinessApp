import { createContext, useContext, useState, useEffect } from "react";
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

  // On initialization:
  useEffect(() => {
    if (localStorage.getItem(Keys.TOKEN) == null) {
      GetUserFromToken();
    } else console.log("hi");
  }, [api]);

  /**
   * Precondition: the user is logged in.
   */
  function Logout() {
    // TODO: broken
    const { isLoading, error, data } = useQuery(
      `${localStorage.getItem(Keys.TOKEN)} logout`,
      () => api.delete("/token/").then((res) => res)
    );
    if (error) {
      return;
    }
    if (isLoading) {
      setUser(UserState.loading());
      return;
    }
    localStorage.setItem(Keys.TOKEN, "");
    setUser(UserState.error());
  }

  function Login(username, password) {
    setUser(UserState.loading());
    console.log("trying login");

    api
      .post("/token/", {}, loginHeader(username, password))
      .then((res) => {
        setUser(UserState.success(res.data));
        localStorage.setItem(Keys.TOKEN, res.data["session_token"]);
        GetUserFromToken();
      })
      .catch((err) => setUser(UserState.error()));
  }

  /**
   * Precondition: the lcoal storage must have a valid token.
   * Postcondition: the user object is either null, or has data.
   */
  function GetUserFromToken() {
    setUser(UserState.loading());
    console.log("checking token");

    api
      .get("/user/self/")
      .then((res) => setUser(UserState.success(res.data)))
      .catch((err) => setUser(UserState.error()));
  }

  function CreateUser(email, username, password) {
    // TODO: broken
    const { isLoading, error, data } = useQuery(`${username} CREATE`, () =>
      api
        .post("/user/", {
          email: email,
          username: username,
          password: password,
        })
        .then((res) => res.data)
    );
    if (isLoading) {
      setUser(UserState.loading());
      return;
    }
    if (error) {
      setUser(UserState.error());
    }
    localStorage.setItem(Keys.TOKEN, data);
    Login(username, password);
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
    <UserContext.Provider value={{ user, setUser, Login, Logout }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
