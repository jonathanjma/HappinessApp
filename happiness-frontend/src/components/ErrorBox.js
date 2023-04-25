import Warning from "../media/red-alert-icon.svg";

export default function ErrorBox (props) {
    const errorMessage = props.errorMessage // The error message for that gets displayed in the box.
    return (
        <div className={`bg-gray-100 rounded-xl p-1 shadow-md mb-8 ${errorMessage.length === 0 ? "collapse" : ""} flex-row flex`}>
            <img src={Warning} className="w-5 h-5 ml-2 mt-auto mb-auto"/>
            <p className={"text-red-500 leading-normal mt-3 ml-4 "}>{errorMessage}</p>
        </div>
    );
}