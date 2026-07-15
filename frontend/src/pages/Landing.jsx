import ResourceCard from "../components/ResourceCard";
import { formatDate } from "../services/dashboardUtils";

export default function Landing() {
  const images = [
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1491895200222-0fc4a4c35e18?auto=format&fit=crop&w=800&q=80",
  ];

  const dataMapper = [
    {
      mainTitle: "Impacto del Curso de Nivelacion Matematicas Basicas en el desempeno de los estudiantes en la asignatura Calculo Diferencial",
      type: "PDF",
      updatedAt: "2024-06-01",
      resourceType: "visor",
    },
    {
      mainTitle: "Impacto del Curso de Nivelacion Matematicas Basicas en el desempeno de los estudiantes en la asignatura Calculo Diferencial",
      type: "PDF",
      updatedAt: "2024-10-01",
      resourceType: "simulator",
    }
    
  ];

  return (
    <div className="min-h-screen px-6 py-12">
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
        {dataMapper.map((item, index) => (
          <ResourceCard
            key={index}
            mainTitle={item.mainTitle}
            type={item.type}
            updatedAt={formatDate(item.updatedAt)}
            coverImage={images[index % images.length]}
            resourceType={item.resourceType}
          />
        ))}
      </div>
    </div>
  );
}