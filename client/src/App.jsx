import { useState } from "react"
import "./App.css"

export default function App() {
  const [query, setQuery] = useState("")
  const [days, setDays] = useState("7")
  const [repos, setRepos] = useState([])
  const [summary, setSummary] = useState("")

  const handleSearch = async () => {
    const res = await fetch("http://127.0.0.1:5000/summary", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, days }),
    })

    const data = await res.json()
    setRepos(data.repos)
    setSummary(data.summary)
  }

  return (
    <div className="container">
      <h1>Research Agent</h1>

      {/* 검색 영역 */}
      <div className="search-box">
        <input
          placeholder="검색할 주제를 입력하세요 (예: robot, AI, python)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        <select value={days} onChange={(e) => setDays(e.target.value)}>
          <option value="180">6개월</option>
          <option value="365">1년</option>
          <option value="1095">3년</option>
        </select>

        <button onClick={handleSearch}>검색</button>
      </div>

      {/* 레포 목록 */}
      {repos.length > 0 && (
        <>
          <div className="section-title">레포 목록</div>
          {repos.map((repo) => (
            <div key={repo.id} className="repo-card">
              <div className="repo-name">{repo.full_name}</div>
              <div>{repo.description}</div>
            </div>
          ))}
        </>
      )}

      {/* 요약 */}
      {summary && (
        <>
          <div className="section-title">AI 요약</div>
          <div className="summary-box">{summary}</div>
        </>
      )}
    </div>
  )
}
