import { useState } from 'react';
import calendarIcon from '../assets/icons/calendar-clock.svg';
import './TimeRangeCard.css';


export function TimeRangeCard({ onApply }: {
    onApply: (start: string, end: string) => void
}) {
    const [startTime, setStartTime] = useState('2026-09-01T00:00');
    const [endTime, setEndTime] = useState('2026-09-02T00:00');
    const [error, setError] = useState('');

    function handleApply() {
        if (!startTime || !endTime) {
            setError('Please select both start and end time.');
            return;
        }

        if (new Date(startTime) >= new Date(endTime)) {
            setError('End time must be after start time.');
            return;
        }

        setError('');

        onApply(
            new Date(startTime).toISOString(),
            new Date(endTime).toISOString()
        );
    }

    return (
        <div className="time-range-card">
            <header>
                <img src={calendarIcon} alt="[Time Range]" />
                <h3> Time Range</h3>
            </header>
            <form>
                <div className="time-range-inputs">
                    <div className="time-range-field">
                        <label htmlFor="start-time">Start time:</label>
                        <input
                            id="start-time"
                            type="datetime-local"
                            value={startTime}
                            onChange={(e) => setStartTime(e.target.value)}
                        />
                    </div>
                    <div className="time-range-field">
                        <label htmlFor="end-time">End time:</label>
                        <input
                            id="end-time"
                            type="datetime-local"
                            value={endTime}
                            onChange={(e) => setEndTime(e.target.value)}
                        />
                    </div>
                </div>
                <button type="button" onClick={handleApply}>
                    Apply Range
                </button>

                {error && <p className="time-range-error" role="alert">{error}</p>}
            </form>
        </div>
    );
}