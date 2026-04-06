import UserProfile from "../components/UserProfile";
import { isAuthenticated } from "../services/authService";

export default function Layout({
  children,
  backgroundClass,
  backgroundImage,
  backgroundSVGImage,
  svgFillClass = "text-black",
  path
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
      className={`relative min-h-screen flex flex-col font-sans ${backgroundClass || ""}`}
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

      {/* USER PROFILE BUTTON - Upper Right (only if authenticated) */}
      {isAuthenticated() && (
        <div className="absolute top-4 right-4 z-40">
          <UserProfile />
        </div>
      )}

      {/* CONTENT */}
      <main className={`relative z-10 flex-1 mb-32 ${isAuthenticated() ? "pt-5" : ""}`}>
        {children}
      </main>
    </div>
  );
}
