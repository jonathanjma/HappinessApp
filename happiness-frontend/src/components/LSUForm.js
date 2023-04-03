import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { useUser } from "../contexts/UserProvider";

export default function LSUForm(props) {
  const email = `${(Math.random() + 1).toString(36).substring(7)}@gmail.com` // TODO implement email textbox
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [hasError, setHasError] = useState(false);
  const [hasConfirmError, setHasConfirmError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [beforeEdit, setBeforeEdit] = useState(true);
  const { Login, CreateUser } = useUser();

  // Password validation effects:
  useEffect(() => {
    if (props.isLoggingIn) {
      setHasError(false);
      setErrorMessage("");
      return;
    }
    if (beforeEdit) {
      setBeforeEdit(false);
      return;
    }

    const upperCaseRegex = new RegExp("^(?=.*[A-Z])");
    const digitRegex = new RegExp("^(?=.*[0-9])");

    if (password.length < 8) {
      setHasError(true);
      setErrorMessage("The password must be at least 8 characters long.");
      return;
    }
    if (!upperCaseRegex.test(password)) {
      setHasError(true);
      setErrorMessage("The password must contain at least 1 uppercase letter.");
      return;
    }
    if (!digitRegex.test(password)) {
      setHasError(true);
      setErrorMessage("The password must contain at least 1 digit.");
      return;
    }
    if (password !== confirmPassword) {
      setHasError(true);
      setHasConfirmError(true);
      setErrorMessage("The password fields do not match.");
      return;
    } else {
      setHasConfirmError(false);
    }

    setHasError(false);
    setErrorMessage("");
  }, [password, confirmPassword, props.isLoggingIn]);

  // Sign in effect:
  const signIn = () => {
    if (hasError) {
      console.log("has error");
      toast(`You cannot login. ${errorMessage}`); //FIXME toast message not showing
    } else {
      if (props.isLoggingIn) {
        console.log("You're signing in.");
        // TODO try to see if login failed and show message if it did.
        Login(username, password).then(() => {
          window.location.reload();
        })
      } else {
        console.log("You're signing up")
        CreateUser(email, username, password).then(() => {
          console.log("Create user complete")
          window.location.reload();
        })
      }

    }
  };

  return (
    <>
      <form className="w-full max-w-sm">
        {/*Username*/}
        <div className="md:flex md:items-center mb-6">
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
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
              }}
              placeholder="JahnDoe@example.com"
            />
          </div>
        </div>
        {/*Password*/}
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
              className={`bg-gray-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white  ${
                hasError ? "border-red-500" : "focus:border-blue-500"
              }`}
              id="inline-password"
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
              }}
              placeholder="***************"
            />
            <p className="text-red-500">{errorMessage}</p>
          </div>
        </div>
        {/*Confirm password*/}
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
              className={`bg-gray-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white ${
                hasConfirmError ? "border-red-500" : "focus:border-blue-500"
              }`}
              id="inline-confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
              }}
              placeholder="***************"
            />
          </div>
        </div>
        <div className="md:flex md:items-center">
          <div className="md:w-1/3"></div>
          <div className="md:w-2/3">
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
