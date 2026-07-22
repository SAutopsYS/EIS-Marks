import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import StudentDetail from './pages/StudentDetail'
import StudentsList from './pages/StudentsList'
import Summary from './pages/Summary'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<StudentsList />} />
          <Route path="students/:admissionNo" element={<StudentDetail />} />
          <Route path="summary" element={<Summary />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
