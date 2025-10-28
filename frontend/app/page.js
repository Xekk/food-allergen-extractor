"use client";
import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [preview, setPreview] = useState("");

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!file) return alert("Please select a PDF file.");
    setLoading(true);
    setData(null);

    const formData = new FormData();
    formData.append("file", file);
    const API_URL = process.env.NEXT_PUBLIC_API_URL;

    try {
      const res = await axios.post(`${API_URL}/upload`, formData, {
  headers: { "Content-Type": "multipart/form-data" },
});

      setData(res.data.extracted);
      setPreview(res.data.preview);
    } catch (err) {
      alert("Error uploading file: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "extracted_data.json";
    link.click();
    URL.revokeObjectURL(url);
  };

  const renderTable = (title, obj) => (
    <div style={styles.tableContainer}>
      <h3>{title}</h3>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>Name</th>
            <th style={styles.th}>Value</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(obj).map(([key, val]) => (
            <tr key={key}>
              <td style={styles.td}>{key}</td>
              <td style={styles.td}>{val || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <main style={styles.container}>
      <h1 style={styles.title}>🥗 Allergen & Nutrition Extractor</h1>

      <div style={styles.uploadBox}>
        <input type="file" accept="application/pdf" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={loading} style={styles.button}>
          {loading ? "Processing..." : "Upload & Extract"}
        </button>
      </div>

      {loading && <p>⏳ Processing your file...</p>}

      {data && !data.error && (
        <div style={styles.result}>
          {renderTable("Allergens", data.allergens)}
          {renderTable("Nutritional Values (per 100g)", data.nutrition_per_100g)}

          <button style={styles.downloadButton} onClick={downloadJSON}>
            💾 Download JSON
          </button>

          <h3 style={{ marginTop: "2rem" }}>📄 Text Preview</h3>
          <pre style={styles.preview}>{preview}</pre>
        </div>
      )}

      {data && data.error && (
        <div style={styles.errorBox}>
          <h3>Error parsing output</h3>
          <pre>{data.raw}</pre>
        </div>
      )}
    </main>
  );
}

const styles = {
  container: {
    fontFamily: "Arial, sans-serif",
    padding: "2rem",
    textAlign: "center",
    maxWidth: "900px",
    margin: "auto",
  },
  title: {
    color: "#2c3e50",
    marginBottom: "2rem",
  },
  uploadBox: {
    marginBottom: "2rem",
  },
  button: {
    marginLeft: "10px",
    padding: "10px 20px",
    cursor: "pointer",
  },
  downloadButton: {
    background: "#27ae60",
    color: "white",
    border: "none",
    padding: "10px 20px",
    borderRadius: "6px",
    cursor: "pointer",
    marginBottom: "20px",
  },
  result: {
    textAlign: "left",
    background: "#f9f9f9",
    padding: "20px",
    borderRadius: "8px",
  },
  tableContainer: {
    marginBottom: "2rem",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
  },
  th: {
    background: "#34495e",
    color: "white",
    padding: "8px",
  },
  td: {
    border: "1px solid #ddd",
    padding: "8px",
  },
  preview: {
    background: "#fafafa",
    border: "1px solid #eee",
    padding: "10px",
    borderRadius: "4px",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
  errorBox: {
    background: "#ffe6e6",
    border: "1px solid #ffb3b3",
    padding: "20px",
    borderRadius: "8px",
  },
};
