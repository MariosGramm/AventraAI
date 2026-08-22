import {BrowserRouter, Route, Routes} from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import PrivacyPage from "./pages/PrivacyPage.tsx";
import TermsPage from "./pages/TermsPage.tsx";
import LoginPage from "./pages/LoginPage.tsx";
import RegisterPage from "./pages/RegisterPage.tsx";
import RegisterSuccessPage from "./pages/RegisterSuccessPage.tsx";
import UpgradeSuccessPage from "./pages/UpgradeSuccessPage.tsx";
import AlreadySubscribedPage from "./pages/AlreadySubscribedPage.tsx";
import LoggingOutPage from "./pages/LoggingOutPage.tsx";
import ChatPage from "./pages/ChatPage.tsx";


function App() {

    return(<>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/privacy" element={<PrivacyPage />} />
                <Route path="/terms" element={<TermsPage />}/>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path ="/register-success" element={<RegisterSuccessPage />} />
                <Route path="/dashboard" element={<UpgradeSuccessPage />} />
                <Route path="/already-subscribed" element={<AlreadySubscribedPage />} />
                <Route path="/logging-out" element={<LoggingOutPage />} />
                <Route path="/chat" element={<ChatPage />} />
            </Routes>
        </BrowserRouter>
    </>)
}

export default App