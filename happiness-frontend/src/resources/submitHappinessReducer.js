import { SubmitPageState } from "../keys";
import { initializeDateList } from "../pages/SubmitHappiness";

export const INITIAL_STATE = {
  pageState: SubmitPageState.LOADING,
  happinessEntries: {}, // happiness entries with dates as keys
  selectedDate: new Date(),
}

export const ACTIONS = {
  FETCH_SUCCESS: "fetch success",
  FETCH_ERROR: "fetch error",
  FETCH_LOADING: "fetch loading",
  CHANGE_EDIT: "change edit",
  CHANGE_DATE: "change date",
  CHANGE_COMMENT: "change comment",
  CHANGE_HAPPINESS: "change happiness",
}

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export const happinessReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.FETCH_LOADING:
      return {
        ...state,
        happinessEntries: {},
        pageState: SubmitPageState.LOADING
      }
    case ACTIONS.FETCH_SUCCESS:
      console.log("FETCH_SUCCESS")
      // Requires a payload with happiness entries, which should be an array of 
      // happiness objects.
      const happinessEntries = action.happinessEntries;
      const dates = [];
      initializeDateList(dates);
      console.log(`Happiness entries = ${happinessEntries}`)
      const happinessMap = state.happinessEntries;
      happinessEntries.forEach((entry) => {
        happinessMap[entry.timestamp] = entry;
      });
      dates.forEach((date) => {
        if (!happinessMap.hasOwnProperty(formatDate(date))) {
          happinessMap[formatDate(date)] = {
            comment: "",
            value: 5
          }
        }
      })
      return {
        ...state,
        pageState: happinessMap.hasOwnProperty(formatDate(state.selectedDate))
          ? SubmitPageState.SUBMITTED : SubmitPageState.UNSUBMITTED,
        happinessEntries: happinessMap
      }
    case ACTIONS.FETCH_ERROR:
      return {
        ...state,
        pageState: SubmitPageState.ERROR,
      }
    case ACTIONS.CHANGE_DATE:
      // Requites a payload with a date object, payload.date.
      const date = action.date;
      return {
        ...state,
        selectedDate: date
      }
    case ACTIONS.CHANGE_EDIT:
      // Requires: a happiness value to change the pre edit happiness
      if (state.pageState === SubmitPageState.EDITING) {
        return {
          ...state,
          pageState: SubmitPageState.SUBMITTED,
        }
      } else {
        return {
          ...state,
          pageState: SubmitPageState.EDITING
        }
      }
    case ACTIONS.CHANGE_COMMENT:
      // Requires: a comment value in the payload
      const comment = action.comment;
      const happiness = state.happinessEntries[state.selectedDate];
      happiness.comment = comment;
      // Should have mutated the state (hopefully)
      return state
    case ACTIONS.CHANGE_HAPPINESS:
      // Requires: a happiness value in the payload
      let happinessValue = action.happinessValue
      if (happinessValue > 10 && happinessValue - 10 < 1) {
        happinessValue = 10;
      } else if (happiness > 10) {
        happiness /= 10;
      }
      state.happinessEntries[state.selectedDate].value = happinessValue
      // Should have mutated state (hopefully)
      return state
    default:
      return state
  }
}