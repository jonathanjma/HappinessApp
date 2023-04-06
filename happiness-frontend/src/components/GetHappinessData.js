import { useApi } from "../contexts/ApiProvider";
import { useUser } from "../contexts/UserProvider";
import { useQuery } from "react-query";

// Gets list of Happiness objects for given user (from the past 7 days)
export function PrevWeekData(user) {
  const api = useApi();
  const lastWk = new Date();
  lastWk.setDate(lastWk.getDate() - 7);
  const weekData = lastWk.toISOString().substring(0, 10);
  const {
    isLoading: isLoadingH,
    data: dataH,
    error: errorH,
  } = useQuery("stats happiness data", () =>
    api
      .get("/happiness/", { id: user.id, start: weekData })
      .then((res) => res.data)
  );
  return [isLoadingH, dataH, errorH];
}
// Gets list of Happiness objects for given user (from the past month)
export function PrevMonthData(user) {
  const lastMt = new Date();
  lastMt.setMonth(lastMt.getMonth() - 1);

  const api = useApi();
  const monthData = lastMt.toISOString().substring(0, 10);
  const {
    isLoading: isLoadingHM,
    data: dataHM,
    error: errorHM,
  } = useQuery("stats monthly happiness data", () =>
    api
      .get("/happiness/", { id: user.id, start: monthData })
      .then((res) => res.data)
  );
  return [isLoadingHM, dataHM, errorHM];
}

export function GetCountHappiness(count, user, page = 1) {
  const api = useApi();
  const { isLoading, data, error } = useQuery("get happiness by count", () =>
    api
      .get("/happiness/count", { count: count, id: user.id, page: page })
      .then((res) => res.data)
  );
  return [isLoading, data, error];
}

// Gets list of Happiness objects for given user (for given start and end Date objects)
export function GetRangeHappiness(user, startData, endData) {
  const api = useApi();
  console.log(startData);
  console.log(endData);
  const {
    isLoading: isLoadingH,
    data: dataH,
    error: errorH,
    refetch: refetch,
  } = useQuery("happiness data by range", () =>
    api
      .get("/happiness/", { id: user.id, start: startData, end: endData })
      .then((res) => res.data)
  );
  return [isLoadingH, dataH, errorH, refetch];
}
