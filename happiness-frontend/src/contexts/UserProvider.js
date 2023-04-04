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

  const authHeader = () => {
    const token = localStorage.getItem(Keys.TOKEN)
    return {
      headers: {
        Authorization: `Bearer ${token}`
      }
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
        .delete("/token/", authHeader()).then((res) => {
      localStorage.setItem(Keys.TOKEN, null);
      setUser(UserState.error());
    })
  }

  async function Login(username, password) {
    console.log("Login: trying login");
    setUser(UserState.loading());

    await api
        .post("/token/", {}, loginHeader(username, password))
        .then(async (res) => {
          console.log("Login: success")
          localStorage.setItem(Keys.TOKEN, res.data["session_token"]);
          await GetUserFromToken()
        })
        .catch((err) => {console.log(`REAL LOGIN: error ${err}`); setUser(UserState.error());});
  }

  /**
   * Precondition: the local storage must have a valid token.
   * Postcondition: the user object is either in the error or success state.
   */
  function GetUserFromToken() {
    setUser(UserState.loading());
    console.log(`Auth header: ${JSON.stringify(authHeader())}`)
    if (localStorage.getItem(Keys.TOKEN) !== null) {
      api
          .get("/user/self/", {}, authHeader())
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

  async function CreateUser(email, username, password) {
    await api
        .post("/user/", {
            username: username,
            password: password,
            email: email,
        })
        .then(async (res) => {
          console.log("CreateUser: Got data");
          const data = res.data;
          console.log(`CreateUser: token ${JSON.stringify(data)}`);
          console.log(`CreateUser: username ${data.username}, password ${data.password}`);
          await Login(username, password);
        }).catch((err) => {
          console.log(`CreateUser: user error: ${err}`);
          setUser(UserState.error());
    })
  }

  async function DeleteUser() {
    await api.delete("/user/", authHeader()).then(() => {
      setUser(UserState.error())
      localStorage.setItem(Keys.TOKEN, null)
    })
  }

  return (
    <UserContext.Provider value={{ user, setUser, Login, Logout, GetUserFromToken, CreateUser, DeleteUser}}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
