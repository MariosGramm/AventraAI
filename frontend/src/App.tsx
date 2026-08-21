import {BrowserRouter, Route, Routes} from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import PrivacyPage from "./pages/PrivacyPage.tsx";
import TermsPage from "./pages/TermsPage.tsx";
import LoginPage from "./pages/LoginPage.tsx";


function App() {

    return(<>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/privacy" element={<PrivacyPage />} />
                <Route path="/terms" element={<TermsPage />}/>
                <Route path="/login" element={<LoginPage />} />
            </Routes>
        </BrowserRouter>
    </>)
}

export default App