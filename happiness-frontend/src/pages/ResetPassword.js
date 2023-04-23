import {useEffect, useState} from "react";
import DynamicSmile from "../components/DynamicSmile";
import {useMutation} from "react-query";
import {useApi} from "../contexts/ApiProvider";
import {useParams} from "react-router-dom";

export default function ResetPassword() {
    const [hasError, setHasError] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [message, setMessage] = useState("");
    const [password, setPassword] = useState("");
    const [hasSubmitted, setHasSubmitted] = useState(false)
    const { token } = useParams()
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
        const upperCaseRegex = new RegExp("^(?=.*[A-Z])");
        const digitRegex = new RegExp("^(?=.*[0-9])");
        const emailRegex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

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
        togglePassResetMutation.mutate(password)
        setMessage("Password changed.")
    }


    useEffect(() => {
        if (togglePassResetMutation.isError) {
            setHasError(true)
            setMessage("Error resetting password. Check your internet connection")
        } else if (!hasSubmitted){
            setHasError(false)

        } else {
            setMessage("Password reset!")
        }
    }, [togglePassResetMutation.isError])

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
                Enter your new password. <br></br><br></br><br></br> Make it a strong one :P
            </p>

            <div className="flex-row flex">
                <input
                    type="password"
                    className={`bg-gray-200 ${
                        hasError ? "border-red-500 border-4" : "border-gray-400 border-2"
                    } rounded w-80 py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white mt-10 ml-10`}
                    value={password}
                    onChange={(e) => {
                        setPassword(e.target.value)
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
            <p className="text-white ml-10 mt-4 text-xl">{message}</p>
        </div>
    );
}

