import { ModernHeader } from '../layout/ModernHeader';
import { Sidebar } from '../layout/Sidebar';
import { Dashboard } from './Dashboard';
import '../layout/MainLayout.css';
import './HeaderDesignTest.css';

export function HeaderDesignTest() {
    return (
        <div className="main-layout header-design-page">
            <ModernHeader />
            <Sidebar />
            <main className="main-content">
                <section className="header-design-page__toolbar" aria-label="Dashboard card settings">
                    <div>
                        <span className="header-design-page__label">DESIGN LAB / 01</span>
                        <h2>Dashboard Design Test</h2>
                        <p>Choose which cards to show in the dashboard.</p>
                    </div>
                </section>
                <Dashboard />
            </main>
        </div>
    );
}
