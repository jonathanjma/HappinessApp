import { useEffect, useState } from "react";
import "react-toastify/dist/ReactToastify.css";
import { useUser } from "../../contexts/UserProvider";
import { Keys } from "../../keys";
import Warning from "../../media/red-alert-icon.svg";
import { useNavigate } from "react-router-dom";
import ErrorBox from "./ErrorBox";
import PasswordErrorBox from "./PasswordErrorBox";

export default function LSUForm(props) {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [beforeEdit, setBeforeEdit] = useState(true);
  const [checkPassword, setCheckPassword] = useState(false);
  const { Login, CreateUser, user } = useUser();

  const emailRegex =
    /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  // Input validation effects:
  useEffect(() => {
    if (props.isLoggingIn) {
      setHasError(false);
      setErrorMessage("");
      return;
    }

    if (beforeEdit) {
      setBeforeEdit(false);
      setErrorMessage("");
      setHasError(true);
      return;
    }
    if (username.trim().length === 0) {
      setHasError(true);
      setErrorMessage("Username is empty");
      return;
    }
    if (username.trim() !== username) {
      setHasError(true);
      setErrorMessage("Username cannot start or end with spaces.");
      return;
    }
    // Tests email
    if (!emailRegex.test(email)) {
      setHasError(true);
      setErrorMessage("Email is invalid");
      setCheckPassword(!checkPassword);
      return;
    }
    const digitRegex = new RegExp("^(?=.*[0-9])");
    const upperCaseRegex = /[A-Z]/;

    if (password.length < 8) {
      setHasError(true);
      setErrorMessage("The password must be at least 8 characters long");
      return;
    }
    if (!upperCaseRegex.test(password)) {
      setHasError(true);
      setErrorMessage("The password must contain at least 1 uppercase letter");
      return;
    }
    if (!digitRegex.test(password)) {
      setHasError(true);
      setErrorMessage("The password must contain at least 1 digit");
      return;
    }
    if (password !== confirmPassword) {
      setErrorMessage("The password fields do not match");
      setHasError(true);
      return;
    }
    setHasError(false);
    setErrorMessage("");
  }, [password, confirmPassword, props.isLoggingIn, username, email]);

  // Sign in effect:
  async function signIn() {
    if (!hasError && props.isLoggingIn) {
      await Login(username, password);
      if (user.type !== Keys.SUCCESS) {
        console.log("Login error");
        setErrorMessage("Username password combination not found");
        setHasError(true);
      } else {
        console.log("RELOADING:");
        window.location.reload();
      }
    } else if (!hasError) {
      await CreateUser(email, username, password);
      if (user.type !== Keys.SUCCESS) {
        console.log("Sign up error");
        setErrorMessage("Username or email already taken");
      } else {
        console.log("RELOADING:");
        window.location.reload();
      }
    }
  }

  return (
    <>
      <form className="w-full max-w-sm">
        {/* Username */}
        <div className={`md:flex md:items-center mb-6`}>
          <div className="md:w-1/3">
            <label
              className="block text-gray-500 font-bold md:text-right mb-1 md:mb-0 pr-4"
              htmlFor="inline-full-name"
            >
              Username
            </label>
          </div>
          <div className="md:w-2/3">
            <input
              className="bg-gray-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-blue-500"
              id="inline-full-name"
              type="text"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
              }}
              placeholder="Fiddle01"
            />
          </div>
        </div>
        {/* Email */}
        <div
          className={`md:flex md:items-center mb-6 ${
            props.isLoggingIn ? "collapse" : ""
          }`}
        >
          <div className="md:w-1/3">
            <label
              className="block text-gray-500 font-bold md:text-right mb-1 md:mb-0 pr-4"
              htmlFor="inline-full-name"
            >
              Email
            </label>
          </div>
          <div className="md:w-2/3">
            <input
              className="bg-gray-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-blue-500"
              id="inline-full-name"
              type="text"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
              }}
              placeholder="JahnDoe@example.com"
            />
          </div>
        </div>
        {/* Password */}
        <div className="md:flex md:items-center mb-6">
          <div className="md:w-1/3">
            <label
              className="block text-gray-500 font-bold md:text-right mb-1 md:mb-0 pr-4"
              htmlFor="inline-password"
            >
              Password
            </label>
          </div>
          <div className="md:w-2/3">
            <input
              className={`bg-gray-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-blue-500`}
              id="inline-password"
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
              }}
              placeholder="***************"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  signIn();
                }
              }}
            />
          </div>
        </div>
        {/* Confirm password */}
        <div
          className={`md:flex md:items-center mb-6 ${
            props.isLoggingIn ? "collapse" : ""
          }`}
        >
          <div className="md:w-1/3">
            <label
              className="block text-gray-500 font-bold md:text-right mb-1 md:mb-0 pr-4"
              htmlFor="inline-password"
            >
              Confirm Password
            </label>
          </div>
          <div className="md:w-2/3">
            <input
              className={`bg-gray-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-blue-500`}
              id="inline-confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
              }}
              placeholder="***************"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  signIn();
                }
              }}
            />
          </div>
        </div>
        <div className="md:flex md:items-center">
          <div className="md:w-1/3"></div>
          <div className="md:w-2/3">
            {/* Error boxes */}
            <ErrorBox errorMessage={errorMessage} />

            {/* Sign in button */}
            <button
              className="shadow bg-tangerine-500 hover:bg-tangerine-400 focus:shadow-outline focus:outline-none text-white font-bold py-2 px-4 rounded"
              type="button"
              onClick={signIn}
            >
              {props.isLoggingIn ? "Login" : "Sign Up"}
            </button>
          </div>
        </div>
      </form>
    </>
  );
}
