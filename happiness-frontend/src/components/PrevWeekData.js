import { useApi } from "../contexts/ApiProvider";
import { useUser } from "../contexts/UserProvider";
import { useQuery } from "react-query";

export default function PrevWeekData() {
  const api = useApi();
  const { user: userState } = useUser();
  const me = userState.user;
  const lastWk = new Date();
  lastWk.setDate(lastWk.getDate() - 7);
  const weekData = lastWk.toISOString().substring(0, 10);
  const {
    isLoading: isLoadingH,
    data: dataH,
    error: errorH,
  } = useQuery("stats happiness data", () =>
    api
      .get("/happiness/?id=" + me.id + "&start=" + weekData)
      .then((res) => res.data)
  );
  return [isLoadingH, dataH, errorH];
}
