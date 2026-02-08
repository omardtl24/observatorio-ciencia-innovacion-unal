export default function Layout({
  children,
  backgroundClass,
  backgroundImage,
  backgroundSVGImage,
  svgFillClass = "text-black",
}) {
  const BgSVG = backgroundSVGImage;

  const backgroundStyle = backgroundImage
    ? {
        backgroundImage: `url(${backgroundImage})`,
        backgroundRepeat: "repeat",
        backgroundPosition: "top center",
        backgroundSize: "100% auto",
      }
    : {};

  return (
    <div
      className={`relative min-h-screen flex flex-col font-ancizar ${backgroundClass || ""}`}
      style={backgroundStyle}
    >
      {/* SVG BACKGROUND */}
      {BgSVG && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <style>{`
            .svg-background text,
            .svg-background path,
            .svg-background * {
              fill: currentColor !important;
            }
          `}</style>
          <BgSVG className={`svg-background w-full h-auto ${svgFillClass}`} />
        </div>
      )}
      {/* CONTENT */}
      <main className="relative z-10 flex-1 mb-32">
        {children}
      </main>
    </div>
  );
}
