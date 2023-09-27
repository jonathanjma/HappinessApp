import DynamicSmile from "../happiness/DynamicSmile";
import { useEffect, useState } from "react";
import { useMutation } from "react-query";
import { useApi } from "../../contexts/ApiProvider";
import { useParams } from "react-router-dom";
import PublicRoute from "../../components/PublicRoute";
import ErrorBox from "../../components/signIn/ErrorBox";

export default function RequestResetPassword(props) {
  const [email, setEmail] = useState("");
  const [emailUnsubmitted, setEmailUnsubmitted] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [message, setMessage] = useState("");
  const { token } = useParams();
  const api = useApi();
  const toggleEmailMutation = useMutation({
    mutationFn: (value) => {
      return api.post("/user/initiate_password_reset/", {
        email: value,
      });
    },
  });

  useEffect(() => {
    if (toggleEmailMutation.isError) {
      setHasError(true);
      setErrorMessage(
        "Error sending email. Are you sure an account is associated with that email?"
      );
      setMessage("");
    } else if (toggleEmailMutation.isSuccess) {
      setHasError(false);
      setMessage(
        "Email sent. Emails can take up to a few minutes to be received."
      );
      setErrorMessage("");
    }
  }, [toggleEmailMutation.isError, toggleEmailMutation.isSuccess]);
  let submitEmail = () => {
    if (
      email === "" ||
      !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(email)
    ) {
      setHasError(true);
      setErrorMessage("Email invalid");
    } else {
      setMessage("Email sending...");
      setEmailUnsubmitted(false);
      setHasError(false);
      console.log("Mutating email");
      toggleEmailMutation.mutate(email);
    }
  };

  return (
    // Root div
    <div className=" bg-raisin-600 h-screen w-screen flex flex-col absolute inset-0">
      <div className="flex flex-row">
        <h1 className="text-tangerine-50 text-6xl md:text-6xl ml-10 mt-10">
          <b>Forgot your password?</b>
        </h1>
        <span className="mt-10 ml-10 mobile-hidden">
          <DynamicSmile happiness={10} />
        </span>
      </div>
      <span className="mt-10 ml-10 md:hidden">
        <DynamicSmile happiness={10} />
      </span>

      <p className=" text-3xl leading-9  ml-10 text-white mt-10">
        We can help. <br></br> <br></br>
        Enter the email you used to create your account.
      </p>

      <div className="flex-col flex">
        <input
          type="email"
          className={`bg-gray-200 ${
            hasError ? "border-red-500 border-4" : "border-gray-400 border-2"
          } rounded w-80 py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white mt-10 ml-10`}
          value={email}
          onChange={(e) => {
            setEmailUnsubmitted(true);
            setEmail(e.target.value);
            setHasError(false);
            setMessage("");
            setErrorMessage("");
          }}
          placeholder="john.doe@example.com"
        ></input>
        <button
          className=" bg-green-500 border-2 border-green-600 rounded w-40 py-2 px-4 text-white leading-tight focus:outline-none mt-4 ml-10"
          onClick={submitEmail}
        >
          <b>Submit</b>
        </button>
      </div>
      <div className="w-2/5 ml-10 mt-4">
        <ErrorBox errorMessage={errorMessage} />
      </div>
      <p className="text-white ml-10 mt-4 text-xl">{message}</p>
    </div>
  );
}
