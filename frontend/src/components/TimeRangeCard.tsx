import { useState } from 'react';
import calendarIcon from '../assets/icons/calendar-clock.svg';
import './TimeRangeCard.css';


export function TimeRangeCard({ onApply }: {
    onApply: (start: string, end: string) => void
 }) {
    const [startTime, setStartTime] = useState('');
    const [endTime, setEndTime] = useState('');

    function handleApply() {
        if (!startTime || !endTime || startTime >= endTime) {
            return;
        }
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
                <label htmlFor="start-time">Start time:</label>
                <input 
                    id="start-time"
                    type="datetime-local" 
                    value={startTime} 
                    onChange={(e) => setStartTime(e.target.value)} 
                />
                <label htmlFor="end-time">End time:</label>
                <input 
                    id="end-time"
                    type="datetime-local" 
                    value={endTime} 
                    onChange={(e) => setEndTime(e.target.value)} 
                />
                <button type="button" onClick={handleApply}>
                    Apply Range
                </button>
            </form>
        </div>
    );
}