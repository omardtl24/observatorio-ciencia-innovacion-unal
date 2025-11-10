export default function Dashboard() {
  const accessToken = localStorage.getItem("access_token");
  const email = localStorage.getItem("email");
  const names = localStorage.getItem("names");
  const lastNames = localStorage.getItem("last_names");
  const picture = localStorage.getItem("picture");

  if (!accessToken) return <p>Unauthorized</p>;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "1.5rem",
        padding: "1rem",
      }}
    >
      {picture && (
        <img
          src={decodeURIComponent(picture)}
          alt="Foto de perfil"
          style={{
            width: "90px",
            height: "90px",
            borderRadius: "50%",
            objectFit: "cover",
            boxShadow: "0 2px 6px rgba(0,0,0,0.25)",
          }}
        />
      )}

      <div>
        <h1>Bienvenido,</h1>
        <h1>{names} {lastNames}</h1>
        <p>Correo: {email}</p>

        <button
          onClick={() => {
            localStorage.clear();
            window.location.href = "/login";
          }}
          style={{
            marginTop: "1rem",
            padding: "0.5rem 1rem",
            borderRadius: "8px",
            cursor: "pointer",
          }}
        >
          Logout
        </button>
      </div>
    </div>
  );
}
