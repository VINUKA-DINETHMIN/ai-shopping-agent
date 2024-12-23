import React, { useState } from "react";

function App() {
  const [criteria, setCriteria] = useState({ budget: "", product: "" });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setCriteria({ ...criteria, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); // Show loading state

    try {
      const response = await fetch("http://localhost:5000/api/auth/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(criteria),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch recommendations.");
      }

      const data = await response.json();
      console.log(data); // Log the response data
      setResults(data);
    } catch (error) {
      console.error(error);
      setResults([]); // Clear results on error
    } finally {
      setLoading(false); // Hide loading state
    }
  };

  return (
    <div>
      <h1>AI Shopping Agent</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Budget:
          <input
            type="number"
            name="budget"
            value={criteria.budget}
            onChange={handleChange}
            required
          />
        </label>
        <br />
        <label>
          Product Type:
          <input
            type="text"
            name="product"
            value={criteria.product}
            onChange={handleChange}
            required
          />
        </label>
        <br />
        <button type="submit" disabled={loading}>
          {loading ? "Loading..." : "Get Recommendations"}
        </button>
      </form>
      <h2>Recommendations:</h2>
      <ul>
        {results.length === 0 ? (
          <li>No recommendations available.</li>
        ) : (
          results.map((item, index) => (
            <li key={index}>
              {item.name} - Rs. {item.price}
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

export default App;
