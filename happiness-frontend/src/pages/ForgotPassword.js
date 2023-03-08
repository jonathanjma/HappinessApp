import DynamicSmile from "../components/DynamicSmile";
import { useState } from "react";

export default function ForgotPassword() {
  let msgText = () => {
    if (hasError) {
      return "Invalid email provided.";
    } else if (!emailUnsubmitted) {
      return "Email sent.";
    } else {
      return "";
    }
  };
  const [email, setEmail] = useState("");
  const [emailUnsubmitted, setEmailUnsubmitted] = useState(true);
  const [hasError, setHasError] = useState(false);
  let submitEmail = () => {
    if (
      email === "" ||
      !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(email)
    ) {
      setHasError(true);
      // TODO show error
    } else {
      setEmailUnsubmitted(false);
      setHasError(false);
      // TODO submit email
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

      <div className="flex-row flex">
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
          }}
          placeholder="john.doe@example.com"
        ></input>
        <button
          className=" bg-green-500 border-2 border-green-600 rounded w-40 py-2 px-4 text-white leading-tight focus:outline-none mt-10 ml-3 mr-2"
          onClick={submitEmail}
        >
          <b>Submit</b>
        </button>
      </div>
      <p className="text-white ml-10 mt-4 text-xl">{msgText()}</p>
    </div>
  );
}
