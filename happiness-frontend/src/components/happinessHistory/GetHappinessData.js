import { useApi } from "../../contexts/ApiProvider";
import { useQuery } from "react-query";

// Gets list of Happiness objects for given user (from the past 7 days)
export function PrevWeekData(userMode, id) {
  const api = useApi();
  const lastWk = new Date();
  lastWk.setDate(lastWk.getDate() - 7);
  const weekData = lastWk.toLocaleDateString("sv").substring(0, 10);
  const get_url =
    (userMode ? `/happiness/?id=${id}&` : `/group/${id}/happiness?`) +
    `start=${weekData}`;
  const {
    isLoading: isLoadingH,
    data: dataH,
    error: errorH,
  } = useQuery("weekly happiness data " + get_url, () =>
    api.get(get_url).then((res) => res.data)
  );
  return [isLoadingH, dataH, errorH];
}

export function GetCountHappiness(count, user, page = 1) {
  const api = useApi();
  const { isLoading, data, error } = useQuery(
    "get happiness by count",
    () =>
      api
        .get("/happiness/count", { count: count, id: user.id, page: page })
        .then((res) => res.data),
    { refetchOnWindowFocus: false }
  );
  return [isLoading, data, error];
}

// Gets list of Happiness objects for given user (for given start and end Date objects)
export function GetRangeHappiness(userMode, id, startDate, endDate) {
  const api = useApi();
  const get_url =
    (userMode ? `/happiness/?id=${id}&` : `/group/${id}/happiness?`) +
    `start=${startDate}&end=${endDate}`;
  const {
    isLoading: isLoadingH,
    data: dataH,
    error: errorH,
    refetch,
  } = useQuery(
    "happiness data by range " + get_url,
    () => api.get(get_url).then((res) => res.data),
    { refetchOnWindowFocus: false }
  );
  return [isLoadingH, dataH, errorH, refetch];
}
