import { useEffect, useState } from "react";
import UserProfile from "../components/UserProfile";
import { isAuthenticated } from "../services/authService";
import ErrorPopup from "../components/ErrorPopup";

export default function Layout({
  children,
  backgroundClass,
  profileBackgroundClass,
  backgroundImage,
  backgroundSVGImage,
  svgFillClass = "text-black",
  path
}) {
  const BgSVG = backgroundSVGImage;
  const [hasVisibleErrorPopup, setHasVisibleErrorPopup] = useState(false);
  const [hasVisibleResourceFullscreen, setHasVisibleResourceFullscreen] = useState(false);
  const [globalError, setGlobalError] = useState(null);

  useEffect(() => {
    const handleErrorPopupVisibility = (event) => {
      setHasVisibleErrorPopup(Boolean(event?.detail?.visible));
    };

    window.addEventListener("error-popup-visibility", handleErrorPopupVisibility);

    const handleShowErrorPopup = (event) => {
      const message = event?.detail?.message || event?.detail?.error || null;
      if (message) setGlobalError(message);
    };

    window.addEventListener("show-error-popup", handleShowErrorPopup);

    return () => {
      window.removeEventListener("error-popup-visibility", handleErrorPopupVisibility);
      window.removeEventListener("show-error-popup", handleShowErrorPopup);
    };
  }, []);

  useEffect(() => {
    const handleResourceFullscreenVisibility = (event) => {
      setHasVisibleResourceFullscreen(Boolean(event?.detail?.visible));
    };

    window.addEventListener("resource-fullscreen-visibility", handleResourceFullscreenVisibility);

    return () => {
      window.removeEventListener("resource-fullscreen-visibility", handleResourceFullscreenVisibility);
    };
  }, []);

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
      {isAuthenticated() && !hasVisibleResourceFullscreen && (
        <div
          className={`relative z-20 w-full ${
            hasVisibleErrorPopup ? "bg-secondary-gray-base" : (profileBackgroundClass || backgroundClass || "")
          }`}
        >
          <div className="mx-auto flex max-w-6xl justify-end px-6 pt-3 pb-0">
            <UserProfile />
          </div>
        </div>
      )}

      {/* CONTENT */}
      <main className="relative z-10 flex-1 mb-32">
        {children}
      </main>
      <ErrorPopup error={globalError} onClose={() => setGlobalError(null)} />
    </div>
  );
}
