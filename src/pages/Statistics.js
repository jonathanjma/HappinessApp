import Graph from "../components/Graph";
import { useState } from "react";
import { useResolvedPath } from "react-router-dom";
export default function Statistics() {
  const [graphs, setGraphs] = useState([
    {
      id: 1,
      name: "Weekly",
      img: "https://cdn.discordapp.com/attachments/879121725500059668/1059875195734736957/image.png",
    },
  ]);

  return (
    <>
      <div className="flex flex-wrap justify-center items-center">
        {graphs.map((graph) => {
          return <Graph id={graph.id} name={graph.name} img={graph.img} />;
        })}
      </div>
    </>
  );
}

/*
goals: include checkboxes to show which items to show or not (or use array passed through from settings page)
- graph component can be used in many places, including profile, statistics, etc (maybe even used in the preview)
*/
