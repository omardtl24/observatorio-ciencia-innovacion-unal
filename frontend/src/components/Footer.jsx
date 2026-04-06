import footer from '../assets/banners/footer.png';
import copy_icon from '../assets/icons/footer/copy.svg';
import copy_hover_icon from '../assets/icons/footer/copy-hover.svg';
import email_icon from '../assets/icons/footer/email.svg';
import phone_icon from '../assets/icons/footer/phone.svg';
import schedule_icon from '../assets/icons/footer/schedule.svg';
import map_icon from '../assets/icons/footer/map.svg';

export default function Footer() {
  const contact_items = [
    { label: "Correo electrónico", icon: email_icon, content: "obsindica_fcbog@unal.edu.co", copyable: true },
    { label: "Teléfono", icon: phone_icon, content: "(+57 601) 316 5000 Ext.15622", copyable: true },
    { label: "Dirección", icon: map_icon, content: "Edificio 476 Ed. 476 Of. 6 - 7 UNAL", copyable: true },
    { label: "Horario de atención", icon: schedule_icon, content: "Lunes - Viernes 09:00 - 16:00", copyable: true },
  ]
  return (
    <footer className="w-full bg-transparent mt-5">
      {/* 2×2 GRID */}
      <div className="w-full mx-auto grid grid-cols-1 md:grid-cols-2 items-stretch">

        {/* === UP LEFT === */}
        <div className="flex flex-col items-center justify-center">
          <h1 className="font-serif italic font-bold text-primary-blue bg-white text-6xl">
            ¡Contáctanos!
          </h1>
        </div>

        {/* === UP RIGHT === */}
        <div className="flex flex-col items-center justify-center md:items-start px-6 md:px-12 lg:px-20 mb-3 mx-16">
          <h2 className="font-sans text-primary-blue bg-white text-2xl">
            Para más información sobre Divulgación y Medios, no dudes en ponerte en contacto con nosotros.
          </h2>
        </div>

        {/* === BOTTOM ROW WRAPPER (ensures equal height) === */}
        <div className="col-span-1 md:col-span-2 flex flex-col md:flex-row items-stretch">
          {/* === LEFT: Contact items define height === */}
          <div className="bg-primary-cyan p-12 w-full text-white flex flex-col space-y-4">
            {contact_items.map((item, index) => (
              <div key={index} className="mx-12">
                <p className="text-m font-sans mx-14">{item.label}</p>

                <div className="flex items-center space-x-1 relative">
                  {/* Element icon */}
                  <img src={item.icon} className="w-12 h-12" />

                  {/* Element content */}
                  <div className="flex-1 group flex items-center bg-primary-cyan p-2 rounded-md border border-white transition-all duration-200 hover:bg-secondary-cyan-accent hover:text-primary-cyan hover:border-secondary-cyan-accent">
                    <span className="text-xl font-sans flex-1 px-2">{item.content}</span>

                    {/* Copy button */}
                    {item.copyable && (
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(item.content);
                          alert(`Copiado: ${item.content}`);
                        }}
                        className="flex items-center"
                      >
                        <img src={copy_icon} className="w-10 h-10 block group-hover:hidden" />
                        <img src={copy_hover_icon} className="w-10 h-10 hidden group-hover:block" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* === RIGHT: Image fully fills the left's height, object-cover zooms/crops === */}
          <div className="w-full flex">
            <img
              src={footer}
              alt="UNAL Logo"
              className="w-full h-full object-cover"
            />
          </div>

        </div>

        
      </div>
    </footer>
  );
}