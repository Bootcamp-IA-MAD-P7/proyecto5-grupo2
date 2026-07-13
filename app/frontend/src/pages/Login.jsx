/* =============================================================================
   LOGIN PAGE - HOTEL INSIGHTS
   =============================================================================
   Pantalla de inicio de sesion. Primera pantalla que ve el usuario.
   ============================================================================= */

import React, { useState } from "react";
import "./Login.css";

/* =============================================================================
   COMPONENTE LOGIN
   =============================================================================
   Recibe una funcion "onLogin" desde el padre (App.jsx).
   Cuando el usuario hace login, se llama a esa funcion.
   ============================================================================= */
function Login({ onLogin }) {
  
  // ---------------------------------------------------------------------------
  // ESTADO: Guardamos lo que el usuario escribe
  // ---------------------------------------------------------------------------
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // ---------------------------------------------------------------------------
  // FUNCION: Cuando el usuario envia el formulario
  // ---------------------------------------------------------------------------
  const handleSubmit = (event) => {
    // Prevenir que la pagina se recargue
    event.preventDefault();
    
    // Por ahora, simulamos el login sin backend
    // Mas adelante aqui iria la llamada a la API
    console.log("Login con:", email, password);
    
    // Llamamos a la funcion del padre para cambiar de pantalla
    onLogin();
  };

  // ---------------------------------------------------------------------------
  // RENDER: Lo que se ve en pantalla
  // ---------------------------------------------------------------------------
  return (
    
    <div className="login-screen">
      
      {/* =====================================================================
          COLUMNA IZQUIERDA: Imagen de fondo + texto
          ===================================================================== */}
      <div className="login-left">
        <div className="login-left-img" />
        <div className="login-left-overlay" />
        <div className="login-left-content">
          <h2>Predice las cancelaciones. Protege tus beneficios.</h2>
          <p>
            Anticipa cancelaciones, optimiza ingresos y toma decisiones 
            basadas en datos con Hotel Insights.
          </p>
        </div>
      </div>

      {/* =====================================================================
          COLUMNA DERECHA: Logo + formulario
          ===================================================================== */}
      <div className="login-right">
        
        {/* Logo del hotel */}
        <div className="login-logo-area">
          <div className="login-logo-img">
            {/* 
              /logo.png busca en la carpeta public/
              Vite sirve todo lo de public/ directamente en la raiz
            */}
            <img src="/logo.png" alt="Hotel Insights Logo" />
          </div>
          <div className="login-logo-text">HOTEL INSIGHTS</div>
          <div className="login-logo-sub">Predicción de cancelaciones</div>
        </div>

        {/* Formulario */}
        <form className="login-form" onSubmit={handleSubmit}>
          
          {/* Campo Email */}
          <div className="login-field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              placeholder="recepcion@hotel.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          {/* Campo Contraseña */}
          <div className="login-field">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {/* Boton */}
          <button type="submit" className="login-btn">
            Iniciar Sesión
          </button>
        </form>

        {/* Footer */}
        <div className="login-footer">
          No tienes cuenta? <a href="#">Solicitar acceso</a>
        </div>
      </div>
    </div>
  );
}

export default Login;
