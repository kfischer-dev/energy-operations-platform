import { BrowserRouter, Routes, Route } from 'react-router';
import { MainLayout } from './layout/MainLayout'
import { SidebarProvider } from './layout/SidebarState'
import { Assets } from './pages/Assets'
import { Balance } from './pages/Balance'
import { Dashboard } from './pages/Dashboard'
// import { HeaderDesignTest } from './pages/HeaderDesignTest'
import { Simulation } from './pages/Simulation'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <SidebarProvider>
      <Routes>
        {/* <Route path="/design-test" element={<HeaderDesignTest />} /> */}
        <Route path="*" element={
          <MainLayout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/assets" element={<Assets />} />
              <Route path="/balance" element={<Balance />} />
              <Route path="/simulation" element={<Simulation />} />
            </Routes>
          </MainLayout>
        } />
      </Routes>
      </SidebarProvider>
    </BrowserRouter>
  )
}

export default App
