import { createContext, useContext } from "react";
import ApiClient from "../ApiClient";
import { QueryClient, QueryClientProvider } from "react-query";

const ApiContext = createContext();

export default function ApiProvider({ children }) {
  const api = new ApiClient();
  const queryClient = new QueryClient();

  return (
    <ApiContext.Provider value={api}>
      <QueryClientProvider client={queryClient} value={api}>
        {children}
      </QueryClientProvider>
    </ApiContext.Provider>
  );
}

export function useApi() {
  return useContext(ApiContext);
}
