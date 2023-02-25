import DynamicSmile from "../components/DynamicSmile";

export default function ForgotPassword() {
  return (
    // Root div
    <div className=" bg-raisin-600 h-screen w-screen flex flex-col absolute inset-0">
      <div className="flex flex-row">
        <h1 className="text-tangerine-50 text-6xl md:text-6xl ml-10 mt-10 ">
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
    </div>
  );
}
