import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { NavigationBar } from "./components/NavigationBar"
import { Dashboard } from "./pages/Dashboard"
import { FlashcardsPage } from "./pages/FlashcardsPage"
import { StudyPlanPage } from "./pages/StudyPlanPage"
import { ExamPage } from "./pages/ExamPage"
import { UploadPage } from "./pages/UploadPage"
import { SettingsPage } from "./components/SettingsPage"
import { ThemeProvider } from "./contexts/ThemeContext"

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
          <NavigationBar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/flashcards" element={<FlashcardsPage />} />
              <Route path="/study-plan" element={<StudyPlanPage />} />
              <Route path="/exam" element={<ExamPage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ThemeProvider>
  )
}

export default App
