let happinessNumberEdges = (happiness) => {
  //Saddest point: 200
  //Happiest point: 160
  return 190 - (happiness / 10) * 4;
};
let happinessNumberMiddle = (happiness) => {
  //Saddest point: 160
  //Happiest point: 200
  return 150 + (happiness / 10) * 4;
};

export default function DynamicSmile(props) {
  const scalar = 10
  return (
    <div className="flex-1 flex-row ">
      <svg width="90" height="90" viewBox="0 0 256 256" className="flex-1">
        <circle cx="128" cy="128" r="120" className="smile-head" />
        <circle cx="98" cy="94" r="13" />
        <circle cx="158" cy="94" r="13" />
        <path
          className="smile-mouth"
          d={`M80,${happinessNumberEdges(
            props.happiness*scalar
          )}, Q128,${happinessNumberMiddle(
            props.happiness*scalar
          )} 176,${happinessNumberEdges(props.happiness*scalar)}`}
        />
      </svg>
    </div>
  );
}
