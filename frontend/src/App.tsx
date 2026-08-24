import {BrowserRouter, Navigate, Route, Routes} from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import PrivacyPage from "./pages/PrivacyPage.tsx";
import TermsPage from "./pages/TermsPage.tsx";
import LoginPage from "./pages/LoginPage.tsx";
import RegisterPage from "./pages/RegisterPage.tsx";
import RegisterSuccessPage from "./pages/RegisterSuccessPage.tsx";
import UpgradeSuccessPage from "./pages/UpgradeSuccessPage.tsx";
import AlreadySubscribedPage from "./pages/AlreadySubscribedPage.tsx";
import LoggingOutPage from "./pages/LoggingOutPage.tsx";
import ForgotPasswordPage from "./pages/ForgotPasswordPage.tsx";
import ResetPasswordPage from "./pages/ResetPasswordPage.tsx";
import ChatPage from "./pages/ChatPage.tsx";
import ProfilePage from "./pages/ProfilePage.tsx";

function GuestRoute({ children }: { children: React.ReactNode }) {
    const token = localStorage.getItem('token')
    if (token) return <Navigate to="/chat" replace />
    return <>{children}</>
}

function App() {

    return(<>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<GuestRoute><LandingPage /></GuestRoute>} />
                <Route path="/privacy" element={<PrivacyPage />} />
                <Route path="/terms" element={<TermsPage />}/>
                <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
                <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />
                <Route path ="/register-success" element={<RegisterSuccessPage />} />
                <Route path="/dashboard" element={<UpgradeSuccessPage />} />
                <Route path="/already-subscribed" element={<AlreadySubscribedPage />} />
                <Route path="/logging-out" element={<LoggingOutPage />} />
                <Route path="/forgot-password" element={<GuestRoute><ForgotPasswordPage /></GuestRoute>} />
                <Route path="/reset-password" element={<GuestRoute><ResetPasswordPage /></GuestRoute>} />
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/profile" element={<ProfilePage />} />
            </Routes>
        </BrowserRouter>
    </>)
}

export default App