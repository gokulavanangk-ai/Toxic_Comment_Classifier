import axios from "axios";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Register() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setMsg("");

    try {
      await axios.post("http://localhost:8082/register", form);
      setMsg("Registration successful!");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError(err.response?.data?.error || "Register failed");
    }
  };

  return (
    <div className="container vh-100 d-flex justify-content-center align-items-center">
      <div className="card p-4 border border-2 rounded-3" style={{ width: "350px" }}>
        <h4 className="text-center mb-4 fw-bold">Register</h4>

        {msg && <div className="alert alert-success">{msg}</div>}
        {error && <div className="alert alert-danger">{error}</div>}

        <form onSubmit={handleRegister}>
          <input
            className="form-control mb-3"
            name="username"
            placeholder="Username"
            onChange={handleChange}
            required
          />
          <input
            className="form-control mb-3"
            type="password"
            name="password"
            placeholder="Password"
            onChange={handleChange}
            required
          />
          <button className="btn btn-success w-100">REGISTER</button>
        </form>

        <p className="text-center mt-3">
          Already have an account?{" "}
          <span
            className="text-primary"
            style={{ cursor: "pointer" }}
            onClick={() => navigate("/login")}
          >
            Login
          </span>
        </p>
      </div>
    </div>
  );
}

export default Register;
