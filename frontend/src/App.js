import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./login";
import Register from "./register";
import MainApp from "./mainapp";


function App() {
  const isLoggedIn = !!localStorage.getItem("token");

  return (
    <Routes>

      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={isLoggedIn ? <MainApp /> : <Navigate to="/login" replace /> }/>
      
    </Routes>
  );
}

export default App;
