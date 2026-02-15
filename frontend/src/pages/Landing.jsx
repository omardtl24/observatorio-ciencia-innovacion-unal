import ResourceCard from "../components/RessourceCard";

export default function Landing() {
  const images = [
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1491895200222-0fc4a4c35e18?auto=format&fit=crop&w=800&q=80",
  ];

  const datta_mapper = [
    { main_title: "Impacto del Curso de Nivelación Matermáticas Básicas",
      auxiliar_title: "en el desempeño de los estudiantes en la asignatura Cálculo Diferencial",
      type: "PDF", update_at: "2024-06-01T00:00:00Z", resourceType: "visor" },
      { main_title: "Impacto del Curso de Nivelación Matermáticas Básicas",
      auxiliar_title: "en el desempeño de los estudiantes en la asignatura Cálculo Diferencial",
      type: "PDF", update_at: "2024-10-01T00:00:00Z", resourceType: "simulator" }
    
  ];

  return (
    <div className="min-h-screen px-6 py-12">
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
        {datta_mapper.map((item, index) => (
          <ResourceCard
            key={index}
            title={item.name}
            main_title={item.main_title}
            auxiliar_title={item.auxiliar_title}
            type={item.type}
            updatedAt={new Date(item.update_at)
                    .toLocaleDateString("es-ES", {
                        year: "numeric",
                        month: "long",
                    })
                    .replace(/^\w/, (c) => c.toUpperCase())
                }
            coverImage={images[index % images.length]}
            resourceType={item.resourceType}
          />
        ))}
      </div>
    </div>
  );
}