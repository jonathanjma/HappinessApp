import { Keys } from "../keys"
/**
 * The user state represents the state of loading the current user from the backend.
 * A success state represents when the user is logged in and returns the user object.
 * The error state represents when the user is logged out or there is an issue in getting the object.
 * The loading state represents when the object is loading from the backend.
 */
export class UserState {
  static success(user) {
    return { type: Keys.SUCCESS, user: user }
  }
  static error() {
    return { type: Keys.ERROR }
  }
  static loading() {
    return { type: Keys.LOADING }
  }
}