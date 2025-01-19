import './input-form.css';

const Form = ({ headerText, children, footerContent, onSubmit }) => {
    return (
      <form className="form" onSubmit={onSubmit}>
        {/* Form Header */}
        <div className="form-header">
          <h3>{headerText}</h3>
        </div>
  
        {/* Form Body */}
        <div className="form-body">
          {children}
        </div>
  
        {/* Form Footer */}
        <div className="form-footer">
          {footerContent}
        </div>
      </form>
    );
  };
  
  export default Form;