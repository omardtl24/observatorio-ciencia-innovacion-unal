import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function Layout({ children, backgroundClass, backgroundImage }) {
  const backgroundStyle = backgroundImage
    ? {
        backgroundImage: `url(${backgroundImage})`,
        backgroundRepeat: "repeat",
        backgroundPosition: "top left",
        backgroundSize: "100% auto"
      }
    : {};

  return (
    <div className={`min-h-screen flex flex-col bg-gray font-ancizar ${backgroundClass || ""}`} style={backgroundStyle}>
      <Navbar />
      <main className="flex-1 mb-32">{children}</main>
      <Footer />
    </div>
  );
}



