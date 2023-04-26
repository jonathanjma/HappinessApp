import {useEffect, useState} from "react";
import ErrorBox from "./ErrorBox";

/**
 * Props: <br />
 * password - the password state on the parent page <br /> <br />
 * setHasError - controls error state on parent page <br /> <br />
 * setErrorMessage - controls error message on parent page <br /> <br />
 * errorMessage - Error message to show in text box <br /> <br />
 * checkPassword - Tells prop when to check password validity when this boolean changes <br /> <br />
 */
export default function PasswordErrorBox (props) {

    const password = props.password  // The password state on the parent page.
    const setHasError = props.setHasError  // Control's the parent page error state.
    const [errorMessage, setErrorMessage] = useState("")


    useEffect(() => {
        const digitRegex = new RegExp("^(?=.*[0-9])");
        const upperCaseRegex = /[A-Z]/

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
        setHasError(false);
        setErrorMessage("");
    }, [password])
    useEffect(() => {
        setErrorMessage("")
        setHasError(false);
    }, [])

    return (
        <ErrorBox errorMessage={errorMessage} />
    )
}