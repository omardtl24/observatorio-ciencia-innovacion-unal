export default function Dashboard() {
  const accessToken = localStorage.getItem("access_token");
  const email = localStorage.getItem("email");
  const names = localStorage.getItem("names");
  const lastNames = localStorage.getItem("last_names");

  if (!accessToken) return <p>Unauthorized</p>;

  return (
    <div>
      <h1>Bienvenido,</h1>
      <h1>{names} {lastNames}</h1>
      <p>Correo: {email}</p>

      <button 
        onClick={() => {
          localStorage.clear();
          window.location.href = "/login";
        }}
        style={{ marginTop: "1rem", padding: "0.5rem 1rem", borderRadius: "8px", cursor: "pointer" }}
      >
        Logout
      </button>
    </div>
  );
}
