import { useEffect, useState } from 'react';
import AdminCRM from './components/AdminCRM';

type View = 'home' | 'admin';

function PublicLanding() {
  const goStaff = (event: React.MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();
    window.history.pushState(null, '', '/admin');
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <main className="legacy-page">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Manrope:wght@300;400;500;600;700;800;900&display=swap');
        :root{--bg:#080f1d;--panel:#0d1527;--gold:#d4af37;--gold2:#b8960e;--text:#f1eee8;--muted:#8a90a0}
        *{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg)}
        .legacy-page{min-height:100vh;background:var(--bg);color:var(--text);font-family:Manrope,system-ui,sans-serif;overflow:hidden;letter-spacing:-.01em}.noise{position:fixed;inset:0;pointer-events:none;opacity:.025;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
        .nav{position:fixed;inset:0 0 auto 0;height:64px;z-index:50;background:rgba(8,15,29,.86);backdrop-filter:blur(18px);border-bottom:1px solid rgba(212,175,55,.13)}
        .wrap{width:min(1110px,calc(100% - 80px));margin:auto}.nav .wrap{height:64px;display:flex;align-items:center;justify-content:space-between}.brand{display:flex;gap:12px;align-items:center;color:var(--text);text-decoration:none}.brand-mark{color:var(--gold);font-size:20px}.brand-title{font-family:Instrument Serif,serif;font-size:17px;line-height:1}.brand-sub{font-size:9px;color:var(--muted);letter-spacing:.22em;text-transform:uppercase}.links{display:flex;align-items:center;gap:32px}.links a{font-size:12px;color:#7e8493;text-decoration:none;font-weight:700}.links a:hover,.links a.active{color:var(--gold)}.btn-outline{border:1px solid rgba(212,175,55,.65);color:var(--gold)!important;padding:10px 26px;letter-spacing:.06em}
        .hero{position:relative;min-height:760px;padding-top:64px;display:flex;align-items:center}.hero-bg,.cta-bg{position:absolute;inset:0;background-image:linear-gradient(90deg,rgba(8,15,29,.94) 0%,rgba(8,15,29,.78) 41%,rgba(8,15,29,.32) 75%,rgba(8,15,29,.67) 100%),linear-gradient(180deg,rgba(8,15,29,0) 55%,var(--bg) 100%),url('/am1.jpg');background-size:cover;background-position:center top;filter:saturate(.88)}.hero .wrap{position:relative;z-index:2}.eyebrow{display:flex;align-items:center;gap:18px;color:var(--gold);font-size:11px;font-weight:900;letter-spacing:.22em;text-transform:uppercase;margin-bottom:34px}.eyebrow:before{content:"";width:50px;height:1px;background:var(--gold)}h1{font-size:72px;line-height:.98;margin:0 0 26px;font-weight:900;letter-spacing:.015em}.gold{color:var(--gold)}.italic{font-family:Instrument Serif,serif;font-style:italic}.hero-sub{color:var(--gold);font-size:20px;margin-bottom:32px}.copy{color:#8f96a6;line-height:1.72;font-weight:300}.hero-copy{max-width:470px;font-size:16px;margin-bottom:36px}.actions{display:flex;gap:16px;align-items:center}.btn{height:52px;padding:0 33px;border-radius:2px;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;font-size:13px;font-weight:900;letter-spacing:.08em}.btn-primary{background:linear-gradient(135deg,var(--gold),var(--gold2));color:#07101e}.btn-ghost{border:1px solid rgba(212,175,55,.45);color:var(--gold);background:rgba(6,12,23,.18)}.trust{margin-top:34px;color:#666e7e;font-size:12px}.trust b{color:var(--gold)}
        .quote{padding:72px 0 120px;background:linear-gradient(180deg,var(--bg),#07101e)}.quote-row{display:grid;grid-template-columns:120px 1fr 120px;gap:24px;align-items:center}.line{height:1px;background:linear-gradient(90deg,transparent,rgba(212,175,55,.45),transparent)}blockquote{margin:0;text-align:center;border-left:2px solid var(--gold);padding:0 0 0 28px}.quote p{font-family:Instrument Serif,serif;font-size:22px;font-style:italic;line-height:1.6;margin:0}.quote footer{margin-top:14px;color:#606777;font-size:12px}
        .benefits{padding:0 0 210px}.section-head{margin-bottom:72px}.section-title{font-size:43px;line-height:1.15;margin:0;font-weight:800;letter-spacing:-.04em}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.card{min-height:160px;background:rgba(16,23,40,.8);border:1px solid rgba(212,175,55,.15);padding:31px 28px}.card h3{font-size:16px;margin:0 0 14px}.card p{font-size:13px;color:#9aa0ad;line-height:1.65;margin:0}
        .authority{padding:0 0 180px;background:#08101f}.authority-grid{display:grid;grid-template-columns:520px 1fr;gap:80px;align-items:center}.portrait{position:relative;border:1px solid rgba(212,175,55,.22);padding:8px}.portrait:after{content:"✦";position:absolute;right:-5px;bottom:45px;color:#c6cad1;font-size:28px}.portrait img{display:block;width:100%;aspect-ratio:1/1.32;object-fit:cover;object-position:top}.authority h2{font-size:44px;line-height:1.16;margin:0 0 34px}.stats{display:grid;grid-template-columns:1fr 1fr;gap:12px}.stat{border:1px solid rgba(212,175,55,.16);background:rgba(10,18,32,.45);padding:26px 28px}.num{font-family:Instrument Serif,serif;font-size:70px;color:var(--gold);line-height:.9}.stat p{font-size:12px;color:#7d8494;margin:10px 0 0}
        .final{position:relative;min-height:430px;display:flex;align-items:center;text-align:center}.cta-bg{background-image:linear-gradient(180deg,rgba(8,15,29,.8),rgba(8,15,29,.92)),url('/am3.jpg');background-position:center}.final .wrap{position:relative;z-index:2}.final h2{font-size:44px;line-height:1.2;margin:0 0 34px;font-weight:900;letter-spacing:.03em}.final .actions{justify-content:center}.footer{height:72px;background:#111;display:flex;align-items:center}.footer .wrap{display:flex;align-items:center;justify-content:space-between;color:#626978;font-size:11px}.staff{color:#777f8f;text-decoration:none;letter-spacing:.35em;text-transform:uppercase;font-size:10px}
        @media(max-width:900px){.wrap{width:min(100% - 36px,700px)}.links{gap:14px}.links a:not(.btn-outline){display:none}.hero{min-height:720px}.hero-bg{background-position:58% top}h1{font-size:48px}.section-title,.authority h2,.final h2{font-size:34px}.cards,.authority-grid{grid-template-columns:1fr}.authority-grid{gap:44px}.portrait{max-width:460px}.quote-row{grid-template-columns:1fr}.quote-row .line{display:none}.actions{flex-direction:column;align-items:flex-start}.final .actions{align-items:center}.btn{width:100%;max-width:330px}.footer{height:auto;padding:28px 0}.footer .wrap{gap:18px;flex-direction:column}}
      `}</style>
      <div className="noise" />
      <header className="nav">
        <div className="wrap">
          <a className="brand" href="#inicio" aria-label="Inicio">
            <span className="brand-mark">⚖</span>
            <span><span className="brand-title">Dr. Luis Ángel Méndez</span><br /><span className="brand-sub">Derecho Penal</span></span>
          </a>
          <nav className="links" aria-label="Navegación principal">
            <a className="active" href="#programa">Programa Completo</a>
            <a href="#beneficios">Beneficios</a>
            <a href="#autoridad">Experiencia</a>
            <a href="#contacto">Contacto</a>
            <a href="/admin" onClick={goStaff}>Acceso Staff</a>
            <a className="btn-outline" href="https://wa.me/5491138641863?text=Quiero%20inscribirme%20en%20el%20Curso%20Penal%20Pr%C3%A1ctico" target="_blank" rel="noreferrer">Inscribite Ahora</a>
          </nav>
        </div>
      </header>

      <section id="inicio" className="hero">
        <div className="hero-bg" />
        <div className="wrap">
          <div className="eyebrow">Curso Penal Práctico</div>
          <h1>DEJÁ DE<br /><span className="gold">LITIGAR EN</span><br />SOLEDAD</h1>
          <div className="hero-sub italic">Curso de Capacitación Penal Práctica: De la teoría a la trinchera</div>
          <p className="copy hero-copy">Tu primer caso penal no tiene por qué ser una batalla solitaria. Seguridad jurídica y respaldo técnico para el abogado que recién empieza.</p>
          <div className="actions"><a className="btn btn-primary" href="#programa">VER CAPACITACIÓN Y PROGRAMA →</a><a className="btn btn-ghost" href="https://wa.me/5491138641863?text=Quiero%20inscribirme%20en%20el%20Curso%20Penal%20Pr%C3%A1ctico" target="_blank" rel="noreferrer">Inscribirse Directo</a></div>
          <p className="trust"><b>Cupos limitados</b> — Calidad garantizada de seguimiento</p>
        </div>
      </section>

      <section className="quote"><div className="wrap quote-row"><div className="line" /><blockquote><p>“La diferencia entre un abogado que fracasa en su primer caso y uno que triunfa no es el talento —<br /><span className="gold">es el respaldo que tiene detrás.</span>”</p><footer>— Dr. Luis Ángel Méndez</footer></blockquote><div className="line" /></div></section>

      <section id="programa" className="benefits"><div className="wrap"><div className="section-head"><div className="eyebrow">Ecosistema de Defensa</div><h2 className="section-title">Todo lo que necesitás desde el inicio<br /><span className="gold">de la defensa en tu primer día de trabajo</span></h2></div><div id="beneficios" className="cards"><article className="card"><h3>Acompañamiento Individual</h3><p>Curso y seguimiento personalizado de tus casos reales. No sos un número — sos un profesional en formación con respaldo directo del Dr. Méndez.</p></article><article className="card"><h3>Canal de Consultas 24/7</h3><p>Soporte constante ante dudas procesales de urgencia. Porque en derecho penal, los plazos no esperan y las decisiones se toman en tiempo real.</p></article><article className="card"><h3>Formación Práctica</h3><p>Herramientas concretas para la defensa efectiva desde el inicio. Técnicas procesales, estrategia de audiencias y manejo de prueba en casos reales.</p></article></div></div></section>

      <section id="autoridad" className="authority"><div className="wrap authority-grid"><div className="portrait"><img src="/am2.jpg" alt="Dr. Luis Ángel Méndez" /></div><div><div className="eyebrow">Autoridad & Trayectoria</div><h2>La experiencia que<br /><span className="gold">marca la diferencia</span></h2><div className="stats"><div className="stat"><div className="num">+20</div><p>años de experiencia en tribunales</p></div><div className="stat"><div className="num">100%</div><p>dedicación al derecho penal argentino</p></div></div></div></div></section>

      <section id="contacto" className="final"><div className="cta-bg" /><div className="wrap"><h2>EMPEZÁ TU<br /><span className="gold">CURSO HOY</span></h2><div className="actions"><a className="btn btn-primary" href="#programa">VER PROGRAMA COMPLETO</a><a className="btn btn-ghost" href="https://wa.me/5491138641863?text=Quiero%20inscribirme%20en%20el%20Curso%20Penal%20Pr%C3%A1ctico" target="_blank" rel="noreferrer">Inscribirse Directo</a></div></div></section>

      <footer className="footer"><div className="wrap"><span>Dr. Luis Ángel Méndez</span><a className="staff" href="/admin" onClick={goStaff}>Acceso Staff</a><span>© 2026 Dr. Luis Ángel Méndez. Todos los derechos reservados.</span></div></footer>
    </main>
  );
}

export default function App() {
  const [view, setView] = useState<View>(() => (window.location.pathname.startsWith('/admin') ? 'admin' : 'home'));

  useEffect(() => {
    const handlePopState = () => setView(window.location.pathname.startsWith('/admin') ? 'admin' : 'home');
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigateToHome = () => {
    setView('home');
    if (window.location.pathname !== '/') window.history.pushState(null, '', '/');
  };

  return <>{view === 'admin' ? <AdminCRM onNavigateToHome={navigateToHome} /> : <PublicLanding />}</>;
}
