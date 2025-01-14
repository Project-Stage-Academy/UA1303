import './button.css'

const Button = ({ text, onClick, variant = 'default', style }) => {
    const buttonClass = `button ${variant}`;

    return (
        <button className={buttonClass} style ={style} onClick={onClick}>{
            text}
        </button>
    );
};

export default Button;