import Histories from "../components/Histories";
import Users from "../components/Users";

export default function History(props) {
  return (
    <>
      <div>
        <p className="text-center text-5xl font-medium m-3 text-raisin-600">
          History
        </p>
      </div>
      <Histories id={props.id} max={Users(props.id).data.length} division={true} />
    </>
  );
}
