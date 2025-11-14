export default function Visors() {
  const visorUrl = import.meta.env.VITE_TEST_BI_DAHBOARD;

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
