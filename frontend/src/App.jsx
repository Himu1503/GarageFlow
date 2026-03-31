import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import { CustomerLoginPage } from "./pages/CustomerLoginPage";
import { CustomerRegisterPage } from "./pages/CustomerRegisterPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LandingPage } from "./pages/LandingPage";
import { UserLoginPage } from "./pages/UserLoginPage";
import { UserRegisterPage } from "./pages/UserRegisterPage";

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login/user" replace />;
  return children;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login/user" element={<UserLoginPage />} />
      <Route path="/login/customer" element={<CustomerLoginPage />} />
      <Route path="/register/user" element={<UserRegisterPage />} />
      <Route path="/register/customer" element={<CustomerRegisterPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
