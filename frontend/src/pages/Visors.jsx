export default function Visors() {
  const visorUrl = import.meta.env.VITE_API_URL + "/visor/1/";
  console.log("Visor URL:", visorUrl);

  return (
    <div className="w-full flex justify-center mt-10">
      <div className="w-full max-w-5xl border rounded-lg shadow-lg overflow-hidden">
        <iframe
          src={visorUrl}
          title="Public Visor"
          className="w-full h-[80vh] border-none"
          allowFullScreen
        ></iframe>
      </div>
    </div>
  );
}