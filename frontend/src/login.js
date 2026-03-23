import axios from "axios";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await axios.post("http://localhost:8082/login", form);
      localStorage.setItem("token", res.data.token);
      localStorage.setItem("username", form.username);

      navigate("/"); // ✅ go to main app
    } catch (err) {
      setError(err.response?.data?.error || "Login failed");
    }
  };

  return (
    <div className="container vh-100 d-flex justify-content-center align-items-center">
      <div className="card border border-2 p-4 rounded-3" style={{ width: "350px" }}>
        <h4 className="text-center mb- fw-bold">Login</h4>

        {error && <div className="alert alert-danger">{error}</div>}

        <form onSubmit={handleLogin}>
          <input
            className="form-control my-3"
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
          <button className="btn btn-primary w-100">LOGIN</button>
        </form>

        <p className="text-center mt-3">
          Don’t have an account?{" "}
          <span
            className="text-primary"
            style={{ cursor: "pointer" }}
            onClick={() => navigate("/register")}
          >
            Register
          </span>
        </p>
      </div>
    </div>
  );
}

export default Login;
