import './startup-card.css';

const StartupCard = ({ image, company_name, city, country, industry }) => {
  return (
    <div className="card">
      <img src={image} alt={company_name} className="card-image" />
      <div className="card-content">
        <p className="card-industry">{industry}</p>
        <h4 className="card-title">{company_name}</h4>
        <p className="card-location">
          {city}, {country}
        </p>
      </div>
    </div>
  );
};

export default StartupCard;