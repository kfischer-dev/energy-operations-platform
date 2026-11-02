import { useState } from 'react';
import { Header } from '../layout/Header';
import { ModernHeader } from '../layout/ModernHeader';
import { Sidebar } from '../layout/Sidebar';
import { Dashboard } from './Dashboard';
import '../layout/MainLayout.css';
import './HeaderDesignTest.css';

export function HeaderDesignTest() {
    const [variant, setVariant] = useState<'modern' | 'current'>('modern');

    return (
        <div className="main-layout header-design-page">
            {variant === 'modern' ? <ModernHeader /> : <Header />}
            <Sidebar />
            <main className="main-content">
                <section className="header-design-page__toolbar" aria-label="Header design comparison">
                    <div>
                        <span className="header-design-page__label">DESIGN LAB / 01</span>
                        <h2>Header Design Test</h2>
                        <p>Compare both headers in the existing dashboard.</p>
                    </div>
                    <div className="header-design-page__switch" role="group" aria-label="Header design">
                        <button type="button" aria-pressed={variant === 'current'} onClick={() => setVariant('current')}>
                            Current
                        </button>
                        <button type="button" aria-pressed={variant === 'modern'} onClick={() => setVariant('modern')}>
                            Modern
                        </button>
                    </div>
                </section>
                <Dashboard />
            </main>
        </div>
    );
}
