import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import logo from './logo.svg';
import './App.css';
import Login from './Login';
import ChatBot from './ChatBot';
import PyCode from './PyCode';
import NavigationBar from './NavigationBar';
import { AuthProvider, useAuth } from './AuthContext';

const App = () => {
  return (
    <AuthProvider>
      <div className="app-container">
        <Router>
          <NavigationBar />
          <div className="content-container">
            <Routes>
              <Route path="/" element={<Navigate to="/login" />} />
              <Route path="/login" element={<Login />} />
              <Route
                path="/chat"
                element={<PrivateRoute element={<ChatBot />} />}
              />
              <Route
                path="/code"
                element={<PrivateRoute element={<PyCode />} />}
              />
            </Routes>
          </div>
        </Router>
      </div>
    </AuthProvider>
  );
};


const PrivateRoute = ({ element, ...rest }) => {
  const { isLoggedIn } = useAuth();

  return isLoggedIn ? element : <Navigate to="/login" />;
};


export default App;
