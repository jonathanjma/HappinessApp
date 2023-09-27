import { useEffect, useState } from "react";
import DynamicSmile from "../happiness/DynamicSmile";
import { useMutation } from "react-query";
import { useApi } from "../../contexts/ApiProvider";
import { useParams } from "react-router-dom";
import ErrorBox from "../../components/signIn/ErrorBox";
import PasswordErrorBox from "../../components/signIn/PasswordErrorBox";

export default function ResetPassword() {
  const [hasError, setHasError] = useState(false);
  const [message, setMessage] = useState("");
  const [password, setPassword] = useState("");
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const { token } = useParams();
  const api = useApi();
  const togglePassResetMutation = useMutation({
    mutationFn: (value) => {
      return api.post(`/user/reset_password/${token}`, {
        "password": value
      })
    }
  })
  const submitPassword = () => {
    setHasSubmitted(true)
    if (hasError || password.length === 0) return;

    togglePassResetMutation.mutate(password);
  };

  useEffect(() => {
    if (togglePassResetMutation.isError) {
      setHasError(true);
      setMessage("Error resetting password. Check your internet connection");
    } else if (!hasSubmitted) {
      setHasError(false);
    }
  }, [togglePassResetMutation.isError]);

  useEffect(() => {
    if (togglePassResetMutation.isSuccess) {
      setMessage("Password changed");
    }
  }, [togglePassResetMutation.isSuccess]);

  return (
    // Root div
    <div className=" bg-raisin-600 h-screen w-screen flex flex-col absolute inset-0">
      <div className="flex flex-row">
        <h1 className="text-tangerine-50 text-6xl md:text-6xl ml-10 mt-10">
          <b>Let's get that password reset.</b>
        </h1>
        <span className="mt-10 ml-10 mobile-hidden">
          <DynamicSmile happiness={10} />
        </span>
      </div>
      <span className="mt-10 ml-10 md:hidden">
        <DynamicSmile happiness={10} />
      </span>

      <p className=" text-3xl leading-9  ml-10 text-white mt-10">
        Enter your new password. <br></br>
        <br></br>
        <br></br> Make it a strong one :P
      </p>

      <div className="flex-row flex">
        <input
          type="password"
          className={`bg-gray-200 ${hasError ? "border-red-500 border-4" : "border-gray-400 border-2"
            } rounded w-80 py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white mt-10 ml-10`}
          value={password}
          onChange={(e) => {
            console.log("Password changed " + e.target.value);
            setPassword(e.target.value);
          }}
          placeholder="**************"
        ></input>
        <button
          className=" bg-green-500 border-2 border-green-600 rounded w-40 py-2 px-4 text-white leading-tight focus:outline-none mt-10 ml-3 mr-2"
          onClick={submitPassword}
        >
          <b>Submit</b>
        </button>
      </div>
      <div className="md:w-2/5 ml-10 mt-4 pr-10 ">
        <PasswordErrorBox password={password} setHasError={setHasError} />
      </div>
      <p
        className={`text-white ml-10 mt-4 text-xl ${message.length === 0 ? "collapse" : ""
          }`}
      >
        {message}
      </p>
    </div>
  );
}
