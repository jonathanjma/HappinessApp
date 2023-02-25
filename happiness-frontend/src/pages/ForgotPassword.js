import DynamicSmile from "../components/DynamicSmile";

export default function Welcome() {
  return (
    // Root div
    <div className=" bg-raisin-600 h-screen w-screen flex flex-col">
      <h1 className="text-tangerine-50 text-6xl text-center mt-10 ml-auto mr-auto">
        <b>Forgot your password?</b>
      </h1>

      <div className="flex flex-col items-center">
        <div className="flex-row flex">
          <span className="mt-10 mr-10">
            <DynamicSmile happiness={10} />
          </span>

          <p className=" text-3xl max-w-[300px] mt-10 text-white">
            We can help. Enter the email you used to create your account.
          </p>
        </div>
      </div>
    </div>
  );
}
