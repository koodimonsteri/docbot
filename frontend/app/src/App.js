import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import logo from './logo.svg';
import './App.css';
import ChatBot from './ChatBot';
import PyCode from './PyCode';
import NavigationBar from './NavigationBar';

function App() {
  return (
  <div className="app-container">
    <Router>
      <NavigationBar />
      <div className="content-container">
        <Routes>
          <Route path="/" element={<Navigate to="/chat" />} />
          <Route path="/chat" element={<ChatBot/>}/>
          <Route path="/code" element={<PyCode/>} />
        </Routes>
      </div>
    </Router>
  </div>
  );
}


export default App;
