import { confirmAlert } from "react-confirm-alert";
import "react-confirm-alert/src/react-confirm-alert.css";
import {useUser} from "../contexts/UserProvider"; // Import css

export default function ButtonSettingCard(props) {
  const { Logout, DeleteUser } = useUser();

  /*
      props.id: setting id
      props.icon: setting icon
      props.name: setting name
      props.isSensitive: tells whether a confirmation should come up before the setting is changed.
      */
  const doAction = () => {
    switch (props.id) {
      case 7:
        Logout().then(() => {window.location.reload()})
        break
      case 8:
        DeleteUser().then(() => {window.location.reload()})
        break

    }
  };
  const clicked = () => {
    console.log("Clicked");
    if (props.isSensitive) {
      confirmAlert({
        title: "Are you sure you want to " + props.name.toLowerCase() + "?",
        message: "This cannot be undone.",
        buttons: [
          {
            label: "Yes",
            onClick: doAction,
          },
          {
            label: "No",
          },
        ],
        closeOnEscape: true,
        closeOnClickOutside: true,
        keyCodeForClose: [8, 32],
        willUnmount: () => {},
        onClickOutside: () => {},
        overlayClassName: "overlay-custom-class-name",
      });
    } else {
      doAction();
    }
  };

  return (
    <div className="w-[300px] m-2 py-8 px-8 max-w-sm bg-white rounded-xl shadow-lg space-y-2 sm:py-4 sm:flex sm:items-center sm:space-y-0 sm:space-x-6">
      <p className="text-xl">{props.name}</p>
      <button>
        <img
          className="h-[50px] w-[50px] block mx-auto sm:shrink-0 sm:mx-0"
          src={props.icon}
          onClick={clicked}
        />
      </button>
    </div>
  );
}
