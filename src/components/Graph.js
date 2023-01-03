function Graph(props) {
  console.log("testtest");
  return (
    <div>
      <img className="h-[400px] w-[800px]" src={props.img} />
      <div className="space-y-0.5">
        <p className="text-lg text-black text-center font semi-bold">
          {props.name} Graph for "name"
        </p>
      </div>
    </div>
  );
}
export default Graph;
