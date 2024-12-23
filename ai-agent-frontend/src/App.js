import React, { useState, useEffect } from "react";
import './App.css'; // Import the CSS file for styling

function App() {
  const [criteria, setCriteria] = useState({ budget: "", product: "" });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sortOption, setSortOption] = useState("price");
  const [filterText, setFilterText] = useState("");
  const [useNLP, setUseNLP] = useState(false);
  const [currency, setCurrency] = useState("USD");
  const [language, setLanguage] = useState("en");

  // Voice Recognition setup
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState(""); // State to store the voice input
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

  useEffect(() => {
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onend = () => {
      setIsListening(false);
      // Check if both criteria (budget and product) are set before triggering the form submission
      if (criteria.budget && criteria.product) {
        document.querySelector('.submit-button').click();
      }
    };

    recognition.onresult = (event) => {
      const latestTranscript = event.results[event.results.length - 1][0].transcript;
      setTranscript(latestTranscript); // Update the transcript with the latest result

      // Extract budget and product from the transcript
      const budgetMatch = latestTranscript.match(/\d+/); // Extract number from the command
      const productMatch = latestTranscript.replace("product", "").trim();

      if (budgetMatch) {
        setCriteria((prev) => ({ ...prev, budget: budgetMatch[0] }));
      }

      if (productMatch) {
        setCriteria((prev) => ({ ...prev, product: productMatch }));
      }

      // Automatically submit the form after capturing both budget and product
      if (budgetMatch && productMatch) {
        document.querySelector('.submit-button').click();
      }
    };

    return () => {
      recognition.stop();
    };
  }, [criteria]);

  const handleChange = (e) => {
    setCriteria({ ...criteria, [e.target.name]: e.target.value });
  };

  const handleSortChange = (e) => {
    setSortOption(e.target.value);
    setResults((prevResults) =>
      [...prevResults].sort((a, b) => (e.target.value === "price" ? a.price - b.price : a.name.localeCompare(b.name)))
    );
  };

  const handleFilterChange = (e) => {
    setFilterText(e.target.value);
  };

  const handleNLPChange = (e) => {
    setUseNLP(e.target.checked);
  };

  const handleCurrencyChange = (e) => {
    setCurrency(e.target.value);
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/auth/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...criteria, use_nlp: useNLP, currency, language }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch recommendations.");
      }

      const data = await response.json();
      setResults(data.sort((a, b) => a.price - b.price));
    } catch (error) {
      console.error(error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredResults = results.filter((item) =>
    item.name.toLowerCase().includes(filterText.toLowerCase())
  );

  const startListening = () => {
    recognition.start();
  };

  return (
    <div className="app-container">
      <h1 className="title">AI Shopping Agent</h1>
      <form onSubmit={handleSubmit} className="form-container">
        <div className="form-group">
          <label>Budget:</label>
          <input
            type="number"
            name="budget"
            value={criteria.budget}
            onChange={handleChange}
            required
            className="input-field"
          />
        </div>
        
        <div className="form-group">
          <label>Product Type:</label>
          <input
            type="text"
            name="product"
            value={criteria.product}
            onChange={handleChange}
            required
            className="input-field"
          />
        </div>
        <div className="form-group">
          <label>Use NLP for better results:</label>
          <input
            type="checkbox"
            checked={useNLP}
            onChange={handleNLPChange}
            className="checkbox"
          />
        </div>
        <div className="form-group">
          <label>Currency:</label>
          <select value={currency} onChange={handleCurrencyChange} className="select-field">
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="INR">INR</option>
          </select>
        </div>
        <div className="form-group">
          <label>Language:</label>
          <select value={language} onChange={handleLanguageChange} className="select-field">
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
          </select>
        </div>
        <button
          type="button"
          onClick={startListening}
          className="voice-button"
          disabled={isListening}
        >
          {isListening ? "Listening..." : "Voice Command for Budget and Product"}
        </button>
        <button type="submit" disabled={loading} className="submit-button">
          {loading ? "Loading..." : "Get Recommendations"}
        </button>
      </form>

      <div className="transcript-container">
        <h3>Voice Input:</h3>
        <p>{transcript}</p>
      </div>

      <div className="filters-container">
        <h2>Filters & Sorting</h2>
        <div className="filter-group">
          <label>Sort by:</label>
          <select value={sortOption} onChange={handleSortChange} className="select-field">
            <option value="price">Price</option>
            <option value="name">Name</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Filter by Name:</label>
          <input
            type="text"
            value={filterText}
            onChange={handleFilterChange}
            placeholder="Enter product name"
            className="input-field"
          />
        </div>
      </div>

      <h2>Recommendations:</h2>
      <div className="recommendations-container">
        {filteredResults.length === 0 ? (
          <p>No recommendations available.</p>
        ) : (
          filteredResults.map((item, index) => (
            <div key={index} className="recommendation-card">
              <a href={item.url} target="_blank" rel="noopener noreferrer" className="recommendation-link">
                <h3>{item.name}</h3>
                <p>Price: {currency === "INR" ? `₹${item.price * 75}` : currency === "EUR" ? `€${item.price * 0.9}` : `$${item.price}`}</p>
              </a>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;
