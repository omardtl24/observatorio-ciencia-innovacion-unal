import { useNavigate, useSearchParams } from "react-router-dom";

export default function ConnectionError() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const origin = searchParams.get("origin") || "/";
  const supportEmail = import.meta.env.VITE_SUPPORT_EMAIL || "soporte@tu-dominio.com";

  return (
    <div className="min-h-screen px-6 py-16 flex items-center justify-center">
      <div className="relative w-full max-w-3xl">
        <div className="absolute -top-10 -left-10 w-40 h-40 bg-primary-cyan-soft rounded-full blur-2xl opacity-60" />
        <div className="absolute -bottom-12 -right-8 w-44 h-44 bg-primary-blue-strong rounded-full blur-2xl opacity-20" />

        <div className="relative bg-white/90 backdrop-blur border border-gray-200 rounded-2xl shadow-xl p-8 md:p-12">
          <div className="flex flex-col md:flex-row md:items-center gap-8">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 rounded-2xl bg-red-50 border border-red-200 flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-red-500"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>

            <div className="flex-1">
              <p className="text-sm uppercase tracking-widest text-primary-cyan-strong font-semibold">
                Estado del servicio
              </p>
              <h1 className="mt-2 text-3xl md:text-4xl font-serif italic font-bold text-primary-blue-strong">
                Estamos teniendo problemas de conexión
              </h1>
              <p className="mt-4 text-gray-700 leading-relaxed">
                No pudimos acceder al servicio en este momento. Esto puede deberse a una interrupción temporal.
              </p>
              <p className="mt-4 text-gray-700 leading-relaxed">
                Intenta nuevamente en unos minutos. Si el error continúa, escríbenos a
                {" "}
                <a
                  className="text-primary-cyan-strong underline underline-offset-4"
                  href={`mailto:${supportEmail}`}
                >
                  {supportEmail}
                </a>
                {" "}
                con una breve descripción de lo ocurrido.
              </p>

              <div className="mt-8 flex flex-col sm:flex-row gap-4">
                <button
                  onClick={() => navigate(origin)}
                  className="px-6 py-3 rounded-lg bg-primary-cyan-strong text-white font-semibold hover:brightness-110 transition"
                >
                  Reintentar
                </button>
                <button
                  onClick={() => navigate("/")}
                  className="px-6 py-3 rounded-lg border border-primary-blue-strong text-primary-blue-strong font-semibold hover:bg-primary-blue-strong hover:text-white transition"
                >
                  Volver al inicio
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
