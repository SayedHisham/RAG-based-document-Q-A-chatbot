import React, { useState, useRef } from "react"

export default function App() {
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState("")
  const [status, setStatus] = useState("idle")
  const [isLoading, setIsLoading] = useState(false)
  const fileInputRef = useRef(null)

  const uploadFile = async (file) => {
    const formData = new FormData()
    formData.append("file", file)
    setStatus("processing")

    const response = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData
    })
    const data = await response.json()
    pollStatus()
  }

  const pollStatus = () => {
    const interval = setInterval(async () => {
      const response = await fetch("http://localhost:8000/status")
      const data = await response.json()
      setStatus(data.status)

      if (data.status === "ready" || data.status === "error") {
        clearInterval(interval)
      }
    }, 2000)
  }

  const askQuestion = async () => {
    if (!question.trim()) return
    
    const userMessage = { sender: "user", text: question }
    setMessages(prev => [...prev, userMessage])
    setQuestion("")
    setIsLoading(true)

    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    })
    const data = await response.json()

    const botMessage = { sender: "bot", text: data.answer || data.error }
    setMessages(prev => [...prev, botMessage])
    setIsLoading(false)
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", backgroundColor: "#0f172a", color: "white", fontFamily: "sans-serif" }}>
      
      {/* Header */}
      <div style={{ padding: "16px 24px", backgroundColor: "#1e293b", borderBottom: "1px solid #334155" }}>
        <h1 style={{ margin: 0, fontSize: "20px", fontWeight: "bold" }}>📄 RAG Document Chatbot</h1>
        <p style={{ margin: "4px 0 0", fontSize: "13px", color: "#94a3b8" }}>Upload a PDF and ask questions about it</p>
      </div>

      {/* Upload Bar */}
      <div style={{ padding: "12px 24px", backgroundColor: "#1e293b", borderBottom: "1px solid #334155", display: "flex", alignItems: "center", gap: "12px" }}>
        <input
          type="file"
          accept=".pdf"
          ref={fileInputRef}
          onChange={(e) => uploadFile(e.target.files[0])}
          style={{ display: "none" }}
        />
        <button
          onClick={() => fileInputRef.current.click()}
          style={{ padding: "8px 16px", backgroundColor: "#3b82f6", border: "none", borderRadius: "6px", color: "white", cursor: "pointer", fontSize: "14px" }}
        >
          Upload PDF
        </button>
        <span style={{ fontSize: "13px", color: status === "ready" ? "#22c55e" : status === "processing" ? "#f59e0b" : status === "error" ? "#ef4444" : "#94a3b8" }}>
          {status === "idle" && "No document uploaded"}
          {status === "processing" && "⏳ Processing document..."}
          {status === "ready" && "✅ Document ready!"}
          {status === "error" && "❌ Error processing document"}
        </span>
      </div>

      {/* Chat Window */}
      <div style={{ flex: 1, overflowY: "auto", padding: "24px", display: "flex", flexDirection: "column", gap: "12px" }}>
        {messages.length === 0 && (
          <div style={{ textAlign: "center", color: "#475569", marginTop: "80px" }}>
            <p style={{ fontSize: "16px" }}>Upload a PDF to get started</p>
            <p style={{ fontSize: "13px" }}>Then ask any question about your document</p>
          </div>
        )}
        {messages.map((msg, index) => (
          <div key={index} style={{ display: "flex", justifyContent: msg.sender === "user" ? "flex-end" : "flex-start" }}>
            <div style={{
              maxWidth: "70%",
              padding: "10px 14px",
              borderRadius: msg.sender === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
              backgroundColor: msg.sender === "user" ? "#3b82f6" : "#1e293b",
              fontSize: "14px",
              lineHeight: "1.5"
            }}>
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div style={{ display: "flex", justifyContent: "flex-start" }}>
            <div style={{ padding: "10px 14px", borderRadius: "18px 18px 18px 4px", backgroundColor: "#1e293b", fontSize: "14px", color: "#94a3b8" }}>
              Thinking...
            </div>
          </div>
        )}
      </div>

      {/* Input Bar */}
      <div style={{ padding: "16px 24px", backgroundColor: "#1e293b", borderTop: "1px solid #334155", display: "flex", gap: "12px" }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && askQuestion()}
          placeholder="Ask a question about your document..."
          style={{ flex: 1, padding: "10px 14px", backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "6px", color: "white", fontSize: "14px", outline: "none" }}
        />
        <button
          onClick={askQuestion}
          disabled={isLoading || status !== "ready"}
          style={{ padding: "10px 20px", backgroundColor: isLoading || status !== "ready" ? "#334155" : "#3b82f6", border: "none", borderRadius: "6px", color: "white", cursor: isLoading || status !== "ready" ? "not-allowed" : "pointer", fontSize: "14px" }}
        >
          Send
        </button>
      </div>

    </div>
  )
}