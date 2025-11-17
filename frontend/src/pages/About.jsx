import fullTeamPic from '../assets/banners/team-full.png';
import camilo_pic from '../assets/team/camilo.png';
import camilo_pic_hover from '../assets/team/camilo-hover.png';
import alejandra_pic from '../assets/team/alejandra.png';
import alejandra_pic_hover from '../assets/team/alejandra-hover.png';
import valentina_pic from '../assets/team/valentina.png';
import valentina_pic_hover from '../assets/team/valentina-hover.png';
import omar_pic from '../assets/team/omar.png';
import omar_pic_hover from '../assets/team/omar-hover.png';
import juan_pic from '../assets/team/juan.png';
import juan_pic_hover from '../assets/team/juan-hover.png';

import TeamCard from '../components/TeamCard';

const teamMembers = [
  {
    name: "Camilo Ernesto",
    lastname: "Bahamón Tequia",
    position: "Estudiante de Estadística",
    role: "Estudiante Auxiliar del Observatorio de Gestión y Análisis de indicaciones para la Ciencia y la Innovación",
    email: "email_to_know@unal.edu.co",
    picture: camilo_pic,
    picture_hover: camilo_pic_hover
  },
  {
    name: "Alejandra",
    lastname: "Sánchez Vásquez",
    position: "Docente del Departamento de Matemáticas",
    role: "Coordinadora del Observatorio de Gestión y Análisis de indicaciones para la Ciencia y la Innovación",
    email: "email_to_know@unal.edu.co",
    picture: alejandra_pic,
    picture_hover: alejandra_pic_hover
  },
  {
    name: "Valentina",
    lastname: "Cardona Saldana",
    position: "Estudiante de la Maestría en Estadística",
    role: "Estudiante Auxiliar del Observatorio de Gestión y Análisis de indicaciones para la Ciencia y la Innovación",
    email: "email_to_know@unal.edu.co",
    picture: valentina_pic,
    picture_hover: valentina_pic_hover
  },
  {
    name: "Juan Andres",
    lastname: "Valero Sierra",
    position: "Doctor en Matemáticas",
    role: "Asesor del Observatorio de Gestión y Análisis de indicaciones para la Ciencia y la Innovación.",
    email: "email_to_know@unal.edu.co",
    picture: juan_pic,
    picture_hover: juan_pic_hover
  },
  {
    name: "Omar David",
    lastname: "Toledo Leguizamón",
    position: "Estudiante de Ingeniería de Sistemas y Computación",
    role: "Estudiante Auxiliar del Observatorio de Gestión y Análisis de indicaciones para la Ciencia y la Innovación",
    email: "otoledo@unal.edu.co",
    picture: omar_pic,
    picture_hover: omar_pic_hover
  }
];

export default function About() {
  return (
    <div>
      {/* Banner */}
        <div
            style={{
            backgroundImage: `url(${fullTeamPic})`,
            height: "541px",
            backgroundSize: "cover",
            backgroundPosition: "center",
            position: "relative",
            }}
        >
            <h1
            className="text-white font-ancizar font-bold absolute bottom-4 left-1/2 -translate-x-1/2 text-4xl md:text-6xl lg:text-7xl bg-primary-cyan px-32 py-6"
            >
            CONÓCENOS
            </h1>
        </div>

        {/* Team Section */}
        <div className="max-w-screen-xl my-8 px-4 md:px-0 mx-auto ">
            {/* Heading */}
            <h2 className="font-ancizarItalic font-bold text-7xl md:text-7xl bg-white text-primary-blue inline-block px-4 mb-8">
                ¡Conoce a nuestro equipo!
            </h2>

            {/*<div className="flex flex-col gap-8 w-2/3 mx-auto">*/}
            <div className="grid grid-cols-1 md:grid-cols-1 gap-8 w-2/3  auto-rows-fr">
                {teamMembers.map((member, index) => (
                  <TeamCard key={index} {...member} />
                ))}
            </div>
        </div>



    </div>
  );
}
