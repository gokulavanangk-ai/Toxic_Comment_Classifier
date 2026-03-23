import "./App.css";
import axios from "axios";
import { useState, useEffect, useRef } from "react";
import Navbar from "./comp/navbar";

function MainApp() {
  const [data, setData] = useState({ comment: "" });
  const [comments, setComments] = useState([]);
  const [replyTo, setReplyTo] = useState(null);

  const username = localStorage.getItem("username");
  const token = localStorage.getItem("token");

  const textareaRef = useRef(null);

  // Handle textarea
  const handleChanged = (e) => {
    setData({ ...data, [e.target.name]: e.target.value });
  };

  // Fetch comments
  const fetchComments = async () => {
    try {
      const res = await axios.get("http://localhost:8082/comments");
      setComments(res.data);
    } catch (err) {
      console.error("Failed to fetch comments", err);
    }
  };

  useEffect(() => {
    fetchComments();
  }, []);

  // Post comment / reply
  const gae = async (e) => {
    e.preventDefault();

    if (!data.comment.trim()) return;
    if (!token) {
      alert("Please login to comment");
      return;
    }

    try {
      await axios.post(
        "http://localhost:8082/cmtinsert",
        {
          comment: data.comment,
          parentId: replyTo ? replyTo.id : null,
          replyToUser: replyTo ? replyTo.user : null
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      setData({ comment: "" });
      setReplyTo(null);
      fetchComments();
    } catch (err) {
      alert(err.response?.data?.error || "Login required");
    }
  };

  // Delete comment
  const deleteComment = async (id) => {
    if (!window.confirm("Delete this comment?")) return;

    try {
      await axios.delete(`http://localhost:8082/comment/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      fetchComments();
    } catch {
      alert("Delete failed");
    }
  };

  // Time ago
  function timeAgo(date) {
  const seconds = Math.floor((Date.now() - new Date(date)) / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days} d ago`;
  if (hours > 0) return `${hours} h ago`;
  if (minutes > 0) return `${minutes} m ago`;
  return "Just now";
}

  function CommentTime({ createdAt }) {
  const [time, setTime] = useState(timeAgo(createdAt));

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(timeAgo(createdAt));
    }, 60000); // update every minute

    return () => clearInterval(interval);
  }, [createdAt]);

  return <small>{time}</small>;
}

  // Reply handler (auto @username + focus)
  const handleReply = (parentId, replyUser) => {
    setReplyTo({ id: parentId, user: replyUser });

    setData({
      comment: `@${replyUser} `
    });

    setTimeout(() => {
      textareaRef.current?.focus();
    }, 0);
  };

  return (
    <>
      <Navbar />

      <div className="container-fluid bg-dark text-light">
        <div className="row gap-5">

          {/* LEFT IMAGE */}
          <div className="col-lg-4 col-sm-6 px-5">
            <div className="position-sticky top-0 pt-4">
              <div className="card-custom">
                <img
                  src="https://images.pexels.com/photos/19915588/pexels-photo-19915588.jpeg"
                  className="card-img-top"
                  alt="post"
                />
              </div>
            </div>
          </div>

          {/* COMMENTS */}
          <div className="col-lg-7">
            <h4 className="py-3">Comments ({comments.length})</h4>

            <div className="cardd border-2 p-4">

              {comments
                .filter(c => !c.parentId)
                .map(c => (
                  <div key={c._id} className="my-3">

                    <i className="bi bi-person-circle text-warning mx-2 h3"></i>
                    <label className="text-warning">{c.user}</label>
                    <label className="ps-2">
                      <small><CommentTime createdAt={c.createdAt} /></small>
                    </label>

                    <div className="ps-5">
                      <p>{c.comment}</p>

                      <div className="d-flex gap-3 small">
                        <span
                          className="text-info"
                          style={{ cursor: "pointer" }}
                          onClick={() => handleReply(c._id, c.user)}
                        >
                          Reply
                        </span>

                        {c.user === username && (
                          <span
                            className="text-danger"
                            style={{ cursor: "pointer" }}
                            onClick={() => deleteComment(c._id)}
                          >
                            Delete
                          </span>
                        )}
                      </div>

                      {/* REPLIES */}
                      {comments
                        .filter(r => r.parentId === c._id)
                        .map(r => (
                          <div key={r._id} className="ps-4 border-start mt-2">

                            <small className="text-warning">{r.user}</small>
                            <small className="ps-2">
                              {timeAgo(r.createdAt)}
                            </small>

                            <p className="mb-1">
                              {r.comment}
                            </p>

                            <div className="small d-flex gap-3">
                              <span
                                className="text-info"
                                style={{ cursor: "pointer" }}
                                onClick={() => handleReply(c._id, r.user)}
                              >
                                Reply
                              </span>

                              {r.user === username && (
                                <span
                                  className="text-danger"
                                  style={{ cursor: "pointer" }}
                                  onClick={() => deleteComment(r._id)}
                                >
                                  Delete
                                </span>
                              )}
                            </div>

                          </div>
                        ))}
                    </div>

                    <hr />
                  </div>
                ))}
            </div>
          </div>

          {/* INPUT */}
          <div className="row">
            <div className="col-12 fixed-bottom bg-dark border-top border-light p-3">
              <form onSubmit={gae} className="col-lg-7 mx-auto">

                {replyTo && (
                  <div className="text-warning small mb-1">
                    Replying to <span className="text-info">@{replyTo.user}</span>
                    <span
                      className="ms-2 text-danger"
                      style={{ cursor: "pointer" }}
                      onClick={() => {
                        setReplyTo(null);
                        setData({ comment: "" });
                      }}
                    >
                      ✕
                    </span>
                  </div>
                )}

                <div className="input-group">
                  <textarea ref={textareaRef} name="comment"placeholder="Say your thoughts..." value={data.comment} onChange={handleChanged} 
                  className="form-control btm bg-transparent text-info border-primary shadow-none" rows="1" style={{ resize: "none" }}/>
                  
                  <button className="btn btn-outline-primary ptm fw-bold px-4">POST</button>
                </div>
              </form>
            </div>
          </div>

        </div>
      </div>
    </>
  );
}

export default MainApp;
