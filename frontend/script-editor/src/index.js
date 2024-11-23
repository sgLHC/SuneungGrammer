import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App"; // App.js를 기본 내보내기로 가져옵니다.
import "./App.css"; // 스타일 파일을 가져옵니다.

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
