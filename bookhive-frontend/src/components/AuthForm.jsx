import React, { useState } from "react";
import { apiPost } from "../api";

export default function AuthForm({ onLogin }) {
  const [mode, setMode] = useState("login"); // "login" or "register"
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState(""); // for register only
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setMsg("");
    if (mode === "login") {
      const res = await apiPost("/login", { username, password });
      if (res.user_id) {
        localStorage.setItem("user_id", res.user_id);
        onLogin(res.user_id);
      } else {
        setMsg(res.error || "Login failed");
      }
    } else {
      const res = await apiPost("/register", { username, email, password });
      if (res.user_id) {
        setMsg("Registered! Please login.");
        setMode("login");
      } else {
        setMsg(res.error || "Registration failed");
      }
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-8 p-6 bg-white rounded shadow">
      <h2 className="text-lg font-bold mb-3">{mode === "login" ? "Login" : "Register"}</h2>
      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          className="border p-2 w-full"
          placeholder="Username"
          value={username}
          onChange={e=>setUsername(e.target.value)}
          required
        />
        {mode === "register" && (
          <input
            className="border p-2 w-full"
            placeholder="Email"
            value={email}
            type="email"
            onChange={e=>setEmail(e.target.value)}
            required
          />
        )}
        <input
          className="border p-2 w-full"
          placeholder="Password"
          type="password"
          value={password}
          onChange={e=>setPassword(e.target.value)}
          required
        />
        <button className="bg-blue-600 text-white px-4 py-2 rounded w-full" type="submit">
          {mode === "login" ? "Login" : "Register"}
        </button>
      </form>
      <div className="flex justify-between mt-3">
        {mode === "login" ? (
          <button className="text-blue-700 underline text-sm" onClick={() => setMode("register")}>
            Register
          </button>
        ) : (
          <button className="text-blue-700 underline text-sm" onClick={() => setMode("login")}>
            Back to Login
          </button>
        )}
      </div>
      {msg && <div className="mt-3 text-center text-red-500">{msg}</div>}
    </div>
  );
}
