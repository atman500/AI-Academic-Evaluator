import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://127.0.0.1:8000/evaluate/', formData);
      setResults(res.data.results);
    } catch (err) {
      alert("Error connecting to server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>AI Academic Governance System</h1>
        <p>Categorized Evaluation: Formal, Methodological, and Applied Aspects</p>
      </header>

      <div className="upload-box">
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Analyzing..." : "Run Triple Evaluation"}
        </button>
      </div>

      {results && (
        <div className="dashboard">
          <Section title="Formal Aspect" data={results.formal} />
          <Section title="Methodological Aspect" data={results.methodological} />
          <Section title="Applied Aspect" data={results.applied} />
        </div>
      )}
    </div>
  );
}

// مكون فرعي لعرض كل قسم
const Section = ({ title, data }) => (
  <div className="card">
    <h3>{title}</h3>
    <ul>
      {data.map((item, i) => (
        <li key={i} className={item.includes('[✓]') ? 'text-ok' : item.includes('[X]') ? 'text-ko' : ''}>
          {item}
        </li>
      ))}
    </ul>
  </div>
);

export default App;