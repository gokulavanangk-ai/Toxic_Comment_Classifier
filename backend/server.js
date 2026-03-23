const express = require("express");
const { MongoClient, ObjectId } = require("mongodb");
const cors = require("cors");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const axios = require("axios");

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 8082;


const MONGO_URL =
  "mongodb+srv://gokulavanangk_db_user:kdGF99CgnQFpQqqn@cluster0.kcs7vse.mongodb.net/user?retryWrites=true&w=majority";

const DB_NAME = "user";
const JWT_SECRET = "my_secret_key";

// Python Model API
const MODEL_API = "http://localhost:8000/predict";

let db;

/* CONNECT MONGODB  */

MongoClient.connect(MONGO_URL)
  .then((client) => {
    db = client.db(DB_NAME);
    console.log("MongoDB connected");
  })
  .catch((err) => console.error("Mongo error:", err));

/*  JWT MIDDLEWARE  */

function verifyToken(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth) return res.status(401).json({ error: "Token missing" });

  const token = auth.split(" ")[1];

  try {
    req.user = jwt.verify(token, JWT_SECRET);
    next();
  } catch {
    res.status(403).json({ error: "Invalid token" });
  }
}

/*  REGISTER  */

app.post("/register", async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password)
    return res.status(400).json({ error: "All fields required" });

  const exists = await db.collection("users").findOne({ username });
  if (exists) return res.status(400).json({ error: "User exists" });

  const hash = await bcrypt.hash(password, 10);

  await db.collection("users").insertOne({
    username,
    password: hash,
    createdAt: new Date(),
  });

  res.json({ message: "Registered successfully" });
});

/*  LOGIN  */

app.post("/login", async (req, res) => {
  const { username, password } = req.body;

  const user = await db.collection("users").findOne({ username });
  if (!user) return res.status(401).json({ error: "User not found" });

  const ok = await bcrypt.compare(password, user.password);
  if (!ok) return res.status(401).json({ error: "Wrong password" });

  const token = jwt.sign({ username }, JWT_SECRET, {
    expiresIn: "1d",
  });

  res.json({ token });
});

/*  ADD COMMENT / REPLY (WITH TOXIC CHECK)  */

app.post("/cmtinsert", verifyToken, async (req, res) => {
  const { comment, parentId, replyToUser } = req.body;

  if (!comment || !comment.trim())
    return res.status(400).json({ error: "Comment required" });

  try {
    // Call Python Toxic Model
    const modelResponse = await axios.post(MODEL_API, {
      text: comment,
    });

    const {
      prediction,
      confidence,
    } = modelResponse.data;

    // Block severe toxic comments
    if (prediction === "severe_toxic") {
      return res.status(403).json({
        error: "Comment blocked due to severe toxicity",
        prediction,
        confidence,
      });
    }

    //  Save comment with moderation metadata
    await db.collection("comments").insertOne({
      user: req.user.username,
      comment,
      parentId: parentId ? new ObjectId(parentId) : null,
      replyToUser: replyToUser || null,
      createdAt: new Date(),
      status: prediction === "toxic" ? "flagged" : "visible",
      toxicityLabel: prediction,
      toxicityConfidence: confidence,
    });

    res.json({
      message: "Comment added",
      moderation: prediction,
      confidence,
    });

  } catch (error) {
    console.error("Model API error:", error.message);
    return res.status(500).json({
      error: "Toxicity service unavailable",
    });
  }
});

/*  DELETE COMMENT  */

app.delete("/comment/:id", verifyToken, async (req, res) => {
  const id = new ObjectId(req.params.id);

  const comment = await db.collection("comments").findOne({ _id: id });
  if (!comment) return res.status(404).json({ error: "Not found" });

  if (comment.user !== req.user.username)
    return res.status(403).json({ error: "Unauthorized" });

  await db.collection("comments").deleteMany({
    $or: [{ _id: id }, { parentId: id }],
  });

  res.json({ message: "Deleted" });
});

/*  GET COMMENTS  */

app.get("/comments", async (req, res) => {
  const comments = await db
    .collection("comments")
    .find({ status: "visible" }) // only visible comments
    .sort({ createdAt: 1 })
    .toArray();

  res.json(comments);
});

/*  HEALTH CHECK  */

app.get("/health", (req, res) => {
  res.json({ status: "Node server running" });
});

/*  START  */

app.listen(PORT, () =>
  console.log(`Server running at http://localhost:${PORT}`)
);