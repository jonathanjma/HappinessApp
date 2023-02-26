import {createContext, useContext} from "react";
import ApiClient from "../ApiClient";
// import { toast } from "react-toastify";

const ApiContext = createContext();

export default function ApiProvider({ children }) {
  const onError = {}; //toast('An unexpected error has occurred. Please try again later.');

  const api = new ApiClient(onError);

  return <ApiContext.Provider value={api}>{children}</ApiContext.Provider>;
}

export function useApi() {
  return useContext(ApiContext);
}
