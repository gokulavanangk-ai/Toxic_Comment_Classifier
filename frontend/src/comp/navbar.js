import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function Navbar() {
  const navigate = useNavigate();
  const [showConfirm, setShowConfirm] = useState(false);

  const confirmLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    navigate("/login");
  };

  return (
    <>
      {/*  NAVBAR  */}
      <div className="col-sm-12 bg-dark sticky-top cardd pb-3 position-relative">
        <span>
          <button onClick={() => setShowConfirm(true)}
          className="float-end rounded-pill mt-4 h6 text-light px-3 py-1 bg-dark">
          Logout</button>
        </span>

        <h1 className="text-info">Comment Moderation</h1>
        <h6 className="ps-lg-4 text-warning">Community-driven comment moderation</h6>
      </div>

      {/*  CONFIRM LOGOUT MODAL  */}
      {showConfirm && (
        <div
          className="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
          style={{background: "rgba(0,0,0,0.6)",backdropFilter: "blur(4px)", zIndex: 9999}}>
          <div
            className="bg-dark text-light rounded-4 p-4 shadow-lg"
            style={{ width: "320px" }}>
            <h5 className="text-center text-warning mb-3">
              Confirm Logout
            </h5>

            <p className="text-center small mb-4"> Are you sure you want to logout?</p>

            <div className="d-flex justify-content-between gap-3">
              <button onClick={() => setShowConfirm(false)}
                className="btn btn-outline-secondary w-50 rounded-pill"
              >Cancel</button>

              <button onClick={confirmLogout}
                className="btn btn-danger w-50 rounded-pill"
              >Logout</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
