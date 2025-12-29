import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { BlackScholesLab } from './components/BSLab/BlackScholesLab';
import './App.css'

function Home() {
  return (
    <div style={{ padding: '2rem', color: '#fff', fontFamily: 'Inter, sans-serif' }}>
      <h1>Quant Tools</h1>
      <p>Welcome to the Quant Developer Portal.</p>
      <nav>
        <Link to="/black-scholes-lab" style={{ color: '#38bdf8', textDecoration: 'none', fontSize: '1.2rem' }}>
          ➜ Open Black–Scholes Lab
        </Link>
      </nav>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/black-scholes-lab" element={<BlackScholesLab />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
