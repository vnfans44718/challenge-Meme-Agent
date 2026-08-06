import logo from "../assets/infinite-meme-logo.png";

export default function Header({ isInitial, onReset }) {
  return (
    <div
      className={`flex items-center gap-2 w-4/5 max-w-[600px] mb-6 cursor-pointer ${
        isInitial ? "mx-auto" : "mx-0"
      }`}
      onClick={onReset}
    >
      <h1 className="text-[28px] font-bold text-black m-0">
        Infinite Challenge Meme Finder
      </h1>
      <img src={logo} alt="logo" className="w-12 h-12" />
    </div>
  );
}
