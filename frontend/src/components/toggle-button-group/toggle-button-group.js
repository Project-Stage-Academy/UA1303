import { useState } from 'react';
import './toggle-button-group.css';

const ToggleButtonGroup = ( { options, onChange }) => {
  const [activeKey, setActiveKey] = useState(Object.keys(options)[0]); // First button selected by default

  const handleToggle = (key) => {
    setActiveKey(key); // Update active button
    if (onChange) {
        onChange(key); // Notify parent component of change
    }
  };

  return (
    <div className="toggle-button-group">
      {Object.entries(options).map(([key, value]) => (
        <button
          key={key} // Used as unqiue identifier to make request based on selected item
          type="button"
          className={`toggle-button ${activeKey === key ? 'active' : ''}`}
          onClick={() => handleToggle(key)} // key is passed in parent component on toggle
        >
          {value}
        </button>
      ))}
    </div>
  );
};

export default ToggleButtonGroup;