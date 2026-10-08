import './App.css'
import BalanceSummaryComponent from './components/BalanceSummary'
import { MainLayout } from './layout/MainLayout'

function App() {


  return (
    <>
      <MainLayout>
        <div className="app-container">
          <h1>Hello, Energy Operations Platform!</h1>
          <p>Frontend connected successfully!</p>
        </div>
        <div className="balance-summary-container">
          <BalanceSummaryComponent />
        </div>
      </MainLayout>
    </>
  )
}

export default App
